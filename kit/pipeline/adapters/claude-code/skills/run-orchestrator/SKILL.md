---
name: run-workflow
description: >-
  Orchestrator mode receptionist. Do not run the markdown loader. Tell the
  user to run pipeline-kit run.
---

# Run workflow (orchestrator)

| Attribute | Value |
|-----------|--------|
| Type | IDE adapter |
| Audience | Receptionist in this IDE |
| Adapt | Do not fork per product. Orchestration lives in the pipeline-kit wheel. |

This project is in **orchestrator mode**. Workflow briefs are not on disk.

Do not run `.pipeline/loader/load_workflow.py`. That file is not installed.

The chat message does **not** reach `pipeline-kit run` by itself. You must
persist it, then tell the user to run the CLI.

1. Invent a kebab slug from the ask (`add a line in AGENTS.md` → `agents-md-line`).
2. Write the user's message **verbatim** to `features/{slug}/request.md`.
3. Tell the user to run the command below. Do not invent a different ask.

```bash
pipeline-kit run --slug {kebab-summary} --workflow feature-development --request-file features/{kebab-summary}/request.md
```

`--request "…"` is the same text inline. `--slug` is only the folder name.

Custom associate workflows (orchestrator only):

```bash
pipeline-kit workflows --scaffold my-review
pipeline-kit run --slug {kebab-summary} --workflow my-review --request-file features/{kebab-summary}/request.md
```

Sign-off gates pause with exit 3:

```bash
pipeline-kit approve --slug {slug} --gate requirements
pipeline-kit resume --slug {slug}
```
