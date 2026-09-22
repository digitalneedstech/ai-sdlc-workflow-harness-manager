---
title: Extensions
description: Add a workflow in kit mode or orchestrator mode without forking the kit.
---

A new customer process is an **extension**, not a new platform. The contract depends on which [kit](/docs/capabilities/modes) the project was initialized with — pack (kit mode) or orchestrator.

```text
extensions/
  kit/              markdown pack (skill + JSON + config)
  orchestrator/     Python graphs (pipeline_extensions/)
```

## Kit mode

After `pipeline-kit init`:

1. `.pipeline/skills/{name}/SKILL.md`
2. `.pipeline/workflows/{name}.json` allowlists
3. `workflows.{name}` in `.pipeline/config.json`
4. Optional agent brief on that step’s allowlist
5. Optional receptionist row in `skills/orchestration/SKILL.md`

```bash
python3 .pipeline/loader/load_workflow.py --workflow {name} --step parent --slug try-{name}
```

To **ship** a first-party workflow in this repository, edit `kit/pipeline/` the same way, then `pipeline-kit update` in customer apps. Follow [DOCUMENT-STANDARD](/docs/reference/document-standard).

Step-by-step: [Add a workflow](/docs/guides/add-workflow).

## Orchestrator mode

Associates add Python graphs. Kit mode never imports these files.

```bash
pipeline-kit workflows --scaffold my-review
```

That writes `pipeline_extensions/my_review.py` plus a brief. Do not reuse a first-party name.

Copy-ready examples in the kit clone (`security-review`, `ci-audit`, `dependency-audit`, `accessibility-review`):

```bash
cp -R extensions/orchestrator/pipeline_extensions /path/to/your-app/
pipeline-kit init --mode orchestrator --ide cursor
pipeline-kit workflows
pipeline-kit run --slug pci-sample --workflow security-review --runner fake \
  --request "review auth, secrets, and CSRF on the checkout routes"
```

You can also register a `pipeline_kit.workflows` setuptools entry point. The public import is:

```python
from pipeline_orchestrator.graph import AgentStep, SignoffGate, WorkflowSpec
```

## What not to mix

| Do | Do not |
|----|--------|
| Add a kit workflow in `.pipeline/` (or `kit/pipeline/` to ship it) | Expect `pipeline_extensions/` to run in kit mode |
| Add an orchestrator workflow in `pipeline_extensions/` | Expect the markdown loader to run that graph |
| Keep first-party names reserved | Replace `feature-development` with a custom file of the same name |
