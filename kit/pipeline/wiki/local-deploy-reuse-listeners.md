# Local deploy — reuse existing listeners

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist when INDEX triggers match |
| Adapt | Put this project’s ports and health paths in the local-deploy runbook, not in this page. |

- **Layer:** delivery
- **Load when:** devops, `deploy-local.sh`, preview not coming up, a service already listening, secret material in chat

## Symptom

Local deploy fails because a port is in use, or the agent starts a second
copy of a long-lived process, or a secret appears in HANDOFF.

## Root cause

The runbook for **this repository** defines bind addresses and probes. Starting
another process on a busy port, or killing a foreign PID, breaks the
operator’s session.

## Do not

- Start a second copy of a service whose port already answers.
- Put tokens, passwords, or bootstrap secrets in HANDOFF or wiki.
- Invent cloud or cluster deploy from this skill.

## Convention

Run only `.pipeline/skills/local-deployment/scripts/deploy-local.sh`. Follow
the project runbook. If a configured port already responds, health-check the
existing process. Record a PID only when this script started the process.

## Files

`.pipeline/skills/local-deployment/assets/local-deploy-runbook.md`,
`scripts/deploy-local.sh`, `features/{slug}/deploy-result.env`

## Verify

`OVERALL=passed` in `deploy-result.env`. Health lines match the runbook.
HANDOFF contains no secrets.
