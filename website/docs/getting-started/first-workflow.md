---
title: Your first workflow
description: Smoke-test ask, then a small feature-development change.
---

With the project pack installed and `AGENTS.md` routing to `run-workflow`, smoke-test two intents.

## 1. Ask (no Task chain)

In the IDE, with the repo root open:

> How does local deploy work in this repository?

Expect workflow **`ask`**. The parent runs the loader, reads the allowlist, and answers from the repo. It must **not** start PM → BA → developer.

Details: [Ask workflow](/docs/workflows/ask).

## 2. A small product change

> Add a small label change on the homepage.

Expect **`feature-development`**. The parent classifies **micro / minor / feature** before any specialist Task. A label tweak is usually **micro**: developer → tester (if policy) → devops → retro.

If the parent starts a full PRD for a label, stop and read [change classes](/docs/capabilities/workflows).

Details: [Feature development](/docs/workflows/feature-development).

## 3. Tracker key (only if Jira is on)

If `intake.jira.enabled` is true and MCP is connected:

> Work on ABC-123

Expect intake first, then `jira-story`, `jira-epic`, or `jira-bug` from the issue type. Do not paste the ticket body into chat to “save a step.”

## If nothing happens

1. Confirm the `run-workflow` skill is visible in the IDE.
2. Confirm you opened the repo that contains `.pipeline/` and the adapter folder.
3. Run `pipeline-kit doctor --ide cursor`.
4. Off-repo trivia (weather, news) must **skip** the loader — that is correct.
