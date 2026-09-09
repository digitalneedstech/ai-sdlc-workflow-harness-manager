---
name: bug-fix
description: >-
  Invoke on the bug workflow: the orchestrator resolved a tracker issue to a
  defect, or the user reported broken behavior in existing code. Two roles read
  this file — bug-analyst-agent runs B1–B6 to produce rca.md, and
  developer-agent implements only the approved fix plus its regression test.
  Not for new features (use feature-development) or UI redesign.
---

# Bug fix (analysis then repair)

| Attribute | Value |
|-----------|--------|
| Type | Skill |
| Audience | The named agent, or the parent when this file is on the allowlist |
| Adapt | Change commands or paths only in deploy and testing skills. Planning skills stay product-neutral. |

A defect is not a small feature. There is no plan and no specification: the **root cause on disk** is the requirement. Analysis and repair run in **separate Tasks** so the person who formed the theory is not the person grading their own fix.

`intake-agent → bug-analyst-agent (B1–B6) → developer-agent (B7) → developer-critic-agent → tester-agent → devops-agent → retro-agent`

**Success:** a named code-level cause with file evidence, a fix that removes that cause, and a regression test that fails before the fix and passes after.
**Failure:** a symptom patch, a defensive `try`/`catch` around the crash, a widened type, or a test weakened until it passes.

| When | Read |
|------|------|
| B6 (write the analysis) | [assets/rca-template.md](assets/rca-template.md) |
| B7 (implement) | [`../secure-implementation/SKILL.md`](../secure-implementation/SKILL.md) |

Retry cap and gates come from [`.pipeline/config.json`](../../config.json). No repo, app, host, or port names belong in this file — the analyst discovers the tree from `REPO_ROOT`.

---

## Analyst steps (bug-analyst-agent, read-only)

`B1 SYMPTOM → B2 REPRODUCE → B3 LOCALIZE → B4 ROOT CAUSE → B5 BLAST RADIUS → B6 FIX PLAN`

### B1 Symptom

