# Clarifying questions format

Owned by **feature-development**. BA uses this in spec-generation **S3** (max **7**). PM uses the same shape in product-planning **P3** (max **10**). Write to `features/{slug}/questions.md` and the user reply.

```markdown
Q1. [Decision this unblocks — e.g. who may delete records]
- A) … (Recommended)
- B) …
- C) Other: …

Why it matters: …
Default if unanswered: A
```

Rules:

- Never ask what the repo already answers.
- Each question must unblock a spec section (actors, primary flow, out of scope, data, auth).
- After answers, append them to `questions.md` and continue to S4.
