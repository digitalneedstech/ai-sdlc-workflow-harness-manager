# Langfuse scores, evaluators, and dashboards

> Operator learning (2026-09-18). Companion to `roadmap/eval-harness-langfuse.md`
> (implementation plan) and `OBSERVABILITY.md` (process-score formulas).
> This page answers: what the kit sends, what is an Evaluator vs a score
> config, and how those drive Langfuse dashboards.

## One-line model

```
hooks → events.jsonl → obs flush ──► traces + SCORE VALUES (numbers)
eval judges sync     ──► SCORE CONFIGS (name + type; no numbers)
.pipeline/eval/judges/*.md ──► LANGFUSE EVALUATORS (LLM-as-judge; UI, optional)
score configs + posted values ──► Score Analytics / dashboards
```

Metrics are **not** Evaluators. Flush scores are kit-computed numbers.
Only the 10 `.md` judge prompts are LLM-as-judge Evaluators.

## Three Langfuse objects (do not mix)

| Object | What it is | Who creates it | Has a value? | LLM? |
|--------|------------|----------------|--------------|------|
| **Score config** | Schema for a name: NUMERIC / BOOLEAN, min/max, description | `pipeline-kit eval judges sync` (once per Langfuse project) | No | No |
| **Score value** | A number/boolean on an observation or root | `pipeline-kit obs flush` (every run) **or** an Evaluator after a new observation | Yes | Only if an Evaluator wrote it |
| **Evaluator** | Langfuse job: prompt + model + rule (which observations to grade) | **You**, in the UI, by pasting `.pipeline/eval/judges/*.md` | Writes values later | Yes |

**Where to look (cloud.langfuse.com, same project as `LANGFUSE_*`):**

| UI | What you see |
|----|----------------|
| **Scores → Configs** (or **Settings → Scores**) | Definitions from `eval judges sync` (`waste_ratio`, `task_complete`, `critic_signal`, …) |
| **Traces → a trace → Scores** | Actual numbers from flush and/or judges |
| **Evaluators** | LLM-as-judge jobs (empty until you paste the `.md` files) |
| **Score Analytics** | Charts over posted values, grouped by config name |
| **Sessions** | Pipeline grouping when session id is `{workflow}:{slug}` |

Without a config, flush can still post `waste_ratio=0.2` as an ad-hoc score.
With a config, Langfuse treats that name as a stable metric (type + range),
so analytics, filters, and evaluator output share one catalog.

## Commands (when to run)

| Command | Frequency | What it does |
|---------|-----------|----------------|
| `pipeline-kit obs flush [project]` | After Agent sessions (ledger has new rows) | Builds OTLP traces, posts **score values**, optional dataset upsert. Does **not** run LLM judges. |
| `pipeline-kit eval judges sync [project]` | **Once** per Langfuse project (re-run only if keys/project change or kit score names change) | HTTP create/update of **score configs** for process scores + run-level scores + judge **names**. Does **not** grade traces. Does **not** upload `.md` prompts. |
| Langfuse UI: Evaluators → New | Once per judge you want live | Paste a prompt from `.pipeline/eval/judges/`. Attach to **observation** (not trace). |

`python install.py obs …` is the **legacy** installer and does not understand
`obs` / `eval`. Use `pipeline-kit …` after `uv tool install` / `./install.sh`,
or `cli_main(['obs','flush', …])` from the kit clone.

Windows hooks must call `python` (Store `python3` stub exits 9009 and never
writes `events.jsonl`). Mac can keep `python3`.

## What flush sends (no LLM)

Flush already posted Layer C scores before `eval judges sync` existed.
Sync did **not** replace flush. It registered the **names**. Flush still
computes and POSTs `/api/public/scores`.

### A. Per-step process scores (15) — `SCORE_NAMES`

Attached to `pipeline.step {agent}` observations. Tool discipline, not
spec quality. Formulas: `OBSERVABILITY.md`.

| Score | Type | Meaning |
|-------|------|---------|
| `tool_calls_total` | count | Tool events in the step |
| `tool_calls_legitimate` | count | Total minus waste / high-confidence out-of-contract |
| `waste_ratio` | 0–1 | Repeat read/search/shell or empty Grep |
| `wrong_tool_count` | count | Shell used as cat/head/find/grep |
| `out_of_contract_count` | count | Read/edit outside allowlist |
| `read_amplification` | ratio | Reads ÷ distinct files |
| `search_thrash` | ratio | Searches ÷ distinct patterns |
| `edit_churn` | ratio | Edits ÷ distinct files |
| `discovery_ratio` | 0–1 | Tools before first edit ÷ all tools |
| `retry_ratio` | 0–1 | Failed tools ÷ total |
| `denied_count` | count | `permission_denied` |
| `allowlist_unused_count` | count | Allowlisted paths never Read |
| `verify_coverage` | 0–1 | Share of `verify.rules` hit by shell |
| `integrity_pass` | 0 or 1 | SUCCESS claimed but checks failed |
| `context_peak_percent` | 0–100 | Max `preCompact` context % |

