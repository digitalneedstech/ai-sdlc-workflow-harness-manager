---
title: Kit vs orchestrator
description: Two runtimes, the same first-party workflow names.
---

Pipeline Kit has **two modes**. Pick one per project at `init`. You can add workflows in either mode — see [Extensions](/docs/capabilities/extensions).

| | Kit mode (default) | Orchestrator mode |
|--|--------------------|-------------------|
| Flag | `--mode kit` | `--mode orchestrator` |
| Source in this repo | `kit/pipeline/` | `orchestrator/` |
| What `init` copies | Full markdown pack → `.pipeline/` | No `agents/`, `skills/`, `loader/`, or `workflows/` |
| How a step runs | IDE `run-workflow` + loader allowlist | `pipeline-kit run` via Cursor SDK (or `--runner fake`) |
| Extra workflows | Skill + JSON + `config.json` | `pipeline_extensions/*.py` or entry points |
| Extra install | None | `uv tool install -e ".[orchestrator]"` and `CURSOR_API_KEY` for live runs |

First-party names are the same in both modes: `ask`, `feature-development`, `jira-story`, `jira-epic`, `jira-bug`.

## Kit mode

```bash
pipeline-kit init --ide cursor
pipeline-kit doctor --ide cursor
pipeline-kit workflows
```

Process files sit in `.pipeline/`. The IDE discovers only `run-workflow`.

## Orchestrator mode

```bash
uv tool install -e ".[orchestrator]"
cd /path/to/your-app
pipeline-kit init --mode orchestrator --ide cursor
# chat text is not inherited
pipeline-kit run --slug checkout-redesign --workflow feature-development \
  --request "redesign checkout so guests can pay without an account"
pipeline-kit approve --slug checkout-redesign --gate requirements
pipeline-kit resume --slug checkout-redesign
```

Custom workflows do not appear in kit-mode `workflows` listings and do not change `.pipeline/workflows/`.

Copy-ready examples: `extensions/orchestrator/` in the kit clone.

## Source folders

See [Repository layout](/docs/intro/repo-layout).
