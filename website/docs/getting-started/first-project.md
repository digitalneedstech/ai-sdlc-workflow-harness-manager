---
title: First project
description: Pick a kit at init, then doctor and workflows — what lands on disk.
---

After the CLI is installed, initialize **one application repository**. You must pick a kit. If you omit `--mode`, you get **kit mode**.

Compare them first if you are unsure: [Two kits — pack and orchestrator](/docs/capabilities/modes).

## Kit mode (default)

The markdown pack. Most customer engagements should use this.

```bash
cd /path/to/your-app
pipeline-kit init --ide cursor
pipeline-kit doctor --ide cursor
pipeline-kit workflows
```

Use `--ide claude-code`, `--ide github`, or `--ide none` when appropriate.

### What you should see

- `.pipeline/` with workflows, skills, agents, wiki, loader, hooks, and `config.json`
- `.pipeline/docs/CUSTOMER-GUIDE.md` and `DOCUMENT-STANDARD.md`
- `.pipeline/docs/OBSERVABILITY.md`
- The `run-workflow` skill under the IDE folder you chose
- Policy guardrails merged into `.cursor/hooks.json` when `--ide cursor`

`doctor` checks Python, pack, config, loader, marker, and the optional IDE adapter. `workflows` lists names from the active pack.

Work then happens in the IDE via `run-workflow`. Next: [Your first workflow](/docs/getting-started/first-workflow).

## Orchestrator mode

The Python engine. Same workflow names; different control surface.

```bash
uv tool install -e ".[orchestrator]"
cd /path/to/your-app
pipeline-kit init --mode orchestrator --ide cursor
pipeline-kit doctor --ide cursor
pipeline-kit workflows
```

Set `CURSOR_API_KEY` for live runs. Chat text is **not** inherited.

```bash
pipeline-kit run --slug checkout-redesign --workflow feature-development \
  --request "redesign checkout so guests can pay without an account"
```

### What you should see

- A slim `.pipeline/` — `config.json`, docs, hooks, wiki. **No** `agents/`, `skills/`, `loader/`, or `workflows/`
- `install.json` with `"mode": "orchestrator"`
- The IDE `run-workflow` skill, with orchestrator wording (same path as kit mode)
- The same first-party names from `pipeline-kit workflows`

`--runner fake` and `--dry-run` do not call the SDK. Copy-ready extra workflows: `extensions/orchestrator/` in the kit clone.

## What init does not do

- It does **not** edit root `AGENTS.md`. You paste the routing table ([guide](/docs/guides/agents-md)). Kit mode needs that table; orchestrator mode is driven from the CLI.
- It does **not** enable QA knowledge, Graphify, Archify, or observability.
- It does **not** fill `deploy-local.sh`. That script is a placeholder until you [adapt local deploy](/docs/guides/local-deploy).

## Overlay next

Every new project must customize two files, then deploy and test runbooks if the sample script does not match the stack:

1. [AGENTS.md](/docs/guides/agents-md)
2. [config.json](/docs/guides/config)
3. Optional: [gitignore](/docs/guides/gitignore)

Then run the [new-project checklist](/docs/getting-started/checklist).
