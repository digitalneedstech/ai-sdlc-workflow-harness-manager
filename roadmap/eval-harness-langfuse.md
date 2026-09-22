# Roadmap: AI DLC Pipeline Eval Harness (Langfuse)

> Status: T0–T2 implemented (2026-09-18); later phases 0–5 still planned. Owner: pipeline-kit. Companion docs: `OBSERVABILITY.md` (live process scores), `roadmap/langfuse-scores-evaluators-dashboards.md` (score configs vs flush values vs LLM evaluators, catalogs, dashboards), future `EVALUATION.md` (customer-facing eval guide).

TL;DR — Pipeline-kit already traces agent runs to Langfuse and scores *tool discipline*. Langfuse evals cannot work on those traces yet because judges only see one observation's I/O, and `pipeline.step` spans only store task + status. **First ship:** make this pipeline eval-ready in Langfuse (observation-level judges on `pipeline.step {agent}`) plus the Starter 7 comparison metrics, without breaking Datadog/OTLP adapter contracts. Golden bake-off / full Layer A oracles come later.

## Langfuse research (how eval actually works)

Langfuse stores **scores** (NUMERIC / BOOLEAN / CATEGORICAL / TEXT) on exactly one of: observation, trace, session, dataset run. **Evaluators** = how to score. **Rules** = which live observations to score (filters + sampling). Methods:

1. **Scores via API** — what flush already does for Layer C (`source=API`). Right place for kit Python oracles (file/pytest/deploy). Keep this.
2. **LLM-as-a-Judge** — observation-level only. Trace-level judges deprecated; Cloud cutover **2026-11-16**. Judge sees *that* observation's input, output, metadata, tool_calls — **not children**. Map `{{input}}`/`{{output}}`. Rules filter by name / type / `isRootObservation` / tags. Batch eval on historical needs ingestion v4 (`x-langfuse-ingestion-version: 4` already set).
3. **In-Langfuse code evaluators** — Python/TS in their sandbox: **2s, no network, no third-party, no disk**. Cannot read `features/{slug}` or run pytest. Do **not** put Layer A here.
4. **Annotation queues** — Layer D humans. Score configs make analytics comparable.
5. **Experiments** — UI *prompt* experiments run a Langfuse-hosted prompt; **wrong** for a coding pipeline. Correct path: operator runs the pack → kit links the existing OTel trace to a dataset item (`dataset-run-items`, already stubbed) or OTel experiment attributes. No Langfuse SDK.

### Why the current tree fails judges

Live tree (`pipeline_observability/export.py` `build_conversation_spans`): root `agent` `{workflow}:{slug}` → `generation` → `tool`/`retriever`; sibling `agent` named `pipeline.step {step}` per `subagent_id`. Scores already attach to that step `observationId`. Step **input** = Task prompt clip; **output** = `status` only. Skills are allowlisted files in `kit/pipeline/workflows/*.json`, not spans. Parent vs Task = **many traces** per pipeline (`conversation_id`). `flush_project` hard-requires `LangfuseAdapter`.

Judges on root see the parent chat, not the BA spec. Judges on `pipeline.step ba-agent` cannot read HANDOFF or child tools unless flush **writes clips onto that span**. Do not judge every tool (cost + noise).

### Adapter rule (do not fork)

- Shared: observation tree + score list in `export.py` / `scoring.py` (vendor-neutral names: `pipeline.step`, `pipeline.skills`, score `{name,value,observationId}`).
- Langfuse adapter only: OTLP `langfuse.*` keys, `/api/public/scores`, evaluator/rule HTTP, datasets.
- OTLP stub: scores stay span attributes (`post_scores` already no-ops success).
- Datadog stub: keep `untested`; do not change the Protocol.
- No judge sync or Langfuse score-config HTTP in `scoring.py`.
- `flush_project`: Langfuse remains the only ship path; other adapters return skip, not a crash in the span builder.

## Decisions

