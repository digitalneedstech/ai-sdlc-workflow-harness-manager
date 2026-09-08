# Pipeline kit — customer guide

Audience: **developers and senior architects** who need a delivery pipeline
they can install, adapt, and scale across many customer engagements — each
with a different process, stack, and IDE — without forking a new agent
framework every time.

The rest of this file is the adaptation handbook (install, `AGENTS.md`,
config, deploy, tests). Read the problem and architecture first.

---

## Problem statement

Teams already use coding agents. What they lack is a **repeatable operating
model** for those agents:

1. **Context explosion.** If every skill, agent brief, rule, and wiki page
   lives under `.cursor/` (or `.claude/`), the IDE auto-discovers them. Every
   turn loads far more than the current step needs. Cost and quality both
   degrade as the pack grows.

2. **Pipeline glued to one IDE.** Process (how you plan, specify, implement,
   test, deploy) was mixed with editor wiring. Moving from Cursor to Claude
   Code, or to a repo with no AI folder, meant copying and rewriting the
   whole tree.

3. **One customer’s process baked into another’s repo.** Folder names, ports,
   tracker projects, verify commands, and deploy targets leaked into skills.
   The next customer on Spring + Jira could not reuse the pack without a
   surgical rewrite.

4. **No productized install.** “Copy `.cursor` from last year’s repo” does
   not scale. Architects need project install, user install, and a path to
   org-wide defaults — with a clear override order.

5. **Every ask became the same ladder.** A “how does tax work?” question
   should not start PM → BA → developer. A bug should not run a full feature
   plan. Without a **workflow** as a first-class object, the parent invents
   a new procedure each time.

6. **Hard to add a process.** A new customer wants “architecture review”
   or “release checklist.” That should be a new workflow JSON + skill + a
   config chain — not a new platform.

The requirement: **one kit, many customers, many processes.** Process lives
in a portable pack. The IDE is a thin adapter. Each engagement customizes
config and a few runbooks, not the engine.

---

## How this architecture solves it

```text
IDE adapter (one skill)     .cursor | .claude | .github | none
        │
        ▼
   run-workflow             receptionist: pick workflow, run loader
        │
        ▼
   .pipeline pack           skills, agents, workflows, wiki, rules
        │
        ├── config.json     THIS engagement (verify, deploy, tracker)
        └── loader          allowlist for the current step only
        │
        ▼
   features/{slug}/         artifacts for this run (not product source)
```

**Portable pack, thin IDE.** All process files sit in `.pipeline/`. The IDE
folder holds **only** `run-workflow` (and optional hooks). Cursor, Claude
Code, and GitHub each get the same pack; only the adapter path changes
(`--ide cursor` | `claude-code` | `github` | `none`).

**Workflow as the unit of scale.** A workflow is a named procedure
(`ask`, `feature-development`, `jira-bug`, …) with a chain and a file
allowlist. Adding a customer-specific process means adding a workflow —
not cloning the kit. Different customers can enable different workflows
from the same pack.

**Allowlist per step.** The loader writes `allowed_reads` for the current
specialist. BA does not ingest the deploy runbook; the developer does not
ingest Jira intake. That is what keeps a large pack cheap enough to reuse
across accounts.

**Config is the engagement overlay.** Chains, tracker on/off, path-based
verify reminders, and deploy target names live in `.pipeline/config.json`.
Skills stay free of customer folder names and site URLs. The next account
changes config (and the local-deploy script), not the orchestration skill.

**Install scopes.** `--project` materializes `<repo>/.pipeline`. `--user`
materializes `~/.pipeline`. At runtime the project pack wins; otherwise
the user pack is used. Artifacts always land in the **current** repo’s
`features/`. Architects can later layer org template → user → project
without changing the runtime model.

**Receptionist, not a monolith.** `AGENTS.md` stays a routing table. The
agent does not load the pack until `run-workflow` runs the loader. Trivia
and off-repo asks skip the pipeline entirely.

What you take to the next customer: the **kit** (installer + bundled pack).
What you change per customer: `AGENTS.md`, `config.json`, deploy/test
runbooks. That is the scaling contract.

---

## 1. What you get

| Path | Role |
|------|------|
| `.pipeline/` | Workflows, skills, agent briefs, rules, wiki, loader |
| `.pipeline/config.json` | **Your** chains, tracker, verify reminders, deploy targets |
| `.pipeline/docs/CUSTOMER-GUIDE.md` | This guide (copied into the project on install) |
| `.cursor/skills/run-workflow/` or `.claude/skills/run-workflow/` | The only IDE-discovered skill |

