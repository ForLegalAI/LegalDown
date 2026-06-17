# Changelog

All notable changes to the LegalDown specification are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). LegalDown is in
early draft (v0.1) and is **not yet stable** — breaking changes may occur between draft revisions
without a major version bump until v1.0.

---

## [Unreleased]

### Contract body: sub-clause references, tail text, recitals, headings, citations — 2026-06-17

Removes the biggest body-level blockers for legal drafting. The theme is **reference granularity** —
you can now reference enumerated sub-clauses — plus a few small, self-contained relaxations. Design
rationale and the alternatives considered are in
[`body-constructs-review.md`](body-constructs-review.md). Conditional/optional clauses are
deliberately **out of scope** (an application/assembly layer above the markup).

#### Added

- **Anchorable list items (spec §5.2, §6.3, §13.3).** A list item MAY carry an explicit `{#id}`
  anchor, and `{{ref:}}` resolves to the item's full enumerated path — e.g. `{{ref: cov-dp}}` →
  "7.3(b)(ii)". This makes lettered sub-clauses referenceable for the first time, without hardcoding
  `(b)` (which would break on reorder).

  ```markdown
  Provider shall:

  - comply with all applicable laws, including:
    - data-protection law {#cov-dp}
  ```

  - List-item anchors are **explicit only** (never auto-generated) and share the one document-global
    identifier namespace with headings and attachments.
  - A list that contains an anchored item MUST be rendered with legal enumeration active, so the item
    has a stable label.
  - *(Standalone-paragraph anchors were considered and dropped — list items only.)*

- **Lead-in and concluding (tail) text (spec §8.4).** Specifies how "flush language" renders — a
  paragraph after an enumerated list (in the same list item, or after a list under a heading) is the
  clause's concluding text: it renders flush at the clause level with no enumeration label. No new
  syntax; this is standard CommonMark multi-block list items, now defined for legal output.

- **External citation marker (spec §6.5).** `{{cite: …}}` marks a free-form external citation
  (statute, regulation, case law, another contract). The entire argument is the citation text,
  rendered verbatim — LegalDown never parses or reformats it. It is the only directive that **permits
  commas** in its argument (it takes no parameters); only `}}` may not appear.

  ```markdown
  Processing is lawful only under {{cite: Art. 6(1)(b) of Regulation (EU) 2016/679 (GDPR)}}.
  ```

#### Changed

- **Referenceable recitals (spec §8.5).** Recitals that must be lettered `(A) (B)` and cross-referenced
  are now authored as a lead-in + anchorable list + tail in a section identified as `recitals` (the
  template keys uppercase-letter enumeration off that id), composing the two features above. Block
  quotes remain valid for narrative recitals.

- **Directives allowed in headings (spec §4.2).** Heading text MAY now contain `{{term:}}` and
  `{{ref:}}` (e.g. a heading that names a defined term). Hardcoded numbering, field-spec directives,
  and Markdown emphasis remain disallowed — emphasis is a render-time styling choice. Auto-id
  generation (§5.3) resolves a `{{term:}}` to its display text and omits a `{{ref:}}` (whose number is
  volatile); a heading with `{{ref:}}` SHOULD carry an explicit `{#id}`.

#### Validation changes

| Rule | Level |
|---|---|
| Explicit identifiers (headings + list items) unique across the document | Error |
| A list containing an anchored item is rendered with enumeration active | Error |
| Heading contains a field-spec directive or Markdown emphasis | Error |
| `{{ref:}}` resolves to a section **or** anchored list item | Error |
| `{{cite:}}` argument is non-empty and well-formed | Error |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §4.2, §5.2/§5.3/§5.4, §6.1–§6.3, new §6.5, §8
  (new §8.4 lead-in/tail; §8.5 recitals; renumbered §8.6/§8.7), §11.1/§11.2, §13.2/§13.3, §15.2/§15.3.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — Section Identifiers, Heading Hierarchy,
  Cross-References, new External Citation, Text Formatting, validation summary.
- [`README.md`](README.md) — cross-reference blurb and the structure-at-a-glance snippet.
- [`body-constructs-review.md`](body-constructs-review.md) — design rationale (new).

