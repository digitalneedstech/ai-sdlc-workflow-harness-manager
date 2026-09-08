# Parent Task prompts

Owned by **feature-development**. Parent picks the **workflow** ([orchestration](../../orchestration/SKILL.md)), **classifies** (`change-routing.md`), then orchestrates. Specialists run in a **new `Task`**. Default `subagent_type` is `generalPurpose` (portable). Teams that installed `--ide cursor --agent-stubs` may use the named Cursor types instead. Each prompt must say `Follow .pipeline/agents/{name}.md`. Include `WORKFLOW:`, `CHANGE_CLASS:` and `FEATURE_SLUG` on every prompt.

**Always include:** `REPO_ROOT` (absolute), `FEATURE_SLUG`, `WORKFLOW`, `CHANGE_CLASS: micro|minor|feature`, disk paths.

Feature class: parent slug for PM, Architect, BA, BA critic, tester, devops, retro. Child work uses `FEATURE_SLUG: {parent}/{child}`.

`@signoff:requirements`, `@signoff:architect`, and `@signoff:ba` are parent-only. Do not spawn a Task. Present the artifact, wait for the user, write `signoff-*.md` from [planning-signoff-template.md](planning-signoff-template.md).

---

## Isolation preamble (every specialist)

```text
CONTEXT: This is a new Task. You do not have the parent chat. Use only this prompt and files on disk.
Do not spawn other pipeline agents. Return a HANDOFF in your final message.
WORKFLOW: {feature-development|jira-story|jira-bug|jira-epic}
CHANGE_CLASS: {micro|minor|feature}
```

---

## Intake step (tracker workflows only, first step)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the parent chat. Use only this prompt and files on disk.
You are the intake agent. Follow .pipeline/agents/intake-agent.md and .pipeline/skills/jira-intake/SKILL.md exactly.
If the issue is an epic, continue in this same Task with .pipeline/skills/epic-breakdown/SKILL.md.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {slug}
JIRA_KEY: {KEY}
USER_REQUEST: {verbatim}
CONFIG_PATH: .pipeline/config.json

Fetch read-only. Normalize to features/{slug}/intake.md with the description and ACs verbatim.
Redact secrets and customer data. Do not write back to the tracker. Do not write specs or code.
Classify the issue and return HANDOFF-intake.md with ISSUE_TYPE and WORKFLOW.
```

The parent writes `route.md` **after** this HANDOFF, using its `ISSUE_TYPE` / `WORKFLOW`.

---

## Bug analyst step (bug workflow, after intake)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the parent chat.
You are the bug analyst. Follow .pipeline/agents/bug-analyst-agent.md and .pipeline/skills/bug-fix/SKILL.md steps B1–B6. Read-only on product source.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {slug}
JIRA_KEY: {KEY} | n/a
INTAKE_PATH: features/{slug}/intake.md
ROUTE_PATH: features/{slug}/route.md

Reproduce the defect, trace it to a code-level cause with path:line evidence, map the blast radius,
and write features/{slug}/rca.md with options, a recommendation, and the required regression case.
Do not edit product code — not even the failing test. Do not spawn the developer.
Return HANDOFF-bug-analyst.md.
```

---

## Developer step (bug workflow)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the analyst's chain-of-thought.
You are the developer. Follow .pipeline/agents/developer-agent.md and bug-fix/SKILL.md step B7.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {slug}
RCA_PATH: features/{slug}/rca.md
RECOMMENDED_OPTION: {A | B}
BUG_ANALYST_HANDOFF: features/{slug}/HANDOFF-bug-analyst.md

Write the regression test from rca.md §8 first and confirm it fails for the stated reason.
Implement the recommended option only, plus every in-scope caller in §5. Fill security-preflight.md.
Do not swallow the error, loosen a type, or weaken a test to go green. Do not spawn the critic.
Return HANDOFF-developer.md with ROOT_CAUSE_ADDRESSED and REGRESSION_TEST.
```

---

## Micro / minor — developer (after parent wrote route.md + patch.md)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. CHANGE_CLASS: {micro|minor}
You are the developer. Follow .pipeline/agents/developer-agent.md.
Scope is patch.md only. Do not expand into a new screen/API.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {slug}
PATCH_PATH: features/{slug}/patch.md
ROUTE_PATH: features/{slug}/route.md
TELEMETRY_CONTRACT_PATH: features/{slug}/telemetry-contract.md

Implement AC-1 in patch.md. Fill security-preflight.md (N/A rows ok). Do not spawn critic or devops.
Return HANDOFF-developer.md.
```

For **minor**, next Task is developer-critic (SPEC_PATH may be `patch.md`). For **micro**, next Task is devops, then retro.

---

## PM step (feature class only)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the parent chat. Use only this prompt and files on disk.
You are the product manager. Follow .pipeline/agents/product-manager-agent.md and .pipeline/skills/product-planning/SKILL.md exactly.
Load templates from .pipeline/skills/feature-development/assets/ only when product-planning names them.

REPO_ROOT: {absolute path}
USER_REQUEST: {verbatim}
FEATURE_SLUG: {parent-slug}

