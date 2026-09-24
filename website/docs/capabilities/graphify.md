---
title: Graphify plugin
description: Official Graphify CLI and IDE skill. Used by the QA knowledge overlay.
---

Graphify produces `graphify-out/graph.json` from the application source. The kit registers the official IDE skill and shells out to the official CLI. It does not vendor a renderer.

## Prerequisites

```bash
uv tool install graphifyy
```

## Install / extract / uninstall

```bash
pipeline-kit knowledge init --register-skill --ide cursor
# same skill registration:
pipeline-kit plugins install graphify --ide cursor
pipeline-kit knowledge extract
pipeline-kit plugins status --plugin graphify
pipeline-kit plugins uninstall graphify --ide cursor
# also delete graphify-out/:
pipeline-kit plugins uninstall graphify --ide cursor --purge
```

Cursor project install writes `.cursor/rules/graphify.mdc` via Graphify’s own `graphify cursor install`. Uninstall calls `graphify cursor uninstall`. `--purge` is the only way the kit deletes `graphify-out/`.

If extract fails, run the official commands yourself:

```text
uv tool install graphifyy
graphify install
graphify extract . --code-only
```

Then continue [knowledge bootstrap](/docs/capabilities/knowledge).

## Pack gap

`pipeline-kit scan` reads `graphify-out/graph.json` and the installed workflows, skills, rules, and hooks. It writes `features/assessment/` (report, plan, and `prompt.md`). It does not call a model and it does not write rule, skill, or agent bodies. It needs the `assess` extra and an `assess` license. Output used to be `features/pack-scan/`.

In chat, ask to assess this repo. The `repo-assessment` workflow follows `features/assessment/prompt.md` and the templates in `.pipeline/skills/repo-assessment/assets/`. Scan does not turn on `test_design`. `knowledge init` stays the QA overlay.
