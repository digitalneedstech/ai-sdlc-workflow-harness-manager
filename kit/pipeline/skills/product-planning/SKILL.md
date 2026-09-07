---
name: product-planning
description: >-
  Invoke when the feature-development parent (or product-manager-agent) must
  turn a feature-class ask into a stable plan.md before BA writes specs.
  Research, brainstorm, and ask only blocking questions. Do not use for
  micro/minor, coding, or UI-only redesign.
---

# Product planning (autonomous PM loop)

Turn a feature-class request into one on-disk plan BA can split into child specifications.

**Parent:** spawn PM as a separate `Task`. **PM:** write plan + research + HANDOFF, then return. **Do not** write `specification.md`, implement code, or spawn BA.

**Success:** `features/{slug}/plan.md` is complete, child-spec split is stable, assumptions labeled.  
**Failure:** chat-only plan, silent invention, open Must questions, or invented market facts with no citation.

**Progressive loading:** follow P1–P6 first. Templates are owned by **feature-development** — read them only at the step that names them.

| When | Read (feature-development) |
|------|------|
| P3 (interactive questions) | [../feature-development/assets/questions-format.md](../feature-development/assets/questions-format.md) |
| P2 (research) | [../feature-development/assets/research-template.md](../feature-development/assets/research-template.md) |
| P4 (plan) | [../feature-development/assets/plan-template.md](../feature-development/assets/plan-template.md) |
| P6 (handoff) | [../feature-development/assets/handoff-pm-template.md](../feature-development/assets/handoff-pm-template.md) |

---

## Roles and outputs

| Role | Allowed |
|------|---------|
| Parent | Create `features/{slug}/`, `Task` PM, then BA |
| PM (this skill) | Explore repo, web search, bounded questions, write plan + research + HANDOFF |
| BA | Later `Task` only |

```text
features/{slug}/
  plan.md
  research.md
  questions.md     # if P3 ran
  HANDOFF-pm.md
```

Reuse `{slug}` if the folder exists; update the plan, do not fork a second one.

---

## Steps (do not skip; no product code)

`P1 DISCOVER → P2 RESEARCH → P3 CLARIFY? → P4 PLAN → P5 SELF-GATE → P6 HANDOFF`

**P1 Discover + brainstorm** — Restate intent. Scan the repo enough to know what already exists (routes, APIs, nearby features). List 2–4 product options and why one is preferred. Greenfield: say so.

**P2 Research** — Load the research template. Gather **cited** facts:

- Repo: path + fact (required).
- Web: comparable products, UX conventions, or domain facts that change the plan. Use web search. Quote a URL per claim. If nothing useful is found, write `none — {why}` and continue.
- Do not invent market or competitor claims.

**P3 Clarify** — Ask **only** when an unknown would change scope, actors, success criteria, in/out of scope, authz/PII/money, or the child-spec split.

- One batch, **max 10**, multiple-choice with a recommended default. Format: questions asset (PM may exceed BA’s 7).
- Never ask what the repo already answers.
- Do **not** interrogate a clear, simple feature-class ask. Prefer labeled defaults.
- Interactive + blocking: write `questions.md`, **stop**, wait for answers or “proceed”.
- Non-interactive: apply documented defaults, continue P4, HANDOFF `ASSUMPTIONS_USED`.

**P4 Plan** — Load the plan template. Fill every section. Propose child specs (kebab slugs + one-line job). One child is valid. “Ready for BA” only when the split is stable.

**P5 Self-gate** — All **blockers** below must pass. Else fix or return to P3. Never HANDOFF `SUCCESS` on a failing plan.

**P6 Handoff** — Load the PM handoff template. Write `HANDOFF-pm.md`. Stop. Parent next: BA.

---

## Failure handling (mandatory)

| Situation | Action | HANDOFF |
|-----------|--------|---------|
| Interactive + blocking Unknown | Questions on disk; do not draft a fake-complete plan | `BLOCKED`, `ready_for_ba: false` |
| Non-interactive / user said proceed | Defaults labeled in the plan | `ASSUMPTIONS_USED` |
| P5 blocker fails | Fix plan or return to P3 | stay in P4/P5 or `BLOCKED` |
| Unsafe, illegal, or missing actor/scope that cannot be defaulted | Stop | `BLOCKED` + what parent should do |
| Web search fails | Continue with repo facts; label gaps | continue |

---

## P5 blockers (all required)

- [ ] `features/{slug}/plan.md` on disk
- [ ] `features/{slug}/research.md` on disk (may say no useful web facts)
- [ ] Problem, who it is for, success criteria, non-goals present
- [ ] Proposed child specs listed (at least one kebab slug)
- [ ] Assumptions labeled; no silent auth, payments, or retention invention
- [ ] As-is is factual (paths or explicit greenfield)
- [ ] No product file edits outside `features/{slug}/`

---

## Handoff statuses (mandatory)

| status | Meaning |
|--------|---------|
| `SUCCESS` | Blockers pass; BA may run |
| `ASSUMPTIONS_USED` | Defaults used; BA and BA critic must test them |
| `BLOCKED` | Wait, unsafe, or incomplete; include recovery for parent |

---

## Anti-patterns

Chat-only plan · asking the repo · interrogating a clear ask · inventing competitors · writing `specification.md` · spawning BA from PM · Ready with blocking open questions.
