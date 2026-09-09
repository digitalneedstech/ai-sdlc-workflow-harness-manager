# Feature pipeline change class

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist when INDEX triggers match |
| Adapt | Add a new page after retro. Do not store secrets or customer identifiers. |

- **Layer:** pipeline
- **Load when:** classifying micro / minor / feature, or tempted to run the full PM/BA ladder for a small UI tweak

## Symptom

A full PM → BA → telemetry → tester run for “add a label” / “wire one existing button,” or the opposite: skipping PM/BA on a new checkout flow.

## Root cause

One ladder does not fit all. Parent must classify **before** any `Task`.

## Do not

- Classify **micro** if there is a new route, API, persistence, authz, money, or PII.
- Implement in the parent chat “because it’s small.”
- Keep `skip_*` after the diff grows into a new screen.
- Start BA on feature class before `signoff-requirements.md`.
- Start Architect before requirements sign-off, or on micro/minor.

## Convention

Table in `.pipeline/skills/feature-development/assets/change-routing.md`. Write `features/{slug}/route.md`.

| Class | Chain |
|-------|--------|
| micro | developer → devops → retro |
| minor | developer → developer-critic → devops → retro |
| feature | PM → sign-off → Architect? → sign-off → BA → BA critic → sign-off → waves → one tester → devops → retro |

Unsure → **feature**. Mid-flight growth → rewrite `route.md` to `feature` and start **PM**.

## Files

`.pipeline/skills/feature-development/assets/change-routing.md`, `SKILL.md`, `hooks/subagent-start.py`

## Verify

`features/{slug}/route.md` exists before the first specialist. Hard-upgrade triggers force `feature`. Feature class has `skip_pm: false`. `skip_architect` is set from architect-policy after requirements exist.
