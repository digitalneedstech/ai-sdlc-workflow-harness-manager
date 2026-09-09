# Pipeline state and slim handoffs

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist when INDEX triggers match |
| Adapt | Add a new page after retro. Do not store secrets or customer identifiers. |

- **Layer:** pipeline
- **Load when:** pipeline-state.json, state/*.json, fat HANDOFF pasted into the next Task, missing prior files

## Symptom

The next specialist Task is huge: the parent pasted the previous HANDOFF,
PRD, and architecture into the prompt. Or a specialist cannot find what
the previous step produced.

## Root cause

Handoffs are for humans (HITL). The machine contract is JSON on disk:

- `features/{slug}/pipeline-state.json` — which step is current / completed
- `features/{slug}/state/{agent}.json` — inputs, outputs, short context,
  `next_must_read`

The parent passes only those two paths plus a short job.

## Do not

- Paste a prior HANDOFF body into the next Task
- Ask the parent to recap the PRD in chat
- Skip writing agent state on BLOCKED
- List the whole repository in `next_must_read`

## Convention

1. Parent creates `pipeline-state.json` when the slug folder is created.
2. Each specialist reads prior state, opens listed files, writes its own
   state, updates the pipeline file.
3. Parent updates `current_step` after HANDOFF and after each `@signoff:*`.
4. Child wave state lives under `features/{slug}/{child}/state/`.

## Files

`.pipeline/skills/feature-development/assets/pipeline-state.md`,
`pipeline-state-template.json`, `agent-state-template.json`,
`parent-task-prompt.md`

## Verify

`features/{slug}/pipeline-state.json` exists before the first specialist.
After PM, `state/product-manager-agent.json` lists `prd.md` in `outputs`.
The Architect prompt contains `PRIOR_STATE_PATH` and does not contain the
PM HANDOFF body.
