# Pack gap

Read `context.md` in this directory. It is the install mode, the agent surface already installed, and the product areas in the Graphify graph. Do not re-read `graphify-out/graph.json`.

If the graph section says "Product code is missing", answer with only that fact and the re-extract command. Do not list workflows, skills, sub-agents, rules, or hooks. Do not describe `.pipeline`, `.cursor`, or `pipeline_extensions`.

Otherwise name product folders from that section (for example `news-site/pages`). Do not cite community numbers. When one area needs a closer look, run:

```bash
graphify query "<community or node name>" --budget 1500
```

Answer in chat. Do not create skills, agent briefs, workflows, rules, hooks, or config changes.

Install mode for this project: {{MODE}}

Return five lists. Every item needs a name, why it should exist, the graph community or node it cites, which installed item already covers it (or none), and how to add it in this mode.

## workflows

## skills

## sub-agents

## rules

## hooks

Reuse these agent roles when a new workflow chain can: `developer-agent`, `tester-agent`, `devops-agent`, `retro-agent`. Name a license area (`jira`, `governance`, `evidence`) when the addition needs one. Do not activate a license.

Do not recommend a second copy of a name already listed in `context.md`. Do not recommend a new workflow when a shipped skill or flag already covers that work (`playwright`, `test-design`, `secure-implementation`, `security-review`, `ci-audit`, `dependency-audit`, `accessibility-review`, and the workflows already installed).

How to add, for mode `{{MODE}}`:

{{ADD_STEPS}}
