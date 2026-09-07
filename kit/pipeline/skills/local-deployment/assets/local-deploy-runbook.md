# Local deploy runbook

Source of truth for **this repo**. Devops-agent must follow it; do not substitute a cloud or Kubernetes procedure.

Repo root = directory that contains `pyproject.toml`, `ecommerce-store/`, and `web/`.

## What “deployed locally” means

| Surface | Build (required) | Serve | Success probe |
|---------|------------------|-------|----------------|
| Storefront `ecommerce-store/` | `npm run build` | `npm run preview -- --host 127.0.0.1 --port 4173` if 4173 is free | HTTP `200` from `http://127.0.0.1:4173/` |
| Chorus console `web/` | `npm run build` (engine serves `web/dist`) | Do **not** start a second Vite for production-mode console | If engine already on `:8000`: `GET http://127.0.0.1:8000/health` body contains `"status"` |
| Chorus engine | not a separate compile | Start **only** if `ENGINE_START=1` **and** `:8000` is free | Same `/health` probe |

Default autonomous path: **build + storefront preview + curl**. Do not register `canvas-agent` or print the engine bootstrap secret.

## Target selection

Parent sets `DEPLOY_TARGET`:

- `ecommerce-store` — storefront only (typical feature on Northline Market)
- `chorus` — `web/` production build; pytest if `RUN_PYTEST=1`; engine health only if already listening
- `both` — storefront + `web/` build
- `auto` — script reads `features/{slug}/implementation-notes.md` and `HANDOFF-developer.md`; if neither mentions `web/` or `src/canvas_`, default **ecommerce-store**

## Commands (always via script)

From repo root:

```bash
chmod +x .pipeline/skills/local-deployment/scripts/deploy-local.sh
.pipeline/skills/local-deployment/scripts/deploy-local.sh "$FEATURE_SLUG" "$DEPLOY_TARGET"
```

Optional env:

| Variable | Default | Meaning |
|----------|---------|---------|
| `ENGINE_START` | `0` | `1` = start `uv run canvas-engine` only if `:8000` is free |
| `RUN_PYTEST` | `0` | `1` = `uv run pytest -q` when target includes chorus |
| `STORE_PORT` | `4173` | Vite preview port |
| `HEALTH_PATH` | `/` | Extra storefront path to GET after `/` |

Do not run `npm install` / `uv sync` in this step (hook-blocked; assume the workspace is already set up). If `node_modules` is missing, fail with that reason.

## Validation gate (pipeline complete)

All of the following must be true:

1. Script exit code `0`
2. `features/{slug}/deploy-result.env` has `OVERALL=passed`
3. For storefront targets: `STORE_HEALTH=passed`
4. No secret material in HANDOFF

If any fail → pipeline **does not** complete.

## Safety

- Bind `127.0.0.1` only.
- If a port is already in use, **reuse** it (curl). Do not `kill -9` foreign PIDs.
- Leave preview running for the user; record PID in `features/{slug}/.preview.pid` only if **this** script started it.
- Never `git push`, never deploy off-machine.
