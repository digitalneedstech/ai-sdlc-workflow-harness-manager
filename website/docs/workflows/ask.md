---
title: Ask
description: Read-only Q&A about this repository. No Task chain.
---

Use **`ask`** when the user is asking how / what / why / where / explain about **this repo**.

The chain is empty. The parent runs the loader, reads the allowlist, and answers. No specialist `Task`.

## When it must not run

- Product work (“add”, “fix”, “change”, “implement”) → `feature-development`
- Tracker issue key → Jira workflows (if intake is on)
- “Bootstrap QA knowledge for this repo” → `test-knowledge-bootstrap`
- Weather, trivia, off-repo asks → **do not** run the loader

## Anti-patterns

- Starting PM or BA because the question is long
- Editing product source “while we’re here”
- Loading the entire `.pipeline/wiki/` folder
