---
title: Adapt local deploy
description: Fill the runbook and deploy-local.sh for this repository. Reuse healthy listeners. No secrets in HANDOFF.
---

The shipped runbook and script are **empty overlays**. They do not start an application until you fill them in.

| File | What to change |
|------|----------------|
| `.pipeline/config.json` → `deploy.targets` | Names you will pass as `DEPLOY_TARGET` |
| `.pipeline/skills/local-deployment/assets/local-deploy-runbook.md` | How a human (and devops) starts **your** apps |
| `.pipeline/skills/local-deployment/scripts/deploy-local.sh` | Build, start, and health-check **your** folders and ports |

Until the script matches this repository, devops must not report SUCCESS. You can document a dry-run (“build only, no preview”) in the runbook so the pipeline can still complete.

## Patterns (adapt names and ports to this repo)

**SPA + API** — targets `web`, `api`, `both`, `auto`. Build the UI, preview bound to `127.0.0.1`, start the API, health-check both.

**JVM service + UI** — package the service, serve the UI, probe the health endpoint you already use.

**Python API only** — `pytest` optional, then the existing ASGI/WSGI command on `127.0.0.1`.

## Hard rules

- **Do not** start a second copy if the port is already listening. Health-check the existing process. See [reuse listeners](/docs/troubleshooting/deploy-listeners).
- **Do not** put tokens or bootstrap secrets in HANDOFF or wiki.
- This skill is local build/serve/validate — not cloud deploy.
