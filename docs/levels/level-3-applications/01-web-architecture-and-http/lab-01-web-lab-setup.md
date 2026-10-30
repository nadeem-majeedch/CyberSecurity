---
title: "LAB-301-01 · Build the Web Lab"
description: "Install the vulnerable applications, bind them to the lab address only, and prove the lab cannot be reached from outside."
module_code: CYB-301
level: 3
kind: lab
prerequisites: [CYB-206]
estimated_minutes: 90
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-301-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [docker, juice-shop, dvwa, burp, isolation]
---

# LAB-301-01 · Build the Web Lab

## Scenario and background

Every remaining lab in Level 3 needs a target that is *supposed* to be broken. This lab builds that target:
OWASP Juice Shop and DVWA on `lab-web`, reachable from `lab-analyst` and from nowhere else.

The important part is not `docker run`. It is the containment: a deliberately vulnerable application that
answers on your Wi-Fi is a real incident waiting for a real scanner, and Docker's port publishing has a
well-known habit of bypassing host firewall rules. You will bind to one address, prove the binding, and prove
the network boundary twice.

## Learning objectives

By the end of this lab you can:

1. Install Docker Engine and the Compose plugin from official packages, recording versions.
2. Run Juice Shop and DVWA with port bindings restricted to the lab address.
3. Explain why binding to a specific interface is a stronger control than a host firewall rule alone.
4. Load DVWA's database and set its security level deliberately.
5. Configure Burp Suite Community Edition or OWASP ZAP as a loopback proxy, and state each tool's limits.

## Required tools and versions

| Tool | Version | Where | Notes |
| --- | --- | --- | --- |
| Ubuntu Server | 22.04.x LTS | `lab-web` | From your Level 2 build |
| Docker Engine | 27.x or later | `lab-web` | Official apt repository |
| Docker Compose plugin | v2.29+ | `lab-web` | `docker compose version` |
| OWASP Juice Shop | 20.3.0 (`latest`) | `lab-web` container | `bkimminich/juice-shop` |
| DVWA | current `master` | `lab-web` containers | `ghcr.io/digininja/dvwa`, MariaDB |
| Burp Suite Community | 2026.10.1 | `lab-analyst` | Free; requires a PortSwigger download, no licence key |
| OWASP ZAP | 2.17.0 | `lab-analyst` | Free and open source; optional alternative |
| `curl`, `jq`, `ss` | distribution | both | Verification |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `192.0.2.30:3000` (Juice Shop) and `192.0.2.30:4280` (DVWA), both inside your
    host-only lab network; `127.0.0.1:8080` on your analyst VM (your proxy).
    **Targets you must not use:** any public website, any university or employer system, any address on your
    home or campus network, and any container you have published to `0.0.0.0`.

    A deliberately vulnerable application reachable from your LAN is a live target for anyone on that LAN.
    If any step below shows a binding other than `192.0.2.30`, **stop and fix it before continuing**.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

This lab intentionally deploys software with known, documented vulnerabilities (SQL injection, XSS, broken
access control, weak hashing). The threat is not the application; it is **exposure**. Controls:

- Adapters: `lab-web` has a host-only adapter only. NAT is attached temporarily for image pulls, then removed.
- Bindings: containers publish on `192.0.2.30`, never `0.0.0.0`.
- No port forwarding from the hypervisor to the physical host's LAN interface.
- Snapshots before any configuration change.

What is *not* real here: there is no real user data. Accounts you create are yours, and passwords must be
lab-only strings you would never reuse.

## Environment

| Host | Role | Address | Resources |
| --- | --- | --- | --- |
| `lab-analyst` | Analyst workstation, browser, proxy | 192.0.2.10/24 | 2 vCPU, 4 GB |
| `lab-web` | Target host running containers | 192.0.2.30/24 | 2 vCPU, 4 GB, 30 GB disk |

```text
lab-analyst 192.0.2.10 ──► lab-web 192.0.2.30
                              :3000  Juice Shop  (container)
                              :4280  DVWA        (container + MariaDB)
                              :22    sshd

No route to the internet from either host once NAT is detached.
```

## Before you start

1. Snapshot both VMs as `pre-cyb301`.
2. Confirm the isolation baseline *before* installing anything:

   ```bash
   ping -c1 -W1 8.8.8.8; echo "exit=$?"
   ```

   **Expected:** `100% packet loss` and `exit=1` on `lab-web`. If it succeeds, NAT is still attached — detach
   it before continuing.
3. Note the exact image versions you will install in `evidence/versions.txt` as you go.

## Procedure

### 1. Install Docker Engine on `lab-web`

Follow the official instructions for Ubuntu at
<https://docs.docker.com/engine/install/ubuntu/>. The supported route is Docker's apt repository, not a
convenience script; the script is fine for a throwaway VM but it gives you no pinning and no audit trail.

