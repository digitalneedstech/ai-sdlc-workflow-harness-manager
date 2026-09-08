---
name: feature-development-skill
description: >-
  Invoke this skill when the user wants product work done in this repo.
  Typical user messages are short: “work on …”, “fix …”, “change …”,
  “add a button …”, “develop …”. Do not wait for CHANGE_CLASS, FEATURE_SLUG,
  or a long prompt. Parent classifies micro | minor | feature, then
  orchestrates the matching Task chain. Feature ladder: PM → user sign-off →
  Architect (when large) → user sign-off → BA → BA critic → user sign-off →
  waved telemetry/developer/critic → one tester → devops → retro.
---

# Feature development (parent workflow)

**Entry point:** [orchestration/SKILL.md](../orchestration/SKILL.md) picks the workflow first. This file is the **text-sourced** one. A tracker key routes to `jira-story`, `jira-epic` (both reuse the ladder below with intake in front of Architect/BA and PM skipped) or `jira-bug` ([bug-fix/SKILL.md](../bug-fix/SKILL.md)). Chains and skips live in [`.pipeline/config.json`](../../config.json).

Spawn **one agent per step in a new `Task` (separate context window)**. Classify **first** ([assets/change-routing.md](assets/change-routing.md)): **micro** / **minor** skip PM–BA–telemetry; **tester** follows [assets/tester-policy.md](assets/tester-policy.md). **feature** runs the planning ladder with sequential user sign-off. The subagent does **not** see this parent chat. Inject a **self-contained** prompt ([assets/parent-task-prompt.md](assets/parent-task-prompt.md)). Do **not** auto-continue after PM, Architect, or BA SUCCESS — wait for `@signoff:*`.

**PIPELINE_COMPLETE** only after **devops** `OVERALL=passed` **and** **retro-agent** has run (`SUCCESS` or `NO_NEW_PAGE`).

## Route before any specialist (parent-only)

1. Load [assets/change-routing.md](assets/change-routing.md).
2. Set `change_class` (`micro` | `minor` | `feature`). **Default `feature`** if any hard-upgrade trigger matches or the ask is unclear.
3. Load [assets/tester-policy.md](assets/tester-policy.md). Set `skip_tester` from `run_tester` for that class, unless the user typed `RUN_TESTER: true|false`.
4. Write `features/{slug}/route.md` (and `patch.md` for micro/minor). Seed `skip_architect: true` for micro/minor. On feature class, set it after requirements exist using [assets/architect-policy.md](assets/architect-policy.md) (or `RUN_ARCHITECT: true|false`).
5. Spawn **only** the chain for that class. Do not run the full PM/Architect/BA ladder for a label change.

| Class | Task chain |
|-------|------------|
| **micro** | `developer-agent` → (`tester-agent` if policy on) → `devops-agent` → `retro-agent` |
| **minor** | `developer-agent` → `developer-critic-agent` → (`tester-agent` if policy on) → `devops-agent` → `retro-agent` |
| **feature** | `product-manager-agent` → `@signoff:requirements` → `architect-agent`? → `@signoff:architect` → `ba-agent` → `ba-critic-agent` → `@signoff:ba` → **waves** (`telemetry-agent` → `developer-agent` → `developer-critic-agent` per child) → `tester-agent` (unless policy off) → `devops-agent` → `retro-agent` |

## Context isolation (mandatory — by complexity)

A `Task` subagent is a **fresh context**. Required for every specialist below. Do not do that work in the parent to “save a turn.”

| Agent | Complexity | Why a separate window | Inline in parent? |
|-------|------------|----------------------|-------------------|
| `product-manager-agent` | **High** | Research + plan + questions | **No** |
| `architect-agent` | **High** | Challenge + diagrams + implementation plan | **No** |
| `ba-agent` | **High** | Child specs + order + test plan | **No** |
| `ba-critic-agent` | **High (independence)** | Must not share the author’s reasoning | **No** — never same Task as BA |
| `telemetry-agent` | **Medium** | Allowlist must not inherit BA extras or later code dumps | **No** — never same Task as BA or developer |
| `developer-agent` | **Highest** (feature) / **Low–medium** (micro) | Still product edits | **No** — never inline |
| `developer-critic-agent` | **High (independence)** | Fresh read of diff vs spec | **No** — never same Task as developer |
| `tester-agent` | **High** | Feature-level Playwright + layers | **No** — never same Task as devops |
| `devops-agent` | **Medium–high** | Build/preview logs would drown the parent | **No** |
| `retro-agent` | **Medium** | Learning must not mix with deploy logs | **No** — after devops only |
| `intake-agent` | **Medium** | Raw issue payload + MCP discovery | **No** — parent never calls tracker MCP |
| `bug-analyst-agent` | **High (independence)** | Deep tracing; theory must not be graded by its author | **No** — never same Task as developer |

