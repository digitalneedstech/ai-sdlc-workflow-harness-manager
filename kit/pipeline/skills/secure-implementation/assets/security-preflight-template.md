# Security preflight — {slug}

Copy to `features/{slug}/security-preflight.md`. Check what applies; use `N/A — reason` otherwise.

- [ ] Input from the client is validated on the server/engine (types, ranges, allowlists)
- [ ] No string-concatenated SQL / shell / HQL
- [ ] New or changed UI does not render unsanitized HTML
- [ ] Mutating or sensitive reads have authorization (existing session/authz patterns)
- [ ] No new secrets in source; no `.env` or token files edited
- [ ] Errors shown to users are generic; logs have no tokens, passwords, or raw PII
- [ ] Telemetry follows `telemetry-contract.md` (no extra properties, no vendor SDK unless FR)
- [ ] Dependencies: none added, or listed here with why existing code cannot do it
