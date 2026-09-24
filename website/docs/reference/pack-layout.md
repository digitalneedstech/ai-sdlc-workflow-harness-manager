---
title: Pack layout
description: What .pipeline contains after init, and what the kit repository contains.
---

## After `pipeline-kit init`

```text
.pipeline/
  config.json
  loader/
  skills/
  agents/
  rules/
  workflows/
  wiki/
  commands/          # placeholder; none shipped
  adapters/          # copied pieces as needed
  docs/              # CUSTOMER-GUIDE, DOCUMENT-STANDARD, OBSERVABILITY
  hooks/             # policy guardrails (before-shell, before-mcp, …)
  hooks/obs/         # collector scripts; merged by obs install
features/            # run artifacts (gitignored by most teams)
```

IDE adapter (one of):

```text
.cursor/skills/run-workflow/
.claude/skills/run-workflow/
.github/skills/run-workflow/
```

## Kit repository (this repo)

Grouped by role. Python import names (`pipeline_plugins`,
`pipeline_orchestrator`, …) are unchanged.

```text
kit/                    kit mode pack → <app>/.pipeline
orchestrator/           orchestrator mode engine
extensions/kit/         add a markdown workflow
extensions/orchestrator/  associate Python workflows
capabilities/plugins/   Graphify + Archify
capabilities/knowledge/ QA overlay (consumes Graphify)
capabilities/observability/
capabilities/eval/
capabilities/feature_flags/
```

| Path | Role |
|------|------|
| `pyproject.toml` / `install.sh` | Install the `pipeline-kit` command |
| `install.py` | CLI implementation |
| `kit/pipeline/` | Bundled pack copied to `<app>/.pipeline` |
| `orchestrator/` | Code-owned engine (`--mode orchestrator`) |
| `extensions/` | Add workflows in kit mode or orchestrator mode |
| `capabilities/` | Plugins, knowledge, observability, eval, feature flags |
| `CUSTOMER-GUIDE.md` | Canonical handbook |
| `OBSERVABILITY.md` | Canonical obs handbook |
| `website/` | This documentation site (not copied into packs) |
| `tests/` | pytest |

See [Repository layout](/docs/intro/repo-layout).