**Also a new Task:** retries (`changes-required`, devops `FAILED`). Do not resume the previous subagent thread to “just fix it.”

**Parent-only (no Task):** classify change_class, write `route.md` / `patch.md` / telemetry stubs for micro|minor, paste HANDOFFs, wait for PM / Architect / BA questions, run `@signoff:*` (write sign-off files from [assets/planning-signoff-template.md](assets/planning-signoff-template.md)), apply architect-policy after requirements sign-off, read `spec-order.md` and fan out wave Tasks, set `DEPLOY_TARGET`, choose next `subagent_type`.

**Forbidden:** PM+Architect, Architect+BA, PM+BA, BA+critic, developer+critic, tester+devops, telemetry+developer, implement-then-review in one context, or spawning developer before planning sign-offs.

**Templates (this skill).** Load only when named. Deploy runbook/scripts live in **local-deployment**.

| When | Asset |
|------|--------|
| Parent classifies | [assets/change-routing.md](assets/change-routing.md), [assets/tester-policy.md](assets/tester-policy.md), [assets/architect-policy.md](assets/architect-policy.md) |
| Parent sign-off | [assets/planning-signoff-template.md](assets/planning-signoff-template.md) |
| Parent spawns any step | [assets/parent-task-prompt.md](assets/parent-task-prompt.md) |
| Micro/minor patch | [assets/patch-template.md](assets/patch-template.md) |
| Clarify-first (PM / Architect / BA) | [assets/clarify-first.md](assets/clarify-first.md), [assets/decisions-template.md](assets/decisions-template.md), [assets/questions-format.md](assets/questions-format.md) |
| PM P2–P6 | [assets/research-template.md](assets/research-template.md), [assets/plan-template.md](assets/plan-template.md), [assets/handoff-pm-template.md](assets/handoff-pm-template.md) |
| Architect A2–A5 | [../architecture-design/SKILL.md](../architecture-design/SKILL.md), [assets/architecture-template.md](assets/architecture-template.md), [assets/implementation-plan-template.md](assets/implementation-plan-template.md), [assets/handoff-architect-template.md](assets/handoff-architect-template.md) |
| BA S3 questions | [assets/questions-format.md](assets/questions-format.md) |
| BA S4 draft | [assets/specification-template.md](assets/specification-template.md) |
| BA S4 density | [assets/example-specification.md](assets/example-specification.md) |
| BA S4b–S4c | [assets/spec-order-template.md](assets/spec-order-template.md), [assets/test-plan-template.md](assets/test-plan-template.md), [assets/test-strategy-template.md](assets/test-strategy-template.md) |
| BA S6 handoff | [assets/handoff-template.md](assets/handoff-template.md) |
| Tester | [assets/qa-test-cases-template.md](assets/qa-test-cases-template.md), [assets/qa-signoff-template.md](assets/qa-signoff-template.md) |
| Telemetry | [../observability-telemetry/SKILL.md](../observability-telemetry/SKILL.md) |
| Security preflight | [../secure-implementation/SKILL.md](../secure-implementation/SKILL.md) |
| Retro | [../pipeline-retro/SKILL.md](../pipeline-retro/SKILL.md) |

PM loop: [product-planning/SKILL.md](../product-planning/SKILL.md). Architect loop: [architecture-design/SKILL.md](../architecture-design/SKILL.md). BA loop: [spec-generation/SKILL.md](../spec-generation/SKILL.md). Agents: [product-manager-agent](../../agents/product-manager-agent.md) → [architect-agent](../../agents/architect-agent.md) → [ba-agent](../../agents/ba-agent.md) → … → [devops-agent](../../agents/devops-agent.md) → [retro-agent](../../agents/retro-agent.md). Memory: [AGENTS.md](../../../AGENTS.md), [wiki INDEX](../../wiki/INDEX.md).

---

## Setup

1. Create `features/{slug}/`. Reuse if it exists. Feature class: child specs live in `features/{slug}/{child}/` even when there is only one child.
2. Keep artifacts there: `route.md`, `plan.md` (feature), `decisions.md`, `architecture.md` / `implementation-plan.md` when Architect ran, `signoff-*.md`, `spec-order.md`, `test-plan.md`, child specs, telemetry contracts, HANDOFFs, `security-preflight.md`, `qa-test-cases.md`, `qa-signoff.md`, `deploy-result.env`, `RETRO.md`. Micro/minor stay flat (`patch.md`).

---

## Workflow when `change_class` is **feature**

Each step is a **new `Task` with a full prompt**. Wait for HANDOFF before the next step, except same-wave children which run in **parallel Tasks**.