- **First ship:** eval-ready traces + Starter 7 flush additions + Langfuse observation judges on `pipeline.step {agent}`. Not full Layer A oracles, not golden bake-off, not Layer E adapters.
- Deliverable later: kit eval harness (not docs-only, not a full auto-executor of OpenSpec/SpecKit/BMAD).
- First customer proof: development / feature pipeline. QA and DevOps get catalog slices and stubs, not full oracles in v1.
- Comparison later: same golden tasks across packs as Langfuse dataset experiment runs (`pack_id` + `task_id` + pack version).
- Do **not** collapse trust into one vanity number. Export a dimensional scorecard.
- Keep existing deterministic scores; add new score names with `source=code|judge|human`.
- Langfuse v4: judges target **observations** (root agent + `pipeline.step *`), not deprecated trace-level evaluators.
- Judges only see the targeted observation's input/output/metadata — flush must **write artifact summaries onto those spans**.
- No Langfuse SDK (match current HTTP adapter). Secrets stay in `LANGFUSE_*`.
- No in-Langfuse sandbox code evaluators for pipeline oracles (no disk/network). Kit Python + scores API.
- No Langfuse UI prompt experiments for this pipeline.
- Skills are **metadata on the step observation** (from allowlist `SKILL.md` paths), not fake skill spans (hooks have no skill-start event).
- Session grouping: keep `trace_id` = conversation; set `langfuse.session.id` to `{workflow}:{slug}` when slug exists so Sessions = one pipeline. Fallback: conversation UUID.
- Out of scope v1: executing third-party packs, remote deploy, mixing product telemetry-agent with agent-obs, auto-fixing `test_scoring_groups` unless `scoring.py` is touched, vendor lock-in to Sonar/Checkmarx/CodeQL, and SAST/maintainability product selection.

## Do-not-break guarantees (hard constraints for every phase)

Everything in this plan is **additive**. Any change that violates a row below is a bug, regardless of what it enables:

| Existing behavior | Guarantee |
|---|---|
| 15 `SCORE_NAMES` (Layer C) | Names, formulas, ideals, and step-observation targets unchanged. New scores are new names only; never repurpose an existing name. |
| `pipeline-kit obs report` | Existing output lines unchanged; run-level numbers are appended, never replace. Still works fully offline. |
| Trace identity | `trace_id` stays the Cursor `conversation_id` (32-hex). Session id is a **new** field (`langfuse.session.id`); no re-keying of traces, so historical Langfuse data still lines up. |
| Ledger + hooks | JSONL ledger schema and hook scripts untouched by T0–T2. Flush offset semantics unchanged (error → offset not advanced; re-flush ships same rows). |
| Deterministic score ids | `otel32(trace:step:name)` scheme kept; double-flush stays duplicate-free, including for the new run-level scores. |
| Adapter `Protocol` | No new **required** methods. `ensure_dataset` / `sync_evaluators` are Langfuse-only optionals. Datadog/OTLP stubs keep compiling and return skip, not crash. |
| OTLP span payload | Additive attributes/metadata only (clips, `pipeline.skills`, `steps_expected`, tags). No renames or removals — external OTLP consumers keep parsing. |
| CLI surface | `obs install/uninstall/status/flush/report` signatures unchanged. `eval` is a new sibling subparser. |
| Config / env | `LANGFUSE_*` keys unchanged. New keys (`PIPELINE_EVAL_*`, `eval.quality.command`, `pack_id` override) are optional with safe defaults — absent key ⇒ current behavior. |
| Dataset | `pipeline-kit-agent-runs` upsert behavior unchanged; golden datasets are separate. |
| Fail-open flush | Missing HANDOFF / `features/{slug}` artifacts ⇒ clip omitted and run-level scores 0/N-A; `build_conversation_spans` never raises on missing files. |
| Test suite | `tests/test_observability.py` must stay green after every phase. `test_scoring_groups` is a pre-existing fail on main — do not mask it, do not count it as a regression. |
| Kit install | `install.py` / `init` copy paths only gain files (`eval/`, `EVALUATION.md`); no existing pack file is moved or renamed. |

## Starter 7 — critical comparison metrics (v1)

Source: shipreadymetrics.com AI development metrics catalog. Rules adopted: outcome > activity; every metric gets a counter-metric (Goodhart); trends/distributions, not absolutes. These 7 are the v1 set for **comparing pipelines/packs** (pipeline-kit vs OpenSpec/SpecKit/BMAD, or workflow A vs B). Unit of comparison = **one run** (slug/session), never one chat.

