---
title: config.json reference
description: Workflows, waves, intake, product, test_design, architecture_diagrams, agent_observability, verify, gates, deploy.
---

Path: `.pipeline/config.json`. Do not put secrets or tracker site URLs in this file.

## `workflows`

Each key is a workflow name. Fields you will see:

| Field | Meaning |
|-------|---------|
| `source` | `text` or `jira` |
| `plan_source` | Artifact the planner reads (`prd.md`, `intake.md`, `epic-plan.md`, `rca.md`) |
| `chain` | Ordered specialist tokens and `@signoff:*` / `@waves` |
| `classes` | micro / minor / feature chains (`feature-development` only) |
| `skips` | `skip_pm`, `skip_ba`, `skip_architect`, `skip_telemetry`, … |
| `run_tester` | Force tester on (bugs) |
| `default_change_class` | Starting class for tracker workflows |

## `waves.child_chain`

Expanded per child listed in `features/{slug}/spec-order.md`. Default: developer → developer-critic.

## `intake.jira`

`enabled`, `key_pattern`, `mcp_namespaces`, `tools.issue` / `tools.search`, `epic_children_jql`, `max_children`, `issue_type_map`, `include_comments`, `write_back`.

## `product`

`artifact_dir` (default `features/`). `readonly_agents` may write only there.

## Opt-in blocks

| Block | Set by |
|-------|--------|
| `test_design` | `knowledge init` (`enabled`, `graph_path`, `playwright`, …) |
| `architecture_diagrams` | `plugins install archify` (`version` `v2.16.0`, `fallback` mermaid) |
| `agent_observability` | `obs install` (adapter, redact, dataset, retention) |

## `verify.rules`

Path substring + message. Optional `expect` regex for obs integrity.

## `gates`

`retry_cap` (default 2), `require_signoff_before_deploy`, `require_planning_signoff_before_build`, `complete_after` (`retro-agent`).

## `deploy`

`target` and `targets` list. Must match the local-deploy script.
