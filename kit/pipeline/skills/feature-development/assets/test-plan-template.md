# Feature test plan template

Owned by **feature-development**. BA copies this to `features/{slug}/test-plan.md`. Per-child layer matrices still live in `{child}/test-strategy.md`.

```markdown
# Test plan — {slug}

**change_class:** feature
**spec_order:** features/{slug}/spec-order.md

## Layer rollup

| Layer | Status | Specs that require it |
|-------|--------|------------------------|
| unit | required \| n/a | {child slugs} |
| api | required \| n/a | … |
| e2e | required | … |
| ui | required \| n/a | … |
| telemetry | required \| n/a | … |
| a11y | required \| n/a | … |

**Feature class:** `e2e` cannot be `n/a`. `ui: n/a` only when no child has a user-visible surface.

## Target (required when e2e or ui is required)

| Field | Value |
|-------|-------|
| base_url | http://127.0.0.1:{port} |
| web_server_cmd | optional localhost start command |
| health_path | / (default) |

No host-product directory names — only localhost URL and optional start command.

## Planned cases

| ID | Spec | AC | Layer | Preconditions | Steps | Expected |
|----|------|----|-------|---------------|-------|----------|
| PC-1 | {child-a} | AC-1 | ui | App at base_url | … | … |
| PC-2 | {child-a} | AC-2 | api | … | … | … |
| PC-3 | {child-b} | AC-1 | unit | … | … | … |

Layers: `ui` = Playwright in the browser (unattended). `e2e` = journey (browser, or API journey if `ui: n/a`). `api` = existing HTTP/RPC runner. `unit` = existing unit runner. `telemetry` / `a11y` when the spec needs them.

No CSS selectors here — Playwright chooses `getByRole` after implementation. **Steps and Expected stay binding** for tester `qa-test-cases.md` and for each `test('TC-N')`.

## Coverage

- Must ACs with no planned case: none | {spec/AC ids}
- Layers marked n/a with no reason: none | {layers}

## Execution

One **tester-agent** at feature level after every child developer-critic approves. Not per spec. Not between waves.
```
