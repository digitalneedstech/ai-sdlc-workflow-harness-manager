---
title: Your first workflow
description: Smoke-test ask, then a small feature-development change.
---

These steps assume **kit mode** (the default) — the project pack is installed and `AGENTS.md` routes to `run-workflow`. If you initialized with `--mode orchestrator`, skip to [Orchestrator smoke test](#orchestrator-smoke-test).

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

## Orchestrator smoke test

You initialized with `--mode orchestrator`. Do not wait for `run-workflow` to pick a chain.

```bash
pipeline-kit run --slug label-tweak --workflow feature-development --runner fake \
  --request "Add a small label change on the homepage"
pipeline-kit status --slug label-tweak
```

`--runner fake` writes state under `features/label-tweak/` without calling the Cursor SDK. A live run needs `CURSOR_API_KEY` and `--request` (or `--request-file`). Chat text is not inherited.

Details: [Two kits](/docs/capabilities/modes), [CLI — orchestrator](/docs/reference/cli#orchestrator-mode).
