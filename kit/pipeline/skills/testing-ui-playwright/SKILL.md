---
name: testing-ui-playwright
description: >-
  Tester-only. Bootstrap Playwright, implement qa-test-cases.md 1:1 as
  feature-scoped specs, capture review screenshots, heal locators only.
  Parent must not invoke directly.
disable-model-invocation: true
---

# UI / Playwright testing (tester skill)

| Attribute | Value |
|-----------|--------|
| Type | Skill |
| Audience | The named agent, or the parent when this file is on the allowlist |
| Adapt | If this repository’s UI e2e project is not `automation-tests/`, change the paths in this skill only. |

Maps to [Playwright Test Agents](https://playwright.dev/docs/test-agents): **planner → generator → healer**. CLI-only; optional Playwright MCP for exploration.

## Project (repo-level, outside `.cursor`)

All Playwright code and artifacts live in the project’s UI e2e directory
(default `automation-tests/`):

```text
automation-tests/
  playwright.config.ts
  lib/paths.ts
  lib/captureReviewScreenshot.ts
  scripts/ensure-e2e-toolchain.sh
  templates/seed.spec.ts          # pattern only, not collected
  specs/{slug}/*.spec.ts
  artifacts/{slug}/screenshots/   # TC-*.png for review
  artifacts/{slug}/test-results/  # Playwright dumps
  artifacts/{slug}/playwright-report/
```

`features/{slug}/` keeps QA markdown only: `qa-ui-plan.md`, `qa-test-cases.md`, `qa-signoff.md`, `HANDOFF-tester.md`. Never put specs or PNGs back under `features/`.

## 0. Bootstrap (mandatory first step)

```bash
automation-tests/scripts/ensure-e2e-toolchain.sh
```

If exit ≠ 0 → tester `FAILED`. Never `TESTS: cases-only` for feature class.

Export from `test-strategy.md` Target block:

- `E2E_BASE_URL` (localhost only)
- `E2E_WEB_SERVER_CMD` (optional)
- `E2E_HEALTH_PATH` (default `/`)
- `FEATURE_SLUG` (required — selects `specs/{slug}` and `artifacts/{slug}`)
- `REPO_ROOT`

## Source of truth (do not re-plan)

`features/{slug}/qa-test-cases.md` is written **before** this skill. It is the only case list.

- Implement every row whose Layer is `ui`, `e2e` (browser), or `a11y`.
- One Playwright `test()` per those `TC-*` IDs. Same ID in the test title and in `captureReviewScreenshot(page, "TC-N")`.
- Copy that row’s **Preconditions**, **Steps**, and **Expected** into the spec. Do not invent extra scenarios, merge TCs, drop TCs, or rewrite Expected.
- Do **not** explore Must ACs to invent a second plan. If a TC is too vague to automate, tester `FAILED` / `INPUT_MISSING` — do not guess.
- Locators stay out of markdown. Choose `getByRole` / accessible names in the spec after the UI exists. No CSS/XPath in `qa-ui-plan.md` or `qa-test-cases.md`.

## 1. Planner

Read `qa-test-cases.md` (and `test-plan.md` only to resolve Target URL / layer rollup). Explore the app at `E2E_BASE_URL` only to **discover locators** for those TCs (pattern: `automation-tests/templates/seed.spec.ts`).

Write `features/{slug}/qa-ui-plan.md` as a 1:1 index of the browser TCs — not a new scenario list:

| TC | Spec | Steps (verbatim from qa-test-cases) | Locator notes (roles/names only) |
|----|------|-------------------------------------|----------------------------------|

Every browser `TC-*` must appear once. No CSS selectors.

## 2. Generator

Create `automation-tests/specs/{slug}/*.spec.ts` from that index:

- `test('TC-N …')` implements that row only
- `getByRole` / accessible names
- Header: `// feature: {slug}`
- Import `@playwright/test` normally; import helpers from `../../lib/…` (nest one more `../` per slug segment)
- Assert the row’s **Expected** (visible text, roles, counts, ordering). Do not weaken it.
- After the asserted UI state, call `captureReviewScreenshot(page, "TC-N")`. Do not skip screenshots on pass.

## 3. Healer

```bash
cd automation-tests && npx playwright test
```

On failure: patch **locators and waits only**. Max **2** heal loops. Do not `test.skip`, drop assertions, merge tests, or change Expected to go green. AC mismatch in product → tester `BLOCKED`.

## Screenshots (mandatory when UI ran)

Config sets `screenshot: 'on'` with `outputDir` = `artifacts/{slug}/test-results`. Named review files still require `captureReviewScreenshot`.

Sign-off is not `passed` for the ui layer if `automation-tests/artifacts/{slug}/screenshots/` has no `.png`.

## Sign-off fields

Record in `features/{slug}/qa-signoff.md`: `E2E_BASE_URL`, `E2E_COMMAND`, `E2E_EXIT`, `E2E_SPECS` (`automation-tests/specs/{slug}/…`), `E2E_SCREENSHOTS` (`automation-tests/artifacts/{slug}/screenshots/`), `TOOLCHAIN` line.
