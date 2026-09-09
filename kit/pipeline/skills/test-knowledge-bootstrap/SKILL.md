---
name: test-knowledge-bootstrap
description: >-
  Bootstrap the QA overlay from the official Graphify graph. One Markdown
  review, then promote. Not the feature ladder.
---

# Bootstrap QA knowledge

| Attribute | Value |
|-----------|--------|
| Type | Skill |
| Audience | The named agent, or the parent when this file is on the allowlist |
| Adapt | Do not add a product name. Graphify stays on its official CLI. |

This workflow is **not** feature-development. Do not write product specs or start PM/BA.

## Parent (no specialist work inline)

1. Run the loader with `--workflow test-knowledge-bootstrap --step parent`.
2. Require `graphify-out/graph.json`. If it is missing, run `pipeline-kit knowledge extract`. If extract fails, stop and show the official recovery lines. Do not invent a graph.
3. Choose a stable slug `qa-knowledge-bootstrap` and a `CANDIDATE_RUN` token (UTC timestamp is fine).
4. Spawn **one** `knowledge-curator-agent` Task.
5. Present `test-knowledge/_candidates/{run}/REVIEW.md`. Stop.
6. On approve: `pipeline-kit knowledge validate --run {run}` then `pipeline-kit knowledge promote --run {run}`.
7. On reject: do not promote. Ask for a revised run.

## Curator work

1. Bound **one area** (business capability) from optional seeds plus Graphify communities or paths. Legacy repos: propose scope in the review, then extract semantics for that scope only.
2. Map graph nodes and thin QA adapters (routes, APIs, auth, fixtures, existing tests) into candidate catalogs. Evidence: `observed` only when Graphify EXTRACTED plus source; else `inferred`. Never auto-`verified`.
3. Write candidates only under `test-knowledge/_candidates/{run}/`. Include `REVIEW.md` from the review template.
4. Brownfield with tests: map existing tests/helpers first; do not regenerate automation.
5. Brownfield without tests: routes/APIs/auth/states + unknowns; seed smoke/authz/negative cases as **design** IDs only.
6. Greenfield: empty overlay is valid; later architecture creates `planned` nodes.
7. Static reconcile only (graph/source hash). No browser probe.

## Anti-patterns

Importing Graphify · homemade file/symbol graphs · promoting without a human approve · writing live catalogs from the curator · starting the feature ladder · claiming certified bootstrap when extract failed.
