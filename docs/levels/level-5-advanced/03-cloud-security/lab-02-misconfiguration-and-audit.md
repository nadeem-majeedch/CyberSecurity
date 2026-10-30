---
title: "LAB-503-02 · Misconfiguration Detection and Audit Logs"
description: "Scan deliberately unsafe infrastructure-as-code, fix it to a clean result, record one accepted risk, and reconstruct a cloud attack from audit events."
module_code: CYB-503
level: 5
kind: lab
prerequisites: [CYB-503]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-503-02]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [cloud, misconfiguration, checkov, terraform, cloudtrail, secrets]
---

# LAB-503-02 · Misconfiguration Detection and Audit Logs

!!! note "How this walkthrough was produced"
    The Checkov commands and expected output below were written against current vendor documentation and the
    pinned versions in the tool table. They were **not** captured from a verified run in the author's lab.
    Treat the output as a **shape**, not a transcript: field order, wording and version banners differ between
    releases. Record what you actually see, and report a deviation rather than adjusting your output to match
    this page.

## Scenario and background

A team has committed infrastructure-as-code for an evidence-processing service. It has a public bucket, SSH open to
the world, an admin IAM policy, an unencrypted volume, a single-region trail and an access key in the source.

You will scan it, fix it, record one accepted risk properly, and then investigate a set of audit events showing what
happens when the same template reaches production.

**Nothing is deployed.** `checkov` reads the files; the "cloud" in part two is a JSON extract.

## Learning objectives

1. Run static analysis over Terraform and interpret findings without blindly applying fixes.
2. Remediate the misconfiguration classes that cause most cloud incidents.
3. Record an accepted risk with a baseline, and state its cost.
4. Scan code for committed secrets.
5. Reconstruct an intrusion from audit-log events and identify the control that failed.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | For `checkov` |
| `checkov` | 3.x | `pip install checkov` in a venv |
| Terraform | 1.6+ | Optional; only for `validate`, never `apply` |

```bash
python3 -m venv ~/cloud-lab/venv
~/cloud-lab/venv/bin/pip install --upgrade pip checkov
~/cloud-lab/venv/bin/checkov --version
```

Record the version: check IDs and default checks change between releases.

## Threat model

- A public bucket is readable by anyone, with no credential and no log entry worth trusting.
- Open SSH invites credential stuffing and exploits against the daemon.
- An admin IAM policy turns one stolen key into full account control.
- A single-region trail misses activity everywhere else, and `StopLogging` ends the record entirely.

## Environment

```bash
mkdir -p ~/cloud-lab/iac && cd ~/cloud-lab/iac
```

`main.tf`:

```hcl
provider "aws" { region = "eu-west-1" }

resource "aws_s3_bucket" "evidence" {
  bucket = "lab-evidence-bucket"
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_security_group" "admin" {
  name = "admin-access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ebs_volume" "data" {
  availability_zone = "eu-west-1a"
  size              = 20
}

resource "aws_iam_policy" "service" {
  name = "evidence-service"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}

resource "aws_cloudtrail" "audit" {
  name                          = "audit"
  s3_bucket_name                = aws_s3_bucket.evidence.id
  include_global_service_events = false
  is_multi_region_trail         = false
  enable_log_file_validation    = false
}
```

`variables.tf` — the committed secret:

```hcl
variable "deploy_key" {
  description = "CI key"
  default     = "AKIAIOSFODNN7EXAMPLE"
}
```

## Procedure

### 1. Scan

```bash
cd ~/cloud-lab/iac
~/cloud-lab/venv/bin/checkov -d . --framework terraform --compact
```

**Expected:** a non-zero exit and a list of failed checks covering public ACL, public access block, unencrypted
bucket and volume, open ingress on 22 and 5432, wildcard IAM policy, and trail settings. **Check IDs vary by version** —
record the ones you get rather than copying a table.

Count them:

```bash
~/cloud-lab/venv/bin/checkov -d . --framework terraform --compact -o json > before.json
python3 -c "import json;d=json.load(open('before.json'));r=d['results']['failed_checks'];print('failed:',len(r));print(sorted({c['check_id'] for c in r}))"
```

### 2. Scan for secrets

```bash
~/cloud-lab/venv/bin/checkov -d . --framework secrets --compact
```

**Expected:** the `AKIA...` value is flagged. It is AWS's published example key and cannot authenticate anything; the
detector is matching a pattern, which is exactly what it should do. The lesson is that a pattern-matching scanner will
also flag documentation — so secrets must never be in the repository in the first place.

Also check history, because deleting the line does not remove it:

```bash
cd ~/cloud-lab/iac && git init -q 2>/dev/null; git add -A 2>/dev/null; git -c user.email=l@lab -c user.name=lab commit -qm "iac" 2>/dev/null
sed -i 's/AKIAIOSFODNN7EXAMPLE/REDACTED/' variables.tf
git -c user.email=l@lab -c user.name=lab commit -qam "remove key"
git log -p --all | grep -c AKIAIOSFODNN7EXAMPLE
```