| # | Metric | Catalog anchor | Formula (per run = slug/session) | Counter-metric |
|---|---|---|---|---|
| S1 | **Run success rate** | Agent Run Success / pass@k; DORA | `task_complete` (HANDOFF chain complete + no integrity fail + deploy OVERALL=passed when devops ran) per run; compare % across packs on same task | S5 cost (cheap failures), S3 honesty |
| S2 | **Step-completion rate** | Agent Run Step-Completion | steps reaching SUCCESS ÷ steps attempted in the workflow chain; per-step breakdown shows *where* packs fail | S6 rework |
| S3 | **Claim integrity** (change-failure analog) | Change Failure Rate by authorship | `integrity_pass` min across implement/tester/devops steps; % runs where SUCCESS claim was contradicted | S1 (refusing to claim ≠ good) |
| S4 | **HITL / review burden** | AI Change Review Coverage + Review Latency | `hitl_count` (signoff gates hit + critic changes-required retries) and `hitl_wait_s` per run; designed gates vs extra rework loops | S1 (zero HITL by skipping gates is a fail) |
| S5 | **Cost per successful run** | Cost per Successful Request (FinOps) | Σ usage_details $ across all traces of the run ÷ S1-green runs; failed-run $ reported separately | S1 + S6 (cheap-but-wrong) |
| S6 | **Rework / churn on agent code** | Rework & Code Churn Rate | live `edit_churn` (max per step) + `critic_retry_count` (changes-required loops) per run | S2 (churn can be legit iteration) |
| S7 | **Policy & safety hits** | Vulnerability Introduction / provenance | `out_of_contract_count` + `denied_count` (live) + `secret_leak_count` (new regex over artifacts) per run; ideal 0 | S1 (a locked-down agent that ships nothing) |

Deliberately **not** in v1: acceptance rate, AI contribution %, LoC (gameable activity metrics per the catalog); drift/jailbreak (not this product); DevEx surveys (not Langfuse data).

### Data-point gap table (what flush must add)

| Metric | Already flushed | Missing → add to flush |
|---|---|---|
| S1 | stop status/abort; per-step scores | **`task_complete` BOOLEAN score on root** (from `features/{slug}` artifacts + `deploy-result.env`); needs session-by-slug join |
| S2 | `pipeline.step` spans exist | **`step_success` 0/1 per step** (HANDOFF SUCCESS regex) + `steps_expected` from workflow chain in root metadata |
| S3 | `integrity_pass` per step ✅ | nothing — derive run-level min in dashboard |
| S4 | stop `aborted`; multiple parent traces (weak) | **`hitl_count`, `hitl_wait_s` scores on root**; count `@signoff` gates + critic re-spawns from the ledger step sequence |
| S5 | usage_details on parent generations ✅ (child Tasks often 0) | **session id = `{workflow}:{slug}`** so all traces of a run aggregate; flag runs with incomplete usage |
| S6 | `edit_churn` per step ✅ | **`critic_retry_count` score on root** (same-step re-spawn after critic changes-required) |
| S7 | `out_of_contract_count`, `denied_count` ✅ | **`secret_leak_count` NUMERIC on root** (existing `SECRET_RE` over `features/{slug}` artifacts at flush) |

New flush work = 6 additions: run-level scores `task_complete`, `step_success` (per step), `hitl_count`, `hitl_wait_s`, `critic_retry_count`, `secret_leak_count`; plus session-by-slug + `steps_expected` metadata. All are **kit Python + scores API** (`source=API`) — no judges required for the Starter 7; Layer B judges are the quality explainers on top.

Langfuse view: one dashboard, 7 widgets, filter by `pack_id`/workflow tags; compare packs via same-task runs (dataset runs later). Operator catalog of score configs vs flush values vs LLM evaluators: `roadmap/langfuse-scores-evaluators-dashboards.md`.

## Questions this harness can answer

Rule of thumb: **flush** = *did it run cleanly and finish?* **LLM judges** = *was the artifact any good?* **Dashboards** = those scores over time / by pack. They do **not** answer “is the product good for users.”

### After `obs flush` (no LLM)

**Did the pipeline finish?**

| Question | Score / data |
|----------|----------------|
| Did this run complete? | `task_complete` |
| Where did it die (BA vs developer vs tester vs devops)? | `step_success` by step name |
| Did it claim SUCCESS but checks failed? | `integrity_pass` |

**Was the agent wasting motion?**

| Question | Score |
|----------|--------|
| Repeating reads/searches? | `waste_ratio`, `read_amplification`, `search_thrash` |
| Editing the same files over and over? | `edit_churn` |
| Exploring forever before writing code? | `discovery_ratio` |
| Using shell as cat/grep? | `wrong_tool_count` |
| Tools failing / permission denied? | `retry_ratio`, `denied_count` |

**How much human time?**

| Question | Score |
|----------|--------|
| Extra prompts after the first? | `hitl_count` |
| How long were we waiting on the human? | `hitl_wait_s` |
| Critic sent work back? | `critic_retry_count` |

