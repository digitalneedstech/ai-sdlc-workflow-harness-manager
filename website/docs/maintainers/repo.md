---
title: This repository
description: Kit source layout, sync-kit, tests. Not a customer application.
---

This repository **is** the pipeline-kit source (installer + bundled pack). It is not a customer application.

- Pack body: `kit/pipeline/`
- Installer: `install.py` / `pipeline-kit` CLI
- Customer handbook: `CUSTOMER-GUIDE.md`
- Docs site: `website/` (this Docusaurus app; not copied on `init`)

## Refresh the bundled pack

Maintainers who edit a live `.pipeline` in this repo can refresh the bundle:

```bash
python3 install.py --sync-kit
```

## Tests

```bash
python3 -m pip install pytest
python3 -m pytest -q tests
```

Do not start a nested feature pipeline against this repo unless the change is to the kit itself.