**Expected:** a count of at least 1 — the key is still in history. Rotation, not deletion, is the fix.

### 3. Fix, one class at a time

Replace `main.tf` with:

```hcl
provider "aws" { region = "eu-west-1" }

resource "aws_s3_bucket" "evidence" {
  bucket = "lab-evidence-bucket"
}

resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

resource "aws_s3_bucket_versioning" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_security_group" "admin" {
  name = "admin-access"

  ingress {
    description = "Admin SSH from the office range only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["192.0.2.0/24"]
  }

  egress {
    description = "Package updates via NAT"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ebs_volume" "data" {
  availability_zone = "eu-west-1a"
  size              = 20
  encrypted         = true
}

resource "aws_iam_policy" "service" {
  name = "evidence-service"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "arn:aws:s3:::lab-evidence-bucket/evidence/*"
    }]
  })
}

resource "aws_cloudtrail" "audit" {
  name                          = "audit"
  s3_bucket_name                = aws_s3_bucket.evidence.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
}
```

Re-scan:

```bash
~/cloud-lab/venv/bin/checkov -d . --framework terraform --compact
echo "exit=$?"
```

**Expected:** remaining failures, if any, are narrowed to specific checks. Read each one before changing code — a
scanner is a reviewer, not an authority. If a check demands something your design genuinely cannot do, that is an
accepted risk, not a bug to silence.

### 4. Record one accepted risk

The 443 egress rule is required for package updates. Accept it with a baseline rather than deleting it or ignoring the
whole scan:

```bash
~/cloud-lab/venv/bin/checkov -d . --framework terraform --create-baseline
ls -la .checkov.baseline
~/cloud-lab/venv/bin/checkov -d . --framework terraform --baseline .checkov.baseline --compact
```

**Expected:** the accepted finding no longer fails the build. Write the acceptance in `RISK-ACCEPT-001.md`:

- What is accepted, and the exact check ID.
- Why the control cannot be met (packages must reach the vendor).
- Compensating controls: egress restricted by proxy, DNS filtering, flow logs.
- Owner and review date.

**The cost of a baseline:** it also hides *new* occurrences of that same check. Say so in the document, and require
the baseline to be reviewed at each release.

### 5. Investigate the audit events

`audit-events.json` (one JSON object per line):

```json
{"eventTime":"2026-10-29T08:12:03Z","eventName":"DescribeTrails","userIdentity":{"arn":"arn:aws:iam::111122223333:user/svc-report"},"sourceIPAddress":"198.51.100.24","requestParameters":null,"errorCode":null}
{"eventTime":"2026-10-29T08:12:41Z","eventName":"StopLogging","userIdentity":{"arn":"arn:aws:iam::111122223333:user/svc-report"},"sourceIPAddress":"198.51.100.24","requestParameters":{"name":"audit"},"errorCode":null}
{"eventTime":"2026-10-29T08:13:02Z","eventName":"PutBucketPolicy","userIdentity":{"arn":"arn:aws:iam::111122223333:user/svc-report"},"sourceIPAddress":"198.51.100.24","requestParameters":{"bucketName":"lab-evidence-bucket","policy":"{\"Principal\":{\"AWS\":\"*\"},\"Action\":\"s3:GetObject\"}"},"errorCode":null}
{"eventTime":"2026-10-29T08:14:10Z","eventName":"CreateAccessKey","userIdentity":{"arn":"arn:aws:iam::111122223333:user/svc-report"},"sourceIPAddress":"198.51.100.24","requestParameters":{"userName":"svc-ci"},"errorCode":null}
{"eventTime":"2026-10-29T08:15:55Z","eventName":"AttachUserPolicy","userIdentity":{"arn":"arn:aws:iam::111122223333:user/svc-report"},"sourceIPAddress":"198.51.100.24","requestParameters":{"userName":"svc-ci","policyArn":"arn:aws:iam::aws:policy/AdministratorAccess"},"errorCode":null}
{"eventTime":"2026-10-29T08:21:19Z","eventName":"GetObject","userIdentity":{"arn":"arn:aws:iam::111122223333:user/svc-report"},"sourceIPAddress":"203.0.113.77","requestParameters":{"bucketName":"lab-evidence-bucket","key":"evidence/2026/case-notes.pdf"},"errorCode":"AccessDenied"}
{"eventTime":"2026-10-29T08:22:02Z","eventName":"GetObject","userIdentity":{"arn":"arn:aws:iam::111122223333:user/svc-report"},"sourceIPAddress":"203.0.113.77","requestParameters":{"bucketName":"lab-evidence-bucket","key":"evidence/2026/case-notes.pdf"},"errorCode":null}
{"eventTime":"2026-10-29T08:31:44Z","eventName":"CreateUser","userIdentity":{"arn":"arn:aws:iam::111122223333:user/svc-ci"},"sourceIPAddress":"198.51.100.24","requestParameters":{"userName":"svc-backup"},"errorCode":null}
{"eventTime":"2026-10-29T08:32:10Z","eventName":"DeleteTrail","userIdentity":{"arn":"arn:aws:iam::111122223333:user/svc-ci"},"sourceIPAddress":"198.51.100.24","requestParameters":{"name":"audit"},"errorCode":"AccessDenied"}
{"eventTime":"2026-10-29T09:04:00Z","eventName":"GetObject","userIdentity":{"arn":"arn:aws:iam::111122223333:user/a.khan"},"sourceIPAddress":"198.51.100.31","requestParameters":{"bucketName":"lab-evidence-bucket","key":"evidence/2026/public-notice.pdf"},"errorCode":null}
```

