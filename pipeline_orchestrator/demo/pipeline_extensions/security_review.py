from pipeline_orchestrator.graph import AgentStep, SignoffGate, WorkflowSpec

PROVIDER = "demo"

SPEC = WorkflowSpec(
    name="security-review",
    provider=PROVIDER,
    default_change_class="feature",
    nodes=[
        AgentStep(
            id="security-review-agent",
            context_files=("briefs/security-review-agent.md",),
        ),
        AgentStep(
            id="security-review-critic-agent",
            context_files=("briefs/security-review-critic-agent.md",),
            prior_agent="security-review-agent",
            critic=True,
        ),
        SignoffGate(id="security", artifact_hint="security-findings.md"),
    ],
)
