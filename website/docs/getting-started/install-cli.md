---
title: Install the CLI
description: Install pipeline-kit once per machine with uv, pipx, or ./install.sh from a clone.
---

Install the `pipeline-kit` **command** once on each developer machine. Then [initialize a project](/docs/getting-started/first-project) in each repo.

## From the repository URL

```bash
uv tool install git+<this-repo-url>
# or
pipx install git+<this-repo-url>
```

Replace `<this-repo-url>` with the git remote for this kit.

## From a local clone

```bash
git clone <this-repo-url>
cd pipeline-kit
./install.sh
```

`install.sh` selects `uv` or `pipx` and installs the same `pipeline-kit` command.

## Check it

```bash
pipeline-kit --version
```

## Common commands after that

```bash
pipeline-kit init [project]       # install/update a project pack
pipeline-kit setup                # install/update the user pack
pipeline-kit update [project]     # refresh while preserving config.json
pipeline-kit doctor [project]     # verify the active pack
pipeline-kit workflows [project]  # list available workflows
pipeline-kit uninstall [project]  # remove files managed by the kit
```

The old `python3 install.py` flags remain for compatibility and for the maintainer-only `--sync-kit` operation.

## Next

- [Where you can install](/docs/getting-started/install-scopes) — project vs user
- [IDE adapters](/docs/getting-started/ide-adapters)
- [First project](/docs/getting-started/first-project)
