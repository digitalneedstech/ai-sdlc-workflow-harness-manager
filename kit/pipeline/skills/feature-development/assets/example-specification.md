# Example specification (quality bar)

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Match this **density and shape**, not this story. Do not copy it into a live feature. |

Owned by **feature-development**. Teaching example only.

**What “good” looks like:** problem first, named actors, as-is vs to-be, testable
FRs, error paths, labeled assumptions, explicit out of scope.

---

# Change history for operators

**Status:** Ready for BA critic
**Slug:** `change-history`
**Created:** 2026-01-15
**Source request:** Persist every completed change so operators can review history and add notes
**Codebase grounded:** Yes (existing operations UI and persistence for live work)

---

## 1. Problem

The live operations view is ephemeral. After a change completes, operators
cannot reopen the request, status, or event timeline, and cannot attach notes.
Comparing workers or debugging a failed change requires memory or ad-hoc logs.

## 2. Goals and non-goals

### Goals
- Durable journal of every completed change (request, status, events).
- Operators can add notes on a past change.
- The live view stays the working surface; History is the record surface.

### Non-goals / out of scope
- Cross-region sync or cloud backup of the journal.
- Editing or deleting historical requests.
- New protocol fields beyond existing change events.

## 3. Actors and context

| Actor | Goal | Constraints |
|-------|------|-------------|
| Operator | Find a past change and understand what happened | Local or single-tenant console |
| Platform | Persist dispatch and events | Existing store already used by the live view |

Environment: the operations console already in this repository.

## 4. Current behavior (as-is)

- The live view streams a current change; history is not a first-class
  navigation destination.
- Persistence already exists for live work; the UI does not treat History as
  the durable record.

## 5. Intended behavior (to-be)

### 5.1 Product model
A **change** has id, request text, status, timestamps, and events. An
**operator note** is text attached to a change after the fact.

### 5.2 Primary user journeys
1. Operator opens History.
2. System lists past changes (id, status, time).
3. Operator opens one change; system shows request, timeline, notes.
4. Operator adds a note; system persists it and shows it on reload.

### 5.3 Alternate and error journeys
- Empty journal: explicit empty state, shortcut to the live view.
- Platform unreachable: error state, no fake rows.
- Note save fails: inline error; previous notes remain.

## 6. Functional requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | History lists persisted changes newest-first | Must | Journey 1–2 |
| FR-2 | Change detail shows request, status, event timeline | Must | |
| FR-3 | Operator can save a note onto a change | Must | |
| FR-4 | Live view remains live-only; does not replace History | Must | |

## 7. User experience

- Navigation: History in the primary nav; deep link supported.
- List + detail. Empty / loading / error / success for list, detail, and note save.
- Copy: “No changes yet” + action to open the live view.

## 8. Data and integrations

- Read the existing change and event records; write operator notes only.
- Never log secrets from requests in new telemetry sinks; do not display tokens.

## 9. Non-functional requirements

- **Security:** same authentication as the rest of the console.
- **Reliability:** list/detail fail closed (error, not empty-success).
- **Performance:** list of recent changes; no requirement to load full telemetry until detail.
- **Observability:** existing change events are the source of truth.

## 10. Acceptance criteria

- [ ] AC-1: Given at least one completed change, When the operator opens History, Then the change appears with status and time (FR-1)
- [ ] AC-2: Given a listed change, When the operator opens it, Then request and timeline are visible (FR-2)
- [ ] AC-3: Given a change detail, When the operator saves a note and reloads, Then the note is still there (FR-3)
- [ ] AC-4: Given the platform is down, When the operator opens History, Then an error is shown, not an empty success list (FR-1)

## 11. Assumptions

| ID | Assumption | Default chosen | Impact if wrong |
|----|------------|----------------|-----------------|
| A-1 | The existing store already keeps change events | Reuse; UI is the gap | Need a persistence FR |
| A-2 | Notes are plain text, no rich preview | Plain textarea | Extra UX work |

## 12. Open questions

none

## 13. Traceability

- “Persist changes + notes” → FR-1–3, AC-1–3
- Off-site backup explicitly out of scope

## 14. Ready for critic

- [x] Required sections filled
- [x] Assumptions labeled
- [x] ACs testable
- [x] Out of scope written
