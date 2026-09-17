---
title: Loader and allowlists
description: The receptionist runs load_workflow.py so each specialist reads only the current step’s files.
---

The loader is how a large pack stays cheap. `run-workflow` runs:

```bash
python3 .pipeline/loader/load_workflow.py --workflow {name} --step {step} --slug {slug}
```

It writes `allowed_reads` (and active context under `{pack}/state/active-context.json`). The specialist **must not** open other `.pipeline/skills/` files.

## What is allowlisted

Each `.pipeline/workflows/{name}.json` lists `context.parent.files` and `context.steps.{agent}.files` (paths from the project root, `.pipeline/…` prefix).

BA does not ingest the deploy runbook. The developer does not ingest Jira intake. Wiki pages are loaded only when INDEX triggers match — not as a folder.

## Receptionist

`AGENTS.md` is a routing table. The agent does not load the pack until `run-workflow` runs the loader. Weather, locations, and other unrelated asks skip the pipeline entirely.

## Do not edit

`.pipeline/loader/` is kit machinery. Add files by listing them on a workflow allowlist, not by teaching the parent to glob `.pipeline/`.
