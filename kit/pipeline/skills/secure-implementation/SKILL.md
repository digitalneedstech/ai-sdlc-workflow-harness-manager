---
name: secure-implementation
description: >-
  Invoke on feature implement (developer-agent) and developer-critic. Fill
  features/{slug}/security-preflight.md before claiming implementation SUCCESS.
  Not a substitute for the always-on security rule.
---

# Secure implementation (preflight)

Developer copies [assets/security-preflight-template.md](assets/security-preflight-template.md) to `features/{slug}/security-preflight.md` and checks every row that applies. Unchecked Must-security rows ⇒ developer HANDOFF is not SUCCESS.

Developer critic confirms the file exists and matches the diff (authz on new actions, no secret writes, no unsafe HTML).

Do not add a second security agent unless the spec is a security feature; this checklist is the gate.
