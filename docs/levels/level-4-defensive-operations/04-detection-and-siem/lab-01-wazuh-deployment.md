---
title: "LAB-404-01 · Deploy a Local SIEM and Ingest Telemetry"
description: "Run single-node Wazuh 4.14.9, enroll an Ubuntu agent, and prove ingestion with a synthetic event before writing any rules."
module_code: CYB-404
level: 4
kind: lab
prerequisites: [CYB-404]
estimated_minutes: 180
difficulty: advanced
safety: isolated-vm
lab_ids: [LAB-404-01]
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [wazuh, siem, docker, agent-enrollment, ingestion, logtest]
---

# LAB-404-01 · Deploy a Local SIEM and Ingest Telemetry

## Scenario and background

You need somewhere for detections to live. The SIEM will run on its own VM, receive logs from `lab-ubuntu`, and be
reachable only from the lab network. Before any rule is written, you must be able to answer a simpler question with
evidence: *can I see a specific event from a specific host, parsed, with the fields I expect?*

Most first deployments fail here and then blame the rules. This lab makes ingestion provable.

## Learning objectives

1. Deploy single-node Wazuh 4.14.9 with Docker Compose on Ubuntu 24.04.
2. Configure the indexer precondition that most first attempts miss, and explain what it does.
3. Enroll an agent, confirm it is active, and confirm its clock agrees with the manager.
4. Add a monitored log file and prove a specific synthetic line is decoded and stored.
5. Inspect a decoded event's fields with `wazuh-logtest` before trusting any rule.
6. State the resource and exposure constraints of this deployment.

## Required tools and versions

| Tool | Version | Notes |
| --- | --- | --- |
| Ubuntu Server | 24.04 LTS | `lab-siem` |
| Docker Engine + Compose plugin | current stable | Compose v2 syntax (`docker compose`) |
| Wazuh | 4.14.9 | `wazuh-docker` single-node |
| Git | any | To fetch the deployment files |
| VM resources | 8 GB RAM, 4 cores, 50 GB disk | Wazuh's documented single-node requirement |

!!! warning "Authorized scope — read before you begin"
    **Targets you may use:** `lab-siem` (192.0.2.30) and `lab-ubuntu` (192.0.2.20).
    **Targets you must not use:** any host outside the lab, and no public exposure of the dashboard.

    **Exposure:** the dashboard publishes on port 443. Keep `lab-siem` on the host-only network. Do not port-forward
    it, and do not attach it to a bridged adapter. A default-credential SIEM on a shared network is a real incident,
    not a lab.

    Full rules: [Safety Policy](../../../policies/safety-policy.md).

## Threat model

The SIEM is the most valuable host in the lab: it holds authentication logs, process telemetry and alert history, and
it has an API. The threats that matter here are unauthorised access to the dashboard (weak or default credentials),
lateral access from the monitored host to the manager, and loss of data integrity through clock drift or unlogged
agent disconnection.

## Environment

| Host | Role | Address | Resources |
| --- | --- | --- | --- |
| `lab-siem` | Wazuh manager, indexer, dashboard | 192.0.2.30 | 8 GB RAM, 4 cores |
| `lab-ubuntu` | Monitored agent | 192.0.2.20 | 2 GB RAM |
| `lab-win` | Not used in this lab | 192.0.2.40 | off |

Stop `lab-win` while the SIEM runs. Two VMs plus an indexer on a 16 GB host is the practical ceiling.

## Procedure

### 1. Prepare the host

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git curl
sudo usermod -aG docker "$USER"        # log out and back in for this to take effect
docker --version && docker compose version
```

**Expected:** Docker 2x.x and Compose v2.x. A `docker compose` command that reports "unknown command" means you have
the old `docker-compose` binary only.

**The security caveat nobody mentions:** membership of the `docker` group is equivalent to root on the host. Anyone
who can run containers can mount the filesystem. Note that in your report rather than treating the group as a
convenience.

### 2. Set the indexer precondition

```bash
echo 'vm.max_map_count=262144' | sudo tee /etc/sysctl.d/99-wazuh.conf
sudo sysctl --system
sysctl vm.max_map_count
```

**Expected:** `vm.max_map_count = 262144`.

**Why:** the OpenSearch-based indexer memory-maps many segments. With the default (65530) it exits during startup with
an `insufficient max_map_count` error, and the container restarts in a loop. Setting this first saves an hour of
reading logs that say "indexer is not ready".

### 3. Fetch the deployment files

```bash
cd ~ && git clone https://github.com/wazuh/wazuh-docker.git
cd wazuh-docker
git checkout v4.14.9
cd single-node
ls
```

**Expected:** `docker-compose.yml`, `generate-indexer-certs.yml`, and configuration directories including
`config/wazuh_cluster/` and `config/wazuh_dashboard/`.

**Read the compose file before starting it.** You are looking for: published ports, volume mounts, and where the
credentials come from.

```bash
grep -nE 'image:|ports:|- [0-9]+:|INDEXER_PASSWORD|API_PASSWORD|ADMIN_PASSWORD' docker-compose.yml | head -40
ls -a | grep -E '^\.env$' && grep -nE 'PASSWORD' .env
```

**Expected:** images pinned to 4.14.9, ports 443/1514/1515/55000, and a password variable. Record which variable holds
the dashboard/admin credential in **your** deployment — do not assume a default from a tutorial. If the value is a
placeholder, change it before first start and store it in your lab password manager, not in this document.

### 4. Generate certificates and start

```bash
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d
docker compose ps
```

**Expected:** four services (`wazuh.manager`, `wazuh.indexer`, `wazuh.dashboard`, and the certs generator having
exited). `wazuh.indexer` takes the longest; give it two to three minutes.

```bash
docker compose logs --tail=40 wazuh.indexer | grep -iE 'error|started|ready' | tail -10
docker compose logs --tail=20 wazuh.manager | tail -10
```

**Expected:** the indexer reports it started; the manager reports the analysis engine and API starting. A restart loop
on the indexer almost always means `vm.max_map_count` or insufficient RAM.

### 5. Verify the API and dashboard

```bash
curl -k -s -o /dev/null -w '%{http_code}\n' https://localhost:443/
```

**Expected:** `302` (redirect to login) or `200`. A connection refusal means the dashboard container is not up.

Log in from your analyst workstation at `https://192.0.2.30/`. Accept the self-signed certificate warning — this is
why the dashboard must not be exposed beyond the host-only network; there is no publicly trusted certificate here.