**Did it stay in bounds?**

| Question | Score |
|----------|--------|
| Read/edit outside allowlist? | `out_of_contract_count` |
| Secrets in `features/{slug}`? | `secret_leak_count` |
| Verify rules actually run? | `verify_coverage` |

**Compare later (same task, two packs/workflows):** filter Score Analytics by workflow / `pack_id` — success rate, HITL, churn, policy hits.

### After the 10 evaluators are pasted in Langfuse

**Was the work any good (not just “tools looked busy”)?**

| Question | Judge |
|----------|--------|
| Spec complete / testable / not gold-plated? | `spec_completeness`, `spec_testability`, `scope_control` |
| Critic a real review or a rubber stamp? | `critic_signal` |
| Diff match Must FRs; HANDOFF match disk? | `implementation_faithfulness`, `grounding` |
| Tests cover Must ACs? | `test_adequacy` |
| Honest SUCCESS / followed allowlist / no secret dump? | `handoff_honesty`, `instruction_following`, `safety_hygiene` |

### What this cannot answer (v1)

- User/product quality (“is Chorus better?”)
- True $ per success if child Task traces have 0 tokens (S5 is a dashboard join, incomplete until parent usage is present)
- “Which model is smarter?” without A/B on the **same** golden task
- CVE / Sonar / Checkmarx code quality (out of scope)

## Flush inventory — what lands in Langfuse

`pipeline-kit obs flush` POSTs OTLP traces then `/api/public/scores`. Judges are **not** in flush; they run in Langfuse after the observation exists. Dataset upsert is already in flush (`pipeline-kit-agent-runs`).

### Already flushed today

| Data point | Where in Langfuse | Benefit |
|---|---|---|
| Trace `{workflow}:{slug}` | Traces table | One conversation's timeline |
| Session = conversation UUID | Sessions | Weak; parent and Task chats stay split |
| Tags: harness, workflow, change_class, composer_mode, `agent`, subagent names | Trace filters | Filter feature-development vs jira-bug; find which specialist ran |
| User email | `user.id` | Adoption / hero-user views |
| Root input/output | Root observation + trace I/O | User prompt and parent chat result |
| `generation` + usage_details | Cost / tokens UI | $ when parent hooks sent tokens (child Tasks often 0) |
| `time_to_first_tool_ms` | Generation attribute, not a score | Latency proxy |
| `pipeline.step {agent}` | Nested agent observation | Specialist grain for scores |
| Step input = Task text; output = `status` | Step I/O | Weak for judges (status only) |
| Tools / retrievers + verdict | Child spans | Debug thrash; **not** judged |
| Events: prompt, stop, abort, preCompact % | Event spans | Abort rate; context pressure |
| Layer C scores (15 `SCORE_NAMES`) on step observation | Scores + Score Analytics | Waste, OOC, churn, integrity, verify — "was the agent disciplined?" |
| Dataset item per conversation | `pipeline-kit-agent-runs` | List of runs; not a golden experiment |

**Benefit today:** ops dashboards (step hotspots, abort, adoption, incomplete cost). **Not** "did the spec/ACs work."

### New on flush (eval-ready traces + Starter 7)

| Data point | Where | Benefit |
|---|---|---|
| Step **output clip** (HANDOFF / SUCCESS / critic verdict) | `pipeline.step` output | Judges can grade the specialist without reading child tools |
| `pipeline.skills` on step | Observation metadata | Filter/explain which skill pack that agent used |
| `pipeline.change_class`, `pack_id` | Tags + metadata | Bake-off later; filter micro vs feature now |
| `subagent_name` on step | Metadata | Rule filters and Score Analytics by specialist |
| Root metadata: steps that ran + `steps_expected` | Root | Pipeline shape; S2 denominator |
| Session id = `{workflow}:{slug}` | Sessions | Parent + Task traces become **one pipeline session** |
| Run-level scores: `task_complete`, `step_success`, `hitl_count`, `hitl_wait_s`, `critic_retry_count`, `secret_leak_count` | Root / step scores | Starter 7 dashboard |

### Written in Langfuse after flush (not the ship payload)

| Data point | How | Benefit |
|---|---|---|
| Layer B judge scores on the matching `pipeline.step` | Evaluator + rule / batch eval | Spec quality, faithfulness, critic signal, test adequacy |
| `safety_hygiene` on root | Root rule | Policy light without scoring every tool |
| Human `human_*` | Annotation queue | Calibrate judges; "would ship" |

### Still later

