---
title: Knowledge base
description: Opt-in QA overlay. Graphify extracts structure; humans promote catalogs; test-designer writes cases.
---

The knowledge base is an **opt-in QA overlay**. `pipeline-kit init` does **not** enable it. Absent `test_design.enabled`, the feature ladder is unchanged.

It is **not** the pack wiki (agent memory) and **not** Graphify itself. Graphify is an optional plugin the overlay consumes.

## One-time bootstrap

```bash
pipeline-kit init --ide cursor
pipeline-kit knowledge init --register-skill
# If Graphify is missing:
uv tool install graphifyy
pipeline-kit knowledge extract
```

`knowledge init` creates `test-knowledge/` and sets `test_design.enabled`. `--register-skill` registers the official Graphify IDE skill (same as `plugins install graphify`).

`knowledge extract` runs official `graphify extract . --code-only` and writes `graphify-out/graph.json`. Pipeline Kit never imports Graphify and never invents a substitute graph. If extract fails, stop and run the official CLI.

Then in the IDE: **Bootstrap QA knowledge for this repo**. That is workflow `test-knowledge-bootstrap`. Approve one Markdown report, then promote.

```bash
pipeline-kit knowledge status
pipeline-kit knowledge validate --run
pipeline-kit knowledge promote --run
```

Reviewed catalogs under `test-knowledge/` are usually committed. `graphify-out/` is Graphify-owned — commit it if the team wants a shared graph; ignore it if each checkout re-extracts.

## Each feature (only if the flag is on)

1. Architect writes `test-design/model-delta.json` or `no_test_model_change`.
2. BA binds Must ACs to overlay nodes and a lowest test level.
3. `test-designer-agent` writes `cases.json` and `qa-test-cases.md`.
4. You sign off BA. Waves run developer → critic.
5. Tester wave: parallel unit / api / ui Tasks. UI codegen is:

```bash
pipeline-kit knowledge render --slug {slug}
pipeline-kit knowledge playwright --slug {slug}
pipeline-kit knowledge promote-feature --slug {slug}
```

`knowledge playwright` is a **projector** of `cases.json` + `locators.json` into the existing `automation-tests/` tree. It is not Graphify and not `pipeline-kit plugins`.

## CLI

| Command | Purpose |
|---------|---------|
| `knowledge init` | Overlay + `test_design.enabled` |
| `knowledge extract` | Official Graphify extract |
| `knowledge status` | CLI and `graphify-out` |
| `knowledge validate --run` | Candidate report |
| `knowledge promote --run` | Human-approved catalogs |
| `knowledge render --slug` | Render cases |
| `knowledge playwright --slug` | Project Playwright specs |
| `knowledge promote-feature --slug` | Promote per-feature artifacts |

See also [Graphify plugin](/docs/capabilities/graphify) and [bootstrap workflow](/docs/workflows/knowledge-bootstrap).
