---
name: product-planning
description: >-
  Invoke when the feature-development parent (or product-manager-agent) must
  turn a feature-class ask into a stable plan.md before Architect or BA.
  Research, mine prior artifacts, then ask remaining product decisions. Do
  not use for micro/minor, coding, or UI-only redesign.
---

# Product planning (autonomous PM loop)

Turn a feature-class request into one on-disk plan Architect and BA can use
without inventing scope.

**Parent:** spawn PM as a separate `Task`. **PM:** write plan + research +
decisions + HANDOFF, then return. **Do not** write `specification.md`,
implement code, or spawn Architect or BA.

**Success:** `features/{slug}/plan.md` is complete, child-spec split is stable,
`decisions.md` is updated, leftover Unknowns are cosmetic or user-approved.  
**Failure:** chat-only plan, silent invention, open Must questions, or invented
market facts with no citation.

**Progressive loading:** follow P1–P6 first. Templates are owned by
**feature-development** — read them only at the step that names them.

| When | Read (feature-development) |
|------|------|
| P1 / P3 (clarify-first) | [../feature-development/assets/clarify-first.md](../feature-development/assets/clarify-first.md), [../feature-development/assets/decisions-template.md](../feature-development/assets/decisions-template.md) |
| P3 (interactive questions) | [../feature-development/assets/questions-format.md](../feature-development/assets/questions-format.md) |
| P2 (research) | [../feature-development/assets/research-template.md](../feature-development/assets/research-template.md) |
| P4 (plan) | [../feature-development/assets/plan-template.md](../feature-development/assets/plan-template.md) |
| P6 (handoff) | [../feature-development/assets/handoff-pm-template.md](../feature-development/assets/handoff-pm-template.md) |

---

## Roles and outputs

| Role | Allowed |
|------|---------|
| Parent | Create `features/{slug}/`, `Task` PM, then `@signoff:requirements` |
| PM (this skill) | Explore repo, web search, clarify-first questions, write plan + research + decisions + HANDOFF |
| Architect / BA | Later `Task` only |

```text
features/{slug}/
  plan.md
  research.md
  decisions.md
  questions.md     # if P3 ran
  HANDOFF-pm.md
```

Reuse `{slug}` if the folder exists; update the plan, do not fork a second one.

---

## Steps (do not skip; no product code)

`P1 DISCOVER → P2 RESEARCH → P3 CLARIFY → P4 PLAN → P5 SELF-GATE → P6 HANDOFF`

**P1 Discover + brainstorm** — Restate intent. Scan the repo enough to know
what already exists (routes, APIs, nearby features). List 2–4 product options
and why one is preferred. Greenfield: say so. Load
[clarify-first.md](../feature-development/assets/clarify-first.md). Append
facts from `USER_REQUEST`, `route.md`, `intake.md` (if present), and any
existing plan/questions to `decisions.md`.

**P2 Research** — Load the research template. Gather **cited** facts:

- Repo: path + fact (required).
- Web: comparable products, UX conventions, or domain facts that change the plan. Use web search. Quote a URL per claim. If nothing useful is found, write `none — {why}` and continue.
- Do not invent market or competitor claims.

**P3 Clarify** — Follow clarify-first. Run the **PM** coverage checklist. Ask
every remaining decision. Do not prefer silent defaults.

- One batch, **max 20**, multiple-choice with a recommended default. Format: questions asset.
- Never ask what the repo or a prior artifact already answers.
- Interactive + remaining Unknowns: write `questions.md`, **stop**, wait for answers or “proceed”.
- `ASSUMPTIONS_USED` only when the user said proceed / use defaults, or leftovers are cosmetic.

**P4 Plan** — Load the plan template. Fill every section. Propose child specs
(kebab slugs + one-line job). One child is valid. “Ready for BA” only when
the split is stable. Parent next is **sign-off**, then Architect (or BA if
`skip_architect`).

**P5 Self-gate** — All **blockers** below must pass. Else fix or return to P3.
Never HANDOFF `SUCCESS` on a failing plan.

**P6 Handoff** — Load the PM handoff template. Write `HANDOFF-pm.md`. Stop.
Parent next: `@signoff:requirements`.

---

## Failure handling (mandatory)

| Situation | Action | HANDOFF |
|-----------|--------|---------|
| Interactive + Unknown on PM checklist | Questions on disk; do not draft a fake-complete plan | `BLOCKED`, `ready_for_ba: false` |
| User said proceed / leftovers cosmetic | Defaults labeled in the plan | `ASSUMPTIONS_USED` |
| P5 blocker fails | Fix plan or return to P3 | stay in P4/P5 or `BLOCKED` |
| Unsafe, illegal, or missing actor/scope that cannot be defaulted | Stop | `BLOCKED` + what parent should do |
| Web search fails | Continue with repo facts; label gaps | continue |

---

## P5 blockers (all required)

- [ ] `features/{slug}/plan.md` on disk
- [ ] `features/{slug}/research.md` on disk (may say no useful web facts)
- [ ] `features/{slug}/decisions.md` on disk
- [ ] Problem, who it is for, success criteria, non-goals present
- [ ] Proposed child specs listed (at least one kebab slug)
- [ ] Assumptions labeled; no silent auth, payments, or retention invention
- [ ] As-is is factual (paths or explicit greenfield)
- [ ] No product file edits outside `features/{slug}/`

---

## Handoff statuses (mandatory)

| status | Meaning |
|--------|---------|
| `SUCCESS` | Blockers pass; parent may request requirements sign-off |
| `ASSUMPTIONS_USED` | Defaults used; Architect, BA, and BA critic must test them |
| `BLOCKED` | Wait, unsafe, or incomplete; include recovery for parent |

---

## Anti-patterns

Chat-only plan · asking the repo · silent defaults on Must decisions · inventing
competitors · writing `specification.md` · spawning Architect or BA from PM ·
Ready with blocking open questions.
