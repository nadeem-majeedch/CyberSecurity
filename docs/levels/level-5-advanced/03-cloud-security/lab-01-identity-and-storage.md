---
title: "LAB-503-01 · Least Privilege and Object Storage"
description: "Run local S3-compatible storage, write a least-privilege policy, prove the allow works and the deny fails, then close an anonymous bucket policy."
module_code: CYB-503
level: 5
kind: lab
prerequisites: [CYB-503]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-503-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [cloud, iam, s3, minio, least-privilege, storage]
---

# LAB-503-01 · Least Privilege and Object Storage

!!! note "How this walkthrough was produced"
    The MinIO commands and expected output below were written against current vendor documentation and the
    pinned versions in the tool table. They were **not** captured from a verified run in the author's lab.
    Treat the output as a **shape**, not a transcript: field order, wording and version banners differ between
    releases. Record what you actually see, and report a deviation rather than adjusting your output to match
    this page.

## Scenario and background

A reporting service needs to read generated reports from object storage. The obvious implementation gives it the
storage admin key. You are going to replace that with a policy that permits exactly one prefix, prove the boundary
holds in both directions, and then deal with a bucket that somebody made public "temporarily" in 2024.

Everything runs on local MinIO, which implements the S3 API and the same policy evaluation order.

## Learning objectives

1. Run S3-compatible storage locally and administer it with a CLI.
2. Write an identity policy scoped to an action, a resource prefix and a condition.
3. Verify least privilege by testing an allowed action *and* a denied one.
4. Detect anonymous access to a bucket and close it, verified by HTTP status.
5. Use versioning to recover a deleted object.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Docker | 24+ | Or Podman with the same flags |
| MinIO server | latest `RELEASE.*` | Record the tag you pull |
| MinIO client `mc` | latest | From `dl.min.io/client/mc/release/` |
| curl | any | For the anonymous test |

Record your versions:

```bash
docker --version && mc --version
```

## Threat model

- A compromised reporting service with a broad key can read every object in the bucket, including unrelated data.
- An anonymous bucket policy exposes data to anyone with the URL and no authentication at all.
- A presigned URL shared in a ticket is a bearer token until it expires.

## Environment

One Linux VM. Bind the console to loopback only — this is a lab, not a service.

```bash
mkdir -p ~/cloud-lab/data
docker run -d --name minio-lab \
  -p 127.0.0.1:9000:9000 -p 127.0.0.1:9001:9001 \
  -e MINIO_ROOT_USER=labadmin \
  -e MINIO_ROOT_PASSWORD='labadmin-local-only' \
  -v ~/cloud-lab/data:/data \
  minio/minio server /data --console-address ":9001"
docker logs --tail 20 minio-lab
```

**Expected:** the log shows `API: http://...:9000` and `WebUI: http://...:9001`, and `MinIO Object Storage Server`.
The image tag is in the log — record it.

```bash
mc alias set local http://127.0.0.1:9000 labadmin 'labadmin-local-only'
mc mb local/lab-evidence
mc mb local/lab-evidence/reports local/lab-evidence/finance
```

**Expected:** `Bucket created successfully`.

Seed test objects:

```bash
cd ~/cloud-lab
echo "Q3 report — synthetic data" > report-q3.txt
echo "SYNTHETIC payroll placeholder" > payroll.txt
echo "throwaway" > public-notice.txt
mc cp report-q3.txt local/lab-evidence/reports/
mc cp payroll.txt local/lab-evidence/finance/
mc cp public-notice.txt local/lab-evidence/
mc ls -r local/lab-evidence
```

## Procedure

### 1. Establish the problem

```bash
mc admin user add local svc-report 'Svc-Report-Local-2026!'
mc admin policy attach local consoleAdmin --user svc-report   # deliberately wrong
mc alias set svcreport http://127.0.0.1:9000 svc-report 'Svc-Report-Local-2026!'
mc ls -r svcreport/lab-evidence
```

**Expected:** the service account lists **everything**, including `finance/payroll.txt`. That is the finding: a
reporting service can read payroll because it holds an admin policy.

Record this output as your "before" evidence.

### 2. Write a scoped policy

`report-reader.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadReportsOnly",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::lab-evidence/reports/*"]
    },
    {
      "Sid": "ListReportsPrefix",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::lab-evidence"],
      "Condition": {"StringLike": {"s3:prefix": ["reports/*"]}}
    }
  ]
}
```

Note what is **not** there: no `s3:PutObject`, no `s3:DeleteObject`, no wildcard resource, and no access to the bucket
root beyond the `reports/` prefix.

```bash
mc admin policy create local report-reader report-reader.json
mc admin policy detach local consoleAdmin --user svc-report
mc admin policy attach local report-reader --user svc-report
```

**Version note:** older `mc` uses `mc admin policy add` and `mc admin policy set local report-reader user=svc-report`.
If a command is rejected, run `mc admin policy --help` and use the syntax your version documents.

### 3. Prove the allow and the deny

```bash
echo "--- allowed read ---"
mc cat svcreport/lab-evidence/reports/report-q3.txt

echo "--- denied read (different prefix) ---"
mc cat svcreport/lab-evidence/finance/payroll.txt; echo "exit=$?"

echo "--- denied list at root ---"
mc ls svcreport/lab-evidence; echo "exit=$?"

echo "--- denied write ---"
echo "tampered" > evil.txt
mc cp evil.txt svcreport/lab-evidence/reports/evil.txt; echo "exit=$?"

echo "--- denied delete ---"
mc rm svcreport/lab-evidence/reports/report-q3.txt; echo "exit=$?"
```

