---
name: testing-unit
description: >-
  Tester-only. Run unit tests for the current feature slug per test-strategy.md.
  Parent and BA must not invoke directly.
disable-model-invocation: true
---

# Unit testing (tester skill)

Load only when **tester-agent** has `unit: required` in `features/{slug}/test-strategy.md`.

## Inputs

- `REPO_ROOT`, `FEATURE_SLUG`
- `TEST_STRATEGY_PATH` — `features/{slug}/test-strategy.md`
- `UNIT_TEST_CMD` — optional env override

## Steps

1. Read planned cases with layer `unit`.
2. If `unit_test_cmd` is set in the strategy or `UNIT_TEST_CMD` is set, run that command from `REPO_ROOT`.
3. Else if `pytest` is available and a `tests/` tree exists, run targeted tests for files touched by this feature (from `implementation-notes.md` or spec scope). Example: `uv run pytest -q tests/test_module.py`.
4. Else if `package.json` has a `test` script at repo root or the app root named in the spec, run `npm test` there.
5. Add or extend unit tests under the repo's existing test layout when cases are missing. Do not add a new test framework.

## Success

- Exit code `0`
- Every `unit` planned case has a corresponding automated test or explicit mapping in `qa-test-cases.md`

## Failure

Return layer status `failed` with command and stderr summary. Product logic bugs → tester `BLOCKED`, not layer heal.
