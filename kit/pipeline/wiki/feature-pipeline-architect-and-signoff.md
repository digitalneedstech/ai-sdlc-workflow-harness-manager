# Feature pipeline — Architect and planning sign-off

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist when INDEX triggers match |
| Adapt | Add a new page after retro. Do not store secrets or customer identifiers. |

- **Layer:** pipeline
- **Load when:** architect-agent, architecture.md, implementation-plan.md, skip_architect, RUN_ARCHITECT, signoff-requirements.md, signoff-architect.md, signoff-ba.md, @signoff, decisions.md, clarify-first

## Symptom

Developers start from an unsigned PRD, Architect is skipped on a new API,
or PM/BA silently default Must decisions instead of asking.

## Root cause

Feature-class delivery now has three planning gates the user signs in order:
requirements (PRD or Jira intake), architecture (when the story is large),
then BA specs. Planning agents mine prior artifacts first, then ask remaining
checklist items. `gates.require_planning_signoff_before_build` keeps telemetry
and developers from starting early.

## Do not

- Auto-continue after PM, Architect, or BA SUCCESS
- Spawn Architect before `signoff-requirements.md`
- Spawn BA before requirements sign-off, or before architect sign-off when Architect ran
- Start waves / developer before `signoff-ba.md` on feature class
- Run Architect on micro, minor, or jira-bug
- Re-ask a decision already in `decisions.md`
- Invent product or technical defaults when the checklist is still Unknown

## Convention

1. PM or intake writes the requirements artifact. Parent stops for `@signoff:requirements`.
2. Parent applies `architect-policy.md` (or `RUN_ARCHITECT`). Large stories run Architect.
3. Architect reads prior state + requirements, challenges, records or raises concerns, then writes mermaid architecture + implementation plan + state/architect-agent.json.
4. Parent stops for `@signoff:architect` and presents recorded concerns (skipped when `skip_architect`).
5. BA reads architecture when present, asks leftover BA items, writes child specs.
6. BA critic runs, then parent stops for `@signoff:ba`.
7. Only then waves (telemetry → developer → critic).

Hook contract for customer repos that ship `subagent-start.py`: parse
`skip_architect`; require `signoff-requirements.md` before Architect; require
`signoff-architect.md` (unless skip) before BA; require `signoff-ba.md` before
feature-class developer. The kit does not ship those hooks.

## Files

`.pipeline/agents/architect-agent.md`, `.pipeline/skills/architecture-design/SKILL.md`, `.pipeline/skills/feature-development/assets/architect-policy.md`, `clarify-first.md`, `planning-signoff-template.md`, `.pipeline/config.json`

## Verify

`features/{slug}/signoff-ba.md` exists with `SIGNOFF: approved` before the first telemetry or developer Task on feature class. Large stories also have `architecture.md` and `signoff-architect.md`.