Full Layer A oracles (`tests_pass`, `ac_oracle_pass`, …), Layer E quality-gate deltas, golden dataset `aidlc-golden-dev-v1`, ROI R1–R7 scorecard, explicit `run_id` join beyond session-by-slug.

## First ship — Langfuse eval on this pipeline

> Implemented 2026-09-18: T0 in `pipeline_observability/export.py` (step HANDOFF clips, `pipeline.skills`, session `{workflow}:{slug}`, run-level scores), T1 as `pipeline-kit eval judges sync` (`pipeline_eval/` + `kit/pipeline/eval/judges/*.md`; evaluator/rule creation stays a documented UI step — no public API), T2 stub-adapter skip in `flush_project`. Tests: `tests/test_eval.py`.

Grain: **one score per specialist observation**, not per tool. Workflows in `kit/pipeline/config.json` / `kit/pipeline/workflows/*.json` (feature-development classes, jira-story/epic/bug, ask). HITL `@signoff` and `@waves` have no subagent span — skip judges there.

**Judge → observation map (online rules; sampling 100% golden / 10% live later)**

| Observation name (filter) | Judges |
|---|---|
| `pipeline.step ba-agent` | `spec_completeness`, `spec_testability`, `scope_control` |
| `pipeline.step ba-critic-agent` / `developer-critic-agent` | `critic_signal` |
| `pipeline.step developer-agent` | `implementation_faithfulness`, `grounding` |
| `pipeline.step tester-agent` | `test_adequacy` |
| `pipeline.step devops-agent` | `handoff_honesty` only (deploy oracles later) |
| `pipeline.step product-manager-agent` / `architect-agent` / `intake-agent` | `instruction_following` (light) |
| root (`isRootObservation=true`) | `safety_hygiene`; optional `instruction_following` |

Do not attach judges to `tool:` / `retriever:` / `generation`. Layer C scores stay as today.

### Phase T0 — Eval-ready spans + Starter 7 flush additions (*blocks judges*)

