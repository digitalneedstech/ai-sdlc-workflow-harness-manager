# Local deploy runbook

| Attribute | Value |
|-----------|--------|
| Type | Project overlay (edit this file) |
| Audience | devops-agent |
| Adapt | **Required on every new project.** Replace the table and targets with this repository’s apps, commands, and health URLs. |

Source of truth for **this repository**. Devops follows this file and
`scripts/deploy-local.sh`. The shipped script exits non-zero until you
implement it. Do not invent a cloud or Kubernetes procedure.

## Adapt for this project

1. Name each locally runnable surface (UI, API, worker).
2. Fill the table below with **this repo’s** build command, serve command,
   and HTTP probe. Bind `127.0.0.1` only.
3. Set matching names in `.pipeline/config.json` → `deploy.targets`.
4. Implement the same names in `scripts/deploy-local.sh`.

Until those four match, devops must not report SUCCESS.

## What “deployed locally” means

| Surface | Build | Serve | Success probe |
|---------|-------|-------|----------------|
| `{app-a}` | `{build command}` | `{serve on 127.0.0.1:PORT if free}` | `GET http://127.0.0.1:{PORT}{path}` returns success |
| `{app-b}` | `{build command}` | reuse listener if the port already answers | same |

If a port is already in use, **reuse** it (probe). Do not kill a process this
script did not start.

## Target selection

Parent sets `DEPLOY_TARGET` to one value from `deploy.targets` in
`.pipeline/config.json` (default `deploy.target`). Typical names:

- `auto` — choose from `implementation-notes.md` / developer HANDOFF; else the
  first target in `deploy.targets`
- named app — that surface only
- `both` — every surface listed above (only if you implement it)

Do not hard-code demo application names in the parent prompt. Read
`deploy.targets`.

## Commands (always via script)

From the repository root:

```bash
chmod +x .pipeline/skills/local-deployment/scripts/deploy-local.sh
.pipeline/skills/local-deployment/scripts/deploy-local.sh "$FEATURE_SLUG" "$DEPLOY_TARGET"
```

Optional environment variables (define only those the script understands):

| Variable | Default | Meaning |
|----------|---------|---------|
| `{START_FLAG}` | `0` | `1` = start a long-lived process only if its port is free |
| `{HEALTH_PATH}` | `/` | Path to GET after the service is up |

Do not install dependencies in this step. If the workspace is not already set
up, fail with that reason.

## Validation gate

All of the following must be true:

1. Script exit code `0`
2. `features/{slug}/deploy-result.env` has `OVERALL=passed`
3. Each required surface has `{SURFACE}_HEALTH=passed` or an explicit `skipped`
   with reason
4. No secret material in HANDOFF

If any fail, the pipeline does **not** complete.

## Safety

- Bind `127.0.0.1` only.
- Leave a preview running for the operator; record a PID only if **this**
  script started the process.
- Never `git push`. Never deploy off-machine.
- Never copy tokens, passwords, or bootstrap secrets into chat or HANDOFF.
