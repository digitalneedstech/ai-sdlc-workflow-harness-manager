---
title: What is Pipeline Kit
description: A portable workflow pack and installer for coding agents. Process lives in .pipeline. The IDE is a thin adapter.
---

Pipeline Kit is a **portable workflow pack** plus a Python installer for coding agents. Clone the kit, then install `.pipeline` into any customer project — or into `~/.pipeline` on a laptop.

Process lives in the pack. The IDE is a thin adapter: it discovers **only** `run-workflow`. The pack is not tied to a product, a language, or an editor.

:::info Handbook vs this site
This documentation site is the guided product manual. After `pipeline-kit init`, the same adaptation contract is copied to `.pipeline/docs/CUSTOMER-GUIDE.md` in the target repo. Keep that file as the in-repo handbook; use these pages to learn the product.
:::

## What you take where

| You ship | You change per engagement |
|----------|---------------------------|
| The **kit** (installer + bundled pack) | `AGENTS.md`, `.pipeline/config.json`, local-deploy and test runbooks |

## What lands after install

| Path | Role |
|------|------|
| `.pipeline/` | Workflows, skills, agent briefs, rules, wiki, loader |
| `.pipeline/config.json` | This engagement: chains, tracker, verify, deploy |
| `.pipeline/docs/CUSTOMER-GUIDE.md` | Copied handbook |
| `.pipeline/docs/OBSERVABILITY.md` | Agent-run observability handbook |
| `.cursor/skills/run-workflow/` (or `.claude` / `.github`) | The only IDE-discovered skill |

Specialist briefs and skill bodies stay under `.pipeline/` so the IDE does not auto-load them. The parent reads only the allowlist from the loader.

## Shipped workflows

| Name | When it runs |
|------|----------------|
| `ask` | Question about this repo (how / what / why / explain). No Task chain. |
| `feature-development` | Product work from chat (“add”, “fix”, “change”, “implement”). |
| `jira-story` / `jira-epic` / `jira-bug` | Tracker issue key, if Jira intake is enabled. |
| `test-knowledge-bootstrap` | One-time QA overlay bootstrap. Not the feature ladder. |

Opt-in extras — knowledge, plugins, agent-run observability — are documented under [Capabilities](/docs/capabilities/overview). `pipeline-kit init` does not turn them on.

The source repo is grouped as **modes** (`kit/`, `orchestrator/`), **extensions**, and **capabilities**. See [Repository layout](/docs/intro/repo-layout).

## Requirements

Python **3.11+**. The CLI has no other runtime dependencies. Optional plugins (Graphify, Archify) and bundled observability (Langfuse keys) are separate.

## Next

1. [Problems it solves](/docs/intro/problems)
2. [How it works](/docs/intro/how-it-works)
3. [Install the CLI](/docs/getting-started/install-cli)
