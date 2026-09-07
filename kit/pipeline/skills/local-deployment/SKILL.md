---
name: local-deployment
description: >-
  Invoke this skill when the feature pipeline reaches local deploy (after tester
  SUCCESS on feature class, or after developer/critic on micro/minor), or the user
  asks to build/serve/health-check this repo on localhost.
  Use devops-agent as a separate Task. Do not deploy to remote hosts, do not
  register Chorus daemons, do not print bootstrap secrets.
---

# Local deployment

Prove the feature **runs on this machine**. Parent spawns **devops-agent** after the previous specialist on that class (tester / developer-critic / developer). Health must pass before the parent spawns **retro-agent**. Pipeline is **not** complete until retro has also run.

**Progressive loading:** follow this file first. Read the runbook and run **only** the scripts below — do not invent `kubectl`, Docker, or cloud deploys.

| When | Read / run |
|------|----------------|
| Before any command | [assets/local-deploy-runbook.md](assets/local-deploy-runbook.md) |
| All local deploy | [scripts/deploy-local.sh](scripts/deploy-local.sh) `{slug} {target}` |

## Isolation

- Localhost only (`127.0.0.1`). No git commit/push, no `npm publish`, no daemon register.
- Do not start a **second** Chorus engine if `:8000` is already up — health-check the existing one.
- Do not log or paste bootstrap secrets, tokens, or `.env` values into HANDOFF.
- Product code edits are out of scope (send back to developer). Scripts and `features/{slug}/deploy-*` are in scope.

## Steps

1. Confirm the previous specialist succeeded (tester on **feature**; developer-critic on **minor**; developer on **micro**). Feature class also needs `qa-test-cases.md`.
2. Read the runbook. Set `DEPLOY_TARGET` from parent (`auto` | `ecommerce-store` | `chorus` | `both`).
3. Run `scripts/deploy-local.sh` from repo root (see runbook). Capture exit code and `features/{slug}/deploy-result.env`.
4. If build or health fails: HANDOFF `FAILED` — **do not** mark the pipeline complete.
5. If checks pass: write `HANDOFF-devops.md` `SUCCESS` with `PARENT_NEXT: retro-agent`. Parent then spawns retro; **PIPELINE_COMPLETE** is after retro.

## Failure

| Case | HANDOFF |
|------|---------|
| Previous specialist not SUCCESS | `FAILED` `INPUT_MISSING` |
| Script exit ≠ 0 | `FAILED` — include `deploy-result.env` |
| Port conflict you did not start | Health-check existing process; do not kill it |
| Engine not running and `ENGINE_START` unset | Chorus **build** may still pass; engine health is `skipped`. Storefront health must pass for `ecommerce-store` / `both` |
