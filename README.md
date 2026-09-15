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
`jira-bug`, `test-knowledge-bootstrap`. Structured test design is opt-in
(`pipeline-kit knowledge init`). Details:
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
| `knowledge/` | Optional QA overlay commands (consumes Graphify) |
| `pipeline_plugins/` | Optional Graphify and Archify plugin lifecycle |
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
pipeline-kit knowledge init       # opt-in QA overlay (does not run Graphify)
pipeline-kit knowledge extract    # official graphify extract --code-only
pipeline-kit knowledge status     # Graphify CLI and graphify-out
pipeline-kit plugins list         # optional Graphify / Archify plugins
pipeline-kit plugins install graphify
pipeline-kit plugins install archify
pipeline-kit plugins status
pipeline-kit plugins uninstall graphify
pipeline-kit plugins uninstall archify
pipeline-kit uninstall [project]  # remove files managed by the kit
pipeline-kit --version
```

---

## Optional plugins

Graphify and Archify are **optional**. `pipeline-kit init` does not install
them. The kit never vendors their renderers and never `import`s Graphify.

| Plugin | What it does | Default |
|--------|----------------|---------|
| **Graphify** | Official CLI writes `graphify-out/graph.json` for QA test design | Off until `knowledge init` / `plugins install graphify` |
| **Archify** | Pinned Agent Skill (`tt-a1i/archify` `v2.16.0`) for Architect HTML diagrams | Off until `plugins install archify`. Mermaid in `architecture.md` stays required |

### Graphify

Prerequisites: Graphify CLI (`uv tool install graphifyy`).

```bash
pipeline-kit knowledge init --register-skill --ide cursor
# same skill registration:
pipeline-kit plugins install graphify --ide cursor
pipeline-kit knowledge extract
pipeline-kit plugins status --plugin graphify
pipeline-kit plugins uninstall graphify --ide cursor
# also delete graphify-out/:
pipeline-kit plugins uninstall graphify --ide cursor --purge
```

Cursor project install writes `.cursor/rules/graphify.mdc` via Graphify's
own `graphify cursor install`. Uninstall calls `graphify cursor uninstall`.
`--purge` is the only way the kit deletes `graphify-out/`.

### Archify

Prerequisites: GitHub CLI **v2.90+** (`gh skill`), **Node.js 18+**. Chrome
is optional (visual-check). Project-scope Cursor install lands in
`.agents/skills/archify/`.

```bash
pipeline-kit plugins install archify --ide cursor --scope project
pipeline-kit plugins status --plugin archify
pipeline-kit plugins uninstall archify --ide cursor
```

Install runs the pinned command (never `main`):

```bash
gh skill install tt-a1i/archify archify --pin v2.16.0 --agent cursor --scope project
```

Uninstall removes only that managed skill directory. It does **not** delete
`features/*/diagrams/`. `gh skill` has no remove command; the kit verifies
source (`tt-a1i/archify`) and path before deleting.

Delivered HTML is interactive (inline JavaScript). Treat it as active
content. Unattended Architect runs set `ARCHIFY_UPDATE_CHECK_DISABLED=1`.
If Archify is missing or deliver fails, Architect keeps mermaid and records
`mermaid-fallback`.

Troubleshooting: `pipeline-kit plugins status --plugin archify` prints
recovery. Typical causes are missing `gh skill`, Node below 18, or an
unpinned skill.

Details: [CUSTOMER-GUIDE.md](./CUSTOMER-GUIDE.md#22-optional-plugins).

---

## Tests

```bash
python3 -m pip install pytest
python3 -m pytest -q tests
```
