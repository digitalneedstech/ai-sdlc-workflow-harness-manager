# IDE hooks vs an external tool gate

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist when INDEX triggers match |
| Adapt | Add a new page after retro. Do not store secrets or customer identifiers. |

- **Layer:** hooks
- **Load when:** hooks seem ignored, double deny with an external agent portal, or `hooks.json` is edited from the wrong workspace root

## Symptom

Pipeline write or shell gates never fire, or every tool is denied because an
external tool-gate environment is missing.

## Root cause

1. Cursor **project** hooks load from the **workspace root**. Open the
   repository that contains `.cursor/hooks.json`.
2. Some agent portals inject session environment variables. Pipeline hooks
   should **allow immediately** in that case so they do not fight the portal’s
   own human-in-the-loop gate.
3. `failClosed` is off by default: a crashed hook must not freeze the IDE.

## Do not

- Duplicate HITL policy in pipeline hooks while an external portal owns the
  session.
- Use Cursor `type: prompt` hooks for portable policy (they do not travel to
  other IDEs).
- Set `failClosed: true` unless you intend a hard freeze on hook bugs.

## Convention

Command scripts under `.cursor/hooks/*.py`, JSON in and out. Optional format
override: `PIPELINE_HOOK_FORMAT`. Capability overrides belong in environment
variables the hook README documents. The installer does **not** copy hooks;
a project that wants them copies the hook tree itself.

## Files

`.cursor/hooks.json`, `.cursor/hooks/` (project overlay; not part of the
shared pack)

## Verify

Open the repository that owns `hooks.json`. A write to a secret file is
denied. With the portal session variables set, the same hook allows and the
portal decides.
