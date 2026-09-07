---
name: pipeline-retro
description: >-
  Invoke after feature-development devops SUCCESS. Retro-agent summarizes the
  run from disk artifacts (and an optional digest), writes RETRO.md, and
  persists reusable learnings to .pipeline/wiki (plus AGENTS.md index). Do not
  run if deploy failed. Do not invent product code.
---

# Pipeline retro (learnings)

Run **only** after `HANDOFF-devops.md` is `SUCCESS` and `deploy-result.env` has `OVERALL=passed`. Last specialist before parent declares **PIPELINE_COMPLETE**.

**Progressive load:** this file, then [assets/retro-template.md](assets/retro-template.md).

## Inputs (no parent chat)

A `Task` cannot see the parent conversation. Use:

1. `features/{slug}/` artifacts (route, spec/patch, HANDOFFs, critic reports, deploy-result)
2. Optional `CONVERSATION_DIGEST` from the parent (≤ 30 lines, no secrets)
3. Wiki INDEX — do not duplicate an existing page

## Where to put a learning

| Kind | Persist |
|------|---------|
| Recurring error, port, routing, telemetry pitfall | **Wiki page** + `INDEX.md` + wiki table in root `AGENTS.md` |
| Durable coding standard (naming, XSS, SQL) | Short `.pipeline/rules/*.mdc` (one concern) **and** mention it in RETRO |
| Workflow sequence was wrong | Note in RETRO; parent/human updates the skill — retro does not silently rewrite skills |
| One-off | `features/{slug}/RETRO.md` only |

Default is **wiki**, not a new always-on rule. Skip a wiki page if INDEX already covers it (link the existing page in RETRO).

## Do not

- Log tokens, bootstrap secrets, emails, or raw prompts.
- Mark PIPELINE failed because wiki write was skipped (`NO_NEW_PAGE` is SUCCESS).
- Spawn other agents or edit product source.
