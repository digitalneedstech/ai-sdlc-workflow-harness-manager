# QA knowledge review

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Fill placeholders only. Do not add a product, host, or customer name. |

Owned by **test-knowledge-bootstrap**. Curator copies this to `test-knowledge/_candidates/{run}/REVIEW.md`.

```markdown
# QA overlay review — {run}

**area:** {kebab area or "scope-proposal"}
**graph:** graphify-out/graph.json
**evidence rule:** Graphify confidence is never verified

## Scope

{What this run covers. One area. What was left out.}

## Candidates

| Kind | IDs | Evidence | Graph / source |
|------|-----|----------|----------------|
| action | ACT-… | inferred \| observed | … |
| fixture | FIX-… | inferred \| observed | … |
| oracle | ORC-… | inferred \| observed | … |

## Unknowns

| Item | Why it is unknown | Proposed default |
|------|-------------------|------------------|
| … | … | … |

## Do not promote if

- A secret or credential appears in any JSON value
- The curator invented a graph that Graphify did not write
- The area is unbounded ("the whole repo") without a scope proposal

## Decision

approve | edit | reject
```
