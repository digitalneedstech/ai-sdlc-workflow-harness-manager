---
title: Archify plugin
description: Pinned Architect HTML diagrams. Mermaid in architecture.md stays required.
---

Archify is a pinned Agent Skill (`tt-a1i/archify` **`v2.16.0`**). When `architecture_diagrams.enabled` is true, Architect also writes `features/{slug}/diagrams/manifest.json` (`delivered` or `mermaid-fallback`).

Mermaid in `architecture.md` remains **required**. Missing GitHub CLI, Node, Chrome, or a failed `deliver` must not block a valid mermaid architecture.

## Prerequisites

- GitHub CLI **v2.90+** (`gh skill`)
- **Node.js 18+**
- Chrome optional (`visual-check`)

## Install

```bash
pipeline-kit plugins install archify --ide cursor --scope project
pipeline-kit plugins status --plugin archify
pipeline-kit plugins uninstall archify --ide cursor
```

The kit runs (never tracks `main`):

```text
gh skill install tt-a1i/archify archify --pin v2.16.0 --agent cursor --scope project
```

Project-scope Cursor install lands in `.agents/skills/archify/`. `--scope user` installs under the home directory. Teams often commit the pinned skill.

Uninstall deletes only a managed Archify skill directory after verifying source and path. Generated `features/{slug}/diagrams/` files stay. `gh skill` has no remove command.

## Runtime notes

- Delivered HTML is self-contained interactive HTML (inline JavaScript). Treat it as active content when publishing.
- Unattended Architect runs should set `ARCHIFY_UPDATE_CHECK_DISABLED=1` so Archify does not fetch an update manifest. Archify does not send repository contents on that check.
- If Archify is missing or deliver fails, Architect keeps mermaid and records `mermaid-fallback`.

`pipeline-kit plugins status --plugin archify` prints recovery. Typical causes: missing `gh skill`, Node below 18, or an unpinned skill.
