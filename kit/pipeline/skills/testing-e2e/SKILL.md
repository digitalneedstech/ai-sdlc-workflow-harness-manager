---
name: testing-e2e
description: >-
  Tester-only. Run feature-scoped e2e journeys via the automation-tests
  Playwright project or an API integration path when the strategy has no UI.
  Parent must not invoke directly.
disable-model-invocation: true
---

# E2E testing (tester skill)

Load when **tester-agent** has `e2e: required`. **Mandatory for `change_class: feature`.**

## Inputs

- `REPO_ROOT`, `FEATURE_SLUG`
- `TEST_STRATEGY_PATH` — includes Target `base_url`, optional `web_server_cmd`, `health_path`
- Playwright project: `automation-tests/`

## UI path (base_url set)

1. Export `E2E_BASE_URL`, `E2E_WEB_SERVER_CMD`, `E2E_HEALTH_PATH`, `FEATURE_SLUG`, `REPO_ROOT`.
2. Ensure specs exist under `automation-tests/specs/{slug}/` (generator step in **testing-ui-playwright** skill if missing).
3. From the repo root:

```bash
automation-tests/scripts/ensure-e2e-toolchain.sh
cd automation-tests && npx playwright test
```

4. Sign-off requires exit code `0` for this slug's specs only.

## API-only path (no user-visible surface)

When `ui: n/a` and strategy still requires `e2e`, run an integration journey through the public API for **this feature** using the repo's existing test runner. Record the exact command in `qa-signoff.md`.

## Failure

- Missing `base_url` when ui/e2e needs a browser → `failed`
- Non-zero exit → `failed` or `BLOCKED` if the product violates an AC
