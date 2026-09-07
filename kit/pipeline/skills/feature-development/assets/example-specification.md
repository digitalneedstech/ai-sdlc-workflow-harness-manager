# Example specification (quality bar)

Owned by **feature-development**. Teaching example only. Match this **density and shape**, not this product. Do not copy wholesale into a live feature.

**What “good” looks like:** problem first, named actors, as-is vs to-be, testable FRs, error paths, labeled assumptions, explicit out of scope. Real-world density reference in this repo: `spec-operator-console.md` (problem, product model, IA, per-feature requirements).

---

# Activity journal for operator runs

**Status:** Ready for BA critic
**Slug:** `activity-journal`
**Created:** 2026-08-27
**Source request:** Persist every dispatched agent run so operators can review history and add notes
**Codebase grounded:** Yes (`web/` dashboard, SQLite `tasks` / `task_events`)

---

## 1. Problem

The Run console is ephemeral. After a task ends, operators cannot reopen prompt, status, or telemetry, and cannot attach notes. Comparing workers or debugging a failed run requires memory or ad-hoc logs.

## 2. Goals and non-goals

### Goals
- Durable journal of every dispatched task (prompt, status, telemetry).
- Operators can add notes on a past task.
- Run console stays the live surface; Activity is the history surface.

### Non-goals / out of scope
- Cross-host sync or cloud backup of the journal.
- Editing or deleting historical prompts.
- New engine protocol fields beyond existing task events.

## 3. Actors and context

| Actor | Goal | Constraints |
|-------|------|-------------|
| Operator | Find a past run and understand what happened | Local engine; one machine |
| Engine | Persist dispatch + events | Existing SQLite schema |

Environment: local Chorus operator console + engine.

## 4. Current behavior (as-is)

- Run feature streams a live task; history is not a first-class nav destination.
- Persistence already exists in SQLite (`tasks`, `task_events`) per implementation notes; UI does not treat Activity as the durable record.

## 5. Intended behavior (to-be)

### 5.1 Product model
A **task** has id, prompt, status, timestamps, telemetry events. An **operator note** is text attached to a task after the fact.

### 5.2 Primary user journeys
1. Operator opens Activity.
2. System lists past tasks (id, status, time).
3. Operator opens one task; system shows prompt, timeline, notes.
4. Operator adds a note; system persists it and shows it on reload.

### 5.3 Alternate and error journeys
- Empty journal: explicit empty state, shortcut to Run.
- Engine unreachable: error state, no fake rows.
- Note save fails: inline error; previous notes remain.

## 6. Functional requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | Activity lists persisted tasks newest-first | Must | Journey 1–2 |
| FR-2 | Task detail shows prompt, status, event timeline | Must | |
| FR-3 | Operator can PATCH a note onto a task | Must | |
| FR-4 | Run remains live-only; does not replace Activity | Must | |

## 7. User experience

- Nav: Activity in the left rail; deep link `#activity`.
- List + detail. Empty / loading / error / success for list, detail, and note save.
- Copy: “No runs yet” + action to open Run.

## 8. Data and integrations

- Read `tasks` / `task_events`; write operator notes only.
- Never log secrets from prompts in new telemetry sinks; do not display tokens.

## 9. Non-functional requirements

- **Security:** same localhost auth as the rest of the console.
- **Reliability:** list/detail fail closed (error, not empty-success).
- **Performance:** list of recent tasks; no requirement to load full telemetry until detail.
- **Observability:** existing task events are the source of truth.

## 10. Acceptance criteria

- [ ] AC-1: Given at least one dispatched task, When operator opens Activity, Then the task appears with status and time (FR-1)
- [ ] AC-2: Given a listed task, When operator opens it, Then prompt and timeline are visible (FR-2)
- [ ] AC-3: Given a task detail, When operator saves a note and reloads, Then the note is still there (FR-3)
- [ ] AC-4: Given engine down, When operator opens Activity, Then an error is shown, not an empty success list (FR-1)

## 11. Assumptions

| ID | Assumption | Default chosen | Impact if wrong |
|----|------------|----------------|-----------------|
| A-1 | SQLite already stores tasks/events | Reuse; UI is the gap | Need a persistence FR |
| A-2 | Notes are plain text, no markdown preview | Plain textarea | Extra UX work |

## 12. Open questions

none

## 13. Traceability

- “Persist runs + notes” → FR-1–3, AC-1–3
- Cloud backup explicitly out of scope

## 14. Ready for critic

- [x] Required sections filled
- [x] Assumptions labeled
- [x] ACs testable
- [x] Out of scope written
