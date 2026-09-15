# Tester RCA — {layer}

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Fill placeholders only. Do not add a product, host, or customer name. |

Owned by **tester-agent**. Copy to `features/{slug}/tester-rca-{layer}.md` before any heal or approval ask.

```markdown
# Tester RCA — {layer}

**slug:** {slug}
**layer:** unit | api | ui
**tc:** TC-N
**ac:** AC-N | n/a
**owning_child:** {child-slug} | patch | rca
**command:** {exact command}
**cause:** test | product | unclear

## Expected (from the case)

{verbatim Expected / AC}

## Actual

{stderr excerpt or UI state}

## Proposed action

{test heal | product fix after user approval}

## Heal count

{0-2} / 2
```