### B. Run-level scores (Starter 7 inputs) — additive, new names only

On the **root** observation, plus `step_success` per step. Comparison
metrics (shipreadymetrics-aligned). See `eval-harness-langfuse.md`.

| Score | Type | Meaning |
|-------|------|---------|
| `task_complete` | boolean | Expected steps SUCCESS + integrity + deploy `OVERALL=passed` when devops ran |
| `step_success` | 0–1 | That step’s HANDOFF claimed SUCCESS |
| `hitl_count` | count | Extra user prompts after the first |
| `hitl_wait_s` | seconds | Wait on those extra prompts |
| `critic_retry_count` | count | Same-step re-spawns |
| `secret_leak_count` | count | Secret-pattern hits in `features/{slug}` |

### Not scores

| Data | Where | Note |
|------|--------|------|
| Tokens / $ | generation `usage_details` + `cost_details` | Flush prices known models (cache-read discounted). Hooks never send dollars. |
| `time_to_first_tool_ms` | generation attribute | Latency proxy, not a score |

## LLM-as-judge evaluators (10) — optional, UI only

Files: `.pipeline/eval/judges/*.md` (copied on `init`). These **are**
Langfuse Evaluators. `eval judges sync` only reserved the score **names**.

Observation-level only (trace-level judges deprecated; Cloud cutover
2026-11-16). Judge sees **that** observation’s input/output — not child
tools. Flush must write HANDOFF / verdict clips onto `pipeline.step` I/O
or the judge returns “no artifact clip”.

Never attach judges to `tool:` / `retriever:` / `generation`.

| Judge | Target observation | Score |
|-------|-------------------|-------|
| `spec_completeness` | `pipeline.step ba-agent` | 0–1 |
| `spec_testability` | `pipeline.step ba-agent` | 0–1 |
| `scope_control` | `pipeline.step ba-agent` | 0–1 |
| `critic_signal` | `pipeline.step ba-critic-agent`, `pipeline.step developer-critic-agent` | 0–1 |
| `implementation_faithfulness` | `pipeline.step developer-agent` | 0–1 |
| `grounding` | `pipeline.step developer-agent` | 0–1 |
| `test_adequacy` | `pipeline.step tester-agent` | 0–1 |
| `handoff_honesty` | `pipeline.step *` | boolean |
| `instruction_following` | root (`isRootObservation=true`) | 0–1 |
| `safety_hygiene` | root | boolean |

UI steps after sync:

1. **Project Settings → LLM Connections** — add a key, pin one judge model.
2. **Evaluators → New** — paste the `.md` body; map `{{input}}` / `{{output}}`
   to observation input/output.
3. **Rule** = observation **name** filter (table above), not trace.
4. Sampling: 100% golden, ~10% live.

Judges score **new** observations after the rule exists. There is no
`eval judges run` CLI.

## How this drives dashboards

Langfuse charts **scores that exist on observations**, keyed by config name.

```
Flush values ─────────────┐
                          ├──► Score Analytics / custom dashboards
Evaluator values (later) ─┘     filter by tags: workflow, pack_id, step
```

| Dashboard question | Drive from | Source |
|--------------------|------------|--------|
| Was the agent thrashing tools? | `waste_ratio`, `search_thrash`, `edit_churn` | flush |
| Did SUCCESS claims hold? | `integrity_pass`, `handoff_honesty` | flush + optional judge |
| Did the run finish? | `task_complete`, `step_success` | flush |
| How much human wait? | `hitl_count`, `hitl_wait_s` | flush |
| Was the spec/test/diff any good? | `spec_*`, `test_adequacy`, `implementation_faithfulness`, `critic_signal` | LLM evaluator |
| Compare packs later | same score names × `pack_id` / workflow tags | both |

Do **not** collapse these into one trust index. Process scores and quality
judges answer different questions.

Cost-per-successful-run is a **dashboard join** (usage $ ÷ `task_complete`
green runs), not a flush score.

## Daily loop vs one-time

1. **Once:** `obs install`, `.env` with `LANGFUSE_*`, `eval judges sync`,
   paste judges you care about.
2. **Every test:** Agent session → ledger `events.jsonl` → `obs flush` →
   open Traces. Process scores appear immediately.
3. **If evaluators exist:** Langfuse grades matching `pipeline.step` /
   root observations on a delay; scores show on the same trace.

## What `eval judges sync` changed vs old flush

| Before sync | After sync |
|-------------|------------|
| Flush posted Layer C numbers as ad-hoc scores | Same numbers, plus official configs (type/range) |
| No run-level Starter 7 names in Langfuse | Configs exist; **values still only appear after flush** of a run that can compute them |
| No reserved names for `critic_signal` etc. | Names exist so Evaluators write into them instead of inventing labels |
| Dashboards were “whatever flush posted” | Dashboards can treat the catalog as a metric set |

If you never open Score Analytics or Evaluators, flush still works.
Configs make those scores a **comparable metric catalog**, not raw posts.
