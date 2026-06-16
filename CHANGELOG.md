# Changelog

All notable changes to the LegalDown specification are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). LegalDown is in
early draft (v0.1) and is **not yet stable** — breaking changes may occur between draft revisions
without a major version bump until v1.0.

---

## [Unreleased] — 2026-06-16

### Definitions overhaul (BREAKING)

This revision reworks how defined terms are declared (spec §7). The goal was to support the way
lawyers actually define terms — including **inline, at first use** — while making the schema
*simpler*, not more complex. The full design rationale and the alternatives considered are recorded
in [`definitions-review.md`](definitions-review.md).

> **Breaking change.** Every existing `{{def:}}` declaration must be rewritten (see *Migration*
> below). This is acceptable because LegalDown is a v0.1 draft with no stability guarantee.

#### Changed

- **Declaration syntax — term first, then tag.** A definition is now declared by writing the term
  in quotation marks and placing `{{def: id}}` *immediately after it*. The defined term is the text
  inside the quotes. The directive emits no visible output of its own; it anchors the preceding term
  and registers the id.

  ```diff
  - {{def: confidential-info}}
  - **"Confidential Information"** means any non-public information disclosed by one side to the other.
  + "Confidential Information" {{def: confidential-info}} means any non-public information disclosed by one side to the other.
  ```

- **One syntax for sectioned and inline definitions.** The old model required a `{{def:}}` on its
  own line preceding a paragraph and only *inside* a Definitions section. The same `term + tag` form
  now works anywhere — including inline at first use:

  ```markdown
  The Provider shall perform the marketing services described in this Article
  (the "Services" {{def: services}}).
  ```

  This makes the previously unsupported "labeling / first-use" definition pattern
  (`Acme Corporation ("Provider")`) a first-class construct.

- **Definitions may appear anywhere.** The mandatory, single, first-positioned **Definitions
  section** is gone. A top "Definitions" heading remains a *recommended convention* for stipulative
  definitions but is no longer required or structurally constrained. Subheadings under a Definitions
  heading are now allowed.

- **Format-agnostic source.** Defined terms no longer carry emphasis markers (`**bold**`) in source.
  Quotation marks are the only delimiter. Whether a term renders bold, underlined, small-caps, or
  quoted is entirely a render-time decision driven by the style template (§13.7) — applying the
  separation-of-content-and-presentation principle (§1.2) to definitions.

- **Reference by location, not body.** A `{{def:}}` records only `(id, term, location)`. The format
  no longer stores or extracts a "definition text." `{{term:}}` links and generated glossaries
  resolve to the **section/clause** containing the definition. For tooling purposes (circular-
  reference detection, optional glossary previews) a definition's scope is its **containing
  paragraph** — a deterministic unit. Sentence-level extraction is deliberately not specified
  (unreliable in legal/multilingual text).

- **`{{term:}}` rendering** now takes the display term from the quoted span at the definition site
  (spec §7.3 / §13.4 step 3) instead of from `**"..."**`.

#### Added

- **Accepted quotation-mark delimiters (spec §7.2).** A defined set of opening/closing pairs is now
  specified — all accepted by default, configurable per document `language`:

  | Pair | Open / Close | Code points |
  |---|---|---|
  | Straight double | `"` / `"` | U+0022 / U+0022 |
  | Curly double | `“` / `”` | U+201C / U+201D |
  | Guillemets | `«` / `»` | U+00AB / U+00BB |
  | Reversed guillemets | `»` / `«` | U+00BB / U+00AB |
  | Low-high double | `„` / `“` | U+201E / U+201C |
  | Curly single | `‘` / `’` | U+2018 / U+2019 |
  | Low-high single | `‚` / `‘` | U+201A / U+2018 |
  | Single guillemets | `‹` / `›` | U+2039 / U+203A |

  Double-quote forms are recommended; single-quote forms are accepted but validators warn when a
  single-quoted term is ambiguous with an apostrophe (U+2019). *This also resolves a pre-existing
  inconsistency: §7.3 previously said terms were extracted from straight-quoted `**"..."**`, yet the
  French bilingual example used guillemets.*

- **Auto-derived identifiers (spec §7.2).** The `id` on `{{def:}}` may now be omitted; when omitted
  it is derived from the quoted term using the §5.3 slug algorithm (`"Services" {{def:}}` →
  `services`). Explicit ids remain recommended for stability and are required to disambiguate when
  two different terms would slug to the same id.

- **Definitions in attachment files (spec §7.2, §12.4).** A `{{def:}}` inside an attachment file now
  registers a document-wide term (ids remain unique across the combined document, per §15.10).
  Previously attachments could only *reference* terms via `{{term:}}`.

#### Removed

- The requirement that all `{{def:}}` declarations live in a single Definitions section.
- The requirement that the Definitions section be the first level-1 (`#`) heading.
- The prohibition on subheadings within the Definitions section.
- The recommendation to format defined terms as bold quoted text (`**"Term"**`).

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Definitions section is the first `#` heading | Error | **Removed** |
| Definitions section contains no subheadings | Error | **Removed** |
| All `{{def:}}` appear in the Definitions section | Error | **Removed** |
| Defined terms follow `**"Term"**` formatting | Warning | **Removed** (replaced) |
| `{{def:}}` immediately preceded by a recognized quoted span | — | **Added (Error)** |
| Two definitions auto-generate the same id (omitted ids) | — | **Added (Error)** |
| Defined term wrapped in emphasis markers in source | — | **Added (Warning)** |
| Single-quoted term ambiguous with an apostrophe | — | **Added (Warning)** |
| Circular definitions detected | Error | Error (now scoped to the containing paragraph) |
| Definition used before declaration | Warning | **Info** (first-use is normal) |
| `{{def:}}` identifiers are unique | Error | Error (unchanged) |
| `{{term:}}` resolves to a declared definition | Error | Error (unchanged) |
| Declared definition never referenced | Warning | Warning (unchanged) |

### Migration

To upgrade an existing document, rewrite each definition so the term sits in quotes **before** the
tag, drop the bold markers, and move everything onto one line:

```diff
- # Definitions {#definitions}
-
- {{def: confidential-info}}
- **"Confidential Information"** means any non-public information...
-
- {{def: services}}
- **"Services"** means the software development services described in Section {{ref: scope-of-work}}.
+ # Definitions {#definitions}
+
+ "Confidential Information" {{def: confidential-info}} means any non-public information...
+
+ "Services" {{def: services}} means the software development services described in Section {{ref: scope-of-work}}.
```

- `{{term:}}` references are **unchanged** — they still bind to the same ids, so no reference needs
  editing.
- The Definitions section is no longer required to be first and may now be placed anywhere; existing
  documents that keep it first remain valid.
- Terms previously hoisted into the Definitions section purely to get a defined-term label may now be
  defined inline at their first use instead.

### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §7 (rewritten), §8.1, §11.1, §13.4, §14.2,
  §15.2/§15.3/§15.4 validation tables, and the §16 examples.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — Definitions section, text-formatting
  note, validation summary, and the minimal example.
- [`README.md`](README.md) — NDA example, "Definitions are tracked" blurb, and the
  "Document Structure at a Glance" snippet.
- [`definitions-review.md`](definitions-review.md) — design review and rationale (new).
