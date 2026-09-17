---
title: Authoring pack markdown
description: Types, headers, allowlists. Keep the pack enterprise-neutral.
---

When you add or edit markdown under `kit/pipeline/` (or `.pipeline/` after install), follow [DOCUMENT-STANDARD](/docs/reference/document-standard).

1. Pick a type (brief, skill, template, policy, wiki, rule, handbook).
2. Copy the header (Type / Audience / Adapt) and the section order for that type.
3. List the file on the workflow allowlist (`workflows/*.json`) if a step must read it.
4. Do not add the file under `.cursor/` or `.claude/` — the pack stays in `.pipeline/` so the IDE does not auto-load it.

This documentation site (`website/docs`) may be more narrative. Pack files stay precise, short, and product-neutral.

## Preview docs locally

```bash
cd website
npm install
npm start
```

Do not vendor Docusaurus into `kit/pipeline/` or the Python package.
