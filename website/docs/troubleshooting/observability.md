---
title: Observability troubleshooting
description: Empty ledger, missing Langfuse traces, multiple sessions, zero usage, unattributed scores.
---

| Symptom | Likely cause |
|---------|----------------|
| Ledger empty | Wrong workspace root; obs disabled; hooks not merged |
| No Langfuse trace | Keys missing; flush not run; 429 rate limit |
| Three sessions for one pipeline | Separate `conversation_id` per Task (expected today) |
| Usage all zero | Looking at a Task trace; or flush before `afterAgentResponse` |
| Model `auto-smart` | Placeholder until end-of-turn hooks |
| Scores all `unattributed` | No `subagentStart` + `step_context` from the loader |

```bash
pipeline-kit doctor
pipeline-kit obs status
wc -l .pipeline/state/obs/events.jsonl
tail -f .pipeline/state/obs/events.jsonl
```

Open the **project folder** that contains `.cursor/hooks.json` as the only workspace root.
