---
title: Deploy listeners
description: Do not start a second copy on a busy port. Do not put secrets in HANDOFF.
---

## Symptom

Local deploy fails because a port is in use, or the agent starts a second copy of a long-lived process, or a secret appears in HANDOFF.

## Cause

The runbook for **this repository** defines bind addresses and probes. Starting another process on a busy port, or killing a foreign PID, breaks the operator’s session.

## Do not

- Start a second copy of a service whose port already answers
- Put tokens, passwords, or bootstrap secrets in HANDOFF or wiki
- Invent cloud or cluster deploy from this skill

## Convention

Run only `.pipeline/skills/local-deployment/scripts/deploy-local.sh`. If a configured port already responds, health-check the existing process. Record a PID only when this script started the process.
