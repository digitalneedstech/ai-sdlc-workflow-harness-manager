# Kit mode

Default `--mode kit`. The portable pack is [`pipeline/`](./pipeline/).
`pipeline-kit init` copies it to `<app>/.pipeline` (or `setup` to
`~/.pipeline`).

Process lives here: skills, agent briefs, workflow allowlists, wiki,
rules, loader. The IDE adapter is a thin `run-workflow` skill.

To **add a workflow** in kit mode, see
[`extensions/kit/`](../extensions/kit/). To run the same first-party
graphs from Python instead of markdown, use
[`orchestrator/`](../orchestrator/) (`--mode orchestrator`).
