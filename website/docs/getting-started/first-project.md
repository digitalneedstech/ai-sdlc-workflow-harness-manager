---
title: First project
description: init, doctor, workflows — what lands on disk in a customer repository.
---

After the CLI is installed, initialize **one application repository**.

```bash
cd /path/to/your-app
pipeline-kit init --ide cursor
pipeline-kit doctor --ide cursor
pipeline-kit workflows
```

Use `--ide claude-code`, `--ide github`, or `--ide none` when appropriate.

Default is **kit mode** (markdown pack). Optional **orchestrator mode** runs the same first-party names from Python:

```bash
pipeline-kit init --mode orchestrator --ide cursor
```

See [Kit vs orchestrator](/docs/capabilities/modes).

## What you should see

- `.pipeline/` with workflows, skills, agents, wiki, loader, and `config.json`
- `.pipeline/docs/CUSTOMER-GUIDE.md` and `DOCUMENT-STANDARD.md`
- `.pipeline/docs/OBSERVABILITY.md`
- The `run-workflow` skill under the IDE folder you chose

`doctor` checks Python, pack, config, loader, marker, and the optional IDE adapter. `workflows` lists names from the active pack.

## What init does not do

- It does **not** edit root `AGENTS.md`. You paste the routing table ([guide](/docs/guides/agents-md)).
- It does **not** enable QA knowledge, Graphify, Archify, or observability.
- It does **not** fill `deploy-local.sh`. That script is a placeholder until you [adapt local deploy](/docs/guides/local-deploy).

## Overlay next

Every new project must customize two files, then deploy and test runbooks if the sample script does not match the stack:

1. [AGENTS.md](/docs/guides/agents-md)
2. [config.json](/docs/guides/config)
3. Optional: [gitignore](/docs/guides/gitignore)

Then run the [new-project checklist](/docs/getting-started/checklist).
