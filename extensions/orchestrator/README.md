# Orchestrator workflow demos

These are **associate workflows**, not first-party kit chains. Cloning this
repo does not install them into a customer app. Copy the folder below into
a project that was initialized with `--mode orchestrator`.

Kit mode never loads `pipeline_extensions/`.

## What each example shows

| Workflow | Graph | Idea |
|----------|--------|------|
| `security-review` | review agent → critic → sign-off | Findings plus a second pass, then HITL |
| `ci-audit` | audit agent → sign-off | Inspect CI config and required checks |
| `dependency-audit` | audit agent only | Fast pass, no gate |
| `accessibility-review` | review agent → sign-off | UI a11y against `USER_REQUEST` |

The generated stub from `pipeline-kit workflows --scaffold NAME` is one
agent plus one gate. The demos above are the next step: a real brief and,
for security review, a critic.

## Copy into an app

```bash
cp -R extensions/orchestrator/pipeline_extensions /path/to/your-app/
cd /path/to/your-app
pipeline-kit init --mode orchestrator --ide cursor
pipeline-kit workflows
```

You should see the four names with provider `demo` (or the project name if
you change `PROVIDER`).

```bash
# dry-run prints the graph without calling the SDK
pipeline-kit run --slug pci-sample --workflow security-review --dry-run

# fake runner writes state files and pauses at the first gate
pipeline-kit run --slug pci-sample --workflow security-review --runner fake \
  --request "review auth, secrets, and CSRF on the checkout routes"

# live Cursor SDK (needs CURSOR_API_KEY and the orchestrator extra)
pipeline-kit run --slug pci-sample --workflow security-review \
  --request-file features/pci-sample/request.md
pipeline-kit approve --slug pci-sample --gate security
pipeline-kit resume --slug pci-sample
```

`--request` is the user ask. `--slug` is only the folder name under
`features/`.

## Add your own

```bash
pipeline-kit workflows --scaffold my-review
```

Edit `pipeline_extensions/my_review.py` and `briefs/my-review-agent.md`.
Do not reuse a first-party name (`feature-development`, `jira-story`, …).
