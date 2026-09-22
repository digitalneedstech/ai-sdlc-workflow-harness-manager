---
title: Agent-run observability
description: Coding-agent traces and deterministic scores. Local JSONL ledger, then Langfuse. Not product analytics.
---

Portable **agent-run** tracing for Cursor, Claude Code, and GitHub Copilot hooks. It records what the **agent** did: tools, pipeline steps, tokens when the IDE sends them, and Langfuse traces when you flush.

This is a **bundled add-on** (first-party kit code), listed with other opt-in extras on [Plugins](/docs/capabilities/plugins). It is **not** `pipeline-kit plugins install`. Langfuse is the default adapter.

This is **not** customer-application telemetry ([`telemetry-agent`](/docs/capabilities/telemetry)).

Secrets stay in the environment (`LANGFUSE_*`). Never commit API keys.

## What you get

| Piece | Location | Role |
|-------|----------|------|
| Collector | `.pipeline/hooks/obs/obs_collect.py` | Append-only JSONL; fail-open; no network |
| Ledger | `.pipeline/state/obs/events.jsonl` | Raw hook events |
| Offset | `.pipeline/state/obs/offset.json` | Flush commits only after a successful ship |
| IDE hooks | `.cursor/hooks.json` (etc.) | **Appended** entries; existing hooks stay |
| Config | `config.json` → `agent_observability` | Enable, adapter, dataset, redaction |
| CLI | `pipeline-kit obs …` | Install, report, flush, status |

Adapters today: **Langfuse** (OTLP + scores + datasets over HTTP, no SDK). Datadog and generic OTLP stubs exist for future work.

## Install

Observability is opt-in. You still need a `.pipeline/` pack from `init` (you do not have to run feature-development).

```bash
cd /path/to/your-project
pipeline-kit init --ide cursor
pipeline-kit obs install --ide cursor --adapter langfuse
```

Set keys in the project `.env` or your shell (**not** in `config.json`):

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Open **that project folder** as the only workspace root. Hooks in another checkout do not run if the window’s first root is a different repo.

```bash
pipeline-kit obs status
pipeline-kit obs report    # local scores; no network
pipeline-kit obs flush     # ship new ledger rows
pipeline-kit obs uninstall # remove obs hook entries; ledger kept
```

`--ide` can be `cursor`, `claude-code`, or `github`.

You can enable traces without ever running BA/developer Tasks. You cannot install obs **without** `init` (obs needs `.pipeline/hooks/obs/` and `config.json`).

## End-to-end flow

1. IDE fires hooks → `obs_collect.py` appends one JSON line per event.
2. `subagentStart` may attach `step_context` (workflow, step, slug, allowlist).
3. On `afterAgentResponse`, `stop`, `subagentStop`, or `sessionEnd`, a background flush may run.
4. Flush: normalize → score per step → OTLP spans → POST Langfuse → POST scores → optional dataset upsert → advance offset.

Hooks **never** send dollar cost. Langfuse may infer cost from model + usage if you define prices in the Langfuse project.

## Langfuse identity

| Langfuse | Source | Notes |
|----------|--------|--------|
| Trace id | Cursor `conversation_id` | Dashes stripped (32 hex) |
| Session id | Same UUID | Dashed |
| Generation | `generation_id` | Skipped when it equals `conversation_id` |
| User | `user_email` | `langfuse.user.id` |
| Feature slug | Loader `step_context` | Metadata only, not session id |

One user chat is one `conversation_id`. Each Cursor Task spawn gets its **own** id. You may see multiple Langfuse sessions for one pipeline run. Child Task traces often show **0** tokens until the IDE sends usage there.

## Scores (deterministic, no LLM judge)

Scores describe **tool discipline**, not LLM quality. They are computed per pipeline step.

| Score | Ideal | Worry when |
|-------|-------|------------|
| `waste_ratio` | **0** | **> 0.2** |
| `wrong_tool_count` | **0** | any **> 0** |
| `out_of_contract_count` | **0** | any high-confidence miss |
| `retry_ratio` | **0** | **> 0.1** |
| `denied_count` | **0** | any **> 0** |
| `verify_coverage` | **1** | **< 1** after SUCCESS claimed |
| `integrity_pass` | **1** | **0** |
| `read_amplification` / `search_thrash` / `edit_churn` | **≈ 1.0** | **≥ 2** |
| `discovery_ratio` | **~0.2–0.6** on implement steps | **1** = no edit; **0** = edited with no prior tools |

Plain Cursor chat without loader context: waste, wrong-tool, and retries still apply. Allowlist, verify, and integrity need pipeline `step_context` and `verify.rules`.

Full score table: kit repo `OBSERVABILITY.md` (copied to `.pipeline/docs/OBSERVABILITY.md` on init).

## Configuration

In `.pipeline/config.json` → `agent_observability` (enabled by `obs install`):

| Key | Default | Purpose |
|-----|---------|---------|
| `enabled` | `false` until install | Master switch |
| `adapter` | `langfuse` | Ship target |
| `redact` | path globs | Substrings stripped from ledger fields |
| `max_field_chars` | `8000` | Truncate large tool I/O |
| `dataset` | `pipeline-kit-agent-runs` | Langfuse dataset on flush |
| `retention_days` | `14` | Ledger hygiene intent |

Optional `verify.rules` improve `verify_coverage` / `integrity_pass`.

If flush fails or the ledger is empty, see [observability troubleshooting](/docs/troubleshooting/observability).
