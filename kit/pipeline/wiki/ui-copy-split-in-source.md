# Visible copy split across source tokens

| Attribute | Value |
|-----------|--------|
| Type | Wiki |
| Audience | Parent or specialist when INDEX triggers match |
| Adapt | Add a new page after retro. Do not store secrets or customer identifiers. |

- **Layer:** ui
- **Load when:** a label or wordmark grep returns zero hits but the UI still shows the old text

## Symptom

The user asks to change visible text from string A to string B. A literal
search for A returns no matches. It looks as if the copy is already gone.

## Root cause

Framework templates often split one visible word across elements or
expressions (for example two adjacent text nodes, or a string built from
parts). The concatenated UI text is A; no source file contains the contiguous
literal.

## Do not

- Conclude the string is absent because grep failed.
- Search only one package when the ask names another UI tree.
- Rewrite unrelated branding to “make grep work”.

## Convention

1. Search for distinctive substrings of A, not only the full string.
2. Inspect the rendered DOM (or screenshots) to see how the word is composed.
3. Edit the tokens that concatenate to A. Keep the same structure unless the
   spec asks for a visual change.
4. Discover the UI tree from `REPO_ROOT`; do not assume a folder name.

## Files

The component or template the user named. Feature artifacts stay under
`features/{slug}/`.

## Verify

The UI shows B. A search for the old concatenated word no longer matches the
rendered output.