1. Create features/{slug}/ if missing (parent may already have).
2. Run P1–P6. Research the repo and the web; do not implement product code.
3. Follow clarify-first. Mine prior artifacts into decisions.md. Ask every remaining PM checklist item (max 20). Never ask what the repo or decisions.md already answers.
4. If interactive questions are required, return BLOCKED with questions.md and stop.
5. Otherwise write plan.md + research.md + decisions.md + HANDOFF-pm.md.
6. Return the HANDOFF body in your final message.
Do not call Architect, BA, or developer. Do not write specification.md.
```

---

## Architect step (feature class, when skip_architect is false)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the parent chat. Use only this prompt and files on disk.
You are the architect. Follow .pipeline/agents/architect-agent.md and .pipeline/skills/architecture-design/SKILL.md exactly.
Load templates from .pipeline/skills/feature-development/assets/ only when architecture-design names them.

REPO_ROOT: {absolute path}
USER_REQUEST: {verbatim}
FEATURE_SLUG: {parent-slug}
WORKFLOW: {feature-development|jira-story|jira-epic}
PLAN_SOURCE_KIND: pm-plan | jira-story | jira-epic
PLAN_SOURCE_PATH: features/{slug}/plan.md | features/{slug}/intake.md | features/{slug}/epic-plan.md
DECISIONS_PATH: features/{slug}/decisions.md
SIGNOFF_REQUIREMENTS_PATH: features/{slug}/signoff-requirements.md

1. Run A1–A5. Read signed-off requirements, decisions.md, and the repo first.
2. Challenge remaining Architect checklist items (max 15) before drawing diagrams.
3. audience: user → BLOCKED. audience: pm on feature-development → BLOCKED_CHALLENGE_PM. On jira-story/epic treat pm as user.
4. Write architecture.md (mermaid only) + implementation-plan.md + append decisions.md + HANDOFF-architect.md.
5. Return the HANDOFF body in your final message.
Do not call BA or developer. Do not write specification.md.
```

---

## BA step (spec-driven workflows)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the parent chat. Use only this prompt and files on disk.
You are the BA agent. Follow .pipeline/agents/ba-agent.md and .pipeline/skills/spec-generation/SKILL.md exactly.
Load templates from .pipeline/skills/feature-development/assets/ only when spec-generation names them.

REPO_ROOT: {absolute path}
USER_REQUEST: {verbatim}
FEATURE_SLUG: {parent-slug}
PLAN_SOURCE_KIND: pm-plan | jira-story | jira-epic
PLAN_SOURCE_PATH: features/{slug}/plan.md | features/{slug}/intake.md | features/{slug}/epic-plan.md
ARCH_PATH: features/{slug}/architecture.md | none
IMPL_PLAN_PATH: features/{slug}/implementation-plan.md | none
DECISIONS_PATH: features/{slug}/decisions.md
JIRA_KEY: {KEY} | n/a

1. Read the plan source, decisions.md, and architecture/implementation-plan when present. Do not re-ask answered questions. Never call tracker MCP — intake already fetched everything.
2. Run S1–S6. Follow clarify-first. Ask remaining BA checklist items (max 15).
3. Write one specification.md per child under features/{slug}/{child}/, each carrying its source key. Honor the Architect child split when it exists.
4. Write spec-order.md (waves) and test-plan.md plus each child’s test-strategy.md.
5. If interactive clarifying questions are required, return BLOCKED with questions.md and stop.
6. Write HANDOFF.md. Return the HANDOFF body in your final message.
Do not call the critic or developer. Do not edit product source.
```

`jira-epic` adds: “Write exactly one child spec per story in the epic plan’s child table, reading `features/{slug}/stories/{child}.md` for detail. Say why in the HANDOFF if you merge or split any of them.”

---

## BA critic step

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the parent chat or the BA author’s chain-of-thought.
You are the BA critic. Follow .pipeline/agents/ba-critic-agent.md. Read-only.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {parent-slug}
USER_REQUEST: {verbatim}
PLAN_SOURCE_PATH: features/{slug}/plan.md | features/{slug}/intake.md | features/{slug}/epic-plan.md
ARCH_PATH: features/{slug}/architecture.md | none
IMPL_PLAN_PATH: features/{slug}/implementation-plan.md | none
SPEC_ORDER_PATH: features/{slug}/spec-order.md
TEST_PLAN_PATH: features/{slug}/test-plan.md
BA_HANDOFF_PATH: features/{slug}/HANDOFF.md

Review the plan source, architecture when present, every child specification.md, spec-order.md, and test-plan.md.
Flag specs that ignore signed-off ADRs.
Tracker-sourced: check each spec against the verbatim issue text — a paraphrase that weakens an AC is a finding.
Emit CRITIC_VERDICT. Write features/{slug}/HANDOFF-ba-critic.md. Do not spawn telemetry or developer.
```

---

