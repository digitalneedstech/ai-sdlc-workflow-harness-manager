---
title: UI copy split
description: Visible text may be split across tokens. A full-string grep miss is not proof the copy is gone.
---

## Symptom

The user asks to change visible text from A to B. A literal search for A returns no matches. It looks as if the copy is already gone.

## Cause

Templates often split one visible word across elements or expressions. The concatenated UI text is A; no source file contains the contiguous literal.

## Do not

- Conclude the string is absent because grep failed
- Search only one package when the ask names another UI tree
- Rewrite unrelated branding to “make grep work”

## Convention

1. Search for distinctive **substrings** of A.
2. Inspect the rendered DOM (or screenshots) to see how the word is composed.
3. Edit the tokens that concatenate to A. Keep the same structure unless the spec asks for a visual change.
