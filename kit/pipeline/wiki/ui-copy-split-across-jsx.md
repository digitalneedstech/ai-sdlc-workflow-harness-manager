# UI copy split across JSX

- **Slug / date:** header-title-chorus, 2026-08-27
- **Layer:** pipeline
- **Load when:** a copy/label/wordmark rename, and a literal search for the visible string finds nothing

## Symptom

The user asks to change header (or other) text from string A to string B. Grep for A (e.g. `chorus2`) returns zero hits. It looks like the copy is already gone or never existed.

## Root cause

Brand wordmarks and two-tone titles often split one visible word across JSX, e.g. `Chor<span>us2</span>`. The concatenated DOM text is `Chorus2`; no source file contains the contiguous literal `chorus2`.

## Do not

- Conclude the ask is stale because exact-string search missed.
- Flatten the span “to make grep work” unless the patch explicitly drops two-tone styling.
- Search only `ecommerce-store/` when the ask names the operator console (`web/`).

## Fix / convention

For user-visible copy: search a distinctive substring (`us2`, `Chor`), the element (`<h1 className="logo">`), or nearby layout class. Confirm by reading the rendered concatenation, not a single token. Keep existing spans unless the patch says otherwise.

## Files

`web/src/App.tsx` (operator console topbar / sign-in wordmarks)

## How to confirm

Grep for the full visible string *and* a fragment inside the suspected span. If only the fragment hits, treat that as the copy site.