## Telemetry step (per child, after BA critic approve)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the BA author’s chain-of-thought.
You are the telemetry agent. Follow .pipeline/agents/telemetry-agent.md and .pipeline/skills/observability-telemetry/SKILL.md.
Use the contract template in that skill’s assets/.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {parent-slug}/{child-slug}
PARENT_SLUG: {parent-slug}
SPEC_PATH: features/{parent-slug}/{child-slug}/specification.md

Write features/{parent-slug}/{child-slug}/telemetry-contract.md (EVENTS none is valid). No product code. Do not spawn developer.
Return HANDOFF-telemetry.md in that child folder.
```

---

## Developer step (per child)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the parent chat.
You are the developer. Follow .pipeline/agents/developer-agent.md.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {parent-slug}/{child-slug}
PARENT_SLUG: {parent-slug}
SPEC_PATH: features/{parent-slug}/{child-slug}/specification.md
ARCH_PATH: features/{parent-slug}/architecture.md | none
IMPL_PLAN_PATH: features/{parent-slug}/implementation-plan.md | none
TELEMETRY_CONTRACT_PATH: features/{parent-slug}/{child-slug}/telemetry-contract.md
BA_CRITIC_VERDICT: {approve | approve-with-nits}

Implement this child’s Must FRs and the telemetry allowlist only. Follow the signed-off implementation plan when it exists. BLOCKED if spec and plan conflict. Fill security-preflight.md in the child folder. Do not spawn the critic.
Return HANDOFF-developer.md in the child folder.
```

---

## Developer critic step (per child)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the implementer’s chain-of-thought.
You are the developer critic. Follow .pipeline/agents/developer-critic-agent.md. Read-only.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {parent-slug}/{child-slug}
SPEC_PATH: features/{parent-slug}/{child-slug}/specification.md
TELEMETRY_CONTRACT_PATH: features/{parent-slug}/{child-slug}/telemetry-contract.md
DEV_HANDOFF_PATH: features/{parent-slug}/{child-slug}/HANDOFF-developer.md
NOTES_PATH: features/{parent-slug}/{child-slug}/implementation-notes.md

Emit CRITIC_VERDICT. Do not spawn tester. Return HANDOFF-developer-critic.md in the child folder.
```

---

## Tester step

Spawn only when `route.md` has `skip_tester: false` (from [tester-policy.md](tester-policy.md) or `RUN_TESTER`). Feature: after all child critics. Minor: after developer-critic. Micro: after developer. For micro/minor set `PATCH_PATH` instead of `TEST_PLAN_PATH` if there is no test-plan. **Bug workflow:** set `RCA_PATH` instead, after developer-critic approves, and require that the original reproduction no longer reproduces and the regression test is green before `FEATURE_SIGNOFF: passed`.

## Tester step (once, parent slug, after all child critics)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the parent chat.
You are the tester agent. Follow .pipeline/agents/tester-agent.md.
Feature class cannot finish as TESTS: cases-only.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {parent-slug}
TEST_PLAN_PATH: features/{slug}/test-plan.md
SPEC_ORDER_PATH: features/{slug}/spec-order.md

Read the feature test-plan and every child’s test-strategy.md.
Write qa-test-cases.md covering every Must AC. Browser rows need numbered Steps and a concrete Expected.
Run required layers (unit, api, e2e, ui Playwright) unattended.
UI Playwright implements each browser TC-* as one test('TC-N') from qa-test-cases.md (do not re-plan from Must ACs). Review PNGs go to automation-tests/artifacts/{slug}/screenshots/.
Write qa-signoff.md. FEATURE_SIGNOFF: passed only when required layers exited 0.
Return HANDOFF-tester.md. PARENT_NEXT must be devops-agent if STATUS is SUCCESS.
```

---

## Devops step

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the tester’s or developer’s chat.
You are the devops agent. Follow .pipeline/agents/devops-agent.md, .pipeline/skills/local-deployment/SKILL.md and the runbook in its assets/.
Run only .pipeline/skills/local-deployment/scripts/deploy-local.sh — do not invent deploy commands.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {parent-slug}
DEPLOY_TARGET: {one of deploy.targets in .pipeline/config.json; default deploy.target}

If skip_tester is false, refuse unless qa-signoff.md has FEATURE_SIGNOFF: passed.
Do not complete the pipeline unless deploy-result.env has OVERALL=passed.
Do not register daemons or print secrets. Return HANDOFF-devops.md. PARENT_NEXT: retro-agent.
```

---

## Retro step (after devops SUCCESS, every class)

```text
subagent_type: generalPurpose
CONTEXT: This is a new Task. You do not have the parent chat.
You are the retro agent. Follow .pipeline/agents/retro-agent.md, .pipeline/skills/pipeline-retro/SKILL.md and .pipeline/wiki/README.md.

REPO_ROOT: {absolute path}
FEATURE_SLUG: {parent-slug}
CHANGE_CLASS: {micro|minor|feature}
CONVERSATION_DIGEST: {optional ≤30 lines, no secrets}

Write features/{slug}/RETRO.md. Add a wiki page + INDEX + AGENTS.md row only if the learning is reusable and not already indexed.
Return HANDOFF-retro.md. PARENT_NEXT: PIPELINE_COMPLETE.
```
