---
title: Capabilities overview
description: What the kit ships, what is opt-in, and where to drill down.
---

Core delivery is on after `pipeline-kit init`. Everything in the second table is **opt-in**.

## Always available after init

| Capability | What it is |
|------------|------------|
| [Workflows](/docs/capabilities/workflows) | Named procedures with chains and allowlists |
| [Planning gates](/docs/capabilities/planning-gates) | Human sign-off on requirements, architecture, BA |
| [Loader](/docs/capabilities/loader) | Per-step `allowed_reads` |
| [Wiki](/docs/capabilities/wiki) | Trigger-routed agent memory |
| [Feature flags](/docs/capabilities/feature-flags) | Named on/off keys that mirror `config.json` |

## Opt-in

| Capability | How you turn it on |
|------------|--------------------|
| [Knowledge base](/docs/capabilities/knowledge) | `pipeline-kit knowledge init` |
| [Plugins](/docs/capabilities/plugins) | `pipeline-kit plugins install graphify \| archify` |
| [Graphify](/docs/capabilities/graphify) | Official CLI + skill registration |
| [Archify](/docs/capabilities/archify) | Pinned Agent Skill `v2.16.0` |
| [Agent-run observability](/docs/capabilities/observability) | `pipeline-kit obs install` |
| [App telemetry](/docs/capabilities/telemetry) | `features enable telemetry` or `RUN_TELEMETRY` |

:::warning Two different “observability” words
**Agent-run observability** traces what the *coding agent* did (tools, steps, scores). **App telemetry** is a pipeline specialist that extracts *product* analytics events from a spec. Do not mix them.
:::

## Workflow names

`ask`, `feature-development`, `jira-story`, `jira-epic`, `jira-bug`, `test-knowledge-bootstrap`.

Deep dives: [Ask](/docs/workflows/ask), [Feature development](/docs/workflows/feature-development), [Jira](/docs/workflows/jira), [Knowledge bootstrap](/docs/workflows/knowledge-bootstrap).
