---
title: Knowledge bootstrap
description: One-off QA catalog workflow. Not the feature ladder.
---

`test-knowledge-bootstrap` runs **`knowledge-curator-agent` only**. It maps Graphify `graph.json` plus adapters into `test-knowledge/_candidates/{run}/`.

## When to use

In the IDE: **Bootstrap QA knowledge for this repo** — after `pipeline-kit knowledge init` and a successful `knowledge extract`.

It is not `ask` and not `feature-development`. Heavy skips are on (no PM/BA/Architect/tester).

## Parent procedure

1. Run the loader for this workflow.
2. Spawn the curator Task.
3. Present `REVIEW.md`. A human approves, then `pipeline-kit knowledge promote --run`.

After promote, feature-class work can bind ACs to overlay nodes. See [Knowledge base](/docs/capabilities/knowledge).
