---
title: New-project checklist
description: The full customer surface after clone — AGENTS.md, config, deploy, tests, gitignore, smoke test.
---

Use this on every new engagement. The full customer surface is **AGENTS.md + config.json**, then deploy and test files if your runners are not the defaults.

1. Install: `pipeline-kit init --ide cursor` (or `claude-code` / `github` / `none`).
2. Paste the `AGENTS.md` routing table and a short product blurb. See [Adapt AGENTS.md](/docs/guides/agents-md).
3. Edit `.pipeline/config.json`:
   - `verify.rules` for your folders (or leave `[]`)
   - `deploy.targets` for your apps
   - `intake.jira.enabled` (`false` unless you use Jira)
4. Rewrite the local-deploy runbook and `deploy-local.sh` for your stack. See [Adapt local deploy](/docs/guides/local-deploy).
5. Skim `.pipeline/docs/DOCUMENT-STANDARD.md` before editing any other pack markdown.
6. Add `features/` and `.pipeline/state/` to `.gitignore`.
7. Open the repo root in the IDE. Confirm the `run-workflow` skill is visible.
8. Smoke test: ask “How does X work?” (expect `ask`) and “Add a small label change” (expect `feature-development`).

Optional later: tracker MCP, wiki pages after retro, [knowledge](/docs/capabilities/knowledge), [plugins](/docs/capabilities/plugins), [observability](/docs/capabilities/observability).
