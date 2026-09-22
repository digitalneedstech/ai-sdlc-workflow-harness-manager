from pipeline_orchestrator.graph import AgentStep, SignoffGate, WorkflowSpec

PROVIDER = "demo"

SPEC = WorkflowSpec(
    name="accessibility-review",
    provider=PROVIDER,
    default_change_class="feature",
    nodes=[
        AgentStep(
            id="accessibility-review-agent",
            context_files=("briefs/accessibility-review-agent.md",),
        ),
        SignoffGate(id="accessibility", artifact_hint="a11y-findings.md"),
    ],
)
