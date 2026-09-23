# Changelog

All notable changes to the LegalDown specification are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

LegalDown is in early draft. Until v1.0, breaking changes may occur between minor versions; each
will be recorded here with a migration note.

---

## [Unreleased] — targets 0.2

Templates could hold fillable blanks in 0.1, but nothing else a template needs: a template that
said one thing to a consumer and another to a business had to be split in two, drafting guidance
lived in HTML comments that no rendered review ever showed, and turning a template into a document
was left to whichever tool did it. That put the most valuable part of a template — its logic —
outside the format ([#38](https://github.com/ForLegalAI/LegalDown/issues/38)). The design is
recorded in [`proposals/templates.md`](proposals/templates.md).

### 2026-09-23 — Templates (new §15)

> Sections 15–18 are renumbered 16–19 to make room for §15. Rule ids are unchanged, so fixture
> directories and suppressions keep working; citations of section numbers need updating.

#### Added

- **Questions (§15.2).** Optional frontmatter `questions`: value questions (`text`, `date`,
  `money`, `duration`) give a placeholder of the same id a `prompt` and `default`; decision
  questions (`boolean`, `choice`) drive conditions and inline choices.
- **Conditions (§15.3).** `when=` on the anchor marker — `{#id when=q}`, `when=!q`, `when=q:value`,
  `when=!q:value` — on whole sections (with their subsections), list items, top-level and preamble
  paragraphs, include paragraphs, and attachments (`attachments[].when`). One test per marker;
  nesting combines conditions.
- **Alternatives and reference safety (§15.4).** Units whose conditions can never both hold MAY
  share an identifier; every reference must resolve under every combination of answers.
- **`{{choose:}}` (§15.5).** An inline plain-text phrase chosen by a decision; every possible
  answer must be listed.
- **Drafting notes (§15.6).** `> [!DRAFTING]` block quotes (marker case-insensitive), rendered as
  guidance in template views and removed on assembly; a look-alike marker draws a Warning.
- **Assembly (§15.7).** A byte-deterministic transformation of a template and an answers set into
  an ordinary LegalDown document, with defined answer forms, escaping of inserted text, and
  identifier preservation. A template without Errors assembles without Errors for every valid
  answers set. Assembly works on the combined document (template, include fragments, LegalDown
  attachment files) and writes each line back to its own file.
- **Template view (§15.8)** and the **final check (§15.9)**.
- **`duration` placeholder type (§10.7).**
- **Assembly capability (§17.6)**, claimable alongside any conformance level.
- **Bilingual templates (§14.2):** linked templates share questions, conditions, and
  `{{choose:}}` parameter names.
- `fixtures/assembly/` — byte-exact template + answers → output cases; fixture fields
  `requires_capability` and `requires_config` values `answers` and `final`.

#### Changed

- Uniqueness of section identifiers, anchors, attachment ids, and definition ids — and
  auto-generated identifier collisions — applies only between declarations that can appear
  together (§5.2, §5.4, §5.5, §7.2).
- A placeholder's omitted `type` defaults to its declared question's type before `text` (§10.7).
- `{when=...}` markers outside a condition position, and markers repeating an attribute, draw
  `anchor-misplaced`; a `{when=}`-only marker is allowed at the end of a preamble paragraph (§5.7).
- In a template, `questions` and `attachments` are written in YAML block style, a `when` value
  starting with `!` is quoted, and choice value ids avoid the YAML 1.1 boolean/null words (§15.2,
  §15.3), so every YAML parser reads them the same way. Question ids and undeclared placeholder ids
  in a template avoid the same words.
- A placeholder in a frontmatter date field must be the whole value and of type `date` (§3.10);
  otherwise the field's date check applies (§16.6). Placeholders are not allowed in file paths,
  attachment `id`/`when`, language codes, or `field_types`, which a filled-in value could break.
- `questions` joins the structural frontmatter fields that must not hold placeholders (§3.10).
- "Template" now means a document template (§15); every place that meant presentation settings
  says **style template** (§5.7, §6.2–§6.3, §7.2, §10, §13, §16.3, §19).
- Anchor and condition markers are excluded from heading text for identifier generation (§4.2,
  §5.3) and are not recognized inside code or comments (§11.4).

#### Validation changes

| Rule | Before | After |
|---|---|---|
| `question-invalid`, `placeholder-question-mismatch`, `condition-invalid`, `condition-reference-unsafe`, `choose-invalid`, `drafting-note-def` | — | Error (Core) |
| `question-unused`, `condition-never-true`, `drafting-note-unrecognized` | — | Warning (Core) |
| `answer-missing`, `answer-invalid` | — | Error (Assembly) |
| `answer-unknown` | — | Warning (Assembly) |
| `placeholder-unfilled`, `template-construct-present` | — | Error (final option only) |
| `translation-template-mismatch` | — | Error (Full) |
| `anchor-duplicate`, `def-duplicate-id`, `def-autogen-collision`, `attachment-id-duplicate`, `attachment-id-collision`, `attachment-anchor-duplicate`, `include-anchor-duplicate` | Any duplicate | Duplicates between declarations that can appear together |
| `anchor-autogen-collision` | Suffixes in document order | Headings that can never appear together do not collide; suffixes skip only identifiers of headings that can (§5.5) |
| `placeholder-in-structural-field` | Side/party names, `type`, `document_type`, `legaldown`, structure | adds anything inside `questions`, file paths, attachment `id`/`when`, language codes, `field_types` |
| `metadata-date-invalid`, `date-of-birth-invalid` | Any placeholder exempt | Exempt only when the placeholder is the whole value and of type `date` |
| `placeholder-type-invalid` | `text`, `date`, `money` | adds `duration` |
| `duration-invalid-unit` | `{{duration:}}` only | also a `type=duration` placeholder's `unit` |
| `include-heading-skip` | Combined document | Combined document with and without each conditional include |
| `anchor-misplaced` | Misplaced `{#id}` | Misplaced `{#id}` or `{when=...}` |

#### Files touched

- `spec/legaldown-spec.md` — new §15; §1.3, §3.2, §3.9, §3.10, §4.2, §4.4, §5.2–§5.7, §7.2, §8.4,
  §8.6, §10.3, §10.7, §11.1, §11.2, §11.4, §12.2, §13.1, §13.5, §13.7, §14.2–§14.3, §16.1–§16.5,
  §16.7, §16.10, §16.11, new §16.12, §17.2–§17.4, new §17.6, §19; "style template" wording
  throughout; sections 15–18 renumbered 16–19; version 0.2 DRAFT
- `fixtures/` — 15 new rule fixtures, four byte-exact `assembly/` cases, `verify.py`,
  `coverage.json`, README
- `examples/advanced/template/` — reworked as a full template with an answers set and a
  conditional LegalDown attachment; `examples/README.md`
- `llm/legaldown-spec-llm.md` — new Templates section, validation summary, "Not in the language"
- `README.md`, `CONTRIBUTING.md` — templates overview, version, section numbers, fixture and
  assembly-case guidance
- `.gitattributes` — `*.yaml`/`*.yml` normalized to LF, keeping assembly cases byte-stable
- `proposals/templates.md` — the design proposal

---

## [0.1] — 2026-08-14

First published version of the LegalDown specification. Everything below is new.

### The format

- **Document model (§2, §4).** UTF-8 plain text with the `.lgd`, `.legaldown`, or `.legal.md`
  extension: optional YAML frontmatter followed by a body of CommonMark. Heading levels 1–5 define
  the provision hierarchy; content before the first heading is an unnumbered preamble.
- **Metadata (§3).** Parties are organized under named **sides**, each holding one or more party
  objects typed `legal_entity` or `natural_person`, with representatives, identification numbers,
  and addresses. Also: `document_type` (`contract`, `unilateral_act`, `collective_act`),
  `effective_date`, `governing_law`, `language`, `translations`, `authoritative`, `amends`,
  `supersedes`, `attachments`, `field_types`, and an optional `legaldown` version declaration.
  Unknown fields are ignored, so organizations can carry their own metadata.
- **Identifiers and anchors (§5).** Stable `{#id}` anchors on headings, list items, and top-level
  paragraphs, in one shared anchor namespace with attachment ids. Identifiers omitted on headings
  are auto-generated by a **fully deterministic** algorithm, so independent implementations produce
  the same id for the same text.
- **Cross-references (§6).** `{{ref:}}` resolves to the section number generated at render time —
  never written in source — and hyperlinks to its target. `{{attach:}}` references declared
  attachments.
- **Definitions (§7).** A term is written in quotation marks with `{{def:}}` immediately after it,
  anywhere in the document — in a definitions article or inline at first use. `{{term:}}` references
  it, optionally with a `label` for grammatical inflection. Eight quotation-mark pairs are accepted,
  covering the major Western legal languages.
- **Directives (§10, §11).** A formal grammar with quoted values, escaping, and defined recognition
  contexts, plus the typed field specs: `{{date:}}`, `{{money:}}`, `{{duration:}}`, `{{party:}}`,
  `{{side:}}`, `{{field:}}`, and `{{placeholder:}}` for fillable blanks in templates.
- **Composition (§12).** `{{include:}}` splices body-only fragments; attachments are declared in
  frontmatter and rendered after the main body. Both use the same fragment model.
- **Rendering (§13).** Numbering schemes, list enumeration, style templates, and the resolution
  rules for every directive — including the bracketed failure markers (`[BROKEN REF: …]`,
  `[UNDEFINED: …]`) that keep an unresolved reference visible instead of silent.
- **Bilingual documents (§14).** One file per language linked by `translations`, with
  `authoritative` marking the primary. A translation is a secondary document: identifiers originate
  in the primary and are mirrored explicitly.
- **Validation (§15).** 98 checks across structure, references, definitions, field specs, metadata,
  bilingual sets, amendments, attachments, and includes — each with a severity (Error / Warning /
  Info) and a **stable rule id** that implementations report and users can filter on.
- **Conformance levels (§16).** Core (parse and validate one document), Rendering (Core plus
  rendered output), Full (Rendering plus all multi-file processing). An implementation must never
  silently skip a check it cannot perform.
- **Roadmap (§18).** Deliberate deferrals are recorded in the specification itself, so their
  absence reads as a decision rather than an oversight.

### Repository

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — the specification.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — a condensed reference for language
  models reading or authoring LegalDown.
- [`examples/`](examples) — working documents in two tiers: the specification's own examples, and
  an advanced tier exercising every feature, with a table mapping each feature to a live example.
- [`fixtures/`](fixtures) — the conformance corpus: one case per validation rule paired with the
  diagnostic a conforming validator must produce, plus a self-check script.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — design commitments, the pull request checklist, and how to
  propose a change.

### Known limitations

Recorded in §18 and deferred to a later version: qualified cross-document references for
amendments, a `{{meta:}}` directive for inserting frontmatter values into body text, structured
`adopted_by` for collective acts, template-generated attachment labels, a structured signature
model, template-supplied reference label words, and a machine-readable export format.

[0.1]: https://github.com/ForLegalAI/LegalDown/releases/tag/v0.1