```bash
# Attach NAT for this step only, then remove it again.
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**Why the keyring:** apt verifies the repository signature. Adding a third-party repo without the key is how
supply-chain compromises get installed with your own hands — [A03:2025](https://owasp.org/Top10/2025/).

Verify, and allow your user to run Docker without `sudo` (this is a privilege escalation path in itself; on a lab
VM it is acceptable, and you should be able to say why):

```bash
docker version --format '{{.Server.Version}}'
docker compose version
sudo usermod -aG docker "$USER" && newgrp docker
```

### 2. Pull and start Juice Shop, bound to the lab address

```bash
docker pull bkimminich/juice-shop:latest
docker run -d --name juice-shop --restart unless-stopped \
  -p 192.0.2.30:3000:3000 \
  bkimminich/juice-shop:latest
```

**Why `192.0.2.30:3000:3000` and not `3000:3000`:** the three-field form is
`HOST_IP:HOST_PORT:CONTAINER_PORT`. Without the host IP, Docker publishes on `0.0.0.0` — every interface,
including the NAT adapter you will reattach for the next pull.

Confirm the binding:

```bash
ss -tlnp | grep 3000
```

**Expected:** a line whose local address is `192.0.2.30:3000`. If you see `0.0.0.0:3000` or `*:3000`, stop and
recreate the container.

### 3. Start DVWA from its official Compose file

DVWA's repository ships a Compose file that runs the application and MariaDB together. Use it rather than a
third-party image: the widely copied `vulnerables/web-dvwa` image on Docker Hub has not been maintained for
years.

```bash
git clone https://github.com/digininja/DVWA.git ~/dvwa
cd ~/dvwa
git log -1 --format='%H %ad' > ~/lab/level-3/lab-301/evidence/dvwa-commit.txt
docker compose up -d
```

The shipped Compose file publishes on `127.0.0.1:4280`, which is correct but unreachable from `lab-analyst`.
Add an override *in the same directory* — Compose merges it automatically:

```bash
cat > docker-compose.override.yml <<'YAML'
services:
  dvwa:
    ports:
      - "192.0.2.30:4280:80"
YAML
docker compose config | grep -A3 'ports:'
docker compose up -d
```

**Why an override file:** you keep the project's own file untouched (so `git pull` stays clean) while changing
only the binding. **Check the merged result** with `docker compose config` before trusting it — a typo in an
override fails silently more often than it fails loudly.

**Expected:** the ports block shows `published: "4280"` with `host_ip: 192.0.2.30`.

### 4. Initialise DVWA

From `lab-analyst`, open `http://192.0.2.30:4280/setup.php` and select **Create / Reset Database**. Then log in
at `http://192.0.2.30:4280/login.php` with the documented default credentials `admin` / `password`, and set
**DVWA Security → Low** on the security page.

Record in your notes: the fact that the application *shipped* with default credentials is itself a finding class
([WSTG-ATHN-02](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/02-Testing_for_Default_Credentials)).
Here you rely on it deliberately.

### 5. Prove reachability and prove containment

From `lab-analyst` — both applications must answer:

```bash
curl -s -o /dev/null -w 'juice=%{http_code}\n' http://192.0.2.30:3000/
curl -s -o /dev/null -w 'dvwa=%{http_code}\n'  http://192.0.2.30:4280/login.php
```

**Expected:** `juice=200`, `dvwa=200`.

From `lab-web` — the containers must not be listening on any other address:

```bash
sudo ss -tlnp | grep -E ':3000|:4280'
ip -brief addr show
```

Now the boundary test, from a device that is **not** on the host-only network (your phone, or another laptop on
your Wi-Fi):

```text
http://<your-physical-host-LAN-IP>:3000   → must fail
http://<your-physical-host-LAN-IP>:4280   → must fail
```

**Why the physical host may still reach them:** VirtualBox and VMware host-only adapters put *your host* on that
network by design. That is acceptable — your host is not the internet. What must fail is access from another
machine on your LAN, which is the realistic exposure path.

Finally, record the containment checks in `evidence/isolation.txt`, then **detach NAT**:

```bash
ping -c1 -W1 8.8.8.8; echo "exit=$?"      # expect failure again
```

### 6. Configure the proxy on `lab-analyst`

Burp Suite Community Edition is a free download from PortSwigger; there is no licence key and no time limit.
Download it from <https://portswigger.net/burp/downloads>, choose **Linux (x64)** or **Linux (ARM)** for your
platform (`uname -m` tells you which), run the installer, and select **Community Edition** when prompted.

Then:

1. **Proxy → Proxy settings → Add** a listener on `127.0.0.1:8080`. Loopback only — a listener on `0.0.0.0` is
   an open proxy for your whole lab network.
2. In **Settings → Tools → Proxy**, add `192.0.2.30` to the *target scope* so your sitemap stays clean.
3. Install Burp's CA certificate in a **dedicated browser profile**: browse to `http://burp`, download the
   certificate, and import it under the browser's Authorities/Certificates settings.

**What Community Edition does not include:** the vulnerability scanner. It is a manual testing toolkit —
intercept, Repeater, a throttled Intruder, and the sitemap. Automated scanning requires Burp Professional
(paid) or OWASP ZAP (free). Every exercise in this course is completable in Community, because every exercise is
manual.

