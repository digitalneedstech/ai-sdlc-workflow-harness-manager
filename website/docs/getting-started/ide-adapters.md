---
title: IDE adapters
description: Cursor, Claude Code, GitHub, or none. Same pack, different skill path.
---

`--ide` selects a **thin adapter**. The pack does not change.

| Team uses | Install flag | Skill path to name in `AGENTS.md` |
|-----------|----------------|-----------------------------------|
| Cursor | `--ide cursor` | `.cursor/skills/run-workflow/SKILL.md` |
| Claude Code | `--ide claude-code` | `.claude/skills/run-workflow/SKILL.md` |
| GitHub (Copilot / agents) | `--ide github` | `.github/skills/run-workflow/SKILL.md` |
| CLI / no IDE | `--ide none` | Run `load_workflow.py` from the shell |

Open the **repository root** in the IDE so the skill folder is discovered. A multi-root window whose first folder is a different repo will not load that project’s hooks or skills.

Add `--agent-stubs` to create thin `.cursor/agents/*.md` files. Named Cursor Task types (`developer-agent`, …) exist only with stubs. Otherwise the parent uses `generalPurpose` and `Follow .pipeline/agents/{name}.md`.

`--user --ide cursor` writes `~/.cursor/skills/run-workflow` so every repo on that laptop can see the skill even without a project pack.

Policy hooks are optional and not auto-copied. Agent-run observability hooks are opt-in (`pipeline-kit obs install`) and **merge** into an existing `hooks.json` without replacing it.

Per-IDE notes: [Cursor](/docs/adapters/cursor), [Claude Code](/docs/adapters/claude-code), [GitHub](/docs/adapters/github), [none](/docs/adapters/none).
