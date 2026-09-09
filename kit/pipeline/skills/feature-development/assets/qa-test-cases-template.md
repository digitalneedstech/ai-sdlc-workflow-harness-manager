# QA test cases template

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Fill placeholders only. Do not add a product, host, or customer name. |

Owned by **feature-development**. Tester copies this to `features/{slug}/qa-test-cases.md`. Every child Must AC must appear. Feature class must execute automated layers — not cases-only.

Browser rows (`ui` / browser `e2e` / `a11y`) become one Playwright `test('TC-N')` each. **Steps** and **Expected** in this file are binding; locators are chosen later. Number the steps; do not leave a one-line slogan.

```markdown
# Test cases — {slug}

**Test plan:** features/{slug}/test-plan.md
**Status:** Ready for local deploy | Blocked (bugs)

| ID | Spec | AC | FR | Layer | Type | Preconditions | Steps | Expected |
|----|------|----|----|-------|------|---------------|-------|----------|
| TC-1 | {child} | AC-1 | FR-1 | ui | happy | … | 1. … 2. … | … |
| TC-2 | {child} | AC-1 | FR-1 | api | error | … | … | … |
| TC-3 | {child} | AC-2 | FR-2 | unit | happy | … | … | … |
| TC-4 | {child} | AC-… | FR-… | telemetry | telemetry | Contract event `…` | Perform the action | Event would fire with allowlisted props only |
| TC-5 | {child} | — | — | a11y | a11y | UI in spec | Keyboard to control | Name/role/label present |

## Coverage

- Must ACs with no TC: none | {spec/ids}
- Out of scope (not tested): {spec non-goals}

## Execution this step

- Automated: {commands and exits}
- FEATURE_SIGNOFF: see qa-signoff.md
```
