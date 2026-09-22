# Orchestrator mode

Optional `--mode orchestrator`. The chain lives in this Python package
(installed as `pipeline_orchestrator`). `init` does **not** copy
`agents/`, `skills/`, `loader/`, or `workflows/`.

Associates add extra workflows with `pipeline_extensions/` in the
customer app, or a `pipeline_kit.workflows` entry point. Kit mode never
loads those files.

```bash
uv tool install -e ".[orchestrator]"
cd /path/to/your-app
pipeline-kit init --mode orchestrator --ide cursor
pipeline-kit run --slug checkout-redesign --workflow feature-development \
  --request "redesign checkout so guests can pay without an account"
```

Copy-ready examples: [`extensions/orchestrator/`](../extensions/orchestrator/).
Scaffold: `pipeline-kit workflows --scaffold NAME`.

Public import (do not change): `from pipeline_orchestrator.graph import WorkflowSpec`.
