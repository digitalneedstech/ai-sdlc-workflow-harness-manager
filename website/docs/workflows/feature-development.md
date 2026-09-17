---
title: Feature development
description: Chat-driven product work. Classify micro, minor, or feature before any specialist.
---

`feature-development` is the workflow for product work from chat (“add”, “fix”, “change”, “implement”). Source is **text**. Plan artifact for feature class is `prd.md`.

## Classify first

The parent writes `features/{slug}/route.md` **before** any specialist. See [change classes](/docs/capabilities/workflows).

| Class | Default chain (from `config.json`) |
|-------|-------------------------------------|
| micro | developer → tester → devops → retro |
| minor | developer → developer-critic → tester → devops → retro |
| feature | PM → `@signoff:requirements` → architect → `@signoff:architect` → BA → BA critic → `@signoff:ba` → `@waves` → tester → devops → retro |

Feature class includes planning gates. `skip_telemetry` defaults **true**. Override a single run with `RUN_TELEMETRY`, `RUN_TESTER`, `RUN_ARCHITECT`.

## Feature-class shape

Parent folder `features/{slug}/` with nested children. PM analyzes the repo as-is, writes `prd.md`, `research.md`, `decisions.md`. After requirements sign-off, Architect may run. BA splits children. Waves implement. **One** tester. Devops after `FEATURE_SIGNOFF: passed`. Retro last.

Micro/minor stay a flat folder: no PM, no Architect, tester only if policy says so.

## Isolation

Analysis agents (`product.readonly_agents`) write only under `features/`. Developers edit product source. Do not implement in the parent chat.

Details: [planning gates](/docs/capabilities/planning-gates), [test layers](/docs/troubleshooting/test-layers).
