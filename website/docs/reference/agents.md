---
title: Agent roster
description: Fourteen specialist briefs. Analysis agents write only under features/.
---

Briefs live in `.pipeline/agents/*.md`. The parent passes a short job plus state paths. Do not paste prior HANDOFF bodies into the next Task.

| Agent | Role |
|-------|------|
| `intake-agent` | Tracker issue to disk (`intake.md`) |
| `product-manager-agent` | PRD, research, decisions |
| `architect-agent` | Technical design, mermaid, optional Archify |
| `ba-agent` | Specifications, spec-order, test plan |
| `ba-critic-agent` | Specification gate |
| `bug-analyst-agent` | Root cause (`rca.md`) |
| `developer-agent` | Implementer |
| `developer-critic-agent` | Implementation gate |
| `telemetry-agent` | Product event contract (opt-in) |
| `test-designer-agent` | Structured cases when knowledge is on |
| `tester-agent` | One layer: unit / api / ui at feature level |
| `devops-agent` | Local build, serve, validate |
| `retro-agent` | Post-success learning |
| `knowledge-curator-agent` | Overlay candidates from Graphify |

`product.readonly_agents` in config lists who must not edit product source. `test-designer-agent` is **not** added to class chains; the parent inserts it when `test_design.enabled` is true.
