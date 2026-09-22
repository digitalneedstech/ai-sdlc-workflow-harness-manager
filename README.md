# Pipeline kit

Portable **workflow pack** and installer for coding agents.

Clone this repository, then install `.pipeline` into any customer project
(or into `~/.pipeline`). Process lives in the pack. The IDE is a thin adapter
(`run-workflow` only). The pack is not tied to a product, language, or IDE.

**Documentation site (local):** [website/](./website/) — what the kit is,
install, capabilities, plugins, knowledge, observability, and CLI.

```bash
cd website
npm install
npm start
```

Opens `http://127.0.0.1:3000`. The in-repo adaptation contract remains
[CUSTOMER-GUIDE.md](./CUSTOMER-GUIDE.md) (copied to `.pipeline/docs/` on
`init`). This README is the project landing page.

**Agent-run observability (Langfuse, hooks, scores):**
[OBSERVABILITY.md](./OBSERVABILITY.md) — install without running the full
pipeline ladder, trace identity, token usage, score meanings, and ideal values.

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

Optional **orchestrator mode** (`--mode orchestrator`) runs the same
workflows from Python in the wheel via the Cursor SDK. Install the extra
(`uv tool install -e ".[orchestrator]"`) and pass the user ask with
`--request` or `features/<slug>/request.md` — the chat session is not
inherited. Kit mode stays the default. Associates add extra workflows with
`pipeline-kit workflows --scaffold NAME` (orchestrator only).
Copy-ready examples (security review, CI audit, dependency audit,
accessibility review): [`pipeline_orchestrator/demo/`](./pipeline_orchestrator/demo/).

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
| `.pipeline/docs/OBSERVABILITY.md` | Agent-run observability (after `init`; see repo [OBSERVABILITY.md](./OBSERVABILITY.md)) |
| `.cursor/skills/run-workflow/` or `.claude/skills/run-workflow/` | The only IDE-discovered skill |

