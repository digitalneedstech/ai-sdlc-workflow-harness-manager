# Clarify-first (planning agents)

Owned by **feature-development**. PM (P3), Architect (A2), and BA (S3) follow this
file. Do not invent product or technical decisions. Mine prior artifacts first,
then ask the user every remaining decision on the coverage checklist.

Silent `ASSUMPTIONS_USED` is the exception, not the default.

## Lookup then ask

```text
READ ARTIFACTS → APPEND decisions.md → LIST GAPS → ASK USER (if any) → DRAFT
```

1. Read every file in your lookup table that exists on disk, then the repo.
2. Append extracted facts to `features/{slug}/decisions.md` (load
   [decisions-template.md](decisions-template.md) if the file is missing).
3. Walk your coverage checklist. A row already in `decisions.md` or answered
   in `questions.md` is **not** a question.
4. Remaining Unknowns that change scope, actors, success, journeys, data,
   APIs, authz, child split, or testability: write `questions.md`, HANDOFF
   `BLOCKED`, **stop**. Do not draft a fake-complete plan, architecture, or spec.
5. Draft only when the checklist is answered on disk, the leftover is
   cosmetic (copy, density), or the user said “proceed” / “use defaults”.

Never ask what the **repo** already answers. Never re-ask a decision already
recorded in `decisions.md` or `questions.md`.

## Lookup tables

| Agent | Must read before asking |
|-------|-------------------------|
| PM | `USER_REQUEST`, `route.md`, existing `plan.md` / `research.md` / `questions.md` / `decisions.md` on a re-run, `intake.md` if present, repo facts from P2 |
| Architect | Signed-off `plan.md` or `intake.md` / `epic-plan.md`, `research.md`, `HANDOFF-pm.md`, `questions.md`, `decisions.md`, `signoff-requirements.md`, repo |
| BA | All of the above plus `architecture.md`, `implementation-plan.md`, `HANDOFF-architect.md`, architect questions, `signoff-architect.md` (when Architect ran) |

## Coverage checklists (ask if not already decided)

**PM**

- Actors and who may act
- Success criteria
- In / out of scope
- Primary journeys
- MVP vs later
- Authz / PII / money / irreversible actions
- Child-spec split
- Edge cases that change product meaning

**Architect**

- Module boundaries
- Data ownership
- APIs and contracts
- Persistence
- Authz model
- Integrations / vendors
- NFRs that change design (latency, volume, offline)
- Technical child-spec split
- Failure modes

**BA**

- Remaining acceptance criteria
- Empty / loading / error states
- Acceptance edges
- Testability (how a tester would fail the AC)
- Anything architecture left open

## Caps and batches

| Agent | Max questions per batch |
|-------|-------------------------|
| PM | 20 |
| Architect | 15 |
| BA | 15 |

One batch per turn. A **second** batch is allowed only if answers create new
Unknowns. Format: [questions-format.md](questions-format.md).

## When to use ASSUMPTIONS_USED

Only when the user said “proceed” / “use defaults”, or every leftover is
non-blocking (copy, density, cosmetic). Label each default in the plan, spec
§11, or architecture ADRs. Otherwise HANDOFF `BLOCKED`.
