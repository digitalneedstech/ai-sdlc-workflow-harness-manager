---
title: Problems it solves
description: Six operating-model failures that Pipeline Kit is built to remove.
---

Teams already use coding agents. What they lack is a **repeatable operating model** for those agents.

## 1. Context explosion

If every skill, agent brief, rule, and wiki page lives under `.cursor/` (or `.claude/`), the IDE auto-discovers them. Every turn loads far more than the current step needs. Cost and quality both degrade as the pack grows.

**Kit answer:** process files sit in `.pipeline/`. The IDE folder holds only `run-workflow`. The [loader](/docs/capabilities/loader) writes `allowed_reads` for the current specialist.

## 2. Pipeline glued to one IDE

Process (how you plan, specify, implement, test, deploy) was mixed with editor wiring. Moving from Cursor to Claude Code, or to a repo with no AI folder, meant copying and rewriting the whole tree.

**Kit answer:** thin [adapters](/docs/getting-started/ide-adapters). Cursor, Claude Code, GitHub, and `--ide none` get the same pack. Only the adapter path changes.

## 3. One customer’s process baked into another’s repo

Folder names, ports, tracker projects, verify commands, and deploy targets leaked into skills. The next customer on a different stack could not reuse the pack without a surgical rewrite.

**Kit answer:** engagement overlay in [`config.json`](/docs/guides/config). Skills stay free of customer folder names and site URLs.

## 4. No productized install

“Copy `.cursor` from last year’s repo” does not scale. Architects need project install, user install, and a path to org-wide defaults — with a clear override order.

**Kit answer:** `pipeline-kit init` (project), `pipeline-kit setup` (user). Project pack wins at runtime. See [Where you can install](/docs/getting-started/install-scopes).

## 5. Every ask became the same ladder

A “how does tax work?” question should not start PM → BA → developer. A bug should not run a full feature plan. Without a **workflow** as a first-class object, the parent invents a new procedure each time.

**Kit answer:** named workflows (`ask`, `feature-development`, `jira-bug`, …) with a chain and a file allowlist.

## 6. Hard to add a process

A new customer wants “architecture review” or “release checklist.” That should be a new workflow JSON + skill + a config chain — not a new platform.

**Kit answer:** [add a workflow](/docs/guides/add-workflow). Different customers can enable different workflows from the same pack.

## Scaling contract

What you take to the next customer: the **kit**. What you change per customer: `AGENTS.md`, `config.json`, deploy/test runbooks.
