---
title: Cursor
description: Project hooks and skills load from the workspace root. Open the repo that contains .cursor.
---

Install: `pipeline-kit init --ide cursor` (or `setup --ide cursor` for the user skill).

Skill path: `.cursor/skills/run-workflow/SKILL.md`.

## Workspace root

Cursor **project** hooks and skills load from the **workspace root**. Open the repository that contains `.cursor/hooks.json` and `.pipeline/`. A multi-root window whose first folder is another repo will not fire these hooks.

`init --ide cursor` merges policy guardrails (shell, MCP, pack allowlist, specialist start gates) into `.cursor/hooks.json` without replacing existing entries. Agent-run observability still needs `obs install`. See [observability](/docs/capabilities/observability).

`--agent-stubs` creates thin `.cursor/agents/*.md` pointers. Without stubs, parent Tasks use `generalPurpose`.

## Hooks vs an external portal

If an external agent portal owns HITL, pipeline hooks should not duplicate deny/allow policy. `failClosed` is off by default so a crashed hook does not freeze the IDE. See [hooks troubleshooting](/docs/troubleshooting/hooks).
