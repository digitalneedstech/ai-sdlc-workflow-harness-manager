# Pipeline retro after devops

- **Slug / date:** pipeline-retro, 2026-08-27
- **Layer:** pipeline
- **Load when:** tempted to declare PIPELINE_COMPLETE after local health, skip retro, or expect the retro Task to “remember” the parent chat

## Symptom

Deploy is green (`OVERALL=passed`) and the parent stops, or retro invents learnings from chat it cannot see.

## Root cause

Specialists run in a **new `Task`**. Retro has no parent conversation — only `features/{slug}/` plus an optional `CONVERSATION_DIGEST`. Completing at devops drops that learning step.

## Do not

- Treat tester or devops SUCCESS as the last pipeline step.
- Fail the user’s local URL because no new wiki page was needed (`NO_NEW_PAGE` still completes).
- Dump secrets, bootstrap tokens, or raw prompts into wiki / RETRO / digest.
- Silently rewrite a skill from retro. Note the workflow bug in RETRO; a human updates the skill.
- Add an always-on `.pipeline/rules/*.mdc` for a one-off port or error; use a **wiki page**.

## Fix / convention

Every class ends `… → devops → retro`. Parent injects `CONVERSATION_DIGEST` (≤ 30 lines, no secrets) when the run had a non-obvious miss.

Persist reusable lessons: `.pipeline/wiki/{slug}.md` + `INDEX.md` + the wiki table in root `AGENTS.md`. Default is wiki, not a new rule.

## Files

`.pipeline/agents/retro-agent.md`, `.pipeline/skills/pipeline-retro/SKILL.md`, `features/{slug}/RETRO.md`, `HANDOFF-retro.md`

## How to confirm

`HANDOFF-retro.md` is `SUCCESS` or `NO_NEW_PAGE`. Parent then **PIPELINE_COMPLETE**. Local URLs from devops remain valid either way.
