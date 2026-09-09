---
name: jira-intake
description: >-
  Invoke when the pipeline must turn a tracker issue key into on-disk work
  input: the orchestrator matched an issue key, or the user pasted an issue id
  or tracker URL. Fetch the issue over MCP (read-only), normalize it to
  features/{slug}/intake.md, and classify it as story | bug | epic so the
  orchestrator can pick a workflow. Do not write specs, code, or tests.
---

# Tracker intake (read-only)

| Attribute | Value |
|-----------|--------|
| Type | Skill |
| Audience | The named agent, or the parent when this file is on the allowlist |
| Adapt | Change commands or paths only in deploy and testing skills. Planning skills stay product-neutral. |

Turn one issue key into **one normalized file** the rest of the pipeline can read without ever calling the tracker again.

**Success:** `features/{slug}/intake.md` is complete and factual, `ISSUE_TYPE` is set, no secrets or personal data leaked to disk.
**Failure:** invented requirements, a summarized description that drops acceptance criteria, or a tracker write.

All tracker settings come from `intake.jira` in [`.pipeline/config.json`](../../config.json). Never hardcode a site URL, project key, board id, or custom field id in this skill or in the output.

| When | Read |
|------|------|
| Issue type is an epic | [`../epic-breakdown/SKILL.md`](../epic-breakdown/SKILL.md) |
| I4 (normalize) | [assets/intake-template.md](assets/intake-template.md) |

---

## Steps

`I1 CONFIG → I2 CONNECT → I3 FETCH → I4 NORMALIZE → I5 CLASSIFY → I6 HANDOFF`

### I1 Config

Read `intake.jira`: `key_pattern`, `mcp_namespaces`, `tools`, `issue_type_map`, `include_comments`, `write_back`, and (epics only) `epic_children_jql` + `max_children`.

Confirm the injected `JIRA_KEY` matches `key_pattern`. If it does not, `BLOCKED` — do not fetch a guessed key.

### I2 Connect

1. If `mcp_namespaces` is non-empty, try those namespaces in order.
2. If it is empty (the portable default), **discover**: list available namespaces and pick the one exposing the configured `tools.issue` name. Inspect the tool schema before calling it.
3. If a namespace reports `needsAuth`, run its auth tool once, then retry.

No reachable tracker namespace ⇒ `BLOCKED` with this recovery for the parent:

```text
No tracker MCP tool is available for {KEY}. Either connect/authenticate the tracker MCP server,
set intake.jira.mcp_namespaces in .pipeline/config.json, or paste the issue summary,
description, and acceptance criteria into the chat and re-run with work_source: text.
```

### I3 Fetch (read-only)

Call `tools.issue` for the key. Collect, when present: key, issue type, status, priority, summary, description, acceptance criteria, labels, components, fix version, affected version, environment, reporter/assignee **display names only**, linked issues, parent, and attachment **file names**.

- **Reads only.** `write_back` is `false` by default: no transitions, comments, worklogs, or field edits. Ask the user first even when it is `true`.
- Do not download attachment bodies. Record names so the analyst can ask for one.
- Fetch comments only when `include_comments` is `true`, and then only comments that add requirements or reproduction facts.
- One retry on a transient error, then `BLOCKED`. A permission error is `BLOCKED`, not an empty issue.

### I4 Normalize

Load [assets/intake-template.md](assets/intake-template.md) and write `features/{slug}/intake.md`.

- Copy the **description and acceptance criteria verbatim** (converted to Markdown). Summarizing here is how Must requirements get lost.
- Convert tracker markup to plain Markdown; keep code blocks, tables, and step numbering intact.
- Mark anything the issue does not state as `Unknown — not in the issue`. Never fill a gap from imagination; the BA or bug analyst handles gaps with labeled assumptions.
- **Redaction (mandatory):** no tokens, keys, passwords, cookies, auth headers, connection strings, or customer PII (emails, phone numbers, account numbers, addresses). Replace with `[redacted]` and note the field. Display names of reporter/assignee are allowed; nothing else about them is.

### I5 Classify

Lowercase the issue type and map it through `issue_type_map`, falling back to `default`. Record both the raw type and the mapped workflow. A story that is really a defect stays whatever the tracker says — reclassifying is the user's call, not yours; flag it in `NOTES` instead.

### I6 Epic extension

When the mapped workflow is the epic one, continue with [`../epic-breakdown/SKILL.md`](../epic-breakdown/SKILL.md) **in this same Task** — you already hold the connection — and write `features/{slug}/epic-plan.md` before handing off.

---

## Outputs

```text
features/{slug}/intake.md
features/{slug}/epic-plan.md        # epic only, via epic-breakdown
features/{slug}/HANDOFF-intake.md
```

## Failure handling

| Situation | HANDOFF |
|-----------|---------|
| No tracker MCP reachable / auth fails | `BLOCKED` + the recovery block from I2 |
| Key not found or no permission | `BLOCKED` — never continue with an empty issue |
| Key does not match `key_pattern` | `BLOCKED` `INPUT_MISSING` |
| Description empty and no acceptance criteria | `ASSUMPTIONS_USED`; list what is missing so BA or the analyst asks |
| Issue type not in the map | `SUCCESS` with the map `default`; put the raw type in `NOTES` |
| Epic with no children | `ASSUMPTIONS_USED`; `epic-plan.md` records zero stories and the parent should ask the user |

## HANDOFF (`features/{slug}/HANDOFF-intake.md`)

```text
HANDOFF intake-agent → parent
STATUS: SUCCESS | ASSUMPTIONS_USED | BLOCKED
JIRA_KEY: {KEY}
ISSUE_TYPE: story | bug | epic | {raw type}
WORKFLOW: {mapped workflow}
INTAKE_PATH: features/{slug}/intake.md
EPIC_PLAN_PATH: features/{slug}/epic-plan.md | n/a
CHILDREN: n/a | {count} ({keys})
REDACTIONS: NONE | {fields}
NOTES: {ambiguities, missing ACs, raw type mismatch}
PARENT_NEXT: @signoff:requirements | bug-analyst-agent | stop for user
```

## Anti-patterns

Summarizing the description · inventing acceptance criteria · writing to the tracker · pasting the raw payload into chat instead of disk · storing tokens or customer data · fetching every comment · calling tracker MCP from the parent chat · hardcoding a site, project key, or field id.
