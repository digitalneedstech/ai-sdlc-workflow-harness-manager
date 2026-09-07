# Feature pipeline — PM gate and multi-spec waves

- **Layer:** pipeline
- **Load when:** product-manager-agent, plan.md, nested features/{slug}/{child}/, spec-order.md, waves, one feature-level tester

## Symptom

A feature-class ask starts at BA with one flat specification.md, or testers run between child specs, or devops ships without Playwright.

## Root cause

Feature class is now a parent folder: PM plans first, BA splits children, parent fans out implementation waves, one tester signs off.

## Do not

- Spawn BA before HANDOFF-pm.md is SUCCESS or ASSUMPTIONS_USED
- Ask PM questions on a clear, simple feature-class ask
- Put sibling slugs at features/ instead of features/{feature}/{child}/
- Run tester-agent per child or between waves
- Mark tester SUCCESS as TESTS: cases-only on feature class
- Start devops without FEATURE_SIGNOFF: passed

## Fix / convention

1. Parent writes features/{slug}/route.md (change_class: feature, all skip_* false).
2. product-manager-agent writes plan.md and research.md. Blocking questions only (max 10).
3. ba-agent writes each features/{slug}/{child}/specification.md, spec-order.md (**children:** line), test-plan.md, and per-child test-strategy.md.
4. After BA critic approve, parent runs waves: per child telemetry then developer then developer-critic. Parallel children share a wave.
5. One tester-agent at the parent slug runs Playwright/api/unit from the test plan.
6. Devops only after qa-signoff.md has FEATURE_SIGNOFF: passed.

Micro/minor unchanged (flat folder, no PM, no tester).

## Files

.pipeline/agents/product-manager-agent.md, .pipeline/skills/product-planning/SKILL.md, .pipeline/skills/spec-generation/SKILL.md, .pipeline/skills/feature-development/SKILL.md, .cursor/hooks/subagent-start.py

## How to confirm

features/{slug}/plan.md exists before BA. Child specs are subfolders. HANDOFF-tester.md is after every child critic. qa-signoff.md exists before devops.
