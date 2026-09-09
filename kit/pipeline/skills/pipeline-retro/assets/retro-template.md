# Retro template

| Attribute | Value |
|-----------|--------|
| Type | Template |
| Audience | The specialist that writes the artifact |
| Adapt | Fill placeholders only. Do not add a product, host, or customer name. |

Write to `features/{slug}/RETRO.md`.

```markdown
# Retro — {slug}

**change_class:** micro | minor | feature
**devops:** OVERALL=passed
**date:** {YYYY-MM-DD}

## What shipped
{3–6 sentences from spec/patch + deploy URLs}

## What went well
- …

## What was wrong / almost wrong
- … (include the approach that failed)

## Learnings persisted
- Wiki: {path or none} — triggers: …
- Rule: {path or none}
- Skill: none | {human follow-up}

## AGENTS.md
- [ ] Wiki table row added if a new page was created
```
