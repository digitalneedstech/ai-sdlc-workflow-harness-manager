---
title: Add a workflow
description: Skill, workflow JSON, config chain, optional agent brief, receptionist row, loader smoke test.
---

A new customer process should be a **workflow**, not a fork of the kit.

1. Write `.pipeline/skills/{name}/SKILL.md` (plus `assets/` templates if needed).
2. Write `.pipeline/workflows/{name}.json` with `context.parent.files` and `context.steps.{agent}.files` (relative paths from the project root, `.pipeline/…` prefix).
3. Add `workflows.{name}` in `.pipeline/config.json` (`source`, `chain` or `classes`, `skips`). An empty `chain` means parent-only (see `ask`).
4. Optional: add `.pipeline/agents/{role}.md` and list it on that step’s allowlist.
5. If the receptionist should auto-pick it, add one row to `.pipeline/skills/orchestration/SKILL.md` (O1 / O3).
6. Activate and check the printed list:

```bash
python3 .pipeline/loader/load_workflow.py --workflow {name} --step parent --slug try-{name}
```

Confirm `allowed_reads` is the smallest set that step needs.

Follow [DOCUMENT-STANDARD](/docs/reference/document-standard) so the new markdown stays portable.