### Frontmatter: locale/currency cleanup and template placeholders — 2026-06-17

Tightens the document-metadata model so the schema and the rendering rules agree, and adds a
reuse-first way to author templates and drafts. No new structural complexity — these changes
*remove* dangling references and *reuse* the existing `{{placeholder:}}` mechanism.

#### Changed

- **No document-level locale or default currency.** The rendering rules previously told renderers to
  read "the document's locale" and "a default currency from the document metadata" (§10.2–§10.5),
  but the frontmatter schema defined neither field. Formatting (date order, separators, currency
  symbol) is **presentation**, so it is now explicitly a render-time setting — the **active locale**
  from the render template or renderer configuration (§10.1). Currency stays per `{{money:}}`
  directive; an omitted `currency` emits a validation warning and MAY fall back to a render-template
  default, but there is **no document-level default currency**.

- **`identification_number` is a cross-type reserved field.** Clarified (§3.4) that
  `identification_number` is the reserved field name for a registration/national identifier on **any**
  party — RECOMMENDED for `legal_entity`, OPTIONAL for `natural_person` (not every individual has
  one). Prefer it over a custom field so tooling can locate the identifier consistently. Documentation
  clarification, not a schema change.

#### Added

- **Placeholders in frontmatter (spec §3.10).** Template and draft documents MAY use the existing
  `{{placeholder:}}` directive (§10.7) as a **quoted** string value in frontmatter, reusing its ids,
  types, and rendering unchanged:

  ```yaml
  legal_name: "{{placeholder: client-legal-name}}"
  effective_date: "{{placeholder: effective-date, type=date}}"
  ```

  - Allowed in **value** fields (`title`, `legal_name`, `address`, `identification_number`,
    `effective_date`, `governing_law`, …); **not** in identifier or structural fields (any `name`,
    `type`, `document_type`, `sides`/`parties` structure).
  - Must be a quoted YAML string (an unquoted `{{` is invalid YAML).
  - A required field holding a placeholder counts as present — the document is treated as a
    template/draft with unfilled blanks; a placeholder id shared with the body is the same blank.

#### Validation changes

| Rule | Before | After |
|---|---|---|
| `{{placeholder:}}` in a frontmatter identifier/structural field | — | **Added (Error)** |
| `{{money:}}` omitted `currency` looks up a *document* default | (implied) | **Removed** — no document default; warning only |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §3.4 (identifier note), new §3.10
  (frontmatter placeholders), §10.1 (active-locale note), §10.2–§10.5 (locale wording), §10.3
  (currency clause), §10.7 (cross-reference), §13.7 (locale listed among style-template settings),
  §15.5 (validation row).
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — Sides and Parties notes, Placeholder
  section, validation summary.

---

### Definitions overhaul (BREAKING) — 2026-06-16

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
  Quotation marks are the only delimiter, and they are a **source-only delimiter that is never
  rendered** — at neither the defining occurrence nor any `{{term:}}` reference. Whether a term
  renders bold, underlined, or small-caps is entirely a render-time decision driven by the style
  template (§13.7) — applying the separation-of-content-and-presentation principle (§1.2) to
  definitions.

- **Reference by location, not body.** A `{{def:}}` records only `(id, term, location)`. The format
  no longer stores or extracts a "definition text." A `{{term:}}` link targets the definition's
  location (the `{{def:}}` anchor); generated glossaries point to the **section/clause** containing
  it. For tooling purposes (circular-reference detection, optional glossary previews) a definition's
  scope is its **containing paragraph** — a deterministic unit. Sentence-level extraction is
  deliberately not specified (unreliable in legal/multilingual text).

- **`{{term:}}` rendering** now takes the display term from the quoted span at the definition site
  (spec §7.3 / §13.4 step 3) instead of from `**"..."**`. The delimiting quotation marks are not
  rendered.

- **Inflected forms via `label`.** Grammatical inflection (declension, plural, etc.) is expressed
  through the `{{term:}}` `label` override. LegalDown does not encode morphological variants in the
  schema; authoring tools are expected to generate the appropriate `label` automatically.

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
| Declared definition never referenced | Warning | Warning (may false-positive when §7.4 auto term recognition is on) |

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
