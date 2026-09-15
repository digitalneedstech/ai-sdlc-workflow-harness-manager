---
name: architecture-visualization
description: >-
  When architecture_diagrams.enabled, turn settled Architect facts into
  validated Archify JSON/HTML under features/{slug}/diagrams/. Mermaid in
  architecture.md stays required. Fallback is mermaid, never a fake render.
---

# Architecture visualization (optional Archify)

| Attribute | Value |
|-----------|--------|
| Type | Skill |
| Audience | architect-agent, when this file is on the allowlist |
| Adapt | Do not add a product name. Flip `architecture_diagrams.enabled` only via `pipeline-kit plugins install archify`. |

Use the **installed** Archify Agent Skill and its bundled CLI. Do **not**
vendor Archify. Do **not** invent HTML, SVG, or PNG by hand. Do **not**
replace mermaid in `architecture.md`.

Parent checked [architecture-diagrams-policy.md](../feature-development/assets/architecture-diagrams-policy.md).
You enhance diagrams only when `ARCHIFY_ENABLED: true`. If the flag is
absent or false, skip this skill; mermaid-only is SUCCESS.

## When to run

After A2 is clear and mermaid in `architecture.md` is drafted (A3). Never
draw enhanced diagrams before technical decisions settle.

## Inputs

- Signed-off requirements and the mermaid already in `architecture.md`
- `pipeline-kit plugins status --plugin archify` (skill path, pin, Node)
- Installed skill: `SKILL.md` plus `bin/archify.mjs` (Node.js 18+)

## Work

1. Keep the three mermaid slots in `architecture.md` (context, modules,
   sequence or explicit `none`). They are the portable review baseline.
2. If `ARCHIFY_ENABLED` is not true, stop. No manifest required.
3. If Archify is missing, unpinned, or `node bin/archify.mjs doctor` fails:
   write `features/{slug}/diagrams/manifest.json` with
   `"status": "mermaid-fallback"` and a one-line reason. Do **not** BLOCK
   a valid mermaid architecture.
4. Otherwise author typed JSON from the mermaid topology (do not copy
   mermaid styling). Types: `architecture` for context and for
   containers/modules; `sequence` only when A3 requires a sequence
   diagram. Cap each diagram at about 12 primary nodes.
5. Unattended runs: `ARCHIFY_UPDATE_CHECK_DISABLED=1`. Do not start
   `preview`. Do not `brands capture` unless the user supplied a public URL.
6. After every JSON edit:
   `node bin/archify.mjs validate <type> <file.json> --quality showcase --json`
   Showcase must report 9 artifact checks, 0 errors, 0 warnings. Repair
   from diagnostics only (max two focused rounds).
7. Deliver once the candidate is frozen:
   `node bin/archify.mjs deliver <type> <file.json> <file.html> --quality showcase --json`
   Non-zero is not success. Do not claim a failed delivery succeeded.
8. After a zero-exit deliver, run
   `node bin/archify.mjs visual-check <file.html> --json` when Chrome is
   available. Exit 2 (`skipped`) is allowed. Never report
   `visual_review: passed` unless you inspected the HTML or screenshots.
9. Write `features/{slug}/diagrams/manifest.json` from the manifest
   template. Link JSON/HTML in `architecture.md` §11. Put status on
   `HANDOFF-architect.md`.

## Outputs

```text
features/{slug}/diagrams/manifest.json
features/{slug}/diagrams/*.json          # typed source, when delivered
features/{slug}/diagrams/*.html          # delivered HTML, when delivered
features/{slug}/diagrams/*.receipt.json  # validate/deliver/visual-check, when present
```

Leave generated files under `features/{slug}/`. Do not delete mermaid.

## Status values (mandatory)

| status | Meaning |
|--------|---------|
| `delivered` | At least one showcase `deliver` exited 0 |
| `mermaid-fallback` | Plugin missing, unpinned, validate/deliver failed, or skipped |
| `skipped` | `ARCHIFY_ENABLED` was false (no manifest required) |

## Anti-patterns

Replacing mermaid · BLOCKED only because Archify is missing · inventing HTML
without `deliver` · claiming visual review without inspection · starting
preview in an unattended Task · downloading an unpinned Archify from `main`.
