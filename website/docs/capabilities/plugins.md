---
title: Plugins
description: Optional Graphify and Archify. Init does not install them. The kit never vendors their renderers.
---

Graphify (QA graph) and Archify (Architect diagrams) are **optional**. `pipeline-kit init` does not install them. Pipeline Kit never vendors them and never `import`s Graphify.

```bash
pipeline-kit plugins list
pipeline-kit plugins status
```

| Plugin | What it does | Default |
|--------|----------------|---------|
| **[Graphify](/docs/capabilities/graphify)** | Official CLI writes `graphify-out/graph.json` for QA test design | Off until `knowledge init` / `plugins install graphify` |
| **[Archify](/docs/capabilities/archify)** | Pinned Agent Skill (`tt-a1i/archify` `v2.16.0`) for Architect HTML diagrams | Off until `plugins install archify`. Mermaid in `architecture.md` stays required |

`--scope project|user` on install/uninstall/status. Project-scope Cursor install is the usual choice.

Uninstall removes the **managed skill** (and Graphify’s own uninstall). It does not delete `features/{slug}/diagrams/` or, unless `--purge`, `graphify-out/`.
