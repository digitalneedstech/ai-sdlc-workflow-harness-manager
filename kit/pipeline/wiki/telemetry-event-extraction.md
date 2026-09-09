# Telemetry event extraction

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist when INDEX triggers match |
| Adapt | Add a new page after retro. Do not store secrets or customer identifiers. |

- **Layer:** telemetry
- **Load when:** adding analytics/events, or a model wants `page_view` / `gtag` / “track everything”

## Symptom

Vanity events, PII in logs, or a contract with no consumer. Wrong events are worse than none.

## Root cause

Events were brainstormed instead of **extracted from the spec** and **gated**.

## Do not

- Emit properties not on the allowlist.
- Add GA/Segment/`gtag`/`fbq` unless a Must FR names the vendor.
- Use user id as a metric label. Log emails/passwords/`console.log` of secrets.

## Convention

`.pipeline/skills/observability-telemetry/SKILL.md`: candidates only from goals, journey endings, named errors, Must FRs, ACs, §9 with a consumer. Then G1–G7. Cap ≤ 5 events. Zero passing gates → `EVENTS: none` (SUCCESS).

`telemetry-agent` runs **after BA critic, before developer** (feature class). Micro/minor: stub `EVENTS: none`.

## Files

`observability-telemetry/SKILL.md`, `telemetry-agent.md`, `features/{slug}/telemetry-contract.md`

## Verify

Every kept event has BQ + FR/AC. Dropped rows list a gate id. Developer critic rejects extra events.