Specialist briefs and skill bodies stay under `.pipeline/` so the IDE does
not auto-load them. The parent reads only the allowlist from the loader.

**Workflows shipped today**

| Name | When it runs |
|------|----------------|
| `ask` | Question about this repo (how / what / why / explain). No Task chain. |
| `feature-development` | Product work from chat (“add”, “fix”, “change”, “implement”). Feature class: PM → user sign-off → Architect (large stories) → user sign-off → BA → critic → user sign-off → developers. |
| `jira-story` / `jira-epic` / `jira-bug` | Tracker issue key, if Jira intake is enabled. Stories/epics use intake as the requirements pack (same Architect + sign-off gates). Bugs skip planning. |

---

## 2. Install

Install the command once on each developer machine:

```bash
# Directly from the repository
uv tool install git+<pipeline-kit-repo-url>

# Alternative
pipx install git+<pipeline-kit-repo-url>
```

From a local clone, `./install.sh` selects `uv` or `pipx` and installs the
same command.

Then initialize a customer project:

```bash
cd /path/to/your-app
pipeline-kit init --ide cursor
pipeline-kit doctor --ide cursor
pipeline-kit workflows
```

| Command | Purpose |
|---------|---------|
| `pipeline-kit init [project]` | Install/update `<repo>/.pipeline` and its IDE adapter |
| `pipeline-kit setup` | Install/update `~/.pipeline` and a user IDE adapter |
| `pipeline-kit update [project]` | Refresh managed files while retaining local `config.json` values |
| `pipeline-kit update --user` | Refresh the user pack |
| `pipeline-kit doctor [project]` | Check Python, pack, config, loader, marker, and optional IDE adapter |
| `pipeline-kit workflows [project]` | List workflows from the active project or user pack |
| `pipeline-kit uninstall [project]` | Remove managed project files |
| `pipeline-kit uninstall --user` | Remove managed user files |

Install/update commands accept `--ide cursor`, `claude-code`, `github`, or
`none`. Add `--agent-stubs` to create thin `.cursor/agents/*.md` files.

Resolution at run time: project `.pipeline` wins; otherwise `~/.pipeline`.
Run artifacts always go to **this project’s** `features/{slug}/`.

Open the repository root in the IDE so the skill folder is discovered.

The old `python3 install.py` flags remain available for compatibility and
for the maintainer-only `--sync-kit` operation.

---

## 3. What you must configure (every new project)

Two files. Nothing else is required for the first run.

### 3.1 `AGENTS.md` (create or edit)

Keep a short product blurb (what this repo is, how to build/test). Then add
the routing table. Do **not** paste specialist briefs or skill bodies here.

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
| Product work (“work on …”, “fix …”, “change …”, “develop …”, “implement …”, “add …”, or a tracker issue key) | Follow `.cursor/skills/run-workflow/SKILL.md` (or `.claude/skills/run-workflow/SKILL.md`). Run `.pipeline/loader/load_workflow.py` (or `~/.pipeline/loader/load_workflow.py`). Read **only** `allowed_reads`. |
| Question about this repo (how / what / why / where / explain) | Same skill, workflow `ask`. No Task chain. |
| Unrelated asks | Do not run the loader. |