If you prefer ZAP (version 2.17.0, free), install it from <https://www.zaproxy.org/download/> or your Kali
repository, and set the same scope: local proxy on `127.0.0.1:8080`, target `http://192.0.2.30`.

### 7. Record versions and image digests

```bash
{
  docker version --format 'engine={{.Server.Version}}'
  docker compose version
  docker image inspect bkimminich/juice-shop:latest \
    --format 'juice={{index .RepoDigests 0}}'
  cd ~/dvwa && git rev-parse HEAD
} | tee ~/lab/level-3/lab-301/evidence/versions.txt
```

**Why digests:** `latest` moves. A digest pins the exact bytes you tested, so a report written today is still
reproducible in six months.

## Evidence to collect

- `evidence/versions.txt` — engine, Compose, image digest, DVWA commit.
- `evidence/bindings.txt` — `ss -tlnp` output showing `192.0.2.30` bindings only.
- `evidence/isolation.txt` — the failed external access attempt and the failed `ping 8.8.8.8`.
- `evidence/versions-burp.txt` — Burp or ZAP version string from the About dialog.
- One screenshot of each application's landing page, with the URL bar visible.

## Verification

- [ ] Docker Engine and Compose report versions; both recorded.
- [ ] `ss -tlnp` shows `192.0.2.30` for ports 3000 and 4280, and no `0.0.0.0` binding for either.
- [ ] Juice Shop returns `200` from `lab-analyst`; DVWA login page returns `200`.
- [ ] DVWA database was created and security level is `Low`.
- [ ] Access from a non-lab device failed; `ping 8.8.8.8` fails from `lab-web`.
- [ ] Proxy listener is bound to `127.0.0.1` only.
- [ ] Artefacts are stored under `~/lab/level-3/lab-301/evidence/`.

## Teardown and reset

```bash
# Stop the applications without deleting evidence
docker stop juice-shop
cd ~/dvwa && docker compose stop
```

To return to a clean state, revert the VM snapshot `pre-cyb301`. To remove the containers and their volumes
completely (this deletes the DVWA database you created):

```bash
docker rm -f juice-shop
cd ~/dvwa && docker compose down -v
```

Leave the applications running while you work through CYB-302 to CYB-308. Revert to `pre-cyb301` when the level
is finished, and confirm containment one last time before you power the VMs off.

## Reflection

1. Docker publishes ports through its own iptables rules. What does that mean for a host firewall rule that
   denies inbound 3000, and why is the bind address the more reliable control?
2. You gave your user membership of the `docker` group. Explain, in two sentences, why that is equivalent to
   root — and why it was still a reasonable choice on this VM.
3. `latest` was used for Juice Shop. Give one situation where that is fine and one where it invalidates a
   finding.
4. Burp Community has no scanner. Describe how that changes the *shape* of a test you would otherwise automate,
   and what you must do instead.

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Containment | Application reachable from LAN or bound to `0.0.0.0` | Bound to lab address, host-only adapter | Bound, proven externally unreachable, and explained why the bind beats a firewall rule |
| Reproducibility | Versions missing | Versions recorded | Versions plus image digests and DVWA commit |
| Configuration | DVWA not initialised | Initialised, security level set | Initialised with defaults documented as a finding class |
| Evidence | Screenshots only | Bindings and isolation recorded | Evidence set a second person could replay exactly |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `curl` to `192.0.2.30:3000` times out from `lab-analyst` | Container bound to `127.0.0.1`, or VMs on different host-only networks | `docker inspect juice-shop --format '{{json .NetworkSettings.Ports}}'`; recreate with the lab IP; check both VMs' `ip addr` |
| `ss` shows `0.0.0.0:3000` | Port mapping given as `3000:3000` | `docker rm -f juice-shop` and rerun with `192.0.2.30:3000:3000` |
| DVWA page loads but database errors appear | Setup not run, or MariaDB still starting | Wait 30 s, re-run `/setup.php`; `docker compose logs db` |
| `docker compose config` ignores the override | Override in the wrong directory, or wrong service name | File must sit beside `compose.yml`; service name must match (`dvwa`) |
| Browser shows certificate warnings through the proxy | CA not installed in *this* profile | Import the PortSwigger CA into the profile you are using |
| `apt update` fails on the Docker repo after detaching NAT | Expected — no internet | Reattach NAT for installs only, then detach again |

## References

1. Docker — Install Docker Engine on Ubuntu. <https://docs.docker.com/engine/install/ubuntu/> Accessed 2026-10-29.
2. OWASP Juice Shop — Running with Docker. <https://pwning.owasp-juice.shop/companion-guide/latest/part1/running.html> Accessed 2026-10-29.
3. DVWA — official repository and Compose file. <https://github.com/digininja/DVWA> Accessed 2026-10-29.
4. PortSwigger — Burp Suite downloads and Community comparison. <https://portswigger.net/burp/downloads> Accessed 2026-10-29.
5. OWASP ZAP — Download. <https://www.zaproxy.org/download/> Accessed 2026-10-29.
6. OWASP WSTG v4.2 — WSTG-ATHN-02 Testing for Default Credentials.
