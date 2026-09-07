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

Install the `pipeline-kit` tool once:

```bash
uv tool install git+<this-repo-url>
# or: pipx install git+<this-repo-url>
```

For a local clone, `./install.sh` performs the same tool install with `uv`
or `pipx`.

Set up a customer repository:

```bash
cd /path/to/customer-app
pipeline-kit init --ide cursor
pipeline-kit doctor --ide cursor
pipeline-kit workflows
```

Use `--ide claude-code`, `--ide github`, or `--ide none` when appropriate.
To install a shared user pack instead, run `pipeline-kit setup --ide cursor`.

`init` writes `<repo>/.pipeline`; `setup` writes `~/.pipeline`. At runtime
the project pack wins, otherwise the user pack is used. Run artifacts always
land in the **current** project’s `features/`.

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
| `pyproject.toml` / `install.sh` | Install the `pipeline-kit` command with `uv` or `pipx` |
| `install.py` | CLI implementation and backward-compatible Python installer |
| `kit/pipeline/` | Bundled pack copied to `<app>/.pipeline` |
| [CUSTOMER-GUIDE.md](../ai-agents-registry/packages/pipeline-kit/CUSTOMER-GUIDE.md) | Architect / developer handbook (canonical copy in `ai-agents-registry`) |
| `tests/` | Installer tests (`pytest`) |

Maintainers who edit a live `.pipeline` in this repo can refresh the bundle
using the backward-compatible maintainer command:

```bash
python3 install.py --sync-kit
```

How to add a workflow after install: see `.pipeline/README.md` in the
customer repo (“How to add a workflow”).

Common tool commands:

```bash
pipeline-kit init [project]       # install/update a project pack
pipeline-kit setup                # install/update the user pack
pipeline-kit update [project]     # refresh while preserving config.json
pipeline-kit doctor [project]     # verify the active pack and optional IDE adapter
pipeline-kit workflows [project]  # list available workflows
pipeline-kit uninstall [project]  # remove files managed by the kit
pipeline-kit --version
```

---

## Tests

```bash
python3 -m pip install pytest
python3 -m pytest -q tests
```
