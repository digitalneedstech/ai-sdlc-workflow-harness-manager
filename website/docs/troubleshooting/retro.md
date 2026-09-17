---
title: Retro after devops
description: The pipeline completes at retro-agent. NO_NEW_PAGE is still success.
---

## Symptom

Deploy is green (`OVERALL=passed`) and the parent stops, or retro invents learnings from chat it cannot see.

## Cause

Specialists run in a **new Task**. Retro has no parent conversation — only `features/{slug}/` plus an optional `CONVERSATION_DIGEST`. Completing at devops drops that learning step.

## Do not

- Treat tester or devops SUCCESS as the last pipeline step
- Fail the user’s local URL because no new wiki page was needed
- Dump secrets, bootstrap tokens, or raw prompts into wiki / RETRO / digest
- Silently rewrite a skill from retro. Note the bug in RETRO; a human updates the skill
- Add an always-on rule for a one-off error; use a **wiki page**

Every class ends `… → devops → retro`. Parent injects `CONVERSATION_DIGEST` (≤ 30 lines, no secrets) when the run had a non-obvious miss.
