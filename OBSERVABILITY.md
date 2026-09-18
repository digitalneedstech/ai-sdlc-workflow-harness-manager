# Agent-run observability

Portable **agent-run** tracing and deterministic scores for coding agents (Cursor,
Claude Code, GitHub Copilot hooks). This is **not** customer-application telemetry
(`pipeline-kit features enable telemetry` / `telemetry-agent`). It records what
the **agent** did: tools, pipeline steps, tokens when Cursor sends them, and
Langfuse traces when you flush.

Secrets stay in the environment (`LANGFUSE_*`). Never commit API keys.

---

## What you get

| Piece | Location | Role |
|-------|----------|------|
| Collector | `.pipeline/hooks/obs/obs_collect.py` | Append-only JSONL ledger; fail-open; no network |
| Ledger | `.pipeline/state/obs/events.jsonl` | Raw hook events |
| Offset | `.pipeline/state/obs/offset.json` | Flush commits only after a successful ship |
| IDE hooks | `.cursor/hooks.json` (etc.) | **Appended** entries; existing hooks stay |
| Config | `.pipeline/config.json` → `agent_observability` | Enable, adapter, dataset name, redaction |
| CLI | `pipeline-kit obs …` | Install, report, flush, status |

Adapters today: **Langfuse** (OTLP + scores + datasets over HTTP, no SDK).
Datadog and generic OTLP stubs exist for future work.

---

## Install (any project)

Observability is **opt-in**. It is a subcommand of the same `pipeline-kit` CLI,
not a separate product. You still need a `.pipeline/` pack from `init` (you do
not have to run feature-development workflows).

```bash
uv tool install git+<this-repo-url>   # or editable clone

cd /path/to/your/project
pipeline-kit init --ide cursor
pipeline-kit obs install --ide cursor --adapter langfuse
```

