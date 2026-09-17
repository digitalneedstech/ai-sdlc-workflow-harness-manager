---
title: Adapt AGENTS.md
description: The installer does not write AGENTS.md. Paste a routing table so the harness is the entry point.
---

Root `AGENTS.md` is the first thing the agent reads. Without the table, it may start a full delivery ladder for a question, or implement a feature without the harness.

The installer does **not** edit this file. Paste or adapt:

```markdown
# {Project name} — agent instructions

{One paragraph: what this repo is. Language, how to test.}

**Default read.** For product work or a question about this repo, follow the
IDE `run-workflow` skill. Run the loader and read only `allowed_reads`.
Do not open every file under `.pipeline/skills/`.

Unrelated asks (weather, locations, trivia): do not run the loader.

## Which workflow to use

| User intent | What to do |
|-------------|------------|
| Product work (“work on …”, “fix …”, “change …”, “develop …”, “implement …”, “add …”, or a tracker issue key) | Follow the IDE `run-workflow` skill. Run `.pipeline/loader/load_workflow.py` (or `~/.pipeline/loader/load_workflow.py`). Read **only** `allowed_reads`. |
| Question about this repo (how / what / why / where / explain) | Same skill, workflow `ask`. No Task chain. |
| Bootstrap QA knowledge for this repo | Workflow `test-knowledge-bootstrap`. Not the feature ladder. |
| Unrelated asks | Do not run the loader. |

Chains and skips: `.pipeline/config.json`.
File lists: `.pipeline/workflows/`.
Specialist briefs: `.pipeline/agents/`.
```

Use the skill path that matches `--ide`.

Do **not** paste specialist briefs or skill bodies into `AGENTS.md`. Named Cursor Task types exist only with `--agent-stubs`.
