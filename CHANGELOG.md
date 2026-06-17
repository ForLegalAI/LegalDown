# Changelog

All notable changes to the LegalDown specification are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). LegalDown is in
early draft (v0.1) and is **not yet stable** — breaking changes may occur between draft revisions
without a major version bump until v1.0.

---

## [Unreleased]

### Execution, bilingual files, party fields & amendments — 2026-06-17

Addresses the next batch of practical gaps: how translation files work, signature/execution blocks,
inline rendering of party fields, and a note on amendment references. Rationale in
[`signatures-bilingual-review.md`](signatures-bilingual-review.md).

#### Removed

- **Unspecified `{{lang:}}` language block.** §1.3 and the README referenced inline language-block
  directives that were never specified. Removed — **separate files are the only bilingual mechanism**
  (§14).

#### Added

- **Translation-file model (spec §14).** A bilingual document is a **translation set** — one file per
  language, linked by `translations`/`authoritative`, kept structurally identical. The spec now lists
  exactly what MUST match across the set (heading hierarchy, section ids, list-item anchor ids,
  definition ids, attachment ids/order, placeholder ids, party `name`s and `sides` structure,
  `document_type`/`type`, `field_types` keys), what MAY be localized, and what SHOULD match
  (`legal_name`). Renderers MAY produce side-by-side output; `validate --sync` checks the invariants
  (§15.7).

- **Signature / execution blocks (spec §3.11).** An optional `signature` object on a party —
  `mode: each | joint | any` (covering joint representation / *Gesamtvertretung*), plus `witness` and
  `notarized` flags — and a document-level `place_of_signing`. Signature blocks remain generated from
  frontmatter; the spec now defines the data and minimal rendering requirements (layout stays
  template-driven). All optional, so existing documents are unaffected.

  ```yaml
  parties:
    - name: acme
      legal_name: Acme Corporation
      representatives: [{name: John Smith, title: CEO}, {name: Jane Roe, title: CFO}]
      signature: { mode: joint }
  place_of_signing: Prague
  ```

- **Inline party fields (spec §10.4).** `{{party: name, field=…}}` renders a declared party field
  (e.g. `address`, `identification_number`) verbatim — for notices clauses and identification blocks,
  keeping a single source of truth. `field` and `label` are mutually exclusive.

  ```markdown
  Notices to {{party: acme}} shall be delivered to {{party: acme, field=address}}.
  ```

#### Changed

- **Amendment references (spec §3.8).** Added a note: references from an amendment to the original's
  provisions are necessarily by the original's own numbering/quoted text (since `{{ref:}}` is
  internal-only); authors SHOULD quote or describe the provision rather than rely on a number alone.
  Acknowledgment only — no new mechanism.

#### Validation changes

| Rule | Level |
|---|---|
| Translation-set structural invariants match across the set | Error |
| `authoritative` / party `legal_name` differ across the set | Warning |
| `signature.mode` ∈ {each, joint, any}; `witness`/`notarized` booleans; `place_of_signing` string | Error |
| `signature.mode` joint/any with < 2 representatives | Warning |
| `{{party:}}` `field` and `label` not both present | Error |
| `{{party:}}` `field` names a present field | Warning |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §1.3, §2.2, §3.2, §3.4, new §3.11, §3.8, §7.5,
  §10.4, §11.1, §13.5, §14 (rewritten), §15.5/§15.6/§15.7.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — Sides/Parties, Party, Amendments,
  Bilingual sections.
- [`README.md`](README.md) — structure-at-a-glance (drop `{{lang:}}`, add party-field).
- [`signatures-bilingual-review.md`](signatures-bilingual-review.md) — design rationale (new).

---

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
