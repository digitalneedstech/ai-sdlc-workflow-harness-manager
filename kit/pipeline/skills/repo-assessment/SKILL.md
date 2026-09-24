---
name: repo-assessment
description: >-
  Assess this repo and draft missing rules, skills, workflows, and agents.
  Invoke when the user asks what agent files to add, to assess the repo, or
  to run a pack scan. Parent-only. Writes features/assessment/ only.
---

# Repo assessment

| Attribute | Value |
|-----------|--------|
| Type | Skill |
| Audience | The parent chat |
| Adapt | Do not add product folders, hosts, or tracker URLs. |

The parent stays in this skill. Do not spawn specialists. Do not start feature-development. Do not write `route.md`.

Scan decides which files exist. This skill asks the kickstarter questions in chat, runs scan, and fills only the drafts scan listed.

## When to run

The user wants an assessment, a pack scan, or the missing rules, skills, workflows, hooks, or agents for this repo.

Weather and other asks that are not about this repository: stop.

## Steps

1. If `graphify-out/graph.json` is missing, stop and tell the user to run `pipeline-kit knowledge extract`. Do not invent a file list.
2. Run `pipeline-kit scan --no-bootstrap` from the repo root. If it exits because the license or the graph is missing, relay its recovery line and stop. On a terminal, scan asks the missing questions itself. In this chat, it cannot, so the next step does.
3. Read `features/assessment/report.md`. If "Questions still open" lists any question, ask that question in this chat and wait. Append one `id: value` line to `features/assessment/answers.md`. Do not invent an answer. Run scan again. Do not write drafts while that section has questions. Older answers for data, impact, cadence, teams, or jira do not answer workflows, extra-persona, evals, or rule-types.
4. When no questions are open, read `features/assessment/prompt.md` and follow it. Write each rule, skill, agent, and workflow by copying the template in `.pipeline/skills/repo-assessment/assets/` and filling it from the answers and the code. Keep the headings and the attribute table. Scan does not write those bodies.
5. Leave `.cursor/`, `.pipeline/`, and `AGENTS.md` in the repo root unchanged. Tell the user the draft path from the report. Copying a draft into that path is a separate yes. Do not copy until they say so.

## Anti-patterns

Inventing a skill, agent, rule, or workflow whose id is not in `assessment.json`. Copying drafts into the live trees in the same turn. Reading `graphify-out/graph.json`. Starting a product workflow from this skill.