**Expected:** the first read prints the report; every other operation fails with `Access Denied` and a non-zero exit.
If `mc cat` on payroll succeeds, your policy attach did not replace the admin policy — check
`mc admin user info local svc-report`.

Tabulate the result. This table *is* the deliverable: a least-privilege claim without a deny test is a guess.

| Operation | Expected | Observed | Exit |
| --- | --- | --- | --- |
| Read `reports/report-q3.txt` | allow | | |
| Read `finance/payroll.txt` | deny | | |
| List bucket root | deny | | |
| Write `reports/evil.txt` | deny | | |
| Delete `reports/report-q3.txt` | deny | | |

### 4. Find and close an anonymous bucket

Someone applies a public read policy to the root:

```bash
cat > public-read.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": ["*"]},
    "Action": ["s3:GetObject"],
    "Resource": ["arn:aws:s3:::lab-evidence/*"]
  }]
}
JSON
mc anonymous set-json public-read.json local/lab-evidence

echo "--- anonymous read attempt ---"
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9000/lab-evidence/finance/payroll.txt
curl -s http://127.0.0.1:9000/lab-evidence/reports/report-q3.txt
```

**Expected:** `200`, and the payroll placeholder is returned to a request carrying **no credentials at all**. That is
the whole incident in two lines.

Close it and re-test:

```bash
mc anonymous set none local/lab-evidence
mc anonymous get local/lab-evidence
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9000/lab-evidence/finance/payroll.txt
```

**Expected:** `AccessDenied` from `mc anonymous get`, and `403` from curl. A `403` is the proof; a console screenshot is
not.

### 5. Presigned URL expiry

```bash
URL=$(mc share download --expire 1m local/lab-evidence/reports/report-q3.txt | awk '/^http/ {print $1}')
echo "$URL"
curl -s -o /dev/null -w "now: %{http_code}\n" "$URL"
sleep 70
curl -s -o /dev/null -w "after expiry: %{http_code}\n" "$URL"
```

**Expected:** `200` then `403` with `Request has expired`. This is why a presigned link pasted into a ticket is a
credential: whoever has it has the access, until it expires.

### 6. Versioning as a recovery control

```bash
mc version enable local/lab-evidence
mc cp report-q3.txt local/lab-evidence/reports/report-q3.txt
mc rm local/lab-evidence/reports/report-q3.txt
mc ls --versions local/lab-evidence/reports/
```

**Expected:** the object is gone from a normal listing but present with a version ID. Restore it:

```bash
VID=$(mc ls --versions local/lab-evidence/reports/ | awk '/report-q3.txt/ {print $NF}' | head -1)
mc cp --version-id "$VID" local/lab-evidence/reports/report-q3.txt ./restored.txt
cat restored.txt
```

**Expected:** the original content returns. Note in your report that versioning also means "deleted" data still
exists — a privacy and retention consideration, not only a recovery win.

## Evidence to collect

- MinIO image tag and `mc --version`.
- The "before" listing showing the service account could read everything.
- The policy file, and the allow/deny table with observed exits.
- curl status codes before and after closing anonymous access.
- Presigned URL results before and after expiry.
- Restored object content.

## Verification

- [ ] Service account reads `reports/` and is denied on `finance/`, root listing, write and delete.
- [ ] Anonymous request returns `200` before the fix and `403` after.
- [ ] Presigned URL expires.
- [ ] An object is recovered from a version.
- [ ] You can explain why the policy has two statements, not one.

## Teardown and reset

```bash
docker rm -f minio-lab
mc alias remove svcreport 2>/dev/null || true
rm -rf ~/cloud-lab
```

Nothing was exposed beyond loopback.

## Reflection

1. The policy grants `s3:ListBucket` with a prefix condition. What could an attacker learn with it that they could not
   learn from `GetObject` alone?
2. Anonymous read was closed with one command. What process control would have prevented it being opened?
3. Versioning saved the object. What does the attacker with delete rights need in order to defeat versioning, and what
   control stops that?

## Extensions

- Add a second user that may write only to `incoming/`, and test that it cannot overwrite `reports/`.
- Configure bucket lifecycle expiry for `incoming/` and verify what happens to versions.
- Add a `Deny` statement for requests not using TLS and observe which requests fail.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Policy | Copied wildcard | Scoped action and prefix | Condition justified; two statements explained |
| Verification | Allow only | Allow and deny tested | Table with exits; root listing and write tested |
| Exposure | Fixed | Found and closed | Proved with status codes; prevention suggested |
| Recovery | Versioning enabled | Object restored | Retention implication noted |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `mc: unable to initialize` | Wrong endpoint or credentials | `mc alias list`; re-set the alias |
| Everything still allowed | Old policy still attached | `mc admin user info local svc-report` |
| Anonymous still `200` | Cache or wrong policy target | `mc anonymous get`; add `-H 'Cache-Control: no-cache'` to curl |
| `--version-id` unsupported | Older `mc` | `mc cp --help`; use the version flag your client documents |
| Container exits immediately | Port already bound | `docker logs minio-lab`; change the host port |

## References

1. MinIO — `mc admin policy` and `mc anonymous` documentation. Accessed 2026-10-29.
2. Amazon S3 — Bucket policy examples and public access block. Accessed 2026-10-29.
3. Amazon S3 — Presigned URL expiration. Accessed 2026-10-29.
4. AWS — Policy evaluation logic (explicit deny). Accessed 2026-10-29.
