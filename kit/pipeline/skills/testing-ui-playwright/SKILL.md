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

Maps to [Playwright Test Agents](https://playwright.dev/docs/test-agents): **planner → generator → healer**. When `TEST_DESIGN_ENABLED` and `cases.json` exist, the generator is `pipeline-kit knowledge playwright` (not the model). CLI-only; optional Playwright MCP for exploration.

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

When `TEST_DESIGN_ENABLED: true`, `features/{slug}/test-design/cases.json` is the only case list. `qa-test-cases.md` is the human view. Do not invent a second plan from Must ACs.

Otherwise `features/{slug}/qa-test-cases.md` is the only case list (existing path: model writes specs 1:1).

- Implement every row whose Layer is `ui`, `e2e` (browser), or `a11y`.
- One Playwright `test()` per those `TC-*` IDs.
- Do **not** explore Must ACs to invent a second plan.
- Locators stay out of markdown. Role + accessible name only. No CSS/XPath.

## 1. Planner

Explore `E2E_BASE_URL` only to **confirm locators** for those TCs.

When test design is on, write `features/{slug}/test-design/locators.json` (same TC / step indexes, `role` + `name` only). Missing locators → `FAILED` `INPUT_MISSING`.

When test design is off, write `features/{slug}/qa-ui-plan.md` as today (1:1 index, roles/names only).

## 2. Generator

When test design is on:

```bash
pipeline-kit knowledge playwright --slug {slug}
```

Do not hand-write `.spec.ts`. Do not hand-edit generated specs to go green.

When test design is off: create `automation-tests/specs/{slug}/*.spec.ts` from `qa-test-cases.md` as today (`test('TC-N …')`, `getByRole`, `captureReviewScreenshot`).

## 3. Run and healer

```bash
cd automation-tests && npx playwright test
```

Wait for the command (do not background it). On failure, write `tester-rca-ui.md` first.

- `cause: test`: patch **locators.json** (test design) or locators/waits in the spec (legacy). Max **2**. Then regenerate if test design is on. Do not `test.skip`, drop assertions, or change Expected.
- `cause: product` or `unclear`: HANDOFF `NEEDS_APPROVAL`. Do not edit product source.

## Screenshots (mandatory when UI ran)

Config sets `screenshot: 'on'` with `outputDir` = `artifacts/{slug}/test-results`. Named review files still require `captureReviewScreenshot`.

Sign-off is not `passed` for the ui layer if `automation-tests/artifacts/{slug}/screenshots/` has no `.png`.

## Sign-off fields

Record in `features/{slug}/qa-signoff.md`: `E2E_BASE_URL`, `E2E_COMMAND`, `E2E_EXIT`, `E2E_SPECS` (`automation-tests/specs/{slug}/…`), `E2E_SCREENSHOTS` (`automation-tests/artifacts/{slug}/screenshots/`), `TOOLCHAIN` line.
