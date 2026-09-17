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

| Path | Role |
|------|------|
| `pyproject.toml` / `install.sh` | Install the `pipeline-kit` command |
| `install.py` | CLI implementation |
| `kit/pipeline/` | Bundled pack copied to `<app>/.pipeline` |
| `knowledge/` | QA overlay commands |
| `pipeline_plugins/` | Graphify and Archify lifecycle |
| `pipeline_features/` | Feature flag CLI |
| `pipeline_observability/` | Obs CLI, scoring, adapters |
| `CUSTOMER-GUIDE.md` | Canonical handbook |
| `OBSERVABILITY.md` | Canonical obs handbook |
| `website/` | This documentation site (not copied into packs) |
| `tests/` | pytest |
