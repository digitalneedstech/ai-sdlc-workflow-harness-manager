# Local deploy — localhost ports

- **Layer:** engine | storefront | pipeline
- **Load when:** devops, `deploy-local.sh`, preview not coming up, engine already running, bootstrap secret in chat

## Symptom

Deploy “fails” because `:8000` is busy, a second engine is started, or health checks hit the wrong host. Or secrets from first engine start leak into HANDOFF.

## Root cause

Chorus engine is long-lived (`uv run canvas-engine` → `127.0.0.1:8000` + `/health`). Storefront preview is Vite on **`127.0.0.1:4173`**. Binding anything else, or killing a foreign PID, breaks the operator’s session.

## Do not

- Start a second `canvas-engine` if `:8000` already answers.
- Put the bootstrap secret in `HANDOFF` or wiki.
- `curl` non-localhost (pipeline hook denies it).
- Treat tester or devops SUCCESS as pipeline complete (retro is last on **every** class).

## Fix / convention

Run only `.pipeline/skills/local-deployment/scripts/deploy-local.sh`. Reuse listeners. `ENGINE_START=1` only if `:8000` is free. Storefront success = HTTP 200 on `:4173`. Engine health = GET `/health` when already up.

## Files

`local-deployment/assets/local-deploy-runbook.md`, `scripts/deploy-local.sh`, `devops-agent.md`

## How to confirm

`features/{slug}/deploy-result.env` has `OVERALL=passed`. URLs are 127.0.0.1 only.