Check what Docker actually bound:

```bash
sudo ss -tlnp | grep -E ':(443|1514|1515|55000)\b'
```

**Expected:** listeners on `0.0.0.0` (Docker's default) unless you change the mapping. That means the dashboard is
reachable on **every** interface the VM has. Either keep NAT detached while the SIEM runs, or bind explicitly in
`docker-compose.yml`:

```yaml
ports:
  - "192.0.2.30:443:443"
```

Then `docker compose up -d` to recreate the container. Record which option you chose and why — this is the difference
between a lab and an exposure.

**Change the admin password at first login if the deployment uses a placeholder.** Then record: the account, where the
credential is stored, and that the dashboard is reachable only from 192.0.2.0/24.

### 6. Enroll the agent

On `lab-ubuntu`:

```bash
sudo apt update && sudo apt install -y curl gnupg
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo gpg --dearmor -o /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
  | sudo tee /etc/apt/sources.list.d/wazuh.list
sudo apt update
sudo WAZUH_MANAGER='192.0.2.30' WAZUH_AGENT_NAME='lab-ubuntu' apt install -y wazuh-agent
sudo systemctl daemon-reload
sudo systemctl enable --now wazuh-agent
sudo /var/ossec/bin/wazuh-control status
```

**Expected:** `wazuh-agentd is running`, `wazuh-execd is running`, `wazuh-logcollector is running`, and
`wazuh-syscheckd is running`.

**TLS note:** the agent authenticates to the manager on port 1514 with certificates issued during enrollment. If the
agent logs `Unable to connect`, check that 1514 is reachable and that the manager is fully started — enrollment fails
if the manager's authd is not ready yet, and retrying a minute later usually works.

### 7. Confirm the agent is active and the clocks agree

Dashboard → **Agents** → `lab-ubuntu` should show **Active**. Then:

```bash
# On lab-ubuntu
date -u; timedatectl | grep -E 'synchronized|NTP'
# On lab-siem
date -u
```

**Expected:** both report UTC times within a few seconds, and `System clock synchronized: yes`.

**Why this is step seven and not an afterthought:** every correlation rule in LAB-404-03 depends on the two clocks
agreeing. A sequence rule with a two-minute window and a five-minute drift will never fire, and nothing in the SIEM
will tell you why.

### 8. Add a monitored file for controlled tests

Synthetic test lines belong in their own file, clearly separated from real logs.

```bash
# On lab-ubuntu
sudo mkdir -p /var/log/lab404
sudo touch /var/log/lab404/auth-test.log
sudo chmod 640 /var/log/lab404/auth-test.log
sudo chown root:wazuh /var/log/lab404/auth-test.log
```

Add to `/var/ossec/etc/ossec.conf` inside `<ossec_config>`:

```xml
<localfile>
  <log_format>syslog</log_format>
  <location>/var/log/lab404/auth-test.log</location>
</localfile>
```

```bash
sudo systemctl restart wazuh-agent
sudo tail -5 /var/ossec/logs/ossec.log
```

**Expected:** the log collector starts without a configuration error. A malformed XML block stops the agent — check
`ossec.log` rather than restarting repeatedly.

### 9. Prove one event end to end

Write a single line in the exact shape `sshd` produces, then find it:

```bash
echo "$(date '+%b %e %H:%M:%S') lab-ubuntu sshd[4100]: Failed password for invalid user labtest from 192.0.2.55 port 51000 ssh2" \
  | sudo tee -a /var/log/lab404/auth-test.log
sleep 20
```

Search the dashboard for `labtest`, or query the indexer's alerts. Confirm four things:

1. The event is present.
2. `agent.name` is `lab-ubuntu`.
3. The decoded fields include the source address, parsed as `data.srcip` (Wazuh's decoder naming).
4. The rule that matched has an ID you can read — this ID is what LAB-404-03 will reference.

**If the event is absent:** the file is not being read (check the `localfile` block), the agent is disconnected, or the
line's timestamp format is not parseable. Test the line directly before changing anything else:

```bash
sudo /var/ossec/bin/wazuh-logtest
# paste the line at the prompt
```

**Expected:** `wazuh-logtest` prints the decoder stage, the extracted fields, and the matched rule(s) with levels. This
tool is the difference between debugging a rule and guessing at one.

## Evidence to collect

- `evidence/versions.txt` — Docker, Compose, Wazuh image tags.
- `evidence/indexer-health.txt` — output of `docker compose ps` and the indexer log excerpt.
- `evidence/agent-status.txt` — `wazuh-control status` and the dashboard agent state.
- `evidence/clock.txt` — both hosts' UTC time and NTP synchronisation state.
- `evidence/logtest.txt` — the decoded fields and matched rule ID for the synthetic line.
- `evidence/event.json` — the stored alert, with `agent.name`, `data.srcip`, `rule.id`.
- `evidence/exposure.md` — which interfaces and ports are reachable, and from where.

## Verification

- [ ] `vm.max_map_count` is 262144 and persists after reboot.
- [ ] All containers running, indexer not restarting.
- [ ] Dashboard reachable from the lab network and **not** from the host's bridged/NAT address.
- [ ] Default or placeholder credentials replaced, and the storage location recorded.
- [ ] Agent active, with all four daemons running.
- [ ] Clocks agree within seconds, NTP synchronised on both.
- [ ] `wazuh-logtest` shows the decoder and rule ID for the synthetic line.
- [ ] The stored event contains `agent.name`, `data.srcip` and `rule.id`.
- [ ] The synthetic file is separate from real logs and labelled.

## Teardown and reset

```bash
# On lab-siem, from ~/wazuh-docker/single-node
docker compose down -v          # -v removes indexer volumes: all collected data is lost
```

Keep the evidence directory outside the containers. Revert the `lab-siem` snapshot to return to a clean host, and
remove the agent's test file on `lab-ubuntu` if you are not continuing to LAB-404-02.

## Reflection

1. Why does the indexer need `vm.max_map_count`, and what would you check first if it kept restarting?
2. The dashboard uses a self-signed certificate. What does that tell you about the trust boundary, and what would you
   need before exposing an equivalent service in production?
3. You verified the event with `wazuh-logtest` before searching the dashboard. What class of problem does that isolate?
4. Agent enrollment uses certificates issued by the manager. What happens if an agent's key is copied to another
   host, and how would you notice?

## Rubric

| Criterion | 1 — Incomplete | 3 — Competent | 5 — Proficient |
| --- | --- | --- | --- |
| Deployment | Containers start inconsistently | All services stable | Preconditions documented, logs read, credentials handled properly |
| Ingestion | Agent installed, status unknown | Agent active, event searchable | Event decoded, fields named, rule ID identified via `wazuh-logtest` |
| Time | Not checked | Clocks compared | NTP state recorded with the reason it matters for correlation |
| Exposure | Dashboard on a bridged interface | Host-only | Ports and reachability documented, credential storage stated |

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Indexer exits, `max virtual memory areas` error | `vm.max_map_count` too low | Set 262144, `sysctl --system`, restart |
| Indexer OOM-killed | Less than 8 GB assigned to the VM | Increase VM RAM or reduce other VMs |
| Dashboard unreachable | Container not started, or wrong port | `docker compose ps`; check 443 mapping |
| Agent `Unable to connect` | Manager not ready, 1514 blocked, wrong IP | Verify manager health, `ss -tlnp`, retry enrollment |
| Agent active but no events | `localfile` block not loaded, file unreadable | Check `ossec.log`; verify permissions and path |
| Event stored but no `data.srcip` | Decoder did not match the line format | Compare with a real `sshd` line; use `wazuh-logtest` |
| Timestamps an hour off | Timezone mismatch between agent and manager | Use UTC consistently; check `timedatectl` |
| Disk watermark errors | 50 GB disk too small after volume growth | Prune old indices, increase disk |

## References

1. Wazuh 4.14.9 — Docker single-node deployment and requirements.
   <https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html> Accessed 2026-10-29.
2. Wazuh — agent enrollment on Debian/Ubuntu. <https://documentation.wazuh.com/current/installation-guide/wazuh-agent/wazuh-agent-package-linux.html> Accessed 2026-10-29.
3. Wazuh — `localfile` configuration reference and `wazuh-logtest`.
   <https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/localfile.html> Accessed 2026-10-29.
4. OpenSearch — `vm.max_map_count` requirement. Accessed 2026-10-29.
5. Docker — Linux post-installation steps (docker group privileges). Accessed 2026-10-29.
