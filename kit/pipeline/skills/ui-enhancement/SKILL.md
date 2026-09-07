---
name: ui-enhancement
description: >-
  Invoke for a UI redesign of a screen or component. Copy/label/single-button
  without new behavior is NOT this skill — use feature-development CHANGE_CLASS
  micro. New UI flows use feature-development CHANGE_CLASS feature.
---

# UI enhancement (redesign only)

Use this skill when the user wants a **redesign** (layout, visual system, multiple components).

**Do not use** for “add a label”, “rename a button”, or “wire this existing control” — those are **feature-development** `micro` / `minor` ([change-routing.md](../feature-development/assets/change-routing.md)).

## Workflow

1. Confirm it is a redesign (not a micro patch). If not, stop and tell the parent to route `micro`/`minor`/`feature`.
2. Locate the UI under `ecommerce-store/` or `web/`. Ask at most 7 clarifying questions if scope is unclear.
3. Plan: files, no new libraries unless security-reviewed. Get user approval of the plan.
4. After approval, parent still spawns **developer-agent** in a **separate Task** (do not implement in the parent). Treat as **minor** or **feature** per change-routing hard-upgrade triggers.
