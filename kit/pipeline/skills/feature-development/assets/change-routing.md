# Change-class routing

Owned by **feature-development**. Parent classifies **before** any specialist `Task`. Write `features/{slug}/route.md`. When unsure, use **`feature`**.

The **workflow** is chosen first, by [orchestration](../../orchestration/SKILL.md); this file decides the **class** inside it. Tracker workflows start from their `default_change_class` in [`.pipeline/config.json`](../../../config.json) and then apply the same hard-upgrade triggers below.

## Classes

| Class | Examples | Must all be true |
|-------|----------|------------------|
| **micro** | Label/copy/aria, CSS class, hide/show existing control, rename a string | No new behavior, no new function/API, no new screen/route, no persistence, no authz/money/PII, one obvious file |
| **minor** | One helper function, one button wired to an **existing** action, small validation message | No new screen/route, no new persistence/API/vendor, no new authz model, scope ≤ a few files |
| **feature** | New flow, screen, API, data, payments, permissions, telemetry, or unknown | Default. Any hard-upgrade trigger below |

## Hard upgrade → always `feature`

If **any** match, do not use micro/minor:

- New route, page, or information architecture
- New persistence, API, MCP, or third-party SDK
- Authn/authz, money, inventory, PII, secrets
- User did not name the file/control and scope is unclear
- User said “feature”, “end to end”, or pasted a multi-step journey

User override: if they type `CHANGE_CLASS: feature` (or micro/minor), honor it unless a hard-upgrade trigger contradicts **micro**.

## Tester by class

Load [tester-policy.md](tester-policy.md). Set `skip_tester` from that file’s `run_tester` column (or `RUN_TESTER: true|false` in the user ask). Feature default is on; micro/minor default is off. Changing the policy is how you turn testing on for selected classes.

## `features/{slug}/route.md` (required)

```markdown
# Route

**workflow:** feature-development | jira-story | jira-bug | jira-epic
**work_source:** text | jira
**jira_key:** {KEY} | n/a
**issue_type:** story | bug | epic | n/a
**change_class:** micro | minor | feature
**reason:** {one sentence}

skip_pm: true | false
skip_ba: true | false
skip_ba_critic: true | false
skip_telemetry: true | false
skip_developer_critic: true | false
skip_tester: true | false
```

| Field | Set by | Notes |
|-------|--------|-------|
| `workflow` | orchestration O3 | Chain and default skips come from the config entry with this name |
| `work_source` | orchestration O1 | `jira` means intake ran and wrote `intake.md` |
| `jira_key` / `issue_type` | intake HANDOFF | `issue_type` is the mapped type; the raw tracker type goes in `reason` when they differ |
| `change_class` | this file | Hard-upgrade triggers apply to every workflow, including bugs |

Hooks read `workflow` and the `skip_*` flags, so keep them one per line exactly as shown.

## Chains (parent follows exactly)

Chains below are the **text-sourced** workflow. Tracker workflows use the chain in [`.pipeline/config.json`](../../../config.json):

| Workflow | Chain | Plan source for BA |
|----------|-------|--------------------|
| `jira-story` | `intake → ba → ba-critic → waves → tester → devops → retro` | `intake.md` |
| `jira-epic` | same | `epic-plan.md` (one child spec per story) |
| `jira-bug` | `intake → bug-analyst → developer → developer-critic → tester → devops → retro` | `rca.md` replaces the spec |

`jira-bug` sets `skip_pm`, `skip_ba`, `skip_ba_critic`, `skip_telemetry` to `true` and keeps `skip_developer_critic: false`. Its tester default is on regardless of class — a fix without a verified regression is not a fix.

**feature** (default)

`pm → ba → ba-critic → waves (telemetry → developer → developer-critic per child) → tester → devops → retro`

Set all `skip_*` to `false`. Child specs live under `features/{slug}/{child}/`. One tester at the parent after all waves.

**minor**

`developer → developer-critic → devops → retro`

If tester-policy `run_tester` is true for minor (or `RUN_TESTER: true`): insert `tester-agent` before devops.

Parent **before** developer: write `patch.md` (problem, 1–3 ACs, out of scope), `telemetry-contract.md` with `EVENTS: none`, and `HANDOFF-telemetry.md` `STATUS: SUCCESS` (no telemetry Task). Skip PM, BA, BA critic.

`skip_pm: true`, `skip_ba: true`, `skip_ba_critic: true`, `skip_telemetry: true`, `skip_developer_critic: false`, `skip_tester:` from [tester-policy.md](tester-policy.md)

**micro**

`developer → devops → retro`

If tester-policy `run_tester` is true for micro: insert `tester-agent` before devops.

Parent **before** developer: same stubs as minor (`patch.md` can be 10 lines). Skip critic. Still a **separate Task** for developer (parent does not edit product code).

`skip_developer_critic: true`, other skips same as minor except `skip_tester` from policy.

## Complete

- Deploy gate: devops `OVERALL=passed` (all classes)
- When `skip_tester` is false (any class): `features/{slug}/qa-signoff.md` with `FEATURE_SIGNOFF: passed` before devops
- Pipeline complete: after **retro-agent** (`SUCCESS` or `NO_NEW_PAGE`)

If implementation grows (new route, new API) mid-flight: rewrite `route.md` to `feature` and start **PM** — do not keep skipping.