Chains and skips: `.pipeline/config.json`.
File lists: `.pipeline/workflows/`.
Specialist briefs: `.pipeline/agents/`.
Specialist Tasks: `generalPurpose` plus `Follow .pipeline/agents/{name}.md`
(or the named Cursor type if you installed `--agent-stubs`).
```

Use the skill path that matches `--ide`.

**Why this file:** it is the first thing the agent reads. Without the table,
it may start a full delivery ladder for a question, or implement a feature
without the harness.

### 3.2 `.pipeline/config.json`

The installed file is a **generic template**. Edit the keys below. Do not put
secrets, host URLs, or tracker site URLs in any other pack file.

---

## 4. `config.json` — what each area is for

### 4.1 `verify.rules` — remind after edits

After a specialist edits a file, a hook (if present) injects a reminder.
Match a **path substring** from *your* tree.

```json
"verify": {
  "rules": [
    {
      "match": "/frontend/",
      "message": "You edited the UI. Run the frontend build and keep empty/error/loading states."
    },
    {
      "match": "/backend/",
      "message": "You edited the API. Run the unit tests for the module you changed."
    }
  ]
}
```

| Your stack | Typical `match` | Reminder |
|------------|-----------------|----------|
| React / Vue / Angular app in `web/` or `ui/` | `"/web/"` or `"/ui/"` | `npm run build` (or `ng build`) in that folder |
| Spring / Maven | `"/src/main/java/"` | `mvn -pl <module> test` |
| .NET | `"/src/"` | `dotnet test` |
| Python / Django / FastAPI | `"/app/"` or `"/src/"` | `pytest` for the module you touched |
| Go | `"/internal/"` | `go test ./...` |
| Mobile (`ios/`, `android/`) | `"/ios/"` / `"/android/"` | The existing unit/UI test command |
| Docs-only or unknown | `[]` | No reminder; add rules when folders are stable |

**Use case:** Developer changes `frontend/src/Cart.tsx`. The reminder fires.
They should not claim SUCCESS without a build.

Empty `[]` is valid. The pipeline still runs.

### 4.2 `deploy.target` / `deploy.targets` — which process to start

Devops receives `DEPLOY_TARGET` from the parent. Values must match **your**
runbook and script (section 5), not the sample names in the shipped script.

```json
"deploy": {
  "target": "auto",
  "targets": ["auto", "web", "api", "both"]
}
```

| Ask | Target you would inject |
|-----|-------------------------|
| Copy change on the homepage | `web` |
| API-only bug | `api` |
| New field on UI + new endpoint | `both` or `auto` |

The shipped `deploy-local.sh` still contains **sample** folder and port
logic. Until you rewrite it (section 5), `auto` will not start your apps
correctly. Set `targets` to the names you will implement.

### 4.3 `intake.jira` — tracker or not

| Situation | What to set |
|-----------|-------------|
| No Jira (or Azure Boards, GitHub Issues only) | `"enabled": false` |
| Jira + IDE MCP connected | `"enabled": true`, fill `mcp_namespaces` if the server name is not discovered |
| Jira types differ (`Defect`, `Incident`, `Spike`) | Edit `issue_type_map` |

```json
"intake": {
  "jira": {
    "enabled": false,
    "key_pattern": "\\b[A-Z][A-Z0-9_]+-[0-9]+\\b",
    "mcp_namespaces": [],
    "issue_type_map": {
      "story": "jira-story",
      "bug": "jira-bug",
      "defect": "jira-bug",
      "epic": "jira-epic",
      "default": "jira-story"
    }
  }
}
```

**Use case, enabled:** “Work on SHOP-1842” → intake fetches the issue →
story, bug, or epic workflow. No one pastes the ticket by hand.

**Use case, disabled:** The same sentence is treated as text
(`feature-development` or `ask`). Correct for repos with no tracker.

Connect the tracker MCP in the IDE. Tool names in config default to
`getJiraIssue` and `searchJiraIssuesUsingJql`. Change `tools` if your MCP
uses different names. Do not put the Jira site URL or API token in this file.

### 4.4 Leave as-is until you have a reason

| Key | Default meaning |
|-----|-----------------|
| `workflows.*` chains / `classes` | Delivery ladder (micro / minor / feature). Change only if you drop or add a specialist. Feature class includes `@signoff:*` and `architect-agent`. |
| `product.artifact_dir` | `features/` — analysis agents write here only. |
| `gates.retry_cap` | Critic `changes-required` retries (default 2). |
| `gates.require_planning_signoff_before_build` | User must approve PM / Architect / BA artifacts before waves (default true). |
| `waves.child_chain` | Per-child telemetry → developer → critic. |

PM, Architect, and BA follow **clarify-first**: they read prior `features/{slug}/`
artifacts (`decisions.md`, plan, architecture) before asking, then ask remaining
checklist items instead of silent defaults. Override Architect with
`RUN_ARCHITECT: true|false`. Size policy lives in
`.pipeline/skills/feature-development/assets/architect-policy.md`.

---

## 5. Adapt local deploy (different tech)

The shipped files assume a **sample** Node frontend and a sample HTTP
health check. They are placeholders. For any other stack, edit these three:

| File | What to change |
|------|----------------|
| `.pipeline/config.json` → `deploy.targets` | Names you will pass as `DEPLOY_TARGET` |
| `.pipeline/skills/local-deployment/assets/local-deploy-runbook.md` | How a human (and devops) starts **your** apps |
| `.pipeline/skills/local-deployment/scripts/deploy-local.sh` | Build, start, and health-check **your** folders and ports |

**Do not** leave sample folder names, sample ports, or sample process
names in the script if those paths do not exist in the customer repo.
Devops will report SUCCESS on the wrong stack.

### Examples

**React (Vite) + Node API**

- Targets: `web`, `api`, `both`, `auto`
- Web: `npm run build` then `npm run preview -- --host 127.0.0.1 --port 4173`
- API: `npm start` or `node dist/server.js` on 3001
- Health: `GET http://127.0.0.1:4173/` and `GET http://127.0.0.1:3001/health`

