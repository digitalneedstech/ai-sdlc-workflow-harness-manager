---
title: App telemetry vs agent observability
description: telemetry-agent extracts product events from the spec. obs traces the coding agent. Keep them separate.
---

Two features share English words. They are different products.

| | Agent-run observability | App telemetry |
|--|-------------------------|---------------|
| CLI / flag | `pipeline-kit obs …` | `pipeline-kit features enable telemetry` or `RUN_TELEMETRY: true` |
| Specialist | none (hooks + scorer) | `telemetry-agent` |
| Question it answers | Did the *agent* waste tools, miss the allowlist, skip verify? | Which *product* events does this feature owe, if any? |
| Output | JSONL ledger, Langfuse traces and scores | `features/{slug}/telemetry-contract.md` |
| Default | Off until `obs install` | Off. Feature waves stub `EVENTS: none` |

## App telemetry rules

Events are **extracted from the spec** and gated — not brainstormed.

- Candidates only from goals, journey endings, named errors, Must FRs, ACs, and a section that names a consumer.
- Reliability gates G1–G7. Cap ≤ 5 events.
- Zero passing gates → `EVENTS: none` (that is SUCCESS).
- Do not emit properties off the allowlist.
- Do not add a vendor pixel unless a Must FR names the vendor.
- Do not use user id as a metric label. Do not log emails, passwords, or secrets.

Micro/minor always stub telemetry. Default feature waves skip `telemetry-agent` unless you opt in.

Wrong events are worse than none.
