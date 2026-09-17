# Agent-run observability

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist before enabling traces |
| Adapt | Do not put API keys here. Keys stay in the environment. |

This page is **not** the customer-app telemetry contract (`telemetry-agent`).
It covers traces of the coding agent's own tool calls.

**Full handbook:** `.pipeline/docs/OBSERVABILITY.md` in your project (installed on `pipeline-kit init`; canonical copy at the kit repo root `OBSERVABILITY.md`).

## Quick enable

```bash
pipeline-kit obs install --ide cursor --adapter langfuse
```

Open the **project folder** that contains `.cursor/hooks.json`. A multi-root window whose first folder is not that project will not fire these hooks.

The merge **appends** commands. Existing policy or Langfuse Node hooks stay.

## Identity (Langfuse)

| Langfuse | Cursor field | Format |
|----------|--------------|--------|
| Trace id | `conversation_id` | UUID with dashes stripped (32 hex) |
| Session id | same UUID | dashed UUID (`langfuse.session.id`) |
| Generation observation | `generation_id` | metadata `cursor_generation_id`; type `generation` |
| User | `user_email` | `langfuse.user.id` on every span |

Feature slug is metadata, not the session. Usage and scores are documented in **OBSERVABILITY.md**.

## Local first

```bash
pipeline-kit obs report
pipeline-kit obs flush
```

`report` never opens a network socket. `flush` ships new ledger rows only after a successful adapter response, then advances `.pipeline/state/obs/offset.json`.
