# Root cause analysis template

Owned by **bug-fix**. The analyst copies this to `features/{slug}/rca.md`. It is the developer's requirement document on the bug workflow — the equivalent of `specification.md`.

Every factual claim cites `path:line`. Sections that do not apply say `N/A — reason`, never blank.

````markdown
# RCA — {slug}

**Source:** {ISSUE-KEY} | user report
**Status:** Ready for fix | Blocked — {why}
**Analyzed:** {YYYY-MM-DD}
**Severity signals:** {who is affected, how often, is there a workaround}

---

## 1. Symptom

**Expected:** {one line}
**Actual:** {one line}
**Trigger:** {conditions under which it happens}
**Expected behavior source:** issue AC | derived from {path:line} (label which)

## 2. Reproduction

**Layer:** unit | api | e2e | manual
**Command / steps**

```
{exact command, or numbered steps with inputs}
```

**Observed**

```
{output, error, or stack trace — redact tokens and customer data}
```

**Deterministic:** yes | intermittent — {conditions, {n} of {m} attempts}
**Environment needed:** {build, data state, account state, or none}

## 3. Localization

Data path from entry point to failure.

| Hop | Where | What happens |
|-----|-------|--------------|
| 1 | `{path:line}` | … |
| 2 | `{path:line}` | … |

### Candidates considered

| # | Candidate | Evidence for | Evidence against | Verdict |
|---|-----------|--------------|------------------|---------|
| 1 | … | `{path:line}` | … | **cause** |
| 2 | … | … | ruled out by {how} | rejected |

**Introduced by:** {change or version, read-only inspection} | unknown | pre-existing

## 4. Root cause

**One sentence:** {what the code does wrong, at `{path:line}`}

**Proof it produces the symptom:** {the concrete chain from that line to the observed output}

### Why-chain

| Why | Answer |
|-----|--------|
| Why does the symptom appear? | … (`path:line`) |
| Why does that happen? | … (`path:line`) |
| Why does that happen? | … |

**Last in-repo answer:** {where the chain stops, and whether the true cause is a dependency contract, a product decision, or a data state}

## 5. Blast radius

**Other callers of the faulty path**

| Caller | Same cause? | Note |
|--------|-------------|------|
| `{path:line}` | yes — in scope | … |
| `{path:line}` | no | different input shape |

**Other flows with the same defect:** {list, or none — checked {how}}
**What the fix could break:** {shared helper, persisted shape, public behavior}
**Why existing tests missed it:** {no coverage of {path} | test asserts {weak thing} at `{path:line}`}

## 6. Fix options

| Option | What changes | Cost | Risk | Leaves unfixed |
|--------|--------------|------|------|----------------|
| A — minimal | … | … | … | … |
| B — correct | … | … | … | none |

**Recommended:** {A | B} — {why, in one line}

## 7. Fix plan (developer implements exactly this)

| # | File | Function | Change |
|---|------|----------|--------|
| 1 | `{path}` | `{fn}` | {one line} |

**Callers to update:** {from blast radius, or none}

## 8. Regression case (mandatory)

**Layer:** unit | api | e2e | ui
**Location:** {where the test belongs, next to which existing tests}
**Asserts:** {the exact behavior}
**Fails today because:** {the root cause, stated so the developer can confirm the red run}

## 9. Out of scope

- {other defects found while investigating — reported to the parent, not fixed here}
- {refactors that would be nice and are not part of this cause}

## 10. Assumptions

| ID | Assumption | Why defaulted |
|----|------------|---------------|
| A-1 | … | … |
````
