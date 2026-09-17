---
title: Git ignore
description: Recommended ignore entries for run artifacts, optional graph output, and state.
---

Add:

```gitignore
features/
.pipeline/state/
```

`features/` holds plans, specs, HANDOFFs, and deploy logs for one run. Most teams do not commit those. Commit `features/` only if you want specs in git.

`.pipeline/state/active-context.json` is the live allowlist.

## Optional

| Path | Typical policy |
|------|----------------|
| `graphify-out/` | Commit if the team wants a shared structural graph; ignore if each checkout re-runs `knowledge extract` |
| `test-knowledge/` | Usually commit after a bootstrap promote |
| `.agents/skills/archify/` | Often commit the pinned skill |
| `features/{slug}/diagrams/` | Same as other `features/` artifacts. Uninstalling Archify never deletes them |
