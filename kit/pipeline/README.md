# Pipeline pack

IDE-agnostic workflow pack. Skills, agents, rules, commands, wiki, and the
loader live here so Cursor / Claude Code / GitHub do **not** auto-load every file.

**Customers adapting this pack to another repo or stack:** start at
[docs/CUSTOMER-GUIDE.md](docs/CUSTOMER-GUIDE.md) (same file as
`CUSTOMER-GUIDE.md` at the kit repo root).

IDE folders (`.cursor`, `.claude`, `.github`) should host only:

- the `run-workflow` skill
- hooks (still under `.cursor/hooks` in this repo; move them later)

## Install

From a clone of this repository (zero extra dependencies):

```bash
pipeline-kit init                         # creates ./.pipeline
pipeline-kit init /path/to/app
pipeline-kit init /path/to/app --ide cursor --agent-stubs
pipeline-kit setup                        # creates ~/.pipeline
pipeline-kit doctor --ide cursor
pipeline-kit workflows
pipeline-kit uninstall
pipeline-kit uninstall --user
```

| Scope | Pack location | IDE skill |
|-------|---------------|-----------|
| `--project` | `<repo>/.pipeline` | `<repo>/.cursor/skills/run-workflow` (or `.claude` / `.github`) |
| `--user` | `~/.pipeline` | `~/.cursor/skills/run-workflow` when `--ide cursor` |

Resolution when a workflow runs:

1. Walk up from the current project for `.pipeline/config.json` or `.pipeline/workflows/`.
2. If none, use `~/.pipeline`.
3. A project pack **always wins**.
4. `features/{slug}/` is always written in the **current project**, never in `$HOME`.
5. Active allowlist state is `{pack}/state/active-context.json`.

`--ide none` installs the pack only (no Cursor / Claude Code / GitHub). Hooks stay
project-local (`.cursor/hooks.json`); a user-level install does not add hooks.

The installer copies from `kit/pipeline/` in this repository, so it can
create `.pipeline` in an empty project. Maintainers refresh that bundle with
`python3 install.py --sync-kit` if they keep a live `.pipeline` working copy.
That command is maintainer-only; customer installs use the `pipeline-kit`
system command.

## What to add to AGENTS.md

The installer does **not** edit `AGENTS.md`. Paste or adapt this block so the
harness is the entry point:

```markdown
## Which workflow to use

| User intent | What to do |
|-------------|------------|
| Product work (“work on …”, “fix …”, “change …”, “develop …”, or a tracker issue key) | Follow the IDE `run-workflow` skill. Run `.pipeline/loader/load_workflow.py` (or `~/.pipeline/loader/load_workflow.py`). Read only `allowed_reads`. |
| Question about this repo (how / what / why / where / explain) | Same skill, workflow `ask`. No Task chain. |
| Weather, locations, or other unrelated asks | Do not run the loader. Do not load pack files. |

Chains and skips: `.pipeline/config.json` (project, else `~/.pipeline/config.json`).
File lists: `.pipeline/workflows/`. Specialist briefs: `.pipeline/agents/`.
Do not open other `.pipeline/skills/` files unless the active allowlist lists them.
```

Optional: if the team installed `--agent-stubs`, Cursor Task types such as
`developer-agent` exist as thin pointers. Otherwise parent Tasks use
`generalPurpose` and `Follow .pipeline/agents/{name}.md`.

## How to add a workflow

1. Write `.pipeline/skills/{name}/SKILL.md` (plus `assets/` templates if needed).
2. Write `.pipeline/workflows/{name}.json` with `context.parent.files` and
   `context.steps.{agent}.files` (relative paths from the project root, using
   the `.pipeline/…` prefix).
3. Add `workflows.{name}` in `.pipeline/config.json` (`source`, `chain` or
   `classes`, `skips`). An empty `chain` means parent-only (see `ask`).
4. Optional: add `.pipeline/agents/{role}.md` and list it on that step’s allowlist.
5. If the receptionist should auto-pick it, add one row to
   `.pipeline/skills/orchestration/SKILL.md` (O1 / O3).
6. Activate and check the printed list:

```bash
python3 .pipeline/loader/load_workflow.py --workflow {name} --step parent --slug try-{name}
```

Confirm `allowed_reads` is the smallest set that step needs. Do not add every
skill in the pack.

Existing workflows: `ask`, `feature-development`, `jira-story`, `jira-epic`,
`jira-bug`. Feature-class work can run `architect-agent` after signed-off
requirements (see `architect-policy.md` and `@signoff:*` in `config.json`).

## What you do not edit

- Hook scripts under `.cursor/hooks/` (optional; policy stays in
  `.pipeline/config.json`).
- Product source in the host repository, unless the user’s ask is about it.
- `AGENTS.md` from the installer. Teams edit it using the snippet above
  or the customer guide.
- Secrets, tracker site URLs, and project keys — those belong in this project’s
  `config.json` or the environment, never in a shared skill.

## Enterprise (guidance only — not implemented)

When several teams should share one pack, layer overrides. Do not bake org
URLs into the shared tree.

```text
org template repo  →  team defaults  →  ~/.pipeline (user)  →  <repo>/.pipeline (project wins)
```

Practical options later:

- **Golden template** (git clone or copier): every new service gets `.pipeline`
  plus a thin `run-workflow` adapter.
- **Internal package** (`pipx install company-pipeline-kit` from Artifactory).
  Same `install.py`, different distribution.
- **Dotfiles / MDM** for `--user` so laptops share one pack. Projects still
  override via local `.pipeline/config.json`.
- **Cursor Cloud / GitHub org**: check in only the thin adapter; keep the pack
  user- or org-hosted.
- Never put Jira site URLs, project keys, or secrets in the shared pack.
