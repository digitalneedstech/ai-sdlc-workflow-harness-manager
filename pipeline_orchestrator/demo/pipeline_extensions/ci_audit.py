from pipeline_orchestrator.graph import AgentStep, SignoffGate, WorkflowSpec

PROVIDER = "demo"

SPEC = WorkflowSpec(
    name="ci-audit",
    provider=PROVIDER,
    default_change_class="feature",
    nodes=[
        AgentStep(
            id="ci-audit-agent",
            context_files=("briefs/ci-audit-agent.md",),
        ),
        SignoffGate(id="ci", artifact_hint="ci-audit.md"),
    ],
)