From `features/{slug}/intake.md` (or the user's report), state **expected vs actual** in one line each, plus the trigger conditions. If expected behavior is not written anywhere, derive it from the code's own contract (tests, types, docs, neighboring call sites) and label it as derived — do not invent a product rule.

### B2 Reproduce

Establish a deterministic reproduction before touching any theory.

- Prefer the cheapest layer that shows the defect: a unit or API call over a browser run.
- Record the exact command, input, and observed output. "It fails sometimes" is not a reproduction.
- Read logs and stack traces fully; the first frame in your code matters more than the top frame.
- No reproduction after a genuine attempt ⇒ `BLOCKED` naming exactly what you need (build, env, account state, data). **Never** hand an unreproduced bug to the developer.

Non-deterministic defects (timing, ordering, caching) still need a reproduction: state the conditions that make it likely and how often it triggered.

### B3 Localize

Narrow from symptom to code with evidence, not intuition.

1. Trace the data path from the entry point to the failure. Record `path:line` for each hop.
2. List candidate causes and **rank** them. Each candidate carries the evidence for it and the evidence against.
3. Eliminate candidates by reading the code or by running the reproduction with a probe — not by preference.
4. Check history for the introducing change when the defect is a regression (read-only inspection; no commits, no checkouts).

Every claim in the analysis must point at a real `path:line`. If you cannot cite it, you have not localized it.

### B4 Root cause

One sentence naming the **code-level** cause, plus proof that it produces the symptom.

Depth test — the statement fails if it is any of these:

| Not a root cause | Why |
|------------------|-----|
| "Validation is missing" | Where, on which value, and why does absence produce *this* symptom? |
| "The API returns the wrong data" | That is the symptom one layer down. Keep going. |
| "A race condition" | Which two operations, on which shared state, in which order? |
| "Bad input" | Why does bad input reach this line, and which contract should have stopped it? |

Ask why until the next answer would be outside the codebase (a third-party contract, a product decision, or a data state). Record the chain. When the true cause is outside the repo, say so and describe the correct local defense.

### B5 Blast radius

- Every other caller of the faulty code path, with `path:line`.
- Other inputs or flows that hit the same cause — those are part of this bug, not a follow-up.
- What the fix could break: shared helpers, persisted data shape, public behavior others rely on.
- Whether existing tests cover the path at all, and why they did not catch it.

### B6 Fix plan

Load [assets/rca-template.md](assets/rca-template.md) and write `features/{slug}/rca.md`.

Offer at least two options — typically the **minimal** fix and the **correct** fix — with cost and risk, then recommend one. Recommend minimal only when the correct fix is genuinely out of scope, and say what remains unfixed.

The plan must name:

- Exact files and functions to change, and the change in one line each.
- The **regression case**: layer, what it asserts, and why it fails today. This is mandatory; a bug fix without a test that would have caught it is not done.
- Anything explicitly out of scope (other defects found along the way go to the parent as findings, not into this fix).

Stop after B6. You do not edit product code.

---

## Developer step (developer-agent, B7)

`RCA_PATH` replaces `SPEC_PATH`. The recommended option in `rca.md` is the requirement.

1. Write the regression test **first** and watch it fail for the stated reason. If it passes before the fix, the analysis is wrong — HANDOFF `BLOCKED` rather than adjusting the test until it fails.
2. Implement the recommended option only. A different option needs a `BLOCKED` and the parent's decision.
3. Cover every caller listed in blast radius that shares the cause.
4. Run the regression test plus the existing suite for the touched area.
5. Fill `features/{slug}/security-preflight.md` per [`../secure-implementation/SKILL.md`](../secure-implementation/SKILL.md) — defects in validation, authz, or error handling are security-adjacent by default.
6. Write `features/{slug}/implementation-notes.md` and HANDOFF.

**Forbidden repairs:** swallowing the error, catching around the crash without removing the cause, loosening a type or schema to accept bad data, deleting or skipping the failing assertion, widening a permission, or "fixing" by disabling the feature. If the real fix is bigger than the class allows, HANDOFF `BLOCKED` and let the parent reclassify.

---

## Outputs

```text
features/{slug}/rca.md                     # analyst
features/{slug}/HANDOFF-bug-analyst.md     # analyst
{product files}                            # developer — fix + regression test
features/{slug}/security-preflight.md      # developer
features/{slug}/implementation-notes.md    # developer
features/{slug}/HANDOFF-developer.md       # developer
```

## Self-gate before HANDOFF (analyst)

- [ ] Reproduction is deterministic and written as a runnable command or numbered steps
- [ ] Root cause names a specific `path:line` and passes the depth test
- [ ] Why-chain recorded down to the last in-repo answer
- [ ] Every other caller of the faulty path listed, or "none — checked {how}"
- [ ] At least two options with a recommendation and its trade-off
- [ ] Regression case named with layer and assertion
- [ ] No product file changed

## Failure handling

| Situation | HANDOFF |
|-----------|---------|
| Cannot reproduce | `BLOCKED` — name what is missing; parent asks the user |
| Symptom real but cause is in a dependency | `SUCCESS` with the local defense as the recommendation, and the upstream issue named |
| Fix needs a new screen, API, or data model | `BLOCKED` — parent reclassifies to the feature workflow |
| Intake or report missing | `FAILED` `INPUT_MISSING` |
| Regression test passes before the fix | `BLOCKED` — re-run the analyst; do not weaken the test |
| Analyst edited product code | Forbidden — discard and redo read-only |

## Anti-patterns

Fixing before reproducing · a cause with no `path:line` · "defensive" try/catch as the fix · touching one caller when three share the cause · rewriting the module while you are in there · shipping without a regression test · the analyst and the fixer in one Task · pasting stack traces with tokens or customer data into `rca.md`.
