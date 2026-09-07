# Agent memory wiki (this repo)

Hard-won **Chorus / feature-pipeline** patterns from past runs. **Do not load this folder by default.** `AGENTS.md` and [`INDEX.md`](INDEX.md) are the router: read a page only when a trigger matches.

## When to read

1. Scan [`INDEX.md`](INDEX.md) or the compact table in root `AGENTS.md`.
2. If **any** trigger matches the current ask, error, port, or pipeline class, **read that one page**.
3. If nothing matches, skip.

## When to write (retro-agent or a hard-won fix)

After a successful feature pipeline, or after a non-obvious failure you actually fixed:

1. Add `.pipeline/wiki/{short-slug}.md` (template below). Keep under ~120 lines. Record the **wrong** approach too.
2. Add one row to [`INDEX.md`](INDEX.md) (triggers + link).
3. Add the same row to the wiki table in root [`AGENTS.md`](../../AGENTS.md).
4. Prefer a **wiki page** over a new always-on rule. Add a `.pipeline/rules/*.mdc` only if it is a durable coding standard (short, one concern). Change a **skill** only if the workflow itself was wrong.

## Page template

```markdown
# {Title}

- **Slug / date:** {feature slug}, {YYYY-MM-DD}
- **Layer:** pipeline | engine | storefront | hooks | telemetry
- **Load when:** {one-line trigger}

## Symptom
## Root cause
## Do not
## Fix / convention
## Files
## How to confirm
```