1. In `build_conversation_spans`, on each `pipeline.step` observation:
   - Keep input = Task text.
   - Output = JSON clip: `status`, last HANDOFF/`SUCCESS` line from `features/{slug}/HANDOFF-{step}.md` or `HANDOFF.md` (cap `MAX_IO`), critic verdict if present.
   - Metadata: `pipeline.step`, `pipeline.workflow`, `pipeline.change_class`, `pipeline.skills` (skill folder names from that step's `allowed_reads` / workflow JSON `SKILL.md` paths), `subagent_name`, `subagent_id`.
2. Trace tags: existing + distinct step names + `pack_id=pipeline-kit` (env override).
3. `langfuse.session.id` = `{workflow}:{slug}` when slug known (groups parent+Task traces). Trace id unchanged.
4. Root metadata: list of steps that ran + `steps_expected` from workflow chain. Do not dump all HANDOFFs on root.
5. Starter 7 run-level scores on root/step: `task_complete`, `step_success`, `hitl_count`, `hitl_wait_s`, `critic_retry_count`, `secret_leak_count`.
6. Tests: fixture events with `subagent_id` + fake HANDOFF file → step span output contains SUCCESS clip; no HANDOFF → status only, `step_success=0`; Datadog/OTLP `build_otlp` still returns spans (flush still Langfuse-only).

### Phase T1 — Score configs + judge sync (*depends on T0*)

7. `pipeline-kit eval judges sync` (Langfuse HTTP only): create score configs for Layer C names + Layer B judge names; create evaluators from `kit/pipeline/eval/judges/*.md`; create rules filtered by observation **name** `pipeline.step …`.
8. Document LLM connection in Langfuse project settings (required; kit cannot invent keys). Pin project default judge model.
9. After one real flush: batch-eval a `pipeline.step ba-agent` observation; confirm score + reasoning on that span, not the trace.

### Phase T2 — Adapter contract hygiene (*parallel; no Datadog implementation*)

10. Keep the `Adapter` protocol. Optional methods (`ensure_dataset`, `sync_evaluators`) only on Langfuse.
11. No `langfuse.*` keys inside `scoring.py`. Mapping stays in span attrs / Langfuse adapter.
12. `flush_project`: if adapter is a stub, return `{ok:true, skipped}`; default still Langfuse.

## Later phases (full harness)

### Phase 0 — Catalog as source of truth (*blocks later phases*)

1. `kit/pipeline/eval/catalog.yaml` listing every metric (layers A–D, Layer E `status: planned`, QA/DevOps stubs `status: planned`). Copy to `.pipeline/eval/` on `init`. Include optional `eval.quality.command` config key (documented, unused in v1).
2. `EVALUATION.md` (root + copied to `.pipeline/docs/` like `OBSERVABILITY.md`): methods, ideals, customer briefing, Langfuse setup.
3. Golden-task JSON schema: `id`, `prompt`, `lifecycle`, `change_class`, `required_artifacts`, `oracles[]` (command / file / grep / http), `must_acs[]`, `out_of_scope`, `difficulty`.

### Phase 1 — Code oracles + identity (*depends on 0*)

4. New module `pipeline_eval/` (keep `pipeline_observability` for ledger/flush): `catalog.py`, `artifacts.py` (read `features/{slug}` + `deploy-result.env` + HANDOFF SUCCESS regex), `oracles.py` (declared commands localhost-only; timeout; no git push).
5. CLI: `pipeline-kit eval score --slug … --task … --pack …` computes Layer A/C extras, POSTs scores, prints local JSON (works without network like `obs report`).
6. Extend flush tags with pack/task/lifecycle from config or env (`PIPELINE_EVAL_PACK_ID`, …).
7. Tests in `tests/test_eval.py` using a fixture `features/demo` tree.

### Phase 2 — Langfuse judges + annotation (*depends on 1*)

8. Judge prompts in `kit/pipeline/eval/judges/*.md` with `{{input}}` `{{output}}` `{{expected}}`. Numeric 0–1 except booleans for honesty/safety.
9. `eval judges sync` / optional `eval judges test`.
10. `eval annotate sync` — score configs; document UI queue steps rather than inventing queue IDs.
11. `eval calibration` — human vs judge agreement; fail CLI if n too small.

### Phase 3 — Golden bake-off protocol (*depends on 1; parallel with 2*)

12. 6–8 development golden tasks under `kit/pipeline/eval/golden/development/`.
13. `eval dataset upsert` — Langfuse dataset items from golden JSON.
14. `eval experiment record --task --pack --trace-id|--slug` — link the trace after the operator ran that pack. **No** auto-invoking OpenSpec/SpecKit/BMAD.
15. Operator playbook in `EVALUATION.md`: same model, same machine class, N≥3 repeats when variance is high; freeze pack git SHAs.

### Phase 4 — Scorecard (*depends on 1–3*)

16. `eval scorecard --dataset aidlc-golden-dev-v1 --runs packA,packB,…` → Markdown+JSON (customer-safe; `--redact`).
17. Mention scorecard in `CUSTOMER-GUIDE.md` CLI table.

### Phase 5 — QA / DevOps / code-standards catalog only (*parallel after 0*)

18. Golden stubs + metric rows `status: planned`. No runner until a customer QA/DevOps pack exists.
19. Layer E: catalog metrics + config key + N/A rule only. `eval quality --baseline-sha` only when a customer engagement has a gate command.

## Metric catalog (layers A–E, D)

### Layer A — Task success (code oracles). Highest customer weight.

| Metric | Method | Ideal | How |
|---|---|---|---|
| `task_complete` | code | 1 | Required artifacts exist for the workflow class (route, spec or patch, HANDOFF chain, RETRO if claimed done). |
| `pipeline_gates_honored` | code | 1 or N/A | Critic verdicts approve before next step; no SUCCESS after changes-required without a retry artifact. |
| `tests_pass` | code | 1 | Golden-task oracle command(s) exit 0. |
| `ac_oracle_pass` | code | 1 | Passed ACs ÷ declared ACs (file exists, grep, HTTP health, DOM assertion). |
| `deploy_health` | code | 1 or N/A | `deploy-result.env` OVERALL=passed. |
| `integrity_pass` | code (live) | 1 | HANDOFF SUCCESS not contradicted by verify/tester/devops. |

### Layer B — Artifact quality (LLM-as-judge + code shape checks)

| Metric | Target observation | Ideal | Rubric gist |
|---|---|---|---|
| `spec_completeness` | ba-agent | ≥ 0.8 | Must FRs, testable ACs, out-of-scope, personas, non-goals. |
| `spec_testability` | ba-agent | ≥ 0.8 | Each Must AC independently verifiable. |
| `scope_control` | ba-agent | ≥ 0.8 | No gold-plating vs user prompt. |
| `implementation_faithfulness` | developer-agent | ≥ 0.8 | Diff matches Must FRs; no extra persistence/auth/routes. |
| `critic_signal` | critic steps | ≥ 0.7 | Verdict grounded; not rubber-stamp. |
| `test_adequacy` | tester-agent | ≥ 0.8 | Must ACs covered; happy + one negative per Must. |
| `handoff_honesty` | each step | 1 (bool) | SUCCESS only if artifacts support it. |
| `instruction_following` | root | ≥ 0.8 | Followed allowlist / change class / no-commit rules. |
| `grounding` | step + artifacts | ≥ 0.8 | HANDOFF claims match files. |
| `safety_hygiene` | root | 1 (bool) | No secrets in artifacts; no destructive git/remote. |

Code shape checks: `artifact_sections_present`, `security_preflight_present`, `secret_leak_count` (ideal 0).

QA lifecycle (catalog only): `seeded_defect_recall`, `test_flake_rate`, `false_positive_rate`, `coverage_delta`, `assertion_density`.
DevOps lifecycle (catalog only): `deploy_success_rate`, `healthcheck_pass`, `secret_hygiene`, `idempotent_redeploy`, `time_to_healthy`.

### Layer C — Process / cost (live today, per step)

Live 15 (`SCORE_NAMES` in `pipeline_observability/export.py`, computed in `scoring.py`): `tool_calls_total`, `tool_calls_legitimate`, `waste_ratio` (worry > 0.2), `wrong_tool_count` (0), `out_of_contract_count` (0), `read_amplification` / `search_thrash` / `edit_churn` (worry ≥ 2), `discovery_ratio` (0.2–0.6 on implement), `retry_ratio` (worry > 0.1), `denied_count` (0), `allowlist_unused_count`, `verify_coverage` (1), `integrity_pass` (1), `context_peak_percent` (< 80). See `OBSERVABILITY.md`.

Add (code): `wall_time_s`, `critic_retry_count`, `hitl_count`, `hitl_wait_s`. Cost is inferred by Langfuse from model prices — never from hooks.

### Layer E — Post-run code quality vs baseline (catalog now, adapters later)

Delta scoring on the same repo SHA start, **touched files only**: `quality_gate_pass`, `new_blocker_count`, `new_vuln_count`, `maintainability_delta`, `coverage_delta`, `lint_error_delta`. Contract: run the customer's own gate command (`eval.quality.command`); output JSON pass/fail + deltas; POST as code scores on root. No command → **N/A, not 0**. No vendor bake-off (Sonar/Checkmarx/Semgrep/CodeQL) in this plan.

### Layer D — Human annotation (calibration + sales evidence)

Score configs + annotation queue on golden-run sample (≥ 20% of bake-off traces, min 15/pack): `human_task_success` (bool), `human_would_ship` (ship / ship-with-nits / reject), `human_rework` (0–1, ≤ 0.2), `human_spec_approve` (bool), `human_comment` (text). Gate: agreement (κ or %) between `human_*` and matching judges ≥ 0.6 before quoting judge numbers to customers. High disagreement → freeze judges, fix rubrics; never lower thresholds.

## Audiences (aggregations, not new score names)

- **C-suite (quarterly/bake-off), five lights:** Worked / Would ship / Still in policy / Cost per successful task / Safe to scale. Never a single "trust index". They never see `edit_churn`.
- **Managers — delivery bar:** work landed (≥70% first-time pass), SUCCESS trustable (integrity=1), team adoption (≥3 engineers/week, abort <15%), codebase-not-worse veto.
- **Managers — ROI (denominators = completed units only):** R1 cost per completed unit (failed-run $ < 20%, separate line), R2 wall-clock e2e (p90 < 2× median), R3 HITL touchpoints (designed gates vs extra rework), R4 reproducibility (N≥3, success ≥80%, CV ≤ 0.3), R5 failed-attempt spend, R6 net labor ROI (needs stated baseline), R7 throughput per engineer.
- Manager drill-down: scorecard light → traces by slug → `pipeline.step …` → scores + tool verdicts → artifacts. Cadence: daily policy hits; weekly hotspots/cost; quarterly bake-off.

## Relevant files

- `pipeline_observability/scoring.py` — process scores; do not overload with artifact oracles.
- `pipeline_observability/export.py` — `SCORE_NAMES`, `build_conversation_spans` (tags, step I/O, session id), `flush_project`.
- `pipeline_observability/adapters/langfuse.py` — scores/datasets HTTP; extend with evaluator/score-config HTTP; SDK-free.
- `pipeline_observability/adapters/base.py`, `datadog.py`, `otlp.py` — protocol only; stubs stay stubs.
- `pipeline_observability/commands.py` + `install.py` — add `eval` subparser beside `obs`.
- `kit/pipeline/workflows/*.json` — step chains + skill allowlists (source of `steps_expected`, `pipeline.skills`).
- `OBSERVABILITY.md` (+ `kit/pipeline/docs/OBSERVABILITY.md` duplicate — update both) — cross-link eval.
- New: `pipeline_eval/`, `kit/pipeline/eval/` (catalog, judges, golden), `EVALUATION.md`, `tests/test_eval.py`.

## Verification — test in Langfuse after changes

### Phase 1 — local, no network

1. `uv run pytest tests/test_observability.py tests/test_eval.py -q` — fixture ledger + fake `features/demo` tree → new scores (`task_complete`, `step_success`, `hitl_count`, `secret_leak_count`) in the batch with the correct `observationId` (root vs step). Known pre-existing fail on main: `test_scoring_groups` (integrity_pass) — not a regression from this work.
2. `pipeline-kit obs report` — new run-level numbers print next to the existing 15, no network.
3. Payload inspection around `build_otlp`: session id = `{workflow}:{slug}`, step spans carry the HANDOFF clip, `pipeline.skills` metadata present.

### Phase 2 — generate a real run

4. Scratch project: `pipeline-kit init --ide cursor` + `pipeline-kit obs install --ide cursor --adapter langfuse`; `LANGFUSE_*` keys in `.env` only (never config.json).
5. Run one micro/minor pipeline in Cursor with that folder as the **only workspace root** (hooks don't fire otherwise), through devops so HANDOFFs exist.
6. `pipeline-kit obs status` (keys detected, ledger rows > 0) → `pipeline-kit obs flush` → `{ok, events, steps, scores, traces}`; scores ≈ 15×steps + run-level.

### Phase 3 — Langfuse UI checks (one per change)

| Change | Verify |
|---|---|
| Session grouping | Sessions → one `{workflow}:{slug}` session holds parent + Task traces |
| Eval-ready step I/O | Trace → `pipeline.step ba-agent` → output has status + HANDOFF clip; metadata has `pipeline.skills`, `subagent_name` |
| Tags | Filter traces by `pack_id=pipeline-kit` and step-name tags |
| Run-level scores | Root observation → Scores: `task_complete`, `hitl_count`, `critic_retry_count`, `secret_leak_count` (source API) |
| Step scores intact | The 15 existing names still on step observations; values match `obs report` |
| Cost aggregation | Session sums tokens/$ across the run's traces; child Tasks may show 0 tokens (known Cursor gap — flag, don't fix) |

### Phase 4 — judges (after the LLM connection is set in Langfuse project settings)

7. `pipeline-kit eval judges sync` → Evaluators page shows judges + rules filtered by observation name `pipeline.step …`.
8. Batch eval `spec_completeness` on a ba-agent observation → score **and reasoning** land on that observation, not the trace. Debug failures via traces filtered by environment `langfuse-llm-as-a-judge`.

### Phase 5 — comparison smoke test (Starter 7 purpose)

9. Run the same prompt twice (micro vs minor workflow, or delete the tester HANDOFF on one run before flush) → dashboard with 7 widgets grouped by workflow tag: the broken run must show S1=0 and lower S2 while the good one is green. If both look identical, the metrics aren't discriminating — tighten the oracle regex.

### Failure modes to check deliberately

- Missing HANDOFF → `step_success=0`, `task_complete=0`, flush does not crash (fail-open).
- Aborted run (`stop=aborted`) → excluded from the S1 denominator; $ counted as failed-run spend.
- Missing `LANGFUSE_*` keys → flush errors and does **not** advance the offset; re-flush after fixing keys ships the same rows.
- Flush twice → deterministic score ids (`otel32(trace:step:name)`), no duplicates in Langfuse.

## Further considerations

1. Golden target app — a tiny public fixture app in-kit later; until then a throwaway app is the documented target. Do not bind oracles to a specific product repo.
2. Judge cost — sample 100% on golden, ~10% on live. Pin one judge model; changing it invalidates calibration.
3. Fair bake-off — same model tier and HITL policy per pack. Missing gate in a pack (e.g. no critic) → that metric is **N/A**, not a zero that inflates our win. Same rule for Layer E.
4. Child Task traces often report 0 tokens (Cursor) — cost per run is flagged incomplete rather than silently wrong.
5. Goodhart guard — every Starter 7 metric ships with its counter-metric on the same dashboard; watch trends and distributions, not lone absolutes.
