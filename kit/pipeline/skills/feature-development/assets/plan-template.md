# Feature plan template

Owned by **feature-development**. PM copies this to `features/{slug}/plan.md`.

```markdown
# Plan — {title}

**Status:** Draft | Ready for BA
**Slug:** `{slug}`
**Created:** {YYYY-MM-DD}
**Source request:** {one-line user ask}
**Codebase grounded:** Yes (paths in research.md) | No (greenfield)

---

## 1. Problem

What is painful or missing? Who feels it? What happens if we do nothing?

## 2. Who it is for

| Actor | Goal | Constraints |
|-------|------|-------------|
| … | … | … |

## 3. Options considered

| Option | Keep? | Why |
|--------|-------|-----|
| A — … | yes (recommended) | … |
| B — … | no | … |

## 4. Recommended direction

One paragraph. Cite research.md facts (R-ids).

## 5. Proposed child specifications

At least one. Each becomes `features/{slug}/{child-slug}/`.

| Child slug | Job (one line) | Why it is a separate spec |
|------------|----------------|---------------------------|
| `{child-a}` | … | … |

## 6. Success criteria

- S-1: …
- S-2: …

## 7. Non-goals

- …

## 8. Risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| … | … | … |

## 9. Assumptions

| ID | Assumption | Why defaulted |
|----|------------|---------------|
| A-1 | … | … |

## 10. Open questions

none | OQ-1: …

## 11. Ready for sign-off

Yes — split is stable; parent may request requirements sign-off. | No — {what is still blocking}
```
