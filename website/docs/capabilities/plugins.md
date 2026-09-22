---
title: Plugins
description: Optional Graphify and Archify (external plugins) plus bundled agent-run observability. Init does not turn them on.
---

`pipeline-kit init` does not turn these on. There are **two kinds** of optional add-on.

| Kind | What it is | Command |
|------|------------|---------|
| **External plugins** | Third-party tools the kit never vendors and never `import`s | `pipeline-kit plugins install graphify \| archify` |
| **Bundled add-on** | First-party collector, ledger, scores, and flush already in the pack | `pipeline-kit obs install` — **not** `plugins install` |

```bash
pipeline-kit plugins list
pipeline-kit plugins status
pipeline-kit obs status
```

## External plugins

| Plugin | What it does | Default |
|--------|----------------|---------|
| **[Graphify](/docs/capabilities/graphify)** | Official CLI writes `graphify-out/graph.json` for QA test design | Off until `knowledge init` / `plugins install graphify` |
| **[Archify](/docs/capabilities/archify)** | Pinned Agent Skill (`tt-a1i/archify` `v2.16.0`) for Architect HTML diagrams | Off until `plugins install archify`. Mermaid in `architecture.md` stays required |

`--scope project|user` on install/uninstall/status. Project-scope Cursor install is the usual choice.

Uninstall removes the **managed skill** (and Graphify’s own uninstall). It does not delete `features/{slug}/diagrams/` or, unless `--purge`, `graphify-out/`.

## Bundled add-on: agent-run observability

Traces and scores for **coding-agent** tool runs (hooks → local JSONL ledger → Langfuse). Distinct from product [`telemetry-agent`](/docs/capabilities/telemetry). Langfuse is the default **adapter**, not a plugin.

`init` copies `.pipeline/hooks/obs/` unused. `obs install` merges fail-open IDE hook entries and sets `agent_observability.enabled`. `features enable agent-observability` only flips the flag; it does not wire hooks.

```bash
pipeline-kit init --ide cursor
pipeline-kit obs install --ide cursor --adapter langfuse
# LANGFUSE_* in .env — never in config.json
pipeline-kit obs report
pipeline-kit obs flush
pipeline-kit obs uninstall   # hook entries only; ledger kept
```

Full handbook: [Agent-run observability](/docs/capabilities/observability).
