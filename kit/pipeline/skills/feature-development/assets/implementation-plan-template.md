# Implementation plan — {title}

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Fill placeholders only. Do not add a product, host, or customer name. |

**Slug:** `{slug}`
**Architecture:** `features/{slug}/architecture.md`
**Created:** {YYYY-MM-DD}

Ordered file and module work for developers. Not a substitute for child
`specification.md`. BA still writes product ACs. Developers implement the spec
**and** this plan; `BLOCKED` if they conflict.

---

## 1. Change order

| Step | Child slug | Files / modules (existing paths or “new: …”) | Why this order |
|------|------------|----------------------------------------------|----------------|
| 1 | `{child-a}` | `path` — what changes | … |

## 2. Interfaces

Contracts the next child may depend on (function names, routes, events). Cite
architecture ADRs.

- …

## 3. Do not invent

- Out of scope modules
- New libraries unless an ADR named them
- Product behavior not in the signed-off requirements

## 4. Wave alignment

How this order maps to `spec-order.md` waves BA will write. If BA has not run
yet, propose wave grouping; BA may refine with real data/UI dependencies.

- Wave 1 (parallel | sequential): `{child-a}`
