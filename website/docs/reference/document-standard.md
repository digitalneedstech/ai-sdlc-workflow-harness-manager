---
title: Document standard
description: How pack markdown is typed, headed, and kept enterprise-neutral.
---

`.pipeline/docs/DOCUMENT-STANDARD.md` (canonical copy in the kit under `kit/pipeline/docs/`) defines how to author pack files so they stay portable.

## Document types

| Type | Path | What a new project changes |
|------|------|----------------------------|
| Agent brief | `agents/*.md` | Almost never |
| Skill | `skills/*/SKILL.md` | Commands/paths only in deploy and test skills |
| Template | `skills/*/assets/*-template.md` | Placeholders only |
| Policy | `*-policy.md` | True/false columns |
| Wiki | `wiki/*.md` | Add a page after retro |
| Rule | `rules/*.mdc` | Narrow globs to this repo |
| Handbook | `docs/*.md`, pack `README.md` | Per engagement: project `AGENTS.md` and `config.json` |

## Required header

Every brief, skill, policy, wiki page, rule, and handbook starts with Type / Audience / Adapt.

## Section order

- **Agent brief:** Role → Isolation → Inputs → Procedure → Outputs → Failure → Parent next
- **Skill:** Purpose → When to use / not → Adapt → Procedure → Failure → Anti-patterns
- **Wiki:** Symptom → Root cause → Do not → Convention → Files → Verify

## Forbidden in the pack

Application folder names, sample shop names, internal platform names, demo localhost ports, and issue keys from a past engagement. Those belong in the project overlay (`config.json`, `AGENTS.md`, deploy/test skills).

Secrets never appear in pack markdown.
