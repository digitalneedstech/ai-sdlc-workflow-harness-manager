# Architecture diagrams policy (opt-in)

| Attribute | Value |
|-----------|--------|
| Type | Policy |
| Audience | Parent (passes `ARCHIFY_ENABLED` when the flag is on) |
| Adapt | Do not add product folders. Flip `architecture_diagrams.enabled` only via `pipeline-kit plugins install archify`. |

Owned by **feature-development**. Parent reads `.pipeline/config.json`
`architecture_diagrams.enabled` before spawning Architect on feature /
jira-story / jira-epic.

| `architecture_diagrams.enabled` | Parent action |
|---------------------------------|---------------|
| absent or `false` | Mermaid-only architecture. Do **not** require Archify artifacts. |
| `true` | Pass `ARCHIFY_ENABLED: true` to Architect. Architect still writes mermaid. Enhanced JSON/HTML is optional with `mermaid-fallback`. |

Never insert a new agent on the chain. Never add Archify by editing the
bundled class list. Missing GitHub CLI, Node, Chrome, or a failed deliver
must not block a valid mermaid `architecture.md`.

When the flag is on, Architect follows
[architecture-visualization/SKILL.md](../../architecture-visualization/SKILL.md)
during A3 and records `features/{slug}/diagrams/manifest.json`.
