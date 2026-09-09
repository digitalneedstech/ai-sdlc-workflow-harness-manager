---
name: testing-api
description: >-
  Tester-only. Run API or contract tests for the current feature slug per
  test-strategy.md. Parent and BA must not invoke directly.
disable-model-invocation: true
---

# API testing (tester skill)

| Attribute | Value |
|-----------|--------|
| Type | Skill |
| Audience | The named agent, or the parent when this file is on the allowlist |
| Adapt | Override the runner with `API_TEST_CMD` or `api_test_cmd` in the test strategy. Change the fallback command in this skill if this repository does not use pytest. |

Load only when **tester-agent** has `api: required` in `features/{slug}/test-strategy.md`.

## Adapt for this project

Prefer `API_TEST_CMD` or the strategy `api_test_cmd`. The fallback examples
below are defaults, not a required stack.

## Inputs

- `REPO_ROOT`, `FEATURE_SLUG`
- `TEST_STRATEGY_PATH`
- `API_TEST_CMD` — optional env override

## Steps

1. Read planned cases with layer `api`.
2. If `api_test_cmd` is set in the strategy or `API_TEST_CMD` is set, run that command from `REPO_ROOT`.
3. Else run existing API tests that cover the spec's HTTP/RPC/MCP surface (e.g. `uv run pytest -q tests/test_*api*.py` or files named in implementation notes).
4. Add tests using the repo's existing patterns (e.g. in-process test client). **Localhost only** — no `curl` to non-localhost hosts.

## Success

- Exit code `0`
- Every `api` planned case covered

## Failure

Return layer status `failed`. Contract violations in product code → tester `BLOCKED`.