**Spring Boot + Angular**

- Targets: `ui`, `service`, `both`
- UI: `npm ci && npm run build` in `ui/`
- Service: `mvn -DskipTests package` then `java -jar` on 8080
- Health: `GET http://127.0.0.1:8080/actuator/health`

**Python API only**

- Targets: `api`, `auto`
- `pytest` (optional) then `uvicorn app:app --host 127.0.0.1 --port 8000`
- Health: `GET http://127.0.0.1:8000/health`

**Do not start a second copy** if the port is already listening. Check
health on the existing process instead.

Until the script matches the repo, you can set devops to a dry-run
(document “build only, no preview”) in the runbook so the pipeline can
still complete.

---

## 6. Adapt tests (different runners)

Tester skills mention Playwright, API, and unit layers. Point them at
**your** commands by editing the tester brief and the testing skills only
if the defaults do not match.

| Your tests | What to tell the tester (runbook or skill) |
|------------|--------------------------------------------|
| Jest / Vitest | `npm test` in the UI package |
| Playwright already in-repo | Use that project; do not add a second Playwright tree |
| JUnit / TestNG | `mvn test` or `gradle test` |
| pytest | `pytest path/to/module` |
| xUnit / NUnit | `dotnet test` |
| No UI | Skip Playwright; keep unit + API. Feature class may still need a sign-off file. |

Do not add new test frameworks unless a requirement says so.

---

## 7. IDE and editor differences

| Team uses | Install | `AGENTS.md` skill path |
|-----------|---------|------------------------|
| Cursor | `--ide cursor` | `.cursor/skills/run-workflow/SKILL.md` |
| Claude Code | `--ide claude-code` | `.claude/skills/run-workflow/SKILL.md` |
| GitHub (Copilot / agents) | `--ide github` | `.github/skills/run-workflow/SKILL.md` |
| CLI / no IDE | `--ide none` | Run `load_workflow.py` from the shell |

`--user --ide cursor` writes `~/.cursor/skills/run-workflow` so every repo
on that laptop can see the skill even without a project pack.

Named Cursor Task types (`developer-agent`, …) exist only with
`--agent-stubs`. Otherwise the parent uses `generalPurpose`.

---

## 8. Git ignore (recommended)

Add:

```gitignore
features/
.pipeline/state/
```

`features/` holds plans, specs, HANDOFFs, and deploy logs for one run.
`.pipeline/state/active-context.json` is the live allowlist. Most teams do
not commit those. Commit `features/` only if you want specs in git.

---

## 9. Optional later

| Item | When a real project needs it |
|------|------------------------------|
| Tracker MCP | Jira (or compatible) workflows. Enable `intake.jira` and authenticate the MCP in the IDE. |
| Wiki | After a painful run, retro adds one page under `.pipeline/wiki/`. Start with the shipped index or empty it. |
| `.pipeline/rules/*.mdc` | Durable coding standards. They do **not** auto-apply in Cursor (not under `.cursor/rules`). Mention a rule in `AGENTS.md` or on a step allowlist. |
| Hooks | Not copied by the installer. Copy `.cursor/hooks/` + `hooks.json` if you want allowlist enforcement, commit-deny, and verify nudges. The pipeline runs without them. |
| New workflow | See `.pipeline/README.md` (“How to add a workflow”). |

---

## 10. What you should not edit

- `.pipeline/loader/` — allowlist CLI
- `.pipeline/workflows/*.json` — unless you add a workflow
- `.pipeline/agents/*.md` and most skills — unless deploy/test commands are wrong
- Secrets, tokens, tracker site URLs — environment or IDE MCP settings only

---

## 11. New-project checklist

1. Install: `pipeline-kit init --ide cursor` (or `claude-code` / `none`).
2. Paste the `AGENTS.md` table (section 3.1) and a short product blurb.
3. Edit `.pipeline/config.json`:
   - `verify.rules` for your folders (or leave `[]`)
   - `deploy.targets` for your apps
   - `intake.jira.enabled` (`false` unless you use Jira)
4. Rewrite the local-deploy runbook and `deploy-local.sh` for your stack (section 5).
5. Add `features/` and `.pipeline/state/` to `.gitignore`.
6. Open the repo root in the IDE. Confirm the `run-workflow` skill is visible.
7. Smoke test: ask “How does X work?” (expect `ask`) and “Add a small label change” (expect `feature-development`).

That is the full customer surface: **AGENTS.md + config.json**, then deploy
and test files if your tech is not what the sample script starts.
