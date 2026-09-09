# Telemetry contract template

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Fill placeholders only. Do not add a product, host, or customer name. |

Owned by **observability-telemetry**. Telemetry-agent copies this to `features/{slug}/telemetry-contract.md`.

```markdown
# Telemetry contract — {slug}

**Status:** Ready for developer | N/A this increment
**Spec:** features/{slug}/specification.md

## Business questions

| ID | Question | Decision maker | Spec FR/AC |
|----|----------|----------------|------------|
| BQ-1 | … | … | … |

If none: write **EVENTS: none** and skip the table below.

Dropped (not in allowlist): `G#` + one-line reason (so they are not reintroduced in code).

## Events (allowlist)

| Event name | When (user/system action) | Properties (name: type / enum) | BQ | FR/AC |
|------------|---------------------------|--------------------------------|----|-------|
| `example_checkout_started` | User clicks pay | `item_count: int`, `has_promo: bool` | BQ-1 | FR-… |

Forbidden properties: email, password, token, raw prompt, full street address, unconstrained free text.

## Transport

- Use the logging or analytics helper already in this repository
- **No new vendor SDK** unless a Must FR names it

## Explicitly out of scope

- …
```
