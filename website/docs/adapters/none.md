---
title: No IDE
description: Pack only. Run the loader from the shell. No auto-discovered skill.
---

`--ide none` installs `.pipeline/` and skips the editor adapter.

Drive a step yourself:

```bash
python3 .pipeline/loader/load_workflow.py --workflow ask --step parent --slug try-ask
```

Then read only the printed `allowed_reads`. This is the right mode for CI experiments or editors the kit does not adapter yet.

You still overlay `AGENTS.md` if any agent in that editor reads it. Observability hooks require an IDE that fires them — `obs install` needs `--ide cursor`, `claude-code`, or `github`.
