# Agent memory wiki

Reusable lessons from past pipeline runs. **Do not load this folder by
default.** [`INDEX.md`](INDEX.md) is the router: read a page only when a
trigger matches.

| Attribute | Value |
|-----------|--------|
| Type | Wiki handbook |
| Audience | retro-agent and the parent |
| Adapt | Add pages after a hard-won fix. Do not record customer names, secrets, or demo brands. |

## When to read

1. Scan [`INDEX.md`](INDEX.md).
2. If **any** trigger matches the current ask, error, or pipeline class, read
   that one page.
3. If nothing matches, skip.

## When to write

After a successful feature pipeline, or after a non-obvious failure you fixed:

1. Add `.pipeline/wiki/{short-slug}.md` (template below). Keep under ~120
   lines. Record the **wrong** approach too.
2. Add one row to [`INDEX.md`](INDEX.md).
3. Add the same row to the wiki table in root `AGENTS.md` if that file has one.
4. Prefer a wiki page over a new always-on rule. Change a skill only if the
   workflow itself was wrong.

## Page template

```markdown
# {Title}

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist when INDEX triggers match |
| Adapt | Add a new page after retro. Do not store secrets or customer identifiers. |

- **Layer:** pipeline | delivery | hooks | telemetry | ui
- **Load when:** {one-line trigger}

## Symptom
## Root cause
## Do not
## Convention
## Files
## Verify
```
