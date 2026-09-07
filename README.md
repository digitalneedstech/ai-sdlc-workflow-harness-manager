# Pipeline kit

Portable **workflow pack** and installer for coding agents.

Clone this repository, then install `.pipeline` into any customer project
(or into `~/.pipeline`). Process lives in the pack. The IDE is a thin adapter
(`run-workflow` only). The pack is not tied to a product, language, or IDE.

**Handbook (architects and developers):** read
[CUSTOMER-GUIDE.md](./CUSTOMER-GUIDE.md)
first — problem statement, architecture, install, `AGENTS.md`, config, deploy,
and tests. This README is the project landing page; that file is the
adaptation contract.

Requires **Python 3.11+**. No other runtime dependencies.

---

## Why this exists

Teams already use coding agents. They lack a repeatable operating model:
IDE folders explode with skills, process is glued to one editor, every
customer’s stack leaks into the pack, and every ask becomes the same delivery
ladder.

How the architecture solves that — portable pack, workflow as the unit of
scale, per-step allowlists, config as the engagement overlay — is in the
guide:

- [Problem statement](./CUSTOMER-GUIDE.md#problem-statement)
- [How this architecture solves it](./CUSTOMER-GUIDE.md#how-this-architecture-solves-it)

---

## Quick start

Install into a customer repo (full flags and scopes:
[Install](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#2-install)):

```bash
git clone <this-repo-url> pipeline-kit
python3 pipeline-kit/install.py --project /path/to/customer-app
python3 pipeline-kit/install.py --project /path/to/customer-app --ide cursor
python3 pipeline-kit/install.py --project /path/to/customer-app --ide claude-code
python3 pipeline-kit/install.py --project /path/to/customer-app --ide none
python3 pipeline-kit/install.py --user
```

From inside this repo:

```bash
python3 install.py --project /path/to/customer-app
python3 install.py --uninstall --project /path/to/customer-app
```

`--project` (default: `.`) writes `<repo>/.pipeline`. `--user` writes
`~/.pipeline`. At runtime the project pack wins; otherwise the user pack is
used. Run artifacts always land in the **current** project’s `features/`.

After install, the same handbook is copied to
`.pipeline/docs/CUSTOMER-GUIDE.md` in the target repo.

---

## What you get after install

| Path | Role |
|------|------|
| `.pipeline/` | Workflows, skills, agent briefs, rules, wiki, loader |
| `.pipeline/config.json` | This engagement: chains, tracker, verify, deploy |
| `.pipeline/docs/CUSTOMER-GUIDE.md` | Copied handbook |
| `.cursor/skills/run-workflow/` or `.claude/skills/run-workflow/` | The only IDE-discovered skill |

Shipped workflows: `ask`, `feature-development`, `jira-story` / `jira-epic` /
`jira-bug`. Details:
[What you get](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#1-what-you-get).

---

## Adapt per customer

The kit is generic. Every new project must customize two files, then deploy
and test runbooks if the sample script does not match the stack.

| Step | Where |
|------|--------|
| Routing table + product blurb | [AGENTS.md](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#31-agentsmd-create-or-edit) |
| Verify, deploy targets, Jira on/off | [`config.json`](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#4-configjson--what-each-area-is-for) |
| Local start / health checks | [Adapt local deploy](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#5-adapt-local-deploy-different-tech) |
| Test runners | [Adapt tests](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#6-adapt-tests-different-runners) |
| Cursor / Claude Code / GitHub / none | [IDE and editor differences](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#7-ide-and-editor-differences) |
| Ignore run artifacts | [Git ignore](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#8-git-ignore-recommended) |
| Tracker MCP, wiki, hooks, new workflow | [Optional later](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#9-optional-later) |
| Loader, workflow JSON, secrets | [What you should not edit](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#10-what-you-should-not-edit) |
| End-to-end checklist | [New-project checklist](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#11-new-project-checklist) |

Must-configure overview:
[What you must configure](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md#3-what-you-must-configure-every-new-project).

---

## This repository

| Path | Role |
|------|------|
| `install.py` / `install.sh` | CLI: `--project`, `--user`, `--ide`, `--uninstall`, `--sync-kit` |
| `kit/pipeline/` | Bundled pack copied to `<app>/.pipeline` |
| [CUSTOMER-GUIDE.md](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md) | Architect / developer handbook (canonical copy in `ai-agents-registry`) |
| `tests/` | Installer tests (`pytest`) |

Maintainers who edit a live `.pipeline` in this repo can refresh the bundle:

```bash
python3 install.py --sync-kit
```

How to add a workflow after install: see `.pipeline/README.md` in the
customer repo (“How to add a workflow”).

---

## Tests

```bash
python3 -m pip install pytest
python3 -m pytest -q tests
```