Shipped workflows: `ask`, `feature-development`, `jira-story` / `jira-epic` /
`jira-bug`, `test-knowledge-bootstrap`. Structured test design is opt-in
(`pipeline-kit knowledge init`). Details: [What you get](./CUSTOMER-GUIDE.md#1-what-you-get).

---

## Adapt per customer

The kit is generic. Every new project must customize two files, then deploy
and test runbooks if the sample script does not match the stack.

| Step | Where |
|------|--------|
| Routing table + product blurb | [AGENTS.md](./CUSTOMER-GUIDE.md#31-agentsmd-create-or-edit) |
| Verify, deploy targets, Jira on/off | [`config.json`](./CUSTOMER-GUIDE.md#4-configjson--what-each-area-is-for) |
| Local start / health checks | [Adapt local deploy](./CUSTOMER-GUIDE.md#5-adapt-local-deploy-different-tech) |
| Test runners | [Adapt tests](./CUSTOMER-GUIDE.md#6-adapt-tests-different-runners) |
| Cursor / Claude Code / GitHub / none | [IDE and editor differences](./CUSTOMER-GUIDE.md#7-ide-and-editor-differences) |
| Ignore run artifacts | [Git ignore](./CUSTOMER-GUIDE.md#8-git-ignore-recommended) |
| Tracker MCP, wiki, hooks, new workflow | [Optional later](./CUSTOMER-GUIDE.md#9-optional-later) |
| Loader, workflow JSON, secrets | [What you should not edit](./CUSTOMER-GUIDE.md#10-what-you-should-not-edit) |
| End-to-end checklist | [New-project checklist](./CUSTOMER-GUIDE.md#11-new-project-checklist) |

Must-configure overview:
[What you must configure](./CUSTOMER-GUIDE.md#3-what-you-must-configure-every-new-project).

---

## This repository

| Path | Role |
|------|------|
| `pyproject.toml` / `install.sh` | Install the `pipeline-kit` command with `uv` or `pipx` |
| `install.py` | CLI implementation and backward-compatible Python installer |
| `knowledge/` | Optional QA overlay commands (consumes Graphify) |
| `pipeline_plugins/` | Optional Graphify and Archify plugin lifecycle (not observability) |
| `pipeline_observability/` | Agent-run traces, scores, Langfuse flush (`obs` CLI) |
| `pipeline_orchestrator/` | Code-owned workflow engine (`--mode orchestrator`) |
| `pipeline_orchestrator/demo/` | Example associate workflows to copy into an app |
| `kit/pipeline/` | Bundled pack copied to `<app>/.pipeline` |
| [CUSTOMER-GUIDE.md](./CUSTOMER-GUIDE.md) | Architect / developer handbook |
| `website/` | Local Docusaurus documentation (`npm start` in that folder) |
| `tests/` | Installer tests (`pytest`) |

Maintainers who edit a live `.pipeline` in this repo can refresh the bundle
using the backward-compatible maintainer command:

```bash
python3 install.py --sync-kit
```

To cut a release, bump the single source of truth (`VERSION`) rather than editing it by hand:

```bash
pipeline-kit version bump patch --commit --tag   # or: minor | major | version set 1.3.0
git -C /path/to/pipeline-kit push --follow-tags
```

The write and the commit always land in **this** repository — resolved from `--repo`, then
`$PIPELINE_KIT_REPO`, then upwards from the current directory — never in the project where the
kit is installed. Without `--commit` the files change and the git commands are printed instead.
Details: [website/docs/maintainers/repo.md](./website/docs/maintainers/repo.md).

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
pipeline-kit knowledge render --slug {slug}
pipeline-kit knowledge playwright --slug {slug}
pipeline-kit knowledge promote-feature --slug {slug}
pipeline-kit plugins list         # optional Graphify / Archify plugins
pipeline-kit plugins install graphify
pipeline-kit plugins install archify
pipeline-kit plugins status
pipeline-kit plugins uninstall graphify
pipeline-kit plugins uninstall archify
pipeline-kit features list        # named on/off capabilities
pipeline-kit features status
pipeline-kit features enable telemetry
pipeline-kit features disable telemetry
pipeline-kit obs install          # merge agent-run hooks (does not replace existing)
pipeline-kit obs status
pipeline-kit obs report
pipeline-kit obs flush
# Full guide: OBSERVABILITY.md
pipeline-kit uninstall [project]  # remove files managed by the kit
pipeline-kit version              # current kit VERSION (maintainers: bump / set)
pipeline-kit --version
```

---

## QA knowledge flow (opt-in)

`pipeline-kit init` does **not** enable this. Absent `test_design.enabled`,
the feature ladder is unchanged.

**One-time**

1. `pipeline-kit knowledge init [--register-skill]` — `test-knowledge/` + flag on.
2. `pipeline-kit knowledge extract` — official Graphify → `graphify-out/graph.json`.
3. In the IDE: **Bootstrap QA knowledge for this repo**. Approve one Markdown report, then promote.

**Each feature** (only if the flag is on)

1. Architect writes `test-design/model-delta.json` or `no_test_model_change`.
2. BA binds Must ACs to overlay nodes and a lowest test level.
3. `test-designer-agent` writes `cases.json` and `qa-test-cases.md`.
4. You sign off BA. Waves run developer → critic (telemetry only if `RUN_TELEMETRY`).
5. Tester wave: parallel unit / api / ui Tasks. UI codegen is
   `pipeline-kit knowledge playwright` (a projector of `cases.json`, not Graphify).

Graphify and Archify stay under Optional plugins. Observability is the bundled
add-on in that same section (`obs install`). Do not `import graphify`.

## Project features (opt-in flags)

Same keys as `.pipeline/config.json`. Does not replace `knowledge init` or
`plugins install`. Chat overrides (`RUN_TESTER`, `RUN_TELEMETRY`) still win
for a single run.

```bash
pipeline-kit features list
pipeline-kit features status
pipeline-kit features enable test-design
pipeline-kit features disable telemetry
```

---

## Optional plugins

`pipeline-kit init` does not turn these on. **External plugins** (Graphify,
Archify) use `pipeline-kit plugins`. **Agent-run observability** is a
bundled add-on: use `pipeline-kit obs install`, not `plugins install`.
Langfuse is the default adapter, not a plugin. The kit never vendors
Graphify or Archify and never `import`s Graphify.

| Add-on | Kind | What it does | Default |
|--------|------|----------------|---------|
| **Graphify** | External plugin | Official CLI writes `graphify-out/graph.json` for QA test design | Off until `knowledge init` / `plugins install graphify` |
| **Archify** | External plugin | Pinned Agent Skill (`tt-a1i/archify` `v2.16.0`) for Architect HTML diagrams | Off until `plugins install archify`. Mermaid in `architecture.md` stays required |
| **Agent-run observability** | Bundled add-on | Coding-agent traces and scores (hooks → ledger → Langfuse) | Off until `obs install`. Distinct from `telemetry-agent` |

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

### Agent-run observability

Traces and deterministic scores for **coding-agent** tool runs (Cursor / Claude /
Copilot hooks → local ledger → Langfuse). Distinct from customer-app
`telemetry-agent`. Not an entry in `plugins list`.

```bash
pipeline-kit init --ide cursor
pipeline-kit obs install --ide cursor --adapter langfuse
# LANGFUSE_* in .env, then use the IDE in that project root
pipeline-kit obs report
pipeline-kit obs flush
```

Install, identity model, Langfuse usage/cost, every score, ideal targets, and
troubleshooting: **[OBSERVABILITY.md](./OBSERVABILITY.md)**.

---

## Tests

```bash
python3 -m pip install pytest
python3 -m pytest -q tests
```
