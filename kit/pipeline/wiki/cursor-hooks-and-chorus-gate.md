# Cursor hooks vs Chorus tool gate

- **Layer:** hooks
- **Load when:** hooks seem ignored, double deny with Chorus, or `hooks.json` edited from the IdentityIQ parent folder

## Symptom

Pipeline write/shell gates never fire, or every tool is denied with “Chorus tool gate environment is missing.”

## Root cause

1. Cursor **project** hooks load from the **workspace root**. This repo’s `.cursor/hooks.json` applies when the open project is **ai-agents-registry**, not when only the parent IdentityIQ repo is open.
2. Chorus daemon injects `CHORUS_TASK_ID` + `CHORUS_PORTAL`. Pipeline hooks **allow immediately** in that case so they do not fight engine HITL (`tool_gate_hook.py`).
3. `failClosed` is off: a crashed hook must not freeze the IDE.

## Do not

- Duplicate HITL policy in pipeline hooks while a daemon task is running.
- Use Cursor `type: prompt` hooks for portable policy (not Claude/Chorus).
- `failClosed: true` on these scripts unless you intend a hard freeze on hook bugs.

## Fix / convention

Command scripts under `.cursor/hooks/*.py`, JSON in/out. Claude: `PIPELINE_HOOK_FORMAT=claude`. Overrides: `PIPELINE_ALLOW_GIT|DEPS|NET|MCP=1`. MCP writes (Jira/GitHub create/comment/PR) are denied by `before-mcp.py` until that override.

## Files

`.cursor/hooks.json`, `.cursor/hooks/README.md`, `src/canvas_agent_daemon/tool_gate_hook.py`

## How to confirm

Open this folder as the Cursor project. A Write to `.env` is denied. With `CHORUS_TASK_ID` set, the same hook allows (engine decides).
