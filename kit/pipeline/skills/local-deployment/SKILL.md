---
name: local-deployment
description: >-
  Invoke this skill when the feature pipeline reaches local deploy (after tester
  SUCCESS on feature class, or after developer/critic on micro/minor), or the user
  asks to build/serve/health-check this repo on localhost.
  Use devops-agent as a separate Task. Do not deploy to remote hosts. Do not
  print secrets.
---

# Local deployment

| Attribute | Value |
|-----------|--------|
| Type | Skill |
| Audience | The named agent, or the parent when this file is on the allowlist |
| Adapt | **Required:** rewrite the runbook and `deploy-local.sh` for this repository. The shipped script is a placeholder and fails until you do. Read `deploy.targets` from config. |

Prove the feature **runs on this machine**. Parent spawns **devops-agent** after the previous specialist on that class (tester / developer-critic / developer). Health must pass before the parent spawns **retro-agent**. Pipeline is **not** complete until retro has also run.

**Progressive loading:** follow this file first. Read the runbook and run **only** the scripts below — do not invent `kubectl`, Docker, or cloud deploys.

| When | Read / run |
|------|----------------|
| Before any command | [assets/local-deploy-runbook.md](assets/local-deploy-runbook.md) |
| All local deploy | [scripts/deploy-local.sh](scripts/deploy-local.sh) `{slug} {target}` |

## Isolation

- Localhost only (`127.0.0.1`). No git commit/push, no `npm publish`.
- Do not start a second copy of a service whose port already answers — probe the existing process.
- Do not log or paste secrets, tokens, or `.env` values into HANDOFF.
- Product code edits are out of scope (send back to developer). Scripts and `features/{slug}/deploy-*` are in scope.

## Steps

1. Confirm the previous specialist succeeded (tester on **feature**; developer-critic on **minor**; developer on **micro**). Feature class also needs `qa-test-cases.md`.
2. Read the runbook. Set `DEPLOY_TARGET` from the parent to one name in `deploy.targets` (config).
3. Run `scripts/deploy-local.sh` from repo root (see runbook). Capture exit code and `features/{slug}/deploy-result.env`.
4. If build or health fails: HANDOFF `FAILED` — **do not** mark the pipeline complete.
5. If checks pass: write `HANDOFF-devops.md` `SUCCESS` with `PARENT_NEXT: retro-agent`. Parent then spawns retro; **PIPELINE_COMPLETE** is after retro.

## Failure

| Case | HANDOFF |
|------|---------|
| Previous specialist not SUCCESS | `FAILED` `INPUT_MISSING` |
| Script exit ≠ 0 | `FAILED` — include `deploy-result.env` |
| Port conflict you did not start | Health-check existing process; do not kill it |
| Optional long-lived process not running | Health for that surface is `skipped` only if the runbook allows it. Required surfaces must pass. |
