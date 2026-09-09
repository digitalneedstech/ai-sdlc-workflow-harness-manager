# Epic plan template

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Fill placeholders only. Do not add a product, host, or customer name. |

Owned by **epic-breakdown**. Intake copies this to `features/{slug}/epic-plan.md`. It stands in for the PM `prd.md` on the epic workflow, so the BA reads it the same way.

```markdown
# Epic plan — {EPIC-KEY} {title}

**Status:** Ready for BA | Blocked — {why}
**Slug:** `{slug}`
**Source:** tracker epic `{EPIC-KEY}` · **fetched:** {YYYY-MM-DD}
**Children queried with:** `{jql used}` ({n} returned, {m} in scope)

---

## 1. Problem

From the epic's own description. What is missing, who feels it, what happens if the epic is not delivered.

## 2. Who it is for

| Actor | Goal | Constraints |
|-------|------|-------------|
| … | … | … |

## 3. Direction

One paragraph from the epic description and acceptance criteria. No invented strategy — if the epic does not say, write `Unknown — not in the epic`.

## 4. Proposed child specifications

One row per in-scope story. Each becomes `features/{slug}/{child-slug}/`.

| Child slug | Story key | Job (one line) | Detail file |
|------------|-----------|----------------|-------------|
| `{key-lower}-{summary-kebab}` | {KEY} | {verbatim summary} | `stories/{child-slug}.md` |

## 5. Suggested dependency groups

BA turns these into `spec-order.md` waves; confirm them against the specs before committing.

| Group | Mode | Child slugs | Because |
|-------|------|-------------|---------|
| 1 | sequential | … | {stated link or shared data/route} |
| 2 | parallel | … | independent |

## 6. Out of scope (excluded children)

| Story key | Type / status | Why excluded |
|-----------|---------------|--------------|
| {KEY} | Done | already released |
| {KEY} | Bug | runs the bug workflow on its own key |
| {KEY} | — | beyond max_children; split the run |

## 7. Success criteria

From the epic's acceptance criteria.

- S-1: …

## 8. Non-goals

- …

## 9. Risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| … | … | … |

## 10. Assumptions

| ID | Assumption | Why defaulted |
|----|------------|---------------|
| A-1 | … | not stated in the epic or its stories |

## 11. Open questions

none | OQ-1: …

## 12. Ready for BA

Yes — every in-scope story has a slug and a detail file. | No — {what is blocking}
```

## Story detail file — `features/{slug}/stories/{child-slug}.md`

```markdown
# {KEY} — {summary}

**type:** {story | task} · **status:** {status} · **priority:** {priority}
**labels:** {list} · **components:** {list} · **links:** {key: link type}

## Description (verbatim)

{markdown of the story description}

## Acceptance criteria (verbatim)

{AC list, or `Unknown — not in the story`}

## Gaps for the BA

- {what the story does not answer}
```
