# Pipeline kit — agent instructions

This repository **is** the pipeline-kit source (installer + bundled pack).
It is not a customer application.

- Pack body: `kit/pipeline/` (kit mode)
- Orchestrator engine: `orchestrator/` (import `pipeline_orchestrator`)
- Extensions: `extensions/kit/`, `extensions/orchestrator/`
- Capabilities: `capabilities/` (plugins, knowledge, observability, eval, flags)
- Installer: `install.py`
- Customer handbook: `CUSTOMER-GUIDE.md`

Do not start a nested feature pipeline against this repo unless the user
asked to change the kit itself. Unrelated asks (weather, trivia): do not
load pack files.
