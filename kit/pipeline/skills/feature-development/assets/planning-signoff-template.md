# Planning sign-off

Owned by **feature-development**. The **parent** writes this file after the
user approves a planning artifact. Specialists do not write sign-off files.

Write one of:

- `features/{slug}/signoff-requirements.md`
- `features/{slug}/signoff-architect.md`
- `features/{slug}/signoff-ba.md`

```markdown
# Sign-off — {requirements | architect | ba}

**SIGNOFF:** approved
**role:** requirements | architect | ba
**slug:** {slug}
**artifact:** features/{slug}/plan.md | features/{slug}/intake.md | features/{slug}/epic-plan.md | features/{slug}/architecture.md | features/{slug}/HANDOFF.md
**approved_at:** {YYYY-MM-DD}
**note:** {optional user comment} | none
```

`SIGNOFF: approved` must appear exactly like that — parent and (customer) hooks
parse the token.

## Parent rules

- Do not spawn the next specialist until this file exists for that gate.
- On revise: delete or rewrite the file so it no longer says `approved`, then
  re-spawn the author with the user’s comments.
- Void **downstream** sign-offs when an upstream artifact changes:
  - requirements change → delete `signoff-architect.md` and `signoff-ba.md`
  - architecture change → delete `signoff-ba.md`
- Micro / minor / jira-bug never write these files.
