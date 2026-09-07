# Interrupted pipeline Task, no HANDOFF

- **Slug / date:** login-button-label, 2026-09-04
- **Layer:** pipeline
- **Load when:** user-interrupted specialist Task; missing `HANDOFF-*.md`; tester/Playwright/`ensure-e2e-toolchain` “starting”; parent told the user the agent is not running

## Symptom

A tester (or other specialist) Task is interrupted. There is no HANDOFF on disk. The user asks whether it is still running. The parent answers “no” because HANDOFF is absent, then either skips the step or starts a duplicate Task while the first is still alive.

## Root cause

Specialists write HANDOFF **at the end**. Interrupt during toolchain install or Playwright start leaves `features/{slug}/` looking idle. Missing HANDOFF is not proof the Task never started or already stopped.

## Do not

- Treat missing `HANDOFF-tester.md` (or any specialist HANDOFF) as “that agent is not running.”
- Skip tester and go to devops when `route.md` has `skip_tester: false`.
- Spawn a second tester Task without confirming the first is gone (user interrupt / UI stop).
- Invent a HANDOFF for an interrupted run.

## Fix / convention

1. If the user interrupts a specialist: confirm the Task is stopped in the UI, then spawn a **new** Task of the same type with a full prompt.
2. Until HANDOFF exists, the step is incomplete. Ask the user whether to restart; do not infer idle from disk alone.
3. After a successful restart, only the completed HANDOFF counts (`STATUS: SUCCESS`, and for tester `FEATURE_SIGNOFF: passed`).

## Files

`features/{slug}/HANDOFF-tester.md`, `.pipeline/skills/feature-development/assets/tester-policy.md`, `.cursor/skills/testing-ui-playwright/`

## How to confirm

Interrupted run has no HANDOFF. Restarted tester writes `HANDOFF-tester.md` with `FEATURE_SIGNOFF: passed` before devops.
