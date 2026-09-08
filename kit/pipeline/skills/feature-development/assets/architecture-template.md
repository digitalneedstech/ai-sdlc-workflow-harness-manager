# Architecture — {title}

**Status:** Draft | Ready for BA
**Slug:** `{slug}`
**Requirements:** `features/{slug}/plan.md` | `features/{slug}/intake.md` | `features/{slug}/epic-plan.md`
**Created:** {YYYY-MM-DD}

---

## 1. Context

Who uses the system and which existing modules this change touches. Cite paths.

```mermaid
flowchart LR
  user[Actor] --> app[Existing app]
  app --> dep[Existing dependency]
```

## 2. Containers / modules

What we add or change. Prefer existing modules over new ones.

```mermaid
flowchart TB
  ui[UI surface] --> api[API or store]
  api --> data[Persistence or none]
```

## 3. Sequence (required when a new API or multi-step flow exists)

```mermaid
sequenceDiagram
  actor User
  User->>UI: action
  UI->>Service: call
  Service-->>UI: result
```

`none — single-screen local change` is valid when no new API or multi-step flow
exists. Say so.

## 4. ADRs (architecture decisions)

| ID | Decision | Why | Rejected alternative |
|----|----------|-----|----------------------|
| ADR-1 | … | … | … |

## 5. Child-spec split (technical)

If this differs from the PM / intake split, this table **wins** for BA.

| Child slug | Job | Why it is a separate spec |
|------------|-----|---------------------------|
| `{child-a}` | … | … |

## 6. Constraints

- Paths, interfaces, or patterns developers must reuse
- Authz / PII / secrets boundaries
- What must not be invented

## 7. Risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| … | … | … |

## 8. Open questions

none | OQ-1: … (must be empty or cosmetic before Ready)