1. **PM** — `product-manager-agent` (first gate). Stop if `BLOCKED` with questions.
2. **`@signoff:requirements`** — present `plan.md`. Stop until the user approves or revises. Write `signoff-requirements.md`.
3. **Architect policy** — load [assets/architect-policy.md](assets/architect-policy.md). Update `skip_architect` in `route.md`. If skip, drop Architect and `@signoff:architect`.
4. **Architect** — when `skip_architect` is false. Stop if `BLOCKED` (user questions) or `BLOCKED_CHALLENGE_PM` (void requirements sign-off, re-spawn PM).
5. **`@signoff:architect`** — present `architecture.md` + `implementation-plan.md`. Stop until the user approves.
6. **BA** — after requirements sign-off and (if Architect ran) architect sign-off.
7. **BA critic** — reviews plan + architecture (if any) + all child specs + order + test plan. `changes-required` voids any draft BA sign-off and re-spawns BA.
8. **`@signoff:ba`** — present child specs after critic approve. Stop until the user approves. Do not start waves without `signoff-ba.md`.
9. **Waves** — read `spec-order.md`. For each wave, for each child in that wave:
   - `telemetry-agent` → `developer-agent` → `developer-critic-agent`
   - Inject `FEATURE_SLUG: {parent}/{child}` and that child’s `SPEC_PATH`
   - `parallel` wave: spawn one chain per child; wait for every child’s developer-critic `approve` | `approve-with-nits` before the next wave
   - `sequential` wave: finish one child chain before the next child
10. **Tester** — **once**, parent slug, after **all** children have approved developer-critics. Not per spec. Not between waves.
11. **Devops** — only if `FEATURE_SIGNOFF: passed`
12. **Retro** — then **PIPELINE_COMPLETE**

**minor / micro:** do not run this list. Follow the chain in the routing table. Developer still gets a **new Task**; parent never edits product source.

Stop on `BLOCKED`, `FAILED`, or `changes-required` until that gate is cleared. If a micro/minor diff grows into a new flow, reset `route.md` to `feature` and start **PM**.

Set `DEPLOY_TARGET` from developer files (`auto` | `ecommerce-store` | `chorus` | `both`) in the devops prompt.

---

## Critic comments (mandatory)

| Verdict | Parent |
|---------|--------|
| `approve` | Next agent **in a new Task**. After BA critic: `@signoff:ba` first, then waves. |
| `approve-with-nits` | Same; nits optional |
| `changes-required` | Re-spawn **previous** agent in a **new Task** with the report. Void `signoff-ba.md` if BA is re-run. Retry cap **2**, then stop for the user |

---

## Failure (parent)

| Situation | Action |
|-----------|--------|
| PM `BLOCKED` with questions | Wait; re-spawn PM in a new Task |
| Architect `BLOCKED` with user questions | Wait; re-spawn Architect in a new Task |
| Architect `BLOCKED_CHALLENGE_PM` | Void `signoff-requirements.md` (and downstream); re-spawn PM; user re-signs; then Architect |
| BA `BLOCKED` with questions | Wait; re-spawn BA in a new Task |
| User revises a signed-off artifact | Void that sign-off and downstream; re-spawn the author |
| PM, Architect, or BA `BLOCKED` unsafe | Stop |
| Missing plan / spec / architecture / HANDOFF / required `signoff-*.md` | Do not spawn the next agent. When `gates.require_planning_signoff_before_build` is true, do not start telemetry or developer without `signoff-ba.md` (and `signoff-architect.md` unless `skip_architect`) |
| Tester bugs | Re-spawn the **owning child’s** developer (test-plan row names the spec) — **no devops** |
| Devops `FAILED` (compile) | New Task: that child’s developer or retry devops once |
| Devops `FAILED` (health) | Retry devops once in a new Task; then stop. **Not** PIPELINE_COMPLETE |
| Devops `SUCCESS` | Spawn **retro-agent**, then PIPELINE_COMPLETE |

---

## Anti-patterns

Two pipeline steps in one context · specialist work inline in the parent · running the full PM/Architect/BA ladder for a label change · classifying **micro** when a hard-upgrade trigger applies · critic in the same Task as the author · auto-continuing after PM/Architect/BA SUCCESS without `@signoff:*` · starting developer before planning sign-offs · treating tester or devops SUCCESS as done (retro is last) · spawning tester between waves · `TESTS: cases-only` on feature class · inventing kubectl/cloud deploy · logging bootstrap secrets · vanity analytics.

---

## `@signoff:*` tokens (parent-only)

Config chains may include `@signoff:requirements`, `@signoff:architect`, and `@signoff:ba` next to `@waves`. These are **not** Tasks.

1. Summarize the artifact and its path.
2. **Stop.** Do not spawn the next specialist.
3. Wait for the user to approve / sign off, or send revision comments.
4. On approve: write `features/{slug}/signoff-{role}.md` from [assets/planning-signoff-template.md](assets/planning-signoff-template.md).
5. On revise: void that file, re-spawn the author with the comments. Void downstream sign-offs when an upstream artifact changes.

Micro / minor / jira-bug never run these tokens.
