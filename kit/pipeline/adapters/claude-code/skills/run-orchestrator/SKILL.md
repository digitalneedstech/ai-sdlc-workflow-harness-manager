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

Tell the user to run:

```bash
pipeline-kit run --slug {kebab-summary} --workflow feature-development
```

Custom associate workflows (orchestrator only):

```bash
pipeline-kit workflows --scaffold my-review
pipeline-kit run --slug {kebab-summary} --workflow my-review
```

Sign-off gates pause with exit 3:

```bash
pipeline-kit approve --slug {slug} --gate requirements
pipeline-kit resume --slug {slug}
```
