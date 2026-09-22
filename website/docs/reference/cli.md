---
title: CLI reference
description: All pipeline-kit commands — pack, knowledge, plugins, features, observability.
---

Global: `pipeline-kit --version` (same number as `pipeline-kit version`).

## Pack

| Command | Purpose |
|---------|---------|
| `init [project]` | Install/update `<repo>/.pipeline` and its IDE adapter. `--ide`, `--agent-stubs`, `--dry-run` |
| `setup` | Install/update `~/.pipeline` and a user IDE adapter |
| `update [project]` | Refresh managed files while retaining local `config.json` values. `--user` for the home pack |
| `uninstall [project]` | Remove managed project files. `--user` for the home pack |
| `doctor [project]` | Check Python, pack, config, loader, marker, and optional IDE adapter |
| `workflows [project]` | List workflows from the active project or user pack |

`--ide` is `cursor`, `claude-code`, `github`, or `none`.

## Knowledge

`knowledge init | extract | status | validate --run | promote --run | render --slug | playwright --slug | promote-feature --slug`

See [Knowledge base](/docs/capabilities/knowledge).

## Plugins

`plugins list | install graphify\|archify | status | uninstall` with `--ide`, `--scope project|user`. Graphify uninstall `--purge` deletes `graphify-out/`. Agent-run observability is a bundled add-on on the [Plugins](/docs/capabilities/plugins) page; install it with `obs`, not `plugins`.

## Features

`features list | status | enable \| disable` with ids `test-design`, `playwright`, `telemetry`, `tester`, `archify`, `jira-intake`, `agent-observability`.

## Observability

`obs install --adapter langfuse\|datadog\|otlp | uninstall | status | flush | report`

See [Agent-run observability](/docs/capabilities/observability).

## Maintainers

`version [show]` prints `VERSION`. `version bump patch|minor|major` and `version set X.Y.Z` update `VERSION` (and `website/package.json`) in the **kit git checkout** — resolved from `--repo`, then `$PIPELINE_KIT_REPO`, then upwards from the current directory — never in a customer project or the installed wheel. `--commit` commits there with `git -C`; `--tag` (requires `--commit`) adds `vX.Y.Z`. Also `--dry-run`. See [This repository](/docs/maintainers/repo).

## Legacy

`python3 install.py` remains for compatibility and maintainer `--sync-kit`.
