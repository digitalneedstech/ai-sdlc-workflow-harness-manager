# Specification template

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Fill placeholders only. Do not add a product, host, or customer name. |

Owned by **feature-development**. BA fills this into `features/{slug}/specification.md`. Use `N/A — {reason}` instead of deleting a section.

```markdown
# {Feature title}

**Status:** Draft | Ready for BA critic
**Slug:** `{slug}`
**Created:** {YYYY-MM-DD}
**Source request:** {one-line user ask}
**Source:** {ISSUE-KEY} | user request (tracker-sourced work must carry the key)
**Codebase grounded:** Yes (paths below) | No (greenfield)

---

## 1. Problem

What is painful or missing today? Who feels it? What happens if we do nothing?

## 2. Goals and non-goals

### Goals
- …

### Non-goals / out of scope
- … (what this increment will not build)

## 3. Actors and context

| Actor | Goal | Constraints |
|-------|------|-------------|
| … | … | … |

Environment: local app, browser, daemon, CLI, etc.

## 4. Current behavior (as-is)

Facts from the repo or “does not exist.” Cite paths.

## 5. Intended behavior (to-be)

### 5.1 Product model
Entities, states, and relationships in plain language.

### 5.2 Primary user journeys
Numbered end-to-end flows. Each step: actor, action, system response.

### 5.3 Alternate and error journeys
Empty, unauthorized, offline, validation failure, conflict, timeout.

## 6. Functional requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | … | Must | … |
| FR-2 | … | Should | … |

Each FR is testable. No vague “make it nice.” Cross-link journeys.

## 7. User experience (if UI)

- Screens / routes / nav
- Key components and what they show
- Empty, loading, error, success states
- User-visible copy (or reuse existing i18n)
- Accessibility at product level (keyboard, labels)

If no UI: `N/A — backend/service only`.

## 8. Data and integrations

- CRUD data
- External systems
- What must never be logged or sent (secrets, PII)

## 9. Non-functional requirements

- **Security:** authn/authz, trust boundaries
- **Reliability:** failure modes, retries
- **Performance:** only if implied; else a short default
- **Observability:** what operators should see

## 10. Acceptance criteria

- [ ] AC-1: …  (maps to FR-…)
- [ ] AC-2: …
- [ ] AC-3: …

Prefer Given/When/Then when it clarifies. Every Must FR needs ≥1 AC.

## 11. Assumptions

| ID | Assumption | Default chosen | Impact if wrong |
|----|------------|----------------|-----------------|
| A-1 | … | … | … |

Empty table usually means silent invention — go back.

## 12. Open questions

| ID | Question | Blocks |
|----|----------|--------|
| OQ-1 | … | FR-… / AC-… |

If interactive and Must FRs are blocked, status is **not** Ready for BA critic.

## 13. Traceability

- User request → covering sections
- Explicit “not requested, not included”

## 14. Ready for critic

- [ ] Required sections filled
- [ ] Assumptions labeled
- [ ] ACs testable
- [ ] Out of scope written
```
