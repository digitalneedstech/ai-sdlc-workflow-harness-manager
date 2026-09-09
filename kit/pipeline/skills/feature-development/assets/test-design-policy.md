# Test design policy (opt-in)

| Attribute | Value |
|-----------|--------|
| Type | Policy |
| Audience | Parent (inserts `test-designer-agent` when the flag is on) |
| Adapt | Do not add product folders. Flip `test_design.enabled` only via `pipeline-kit knowledge init`. |

Owned by **feature-development**. Parent reads `.pipeline/config.json` `test_design.enabled` before driving the feature / jira-story / jira-epic chain.

| `test_design.enabled` | Parent action |
|-----------------------|---------------|
| absent or `false` | Today's ladder. Do **not** spawn `test-designer-agent`. |
| `true` | After `ba-critic-agent` approve, spawn `test-designer-agent`, then `@signoff:ba`. |

Never insert this agent on `micro`, `minor`, or `jira-bug`. Never add it by editing the bundled chain.

When the flag is on, also pass `TEST_DESIGN_ENABLED: true` to Architect, BA, BA critic, test-designer, and tester. Architect writes `features/{slug}/test-design/model-delta.json` (or `no_test_model_change`). BA binds ACs to overlay nodes instead of free-form automation steps.

`@signoff:ba` presents child specs **and** the stepwise procedures in
`features/{slug}/qa-test-cases.md` (not catalog IDs alone).
