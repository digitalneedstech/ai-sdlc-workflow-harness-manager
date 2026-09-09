# Feature pipeline test layers

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist when INDEX triggers match |
| Adapt | Add a new page after retro. Do not store secrets or customer identifiers. |

- **Layer:** pipeline
- **Load when:** test-strategy, test-plan, UI e2e project, FEATURE_SIGNOFF, skip_tester, cases-only, `qa-test-cases` vs Playwright drift

## Symptom

Tester writes markdown only (`TESTS: cases-only`) or devops runs before automated e2e.

## Root cause

BA must plan layers early; tester must execute them once at feature level; devops must require `qa-signoff.md`.

## Do not

- Mark tester SUCCESS without `FEATURE_SIGNOFF: passed` when `skip_tester: false`
- Run tester-agent per child spec or between waves
- Put host product paths in new `.cursor` skills or `automation-tests` sources
- Install unpinned `@playwright/test` into product `package.json` (it belongs to `automation-tests/`)
- Recreate `features/{slug}/e2e/` or `features/{slug}/screenshots/` — specs and PNGs live in `automation-tests/`
- Let devops substitute health checks for required e2e
- Let Playwright planner invent scenarios from Must ACs instead of implementing `qa-test-cases.md` 1:1

## Convention

Which classes run tester is configured in `.pipeline/skills/feature-development/assets/tester-policy.md` (`run_tester` true/false per micro, minor, feature). Parent copies that into `route.md` `skip_tester`. One-run override: `RUN_TESTER: true|false`.

1. BA writes `features/{slug}/test-plan.md` plus each child’s `test-strategy.md` (feature class).
2. **Feature class (policy default on):** `e2e` is always required. Planning is per spec; **execution is one tester** after all child developer-critics.
3. Tester writes `qa-test-cases.md` from the BA plan, then runs `automation-tests/scripts/ensure-e2e-toolchain.sh` and the `testing-*` skills. Playwright must **not** invent a second scenario list: each browser `TC-*` becomes one `test('TC-N')` with that row’s Steps/Expected; locators (`getByRole`) are chosen after the UI exists. Each UI test writes a full-page PNG under `automation-tests/artifacts/{slug}/screenshots/` via `captureReviewScreenshot`.
4. Devops requires `qa-signoff.md` with `FEATURE_SIGNOFF: passed`.
5. A failing AC re-spawns the **owning child’s** developer.

Target URL and optional start command live in the test-plan Target block (`base_url`, `web_server_cmd`), not in harness source.

## Files

`.pipeline/skills/feature-development/assets/test-plan-template.md`, `test-strategy-template.md`, `qa-test-cases-template.md`, `qa-signoff-template.md`, `.pipeline/skills/testing-*/`, the project UI e2e directory (default `automation-tests/`)

## Verify

`features/{slug}/qa-signoff.md` exists with `FEATURE_SIGNOFF: passed` before devops. `automation-tests/` resolves specs and artifacts from `FEATURE_SLUG` and has no host-specific paths.
