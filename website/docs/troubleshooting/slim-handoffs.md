---
title: Slim handoffs
description: The machine contract is JSON on disk. HANDOFF is for humans.
---

## Symptom

The next specialist Task is huge: the parent pasted the previous HANDOFF, PRD, and architecture into the prompt. Or a specialist cannot find what the previous step produced.

## Cause

Handoffs are for humans (HITL). The machine contract is:

- `features/{slug}/pipeline-state.json` — which step is current / completed
- `features/{slug}/state/{agent}.json` — inputs, outputs, short context, `next_must_read`

The parent passes only those two paths plus a short job.

## Do not

- Paste a prior HANDOFF body into the next Task
- Ask the parent to recap the PRD in chat
- Skip writing agent state on BLOCKED
- List the whole repository in `next_must_read`

Child wave state lives under `features/{slug}/{child}/state/`.
