---
title: Interrupted Task
description: Missing HANDOFF does not prove the specialist stopped. Confirm in the UI before restarting.
---

## Symptom

A tester (or other specialist) Task is interrupted. There is no HANDOFF on disk. The parent answers “not running” and either skips the step or starts a duplicate Task.

## Cause

Specialists write HANDOFF **at the end**. Interrupt during toolchain install leaves `features/{slug}/` looking idle. Missing HANDOFF is not proof the Task never started or already stopped.

## Do not

- Treat missing `HANDOFF-*.md` as “that agent is not running”
- Skip tester when `route.md` has `skip_tester: false`
- Spawn a second Task without confirming the first is gone
- Invent a HANDOFF for an interrupted run

## Convention

1. Confirm the Task is stopped in the UI, then spawn a **new** Task of the same type with a full prompt.
2. Until HANDOFF exists, the step is incomplete. Ask the user whether to restart.
3. After a successful restart, only the completed HANDOFF counts (`STATUS: SUCCESS`, and for tester `FEATURE_SIGNOFF: passed`).
