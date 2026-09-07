---
name: testing-api
description: >-
  Tester-only. Run API or contract tests for the current feature slug per
  test-strategy.md. Parent and BA must not invoke directly.
disable-model-invocation: true
---

# API testing (tester skill)

Load only when **tester-agent** has `api: required` in `features/{slug}/test-strategy.md`.

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
