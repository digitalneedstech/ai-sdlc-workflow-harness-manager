---
title: IDE hooks
description: Hooks load from workspace root. Do not fight an external HITL portal. failClosed is off.
---

## Symptom

Pipeline write or shell gates never fire, or every tool is denied because an external tool-gate environment is missing.

## Cause

1. Cursor **project** hooks load from the **workspace root**.
2. Some agent portals inject session environment variables. Pipeline hooks should **allow immediately** in that case so they do not fight the portal’s HITL gate.
3. `failClosed` is off by default: a crashed hook must not freeze the IDE.

## Do not

- Duplicate HITL policy in pipeline hooks while an external portal owns the session
- Use Cursor `type: prompt` hooks for portable policy (they do not travel to other IDEs)
- Set `failClosed: true` unless you intend a hard freeze on hook bugs

The installer does **not** copy policy hooks. Observability hooks are opt-in via `obs install` and merge without replacing existing entries.
