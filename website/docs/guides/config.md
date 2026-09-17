---
title: Adapt config.json
description: Overlay verify rules, deploy targets, and Jira on/off. Do not put secrets or site URLs here.
---

The installed `.pipeline/config.json` is a **generic template**. Edit the keys below. Do not put secrets, host URLs, or tracker site URLs in any other pack file.

## `verify.rules`

After a specialist edits a file, a hook (if present) injects a reminder. Match a **path substring** from *your* tree. Empty `[]` is valid.

```json
"verify": {
  "rules": [
    {
      "match": "/frontend/",
      "message": "You edited the UI. Run the frontend build and keep empty/error/loading states."
    }
  ]
}
```

Optional `expect` is a regex the observability scorer uses for integrity checks.

## `deploy.target` / `deploy.targets`

Devops receives `DEPLOY_TARGET` from the parent. Values must match **your** runbook and script.

```json
"deploy": {
  "target": "auto",
  "targets": ["auto", "web", "api", "both"]
}
```

The shipped `deploy-local.sh` writes `OVERALL=failed` until you implement build, serve, and health. See [local deploy](/docs/guides/local-deploy).

## `intake.jira`

| Situation | Setting |
|-----------|---------|
| No Jira | `"enabled": false` |
| Jira + IDE MCP connected | `"enabled": true`, fill `mcp_namespaces` if discovery fails |
| Types differ (`Defect`, `Incident`) | Edit `issue_type_map` |

Connect the tracker MCP in the IDE. Do not put the Jira site URL or API token in this file.

## Leave as-is until you have a reason

| Key | Default meaning |
|-----|-----------------|
| `workflows.*` chains / `classes` | Delivery ladder. Change only if you drop or add a specialist. |
| `product.artifact_dir` | `features/` |
| `gates.retry_cap` | Critic retries (default 2) |
| `gates.require_planning_signoff_before_build` | User must approve planning artifacts before waves |
| `waves.child_chain` | Per-child developer → critic |

Full key list: [config reference](/docs/reference/config).