Set keys in the project `.env` or your shell (not in `config.json`):

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your region
```

**Cursor:** open **that project folder** as the only workspace root. Hooks in
`test/.cursor/hooks.json` do not run if the window’s first root is another repo.

```bash
pipeline-kit obs status    # enabled, adapter, ledger size, langfuse_keys
pipeline-kit obs report    # local scores; no network
pipeline-kit obs flush     # ship new ledger rows to Langfuse
pipeline-kit obs uninstall # remove obs hook entries only; ledger kept
```

`--ide` can be `cursor`, `claude-code`, or `github`.

### Without the rest of the pipeline?

You can enable traces and scores **without** ever running BA/developer/devops
Tasks. You cannot install obs **without** `pipeline-kit init` (obs needs
`.pipeline/hooks/obs/` and `config.json`). The copied workflows and skills can
stay unused.

---

## End-to-end flow

1. IDE fires hooks → `obs_collect.py` appends one JSON line per event.
2. `subagentStart` may attach `step_context` (workflow, step, slug, allowlist).
3. On `afterAgentResponse`, `stop`, `subagentStop`, or `sessionEnd`, a background
   flush may run (`obs_flush.py` → `pipeline-kit obs flush`).
4. Flush: normalize ledger → score per step → build OTLP spans → POST Langfuse →
   POST scores → optional dataset upsert → advance offset.

Hooks **never** send dollar cost. On flush, generation spans get USD
`cost_details` from the resolved model + exclusive/cached token buckets
(kit list prices, overridable via `agent_observability.model_prices`).
Unknown or placeholder models (`auto-smart`) omit cost so Langfuse can
still infer from its own catalog.

---

## Langfuse identity

| Langfuse concept | Source | Notes |
|------------------|--------|--------|
| Trace id | Cursor `conversation_id` | Dashes stripped (32 hex) |
| Session id | Same UUID | Dashed (`langfuse.session.id`) |
| Generation | `generation_id` | Type `generation`; skipped when `generation_id` equals `conversation_id` (Task quirk) |
| User | `user_email` | `langfuse.user.id` on spans |
| Feature slug | Loader `step_context` | Metadata only, not session id |

**Parent vs Task:** one user chat is one `conversation_id`. Each Cursor Task
spawn gets its **own** `conversation_id` for tool hooks. You may see multiple
Langfuse sessions/traces for one pipeline run until parent-session grouping is
implemented. Subagent start/stop on the parent still carry `subagent_id` and
task text.

**Model in UI:** Cursor Auto often reports `auto-smart` in hooks; the **served**
model (e.g. `grok-4.6`) usually appears only on `afterAgentResponse` / `stop`.
The exporter uses the **last non-placeholder** `model_id` on the generation span.

**Usage header:** Langfuse reads `langfuse.observation.usage_details` (JSON:
exclusive `input`, `output`, `input_cached_tokens`, `input_cache_creation`)
and `langfuse.observation.cost_details` (USD for those buckets plus `total`).
OTLP also sets `gen_ai.usage.input_cost` / `output_cost` / `cost`. Tokens come
from parent `afterAgentResponse` / `stop` only; child Task traces often show
**0** until Cursor adds tokens there. **TTFT** is not in hooks;
`time_to_first_tool_ms` on the generation is a proxy only.

**Observation tree:** `agent` (chat) → `generation` (turn) → `tool` /
`retriever`; nested `agent` per pipeline step; `event` for session/prompt/stop.

Input: `beforeSubmitPrompt`, else transcript on flush. Output: `afterAgentResponse.text`,
else `stop.status` (including `aborted`).

---

## Scores (deterministic, no LLM judge)

Scores are computed per **pipeline step** (`developer-agent`, `devops-agent`,
`unattributed`, …) and posted to Langfuse on flush. They describe **tool
discipline**, not LLM quality.

### Score reference

| Score | Type | Meaning |
|-------|------|---------|
| `tool_calls_total` | count | Tool events in the step |
| `tool_calls_legitimate` | count | Total minus wasted and high-confidence out-of-contract |
| `waste_ratio` | 0–1 | Repeat read/search/shell, or **empty Grep** |
| `wrong_tool_count` | count | Shell used as `cat`/`head`/`find`/`grep` instead of Read/Grep |
| `out_of_contract_count` | count | High-confidence read/edit outside allowlist or readonly rules |
| `read_amplification` | ratio | Reads ÷ distinct files (re-reads raise it) |
| `search_thrash` | ratio | Searches ÷ distinct patterns |
| `edit_churn` | ratio | Edits ÷ distinct files |
| `discovery_ratio` | 0–1 | Tools before first edit ÷ all tools (explore vs implement) |
| `retry_ratio` | 0–1 | Failed tools ÷ total |
| `denied_count` | count | `permission_denied` failures |
| `allowlist_unused_count` | count | Allowlisted paths never Read |
| `verify_coverage` | 0–1 | Share of `verify.rules` satisfied by shell commands |
| `integrity_pass` | 0 or 1 | HANDOFF claimed SUCCESS but verify/tester/devops checks failed |
| `context_peak_percent` | 0–100 | Max `preCompact` context % if Cursor sent it |

Plain Cursor chat without loader context: waste, wrong-tool, and retries still
apply. Allowlist, verify, and integrity need pipeline `step_context` and
`verify.rules` in `.pipeline/config.json`.

### Ideal values (healthy run)

Interpret per **step**, not only the parent orchestrator. Ratios are **0–1**.

**Target zeros / ones**

| Score | Ideal | Worry when |
|-------|-------|------------|
| `tool_calls_legitimate` | equals `tool_calls_total` | Gap grows |
| `waste_ratio` | **0** | **> 0.2** |
| `wrong_tool_count` | **0** | any **> 0** |
| `out_of_contract_count` | **0** | any high-confidence miss |
| `retry_ratio` | **0** | **> 0.1** |
| `denied_count` | **0** | any **> 0** |
| `verify_coverage` | **1** | **< 1** after SUCCESS claimed |
| `integrity_pass` | **1** | **0** |
| `allowlist_unused_count` | **0** on small specialist allowlists | large unused on parent is often OK |

**Shape (≈ 1.0 is calm)**

| Score | Ideal | Worry when |
|-------|-------|------------|
| `read_amplification` | **1.0** | **≥ 2** |
| `search_thrash` | **1.0** | **≥ 2** |
| `edit_churn` | **1.0** | **≥ 2** |

**Directional**

| Score | Guidance |
|-------|----------|
| `tool_calls_total` | As low as the task allows; no fixed “good” number |
| `discovery_ratio` | **~0.2–0.6** on implement steps; **1** = no edit; **0** = edited with no prior tools |
| `context_peak_percent` | absent or **< 80**; high = context pressure |

Example micro README change on **developer-agent**: `waste_ratio` 0,
`wrong_tool_count` 0, `integrity_pass` 1, amplification metrics ≈ 1.

### Tokens and cost (not scores)

On the Langfuse **generation** observation → Usage:

- Smaller tokens for the same outcome is better; no universal target.
- Cache-heavy input is normal on long chats; cache-read uses a discounted rate.
- **Cost $0** when the model is unknown/`auto-smart`, or no tokens were captured.
  Priced models (e.g. `grok-4.6`) get input/output/cache USD on the generation.

---

## Configuration (`agent_observability`)

In `.pipeline/config.json` (merged on `init`; enabled by `obs install`):

| Key | Default | Purpose |
|-----|---------|---------|
| `enabled` | `false` until install | Master switch |
| `adapter` | `langfuse` | Ship target |
| `sample_rate` | `1.0` | Reserved for future sampling |
| `redact` | path globs | Substrings stripped from ledger fields |
| `max_field_chars` | `8000` | Truncate large tool I/O |
| `dataset` | `pipeline-kit-agent-runs` | Langfuse dataset name on flush |
| `retention_days` | `14` | Documented intent for ledger hygiene |
| `model_prices` | kit defaults | USD per million tokens: `{ "grok-4.6": { "input": 3, "output": 15, "cache_read": 0.3, "cache_write": 3.75 } }` |

Optional `verify.rules` (same config) improve `verify_coverage` / `integrity_pass`:

```json
"verify": {
  "rules": [
    {
      "match": "news-site/",
      "expect": "pytest",
      "message": "Run pytest after news-site changes"
    }
  ]
}
```

---

## Datasets and experiments

Each successful flush can upsert the configured dataset and a dataset-run item
linked to the conversation trace. Use Langfuse Datasets to compare two pack
versions on the same prompt. Scores remain rule-based (no LLM judge).

---

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| Ledger empty | Wrong workspace root; obs disabled; hooks not merged |
| No Langfuse trace | Keys missing; flush not run; 429 rate limit (retry later) |
| Three sessions for one pipeline | Separate `conversation_id` per Task (expected today) |
| Usage all zero | Looking at Task trace; or flush before `afterAgentResponse` |
| Model `auto-smart` | Placeholder until end-of-turn hooks; pin a model in Cursor to test |
| Scores all `unattributed` | No `subagentStart` + `step_context` from loader |

```bash
pipeline-kit doctor
pipeline-kit obs status
wc -l .pipeline/state/obs/events.jsonl
tail -f .pipeline/state/obs/events.jsonl
```

---

## Related docs

| Doc | Role |
|-----|------|
| [CUSTOMER-GUIDE.md](./CUSTOMER-GUIDE.md) | Full kit handbook; obs commands in the CLI table |
| `.pipeline/wiki/agent-observability.md` | Short wiki page copied with the pack |
| `spec` / product telemetry | Use `telemetry-agent`, not `obs` |
