# Test strategy template

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Fill placeholders only. Do not add a product, host, or customer name. |

Owned by **feature-development**. BA copies this to `features/{feature-slug}/{child-slug}/test-strategy.md` during S4c. The feature-level rollup is `test-plan.md`. Tester and BA critic use both.

```markdown
# Test strategy — {child-slug}

**Spec:** features/{feature-slug}/{child-slug}/specification.md
**Feature:** {feature-slug}
**change_class:** feature | minor

## Layer matrix

| Layer | Status | Reason |
|-------|--------|--------|
| unit | required \| n/a | … |
| api | required \| n/a | … |
| e2e | required \| n/a | … |
| ui | required \| n/a | … |
| telemetry | required \| n/a | … |
| a11y | required \| n/a | … |

**Feature class:** `e2e` cannot be `n/a`. `ui: n/a` only when there is no user-visible surface.

## Target (required when e2e or ui is required)

| Field | Value |
|-------|-------|
| base_url | http://127.0.0.1:{port} |
| web_server_cmd | optional shell command to start the app on localhost |
| health_path | / (default) |

No host-product directory names here — only localhost URL and optional start command.

## Optional command overrides

| Field | Value |
|-------|-------|
| unit_test_cmd | optional; else skill picks an existing runner |
| api_test_cmd | optional; else skill picks an existing runner |

## Planned cases

| ID | AC | Layer | Preconditions | Steps | Expected |
|----|----|-------|---------------|-------|----------|
| PC-1 | AC-1 | unit | … | … | … |
| PC-2 | AC-2 | e2e | App at base_url | … | … |

No CSS selectors in planned cases — Playwright chooses `getByRole` after implementation. Steps and Expected remain the case contract.

## Coverage

- Must ACs with no planned case: none | {ids}
- Layers marked n/a with no reason: none | {layers}
```
