# HANDOFF template (PM step)

Owned by **feature-development**. PM writes `features/{slug}/HANDOFF-pm.md` and pastes this body in the final message.

```markdown
# HANDOFF — product-manager-agent

**status:** SUCCESS | BLOCKED | ASSUMPTIONS_USED
**slug:** {slug}
**plan_path:** features/{slug}/plan.md
**research_path:** features/{slug}/research.md
**questions_path:** features/{slug}/questions.md | none
**ready_for_ba:** true | false

## Summary
{3–6 sentences: direction, proposed child specs, what was assumed}

## Proposed children
- {child-slug}: {one-line job}

## Evidence used
- {path or URL}: {fact}

## Assumptions used (if any)
- A-1: …

## Open questions left
- none | OQ-1: …

## Failure / recovery (if not SUCCESS)
- What failed:
- What the parent should do:

## Parent next step
Spawn ba-agent on plan.md. Do not start developer-agent.
```

### Status values (mandatory)

| status | When | `ready_for_ba` | Parent |
|--------|------|----------------|--------|
| `SUCCESS` | P5 blockers pass | `true` | Spawn BA |
| `ASSUMPTIONS_USED` | Non-interactive or user said proceed; defaults labeled | `true` | Spawn BA; BA critic must stress-test Assumptions |
| `BLOCKED` | Interactive wait, unsafe ask, or missing scope | `false` | Wait for user then re-run PM, or stop |

Do not report `SUCCESS` when blockers fail or Must decisions are still open.
