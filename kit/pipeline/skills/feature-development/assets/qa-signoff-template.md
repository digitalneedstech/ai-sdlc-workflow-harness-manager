# QA sign-off template

Owned by **feature-development**. Tester copies this to `features/{slug}/qa-signoff.md`. Devops must not run while `FEATURE_SIGNOFF` is missing or not `passed` (unless `skip_tester: true`).

```markdown
# QA sign-off — {slug}

FEATURE_SIGNOFF: passed | failed | blocked

**test_plan:** features/{slug}/test-plan.md
**qa_test_cases:** features/{slug}/qa-test-cases.md

## Layers

| Layer | Status | Command | Exit |
|-------|--------|---------|------|
| unit | passed \| n/a \| failed | … | {n} |
| api | passed \| n/a \| failed | … | {n} |
| e2e | passed \| failed | … | {n} |
| ui | passed \| n/a \| failed | … | {n} |

## Playwright (when ui or browser e2e ran)

- E2E_BASE_URL: http://127.0.0.1:{port}
- E2E_COMMAND: cd automation-tests && npx playwright test
- E2E_EXIT: {n}
- E2E_SPECS: automation-tests/specs/{slug}/*.spec.ts
- E2E_SCREENSHOTS: automation-tests/artifacts/{slug}/screenshots/
- TOOLCHAIN: {line from ensure-e2e-toolchain.sh}

## Coverage

- Must ACs with no executed case: none | {ids}
- Owning spec for failures: {child-slug} (parent re-spawns that child’s developer)

FEATURE_SIGNOFF: passed only when every required layer exited 0 and every Must AC is covered.
```
