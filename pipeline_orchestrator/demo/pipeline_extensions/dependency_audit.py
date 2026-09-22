from pipeline_orchestrator.graph import AgentStep, WorkflowSpec

PROVIDER = "demo"

SPEC = WorkflowSpec(
    name="dependency-audit",
    provider=PROVIDER,
    default_change_class="feature",
    nodes=[
        AgentStep(
            id="dependency-audit-agent",
            context_files=("briefs/dependency-audit-agent.md",),
        ),
    ],
)
