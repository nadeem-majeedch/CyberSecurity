---
title: "LAB-503-03 · Final Challenge: Container Hardening"
description: "Prove a secret is baked into an image layer, scan and rebuild a container to run non-root with a read-only filesystem, and show what still escapes."
module_code: CYB-503
level: 5
kind: lab
prerequisites: [CYB-503]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-503-03]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [cloud, containers, docker, trivy, supply-chain, final-challenge]
---

# LAB-503-03 · Final Challenge: Container Hardening

!!! note "How this walkthrough was produced"
    The Trivy and Docker commands and expected output below were written against current vendor documentation and the
    pinned versions in the tool table. They were **not** captured from a verified run in the author's lab.
    Treat the output as a **shape**, not a transcript: field order, wording and version banners differ between
    releases. Record what you actually see, and report a deviation rather than adjusting your output to match
    this page.

## Scenario and background

A service was containerised in an afternoon. The image runs as root, carries its API token in the build, uses an
unpinned base, and is deployed with default runtime privileges. You have the image and nothing else: no source
history, no documentation.

Your job is to demonstrate what is wrong — with evidence from the image itself, not from the Dockerfile — then rebuild
it properly and show which risks are gone and which remain.

## Learning objectives

1. Extract evidence from an image: layers, history, configuration and filesystem.
2. Explain why deleting a secret in a later layer does not remove it.
3. Scan an image for vulnerabilities and a Dockerfile for misconfiguration.
4. Rebuild to a non-root, read-only, capability-restricted container and verify each control by test.
5. State the residual risks that hardening does not remove.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Docker | 24+ | Or Podman (`podman` equivalents noted) |
| `trivy` | 0.5x+ | Official release binary or package |
| Python | 3.11+ | Host, only for scripting |

```bash
docker --version
trivy --version
```

Record both. Vulnerability counts change daily because the database changes — **your numbers, not the ones written
here, are the result.**

## Threat model

- An image with a secret in a layer leaks it to anyone who can pull the image.
- Root in the container is root on any mounted volume, and a step closer to the host on escape.
- A vulnerable base package is exploitable by anything that reaches the service.
- A container with the Docker socket mounted is equivalent to root on the host, regardless of `USER`.

## Environment

```bash
mkdir -p ~/cloud-lab/app && cd ~/cloud-lab/app
```

`app.py`:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"evidence-service ok\n")

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
```

`Dockerfile.bad`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
ADD . /app
ENV API_TOKEN=lab-token-do-not-ship-7f3a
ENV DEBUG=true
RUN printf 'API_TOKEN=lab-token-do-not-ship-7f3a\n' > /app/.env
RUN apt-get update && apt-get install -y curl
EXPOSE 8000
CMD ["python", "app.py"]
```

Build it:

```bash
docker build -f Dockerfile.bad -t lab/app:bad .
docker run -d --name bad-app -p 127.0.0.1:8000:8000 lab/app:bad
curl -s http://127.0.0.1:8000/
```

**Expected:** `evidence-service ok`.

## Procedure

### 1. Identify the user and the configuration

```bash
docker inspect --format 'User={{.Config.User}} Env={{.Config.Env}}' lab/app:bad
docker run --rm lab/app:bad id
docker run --rm lab/app:bad whoami
```

**Expected:** `User=` is empty and `whoami` prints `root`. An empty user means the base image's default, which for
`python:*-slim` is root.

### 2. Prove the secret is in the image

The token is visible in configuration:

```bash
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' lab/app:bad | grep API_TOKEN
docker run --rm lab/app:bad cat /app/.env
```

The token is in two places: the image configuration and a file the build created. Now prove the file is in the
filesystem layers:

```bash
docker save lab/app:bad -o /tmp/bad.tar
rm -rf /tmp/bad-ext && mkdir -p /tmp/bad-ext
tar -xf /tmp/bad.tar -C /tmp/bad-ext
grep -r "lab-token-do-not-ship" /tmp/bad-ext --binary-files=text | head -3
```

**Expected:** a hit inside a layer archive. Anyone who can pull the image can do exactly this.

### 3. Delete the secret "properly" and watch it fail

```bash
cat > Dockerfile.bad2 <<'DOCKER'
FROM lab/app:bad
ENV API_TOKEN=
RUN rm -f /app/.env
DOCKER
docker build -f Dockerfile.bad2 -t lab/app:bad2 .
docker save lab/app:bad2 -o /tmp/bad2.tar
rm -rf /tmp/bad2-ext && mkdir -p /tmp/bad2-ext
tar -xf /tmp/bad2.tar -C /tmp/bad2-ext
grep -r "lab-token-do-not-ship" /tmp/bad2-ext --binary-files=text | wc -l
```

**Expected:** a non-zero count. The file really was deleted from the final filesystem — `docker run --rm lab/app:bad2 ls /app` shows no `.env` — but the layer that created it is still in the image, and `rm` adds a layer rather than
removing history. Record the count as your evidence, and record that the file was absent at runtime: both are true,
and only one of them is what people assume.

### 4. Scan

```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed lab/app:bad | tee /tmp/scan-bad.txt
trivy config Dockerfile.bad
```

**Expected:** a vulnerability summary for the base image's packages, and Dockerfile findings including the root user
and the embedded secret. Trivy's Dockerfile checks use `DS` IDs; **record the IDs your version reports**.

Summarise:

```bash
grep -E "Total:|HIGH:|CRITICAL:" /tmp/scan-bad.txt
```

### 5. Rebuild

`Dockerfile`:

```dockerfile
# Pin by digest in production; tag shown for readability
FROM python:3.12-slim

RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --chown=app:app app.py /app/app.py

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/').read()" || exit 1

CMD ["python", "app.py"]
```

```bash
docker build -f Dockerfile -t lab/app:good .
trivy image --severity HIGH,CRITICAL --ignore-unfixed lab/app:good | tee /tmp/scan-good.txt
docker image inspect --format 'User={{.Config.User}}' lab/app:good
```

**Expected:** `User=10001:10001`, and a lower vulnerability count than the bad image. Compare the two summaries in a
table; do not claim zero.

### 6. Run it hardened and test each control

The app listens on 8000, so the host port maps to 8000 inside the container:

```bash
docker run -d --name good-app \
  --read-only --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop=ALL --security-opt no-new-privileges \
  --pids-limit 100 --memory 256m --cpus 0.5 \
  -p 127.0.0.1:8001:8000 lab/app:good
curl -s http://127.0.0.1:8001/
```

**Expected:** the service responds. Now prove the restrictions:

```bash
echo "--- user ---"
docker exec good-app id

echo "--- root filesystem is read-only ---"
docker exec good-app sh -c 'touch /app/x' ; echo "exit=$?"

echo "--- tmpfs is writable ---"
docker exec good-app sh -c 'touch /tmp/x && echo tmp-ok'

echo "--- capabilities ---"
docker exec good-app sh -c 'grep CapEff /proc/self/status'
docker inspect --format '{{.HostConfig.CapDrop}} {{.HostConfig.SecurityOpt}} {{.HostConfig.ReadonlyRootfs}}' good-app

echo "--- no setuid escalation ---"
docker exec good-app sh -c 'python -c "import os; os.setuid(0)"' 2>&1 | tail -1
```

**Expected:** `uid=10001`; the write to `/app` fails with a read-only filesystem error; `/tmp` write succeeds;
`CapDrop=[ALL]`, `no-new-privileges`, `ReadonlyRootfs=true`; and the setuid attempt fails with a permission error.

A missing `USER` and a writable root filesystem are the two conditions that turn an application bug into a host
compromise. Both are now closed.

### 7. Show what hardening does not fix

The container is non-root. Mount the Docker socket and it can control the host anyway:

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  --user 10001:10001 lab/app:good \
  sh -c 'ls -l /var/run/docker.sock'
```

If `docker` is available inside the image you would be able to run containers as root on the host. Explain in
`limits.md`:

- Socket mount = host root, regardless of `USER`.
- A shared kernel means a kernel exploit crosses the boundary.
- `--privileged` and host PID/network namespaces remove most isolation.
- Image scanning at build time says nothing about what runs in production unless the scanned digest is the deployed one.

Then clean up the socket test with `docker rm` (it used `--rm`) and confirm no container is left.

## Evidence to collect

- `docker inspect` output for user and environment on the bad image.
- `grep` count proving the secret survives layer deletion.
- Both scan summaries and the comparison table.
- Verification transcript for user, read-only root, capabilities, setuid.
- `limits.md` with at least three residual risks.

## Verification

- [ ] Secret located inside an image layer and shown to survive deletion.
- [ ] Both images scanned; counts recorded from your run.
- [ ] Final image runs as a non-root UID, proven by `id` inside the container.
- [ ] Read-only root filesystem proven by a failed write, with `/tmp` writable.
- [ ] `CapDrop=ALL` and `no-new-privileges` confirmed by inspection.
- [ ] Residual risks stated, including the socket mount.

## Teardown and reset

```bash
docker rm -f bad-app good-app 2>/dev/null
docker rmi -f lab/app:bad lab/app:bad2 lab/app:good 2>/dev/null
rm -rf /tmp/bad.tar /tmp/bad2.tar /tmp/bad-ext /tmp/bad2-ext /tmp/scan-*.txt ~/cloud-lab/app
```

## Reflection

1. `trivy` reports fewer vulnerabilities after the rebuild. Why is "zero HIGH findings" not the same as "safe"?
2. The token was in two places. Which one would a scanner catch, and which would a human reviewer catch?
3. `--read-only` broke nothing here because the app writes only to `/tmp`. What would you do with an application that
   writes logs to `/var/log`?
4. You pinned a tag, not a digest. What can change under a tag, and why does that matter for a scan result?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Evidence | Read the Dockerfile | Inspected image config | Extracted layer evidence and proved persistence |
| Scanning | Ran once | Before and after | Comparison table; limitations of scanning stated |
| Runtime | Non-root | Non-root and read-only | All five controls verified individually |
| Limits | None stated | One or two | Socket mount, kernel sharing, and digest pinning explained |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `docker build` cannot pull base image | No network or rate limit | Authenticate to the registry or use a local mirror |
| `trivy` database download fails | No network | Note it; use `trivy config` offline and record the limitation |
| `docker exec` denied | Shell not present in slim image | Use `docker run --rm image id` instead |
| Read-only test passes unexpectedly | `/app/x` inside a tmpfs | Test a path outside `/tmp` |
| `--tmpfs` with `noexec` breaks the app | Interpreter in `/tmp` | Keep the interpreter in the image; tmpfs is for scratch data |

## References

1. Docker — Dockerfile reference (`USER`, `COPY --chown`) and runtime security options. Accessed 2026-10-29.
2. Aqua Security — Trivy image and configuration scanning documentation. Accessed 2026-10-29.
3. CIS Docker Benchmark — container runtime and image controls. Accessed 2026-10-29.
4. NIST SP 800-190 — Application Container Security Guide. Accessed 2026-10-29.
