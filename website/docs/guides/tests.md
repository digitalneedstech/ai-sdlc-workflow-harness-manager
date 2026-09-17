---
title: Adapt tests
description: Point tester skills at this repository’s runners. Do not add a second Playwright tree.
---

Tester skills mention Playwright, API, and unit layers. Point them at **your** commands by editing the tester brief and the testing skills only if the defaults do not match.

| Your tests | What to tell the tester |
|------------|-------------------------|
| Jest / Vitest | `npm test` in the UI package |
| Playwright already in-repo | Use that project; do not add a second Playwright tree |
| JUnit / TestNG | `mvn test` or `gradle test` |
| pytest | `pytest path/to/module` |
| xUnit / NUnit | `dotnet test` |
| No UI | Skip Playwright; keep unit + API |

Do not add new test frameworks unless a requirement says so. Do not install unpinned `@playwright/test` into the product `package.json` — it belongs to `automation-tests/` when that tree exists.

Playwright must implement `qa-test-cases.md` 1:1, not invent a second scenario list. See [test layers](/docs/troubleshooting/test-layers).