Analyse it:

```bash
python3 - <<'PY'
import json, collections
high = {"StopLogging","DeleteTrail","PutBucketPolicy","CreateAccessKey","AttachUserPolicy","CreateUser","UpdateTrail"}
rows = [json.loads(l) for l in open("audit-events.json", encoding="utf-8") if l.strip()]
print("events:", len(rows))
for r in rows:
    mark = "HIGH" if r["eventName"] in high else "    "
    print(mark, r["eventTime"], r["eventName"], r["userIdentity"]["arn"].split("/")[-1],
          r["sourceIPAddress"], r["errorCode"] or "ok")
print("\nsource IPs:", collections.Counter(r["sourceIPAddress"] for r in rows))
PY
```

Answer in `audit-findings.md`:

1. Which event removed your ability to see subsequent activity, and at what time?
2. Which events changed identity or policy, and what did they grant?
3. The `AccessDenied` at 08:21:19 followed by success at 08:22:02 — what changed in between?
4. Which single control would have prevented the escalation, and which would have preserved evidence?
5. Which events are benign, and why?

**Expected findings:** logging stopped at 08:12:41; anonymous read granted at 08:13:02; a new key and admin policy at
08:14–08:15; the denial-then-success pair indicates the policy change taking effect; the trail deletion attempt at
08:32 is denied, which is the one control that held.

## Evidence to collect

- `before.json` summary: count and check IDs.
- Secrets scan output and the history `grep` count.
- After-fix scan output and exit code.
- `.checkov.baseline` plus `RISK-ACCEPT-001.md`.
- `audit-findings.md` with the five answers.

## Verification

- [ ] Before/after failure counts recorded with check IDs from your own run.
- [ ] Fixes address public storage, encryption, open ports, wildcard IAM and trail scope.
- [ ] Secret is rotated/removed *and* the history problem is stated.
- [ ] One accepted risk documented with owner, review date and compensating controls.
- [ ] Log-stopping event identified with a timestamp.
- [ ] At least one control named that would have prevented the escalation.

## Teardown and reset

```bash
rm -rf ~/cloud-lab/iac
```

Nothing was applied to a provider. If you ever run `terraform apply` on this template, destroy it the same session and
set a billing alert first.

## Reflection

1. `checkov` flagged the example key. What does that tell you about pattern-based secret detection, and what is the
   real control?
2. The trail deletion was denied, but `StopLogging` succeeded. Why is denying one and not the other a common real-world
   gap?
3. Your baseline is now permanent until reviewed. What process stops it becoming a place where findings go to die?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Scanning | Ran once | Before and after | Check IDs recorded; false positives reasoned about |
| Remediation | Some fixes | All major classes | Each fix explained by the risk it removes |
| Accepted risk | Ignored | Baseline created | Owner, review, compensating controls, trade-off stated |
| Audit analysis | Read the log | Ordered the events | Identified failed control and the denial-then-success pattern |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `checkov` finds nothing | Wrong directory or framework | `checkov -d . --framework terraform`; check file extension `.tf` |
| Exit code 0 with failures | `--soft-fail` set | Remove it; CI should fail |
| Baseline hides too much | Created over all findings | `--create-baseline` only after remediation |
| `terraform validate` fails | Provider not initialised | `terraform init` (network required); scanning does not need it |
| Secrets scan flags docs | Pattern match on example text | Move examples out of scanned paths; do not disable the check |

## References

1. Checkov — policy index and CLI reference. Accessed 2026-10-29.
2. AWS — CloudTrail event reference and log file integrity validation. Accessed 2026-10-29.
3. CIS AWS Foundations Benchmark — logging and monitoring controls. Accessed 2026-10-29.
4. MITRE ATT&CK — T1562.008 (Impair Defenses: Disable Cloud Logs). Accessed 2026-10-29.
