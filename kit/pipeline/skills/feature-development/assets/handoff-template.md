# HANDOFF template (BA step)

Owned by **feature-development**. BA writes `features/{slug}/HANDOFF.md` and pastes this body in the final message.

```markdown
# HANDOFF — ba-agent

**status:** SUCCESS | BLOCKED | ASSUMPTIONS_USED
**slug:** {slug}
**plan_path:** features/{slug}/plan.md
**spec_order_path:** features/{slug}/spec-order.md
**test_plan_path:** features/{slug}/test-plan.md
**spec_paths:**
- features/{slug}/{child}/specification.md
**questions_path:** features/{slug}/questions.md | none
**decisions_path:** features/{slug}/decisions.md
**architecture_path:** features/{slug}/architecture.md | none
**ready_for_ba_critic:** true | false

## Summary
{3–6 sentences: what will be built, wave order, what was assumed}

## Evidence used
- {path}: {fact}

## Assumptions used (if any)
- A-1: …

## Open questions left
- none | OQ-1: …

## Failure / recovery (if not SUCCESS)
- What failed:
- What the parent should do:

## Parent next step
Spawn BA critic. After critic approve, wait for @signoff:ba. Do not start developer-agent.
```

### Status values (mandatory)

| status | When | `ready_for_ba_critic` | Parent |
|--------|------|----------------------|--------|
| `SUCCESS` | Spec-generation S5 blockers pass | `true` | Spawn BA critic |
| `ASSUMPTIONS_USED` | Non-interactive or user said proceed; defaults labeled in spec §11 | `true` | Spawn BA critic; critic must stress-test Assumptions |
| `BLOCKED` | Interactive wait, unsafe/illegal ask, or missing actor/scope that cannot be defaulted | `false` | Do **not** spawn developer. If questions: wait for user, then re-run BA. If unsafe: stop. |

Do not report `SUCCESS` when blockers fail or Must FRs are still open.
