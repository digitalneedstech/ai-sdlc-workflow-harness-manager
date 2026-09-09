---
name: observability-telemetry
description: >-
  Invoke when writing or reviewing product/engine telemetry, analytics events,
  or the telemetry-agent step. Ensures events answer a spec business question,
  stay PII-safe, and reuse existing loggers. Do not add third-party analytics
  pixels unless a Must FR names them.
---

# Observability (business-correct telemetry)

| Attribute | Value |
|-----------|--------|
| Type | Skill |
| Audience | The named agent, or the parent when this file is on the allowlist |
| Adapt | Change commands or paths only in deploy and testing skills. Planning skills stay product-neutral. |

**Goal:** emit **few** events that a product or operator decision can use. Wrong or PII-laden events are worse than none.

**Progressive load:** this file first, then [assets/telemetry-contract-template.md](assets/telemetry-contract-template.md) when drafting the contract.

## How events are extracted (mandatory)

Do **not** brainstorm a dashboard. Pull candidates from the **approved spec only**, then **drop** anything that fails a gate. Reliability comes from rejection, not from adding more events.

### S1 — Candidate sources (only these)

Walk the spec in this order. Each candidate is a **terminal or branching outcome**, not a keystroke.

| Source | What may become a candidate | What must not |
|--------|-----------------------------|---------------|
| §2 Goals | A measurable outcome the increment claims | Vague “improve engagement” |
| §5.2 Primary journeys | Last step of a journey, or a named money/auth/submit | Every screen view in the journey |
| §5.3 Error journeys | **Enum-able** failure the spec already names (unauthorized, validation, timeout) | Raw exception text, unknown errors |
| §6 Must FRs | State change the FR requires the system to record or complete | Should/Could FRs unless they are the only observability ask |
| §10 ACs | Given/When/Then whose **Then** is observable without opening DevTools | ACs that are purely visual copy |
| §9 Observability | Only if it names *who* looks and *what they do* | “Add logging” with no consumer |

If a line is not in that table, it is **not** a candidate.

### S2 — Turn a candidate into a proposed event

One candidate → at most **one** event.

- **When:** the user/system action from the journey/AC (single tense, one actor).
- **Name:** `{object}_{past_verb}` from spec language (`checkout_started`, `note_saved`, `health_check_failed`) — not `click_button_3`.
- **Properties:** only fields the spec already treats as **structured** (counts, booleans, closed enums from the FR). If the spec does not name the field, omit it.

Cap: **≤ 5 events** per increment unless a Must FR explicitly requires a funnel of more steps. Prefer 0–2.

### S3 — Reliability gates (all must pass)

Run **in order**. First failure drops the candidate. Record the drop reason in **Explicitly out of scope** (so the developer does not re-add it).

| # | Gate | Pass | Fail (drop) |
|---|------|------|-------------|
| G1 | **Consumer** | Named role (PM / operator / SRE) **and** a concrete action (“page if error_rate > X”, “drop the feature if start→finish < N%”) | “Might be interesting later” |
| G2 | **Spec link** | FR-id or AC-id | Goal-only or invented KPI |
| G3 | **Countable** | Can be counted or rate-limited without NLP (ints, bools, enums) | Needs parsing free text or screenshots |
| G4 | **PII** | No email, name, address, tokens, prompts, user-typed titles | Any of those as a property |
| G5 | **Cardinality** | Property domain is small/closed **or** omitted | User id / session id as a *metric label* |
| G6 | **Transport** | Fits the logging or analytics API already in this repository | Needs a new vendor SDK unless a Must FR names it |
| G7 | **Idempotent When** | Same user action will not spam unbounded duplicates *unless* the FR is “count attempts” | `mousemove`, `page_view` every route |

**Reliable enough** = G1–G7 all pass **and** a second person (developer critic) can replay: *action in AC → event name → properties ⊆ allowlist*.

If **zero** candidates pass: `EVENTS: none`. That is SUCCESS. Do not lower the gates.

### S4 — Business-value test (surviving events only)

Keep the event only if the contract row can fill:

1. **Decision** — who acts and what they would change
2. **Spec link** — FR or AC
3. **Stable name**
4. **Allowlisted properties** with types/enums

### S5 — Write the contract

Use the template. Every kept event has BQ-id + FR/AC. Dropped candidates appear under out of scope with the **gate id** (G1…G7).


## Correctness rules

- **Allowlist over dump.** If a property is not in the contract, do not send it.
- **No PII:** email, name, address, cart line titles that are user-typed, tokens, passwords, raw prompts, full URLs with secrets.
- **No high-cardinality labels** as metric tags (user id, session id as metric labels). IDs may be in structured logs only if hashed or truncated per existing logging rules.
- **Reuse** the repository’s current logger or analytics helper. Do not add a new vendor SDK unless a Must FR names it.
- **Failures:** log `error_code` enums, not exception messages that leak internals.
- **N/A is valid.** If this increment has no operator or product question that telemetry answers, the contract is explicit `EVENTS: none` — still write the file.

## Pipeline

`telemetry-agent` (after BA critic, **before** developer) writes `features/{slug}/telemetry-contract.md`. Developer implements only those events. Developer critic and tester trace them. Do not invent extra events in code.
