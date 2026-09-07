# Spec order template

Owned by **feature-development**. BA copies this to `features/{slug}/spec-order.md` after drafting child specs.

The `**children:**` line is machine-read by pipeline hooks. Keep kebab slugs, comma-separated, no extra text.

```markdown
# Spec order — {slug}

**children:** {child-a}, {child-b}

## Waves

| Wave | Mode | Child slugs | Depends on |
|------|------|-------------|------------|
| 1 | sequential | {child-a} | none |
| 2 | parallel | {child-b}, {child-c} | {child-a} |

**Mode:** `sequential` = parent runs that wave’s children one after another. `parallel` = parent spawns one Task set per child in the wave and waits for all before the next wave.

## Dependency notes

- {child-b} needs {child-a} because {shared API / table / route}.
- Independent children share a parallel wave.

## Parent orchestration

Waves apply to **implementation only**: per child `telemetry → developer → developer-critic`.
Do not spawn tester until every child in **children** has an approved developer-critic HANDOFF.
```
