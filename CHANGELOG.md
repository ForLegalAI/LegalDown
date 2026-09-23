# Changelog

All notable changes to the LegalDown specification are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

LegalDown is in early draft. Until v1.0, breaking changes may occur between minor versions; each
will be recorded here with a migration note.

---

## [Unreleased]

Nothing yet.

---

## [0.2] — 2026-09-23

The template release. Templates could hold fillable blanks in 0.1, but nothing else a template
needs: a template that said one thing to a consumer and another to a business had to be split in
two, drafting guidance lived in HTML comments that no rendered review ever showed, and turning a
template into a document was left to whichever tool did it. That put the most valuable part of a
template — its logic — outside the format
([#38](https://github.com/ForLegalAI/LegalDown/issues/38)). 0.2 brings it in, as a new §15, while
keeping templates simple, language-neutral, and deterministic. The design and its rationale are
recorded in [`proposals/templates.md`](proposals/templates.md); where the proposal and the
specification differ, the specification is normative.

> **Breaking changes.** Most 0.1 documents are unaffected. The following now draw Errors or
> Warnings they did not draw in 0.1 — see *Migration* below:
>
> - one placeholder id fixing two different currencies or units (`placeholder-type-inconsistent`)
> - a placeholder in a date field that is not the whole value or not of type `date`
>   (`metadata-date-invalid`, `date-of-birth-invalid`), or in a file path, attachment `id`,
>   language code, or `field_types` (`placeholder-in-structural-field`)
> - a blank glued to Markdown punctuation — `&`, `<`, `**`, a link target — in a draft
>   (`insertion-boundary`)
> - an `#id` on a paragraph that holds only an `{{include:}}` (ignored, `anchor-misplaced`)
>
> **Renumbering.** Sections 15–18 are now 16–19 (Validation, Conformance Levels, Complete Examples,
> Roadmap). Rule ids are unchanged, so fixture directories and rule suppressions keep working;
> citations of section numbers need updating.

### Added

**Templates (§15).** A template is an ordinary LegalDown document that declares `questions`,
carries a `when=` condition, or contains a `{{choose:}}` directive.

- **Questions (§15.2).** Optional frontmatter `questions`. Value questions (`text`, `date`,
  `money`, `duration`) give a placeholder of the same id a `prompt` and a `default`; decision
  questions (`boolean`, `choice`) drive conditions and inline choices. A placeholder's omitted
  `type` now defaults to its declared question's type.
- **Conditions (§15.3).** `when=` on the existing anchor marker — `{#id when=q}`, `when=!q`,
  `when=q:value`, `when=!q:value` — on whole units only: sections (with their subsections), list
  items, top-level and preamble paragraphs, `{{include:}}` paragraphs, and attachments
  (`attachments[].when`). One test per marker, with no expression language; nesting combines
  conditions. The syntax uses no English words.
- **Alternatives and reference safety (§15.4).** Units whose conditions can never both hold MAY
  share an identifier, so an either/or clause keeps one reference target. Every `{{ref:}}`,
  `{{term:}}`, and `{{attach:}}` must resolve under every combination of answers.
- **Inline choices — `{{choose:}}` (§15.5).** A plain-text phrase chosen by a decision; every
  possible answer must be listed, so a new choice value cannot silently drop text.
- **Drafting notes (§15.6).** `> [!DRAFTING]` block quotes: guidance for the template user, shown
  in template views and removed on assembly. A look-alike marker draws a Warning.
- **Assembly (§15.7).** A byte-deterministic transformation of a template and an answers set into
  an ordinary LegalDown document: defined answer forms (§15.7.1), an eight-step procedure
  (§15.7.2), escaping and insertion boundaries so answers are inserted as literal text (§15.7.3),
  and identifier preservation. **A template without Errors assembles without Errors for every
  valid answers set** (§15.7.4). Drafts are filled by the same procedure; unanswered blanks keep
  their declared type.
- **Template view (§15.8)** for rendering a template without answers, and the **final check**
  (§15.9), a validation option that rejects any blank, drafting note, or template construct left
  in a document meant for signature.
- **Includes and attachment files in templates (§15.3).** Kept simple so every fragment has one
  place and one condition: `{{include:}}` only in the template's own body, each fragment included
  once, no conditions or drafting notes in fragments, explicit heading identifiers there.
- **Bilingual templates (§14.2).** Linked templates share questions, defaults (a `text` default is
  translated but present in every language or none), placeholders, conditions, and `{{choose:}}`
  parameter names, so one answers set assembles every language version to the same state.
- **Assembly capability (§17.6)**, claimable alongside any conformance level. Templates with
  includes, LegalDown attachment files, or `translations` need Full.
- **`duration` placeholder type (§10.7).**

**Conformance corpus.**

- Fixtures for every new rule id; the corpus now accounts for all 116 rule ids (113 with fixtures).
- `fixtures/assembly/` — six byte-exact cases (template + answers set → expected output),
  including a multi-file case with an `expected/` output tree and a `case.json` level.
- `verify.py` checks assembly cases, `requires_capability` / `requires_config`, `case.json`
  levels, and the total rule count.

### Changed

- Uniqueness of section identifiers, anchors, attachment ids, and definition ids — and
  auto-generated identifier collisions — applies only between declarations that can appear
  together (§5.2, §5.4, §5.5, §7.2), which is what lets alternatives share an identifier.
- Repeated occurrences of one placeholder id that fix a `currency` or `unit` must fix the same
  one, in every document (§10.7) — previously only a SHOULD.
- A placeholder in a frontmatter date field must be the whole value and of type `date`, and
  placeholders are not allowed in file paths, attachment `id`/`when`, language codes, or
  `field_types`, which a filled-in value could break (§3.10, §16.6).
- `{{placeholder:}}` and `{{choose:}}` must be kept apart from Markdown punctuation they could
  combine with, in templates and drafts alike (§15.7.3, `insertion-boundary`).
- An `#id` on a paragraph that holds only an `{{include:}}` is ignored with `anchor-misplaced`, in
  any document: the paragraph is replaced by its fragment, so it is not a reference target
  (§12.2). A `when=` in the same marker still applies in a template.
- `{when=...}` markers outside a condition position, and markers repeating an attribute, draw
  `anchor-misplaced`. In a template, a `{when=}`-only marker is allowed on a preamble paragraph;
  in any other document it remains literal text (§5.7).
- Anchor and condition markers are excluded from heading text for identifier generation (§4.2,
  §5.3) and are not recognized inside code or comments (§11.4).
- "Template" now always means a document template (§15); presentation settings are called the
  **style template** throughout (§5.7, §6.2–§6.3, §7.2, §10, §13, §16.3, §19).

### Validation changes

| Rule | Before | After |
|---|---|---|
| `question-invalid`, `placeholder-question-mismatch`, `condition-invalid`, `condition-reference-unsafe`, `choose-invalid`, `drafting-note-def`, `def-term-variable` | — | Error (Core) |
| `question-unused`, `condition-never-true`, `drafting-note-unrecognized` | — | Warning (Core) |
| `template-fragment-invalid` | — | Error (Core; Full where it reads another file) |
| `insertion-boundary` | — | Error (Core; Full where it reads a fragment) — templates and drafts |
| `answer-missing`, `answer-invalid` | — | Error (Assembly) |
| `answer-unknown` | — | Warning (Assembly) |
| `placeholder-unfilled`, `template-construct-present` | — | Error (final option only) |
| `translation-template-mismatch` | — | Error (Full) |
| `placeholder-type-inconsistent` | Same effective type | Also the same fixed `currency`/`unit` (previously a SHOULD with an optional Warning) |
| `placeholder-in-structural-field` | Side/party names, `type`, `document_type`, `legaldown`, structure | Adds anything inside `questions`, file paths, attachment `id`/`when`, language codes, `field_types` |
| `metadata-date-invalid`, `date-of-birth-invalid` | Any placeholder exempt | Exempt only when the placeholder is the whole value and of type `date` |
| `placeholder-type-invalid` | `text`, `date`, `money` | Adds `duration` |
| `duration-invalid-unit` | `{{duration:}}` only | Also a `type=duration` placeholder's `unit` |
| `anchor-misplaced` | Misplaced `{#id}` | Also `{when=...}`, repeated attributes, and an `#id` on an include-only paragraph (ignored) |
| `anchor-duplicate`, `def-duplicate-id`, `def-autogen-collision`, `attachment-id-duplicate`, `attachment-id-collision`, `attachment-anchor-duplicate`, `include-anchor-duplicate` | Any duplicate | Duplicates between declarations that can appear together |
| `anchor-autogen-collision` | Suffixes in document order | Headings that can never appear together do not collide (§5.5) |
| `include-heading-skip` | Combined document | Also under every combination of answers deciding which conditional includes are present |

### Migration from 0.1

- **Two currencies on one blank.** If `{{placeholder: fee, type=money, currency=EUR}}` and
  `{{placeholder: fee, type=money, currency=USD}}` both appear, pick one currency or use two ids.
- **Placeholders in frontmatter.** Write a date field's placeholder as the whole value with
  `type=date` (`effective_date: "{{placeholder: effective-date, type=date}}"`). Move any
  placeholder out of file paths, attachment ids, language codes, and `field_types`.
- **Blanks next to punctuation.** Separate a blank from `&`, `<`, `\`, `!`, `]`, emphasis markers,
  or a link target with a space or ordinary punctuation (§15.7.3 lists what is allowed).
- **Anchored include lines.** Move an anchor on an `{{include:}}`-only paragraph to a heading
  inside the fragment, and point `{{ref:}}` there.
- **Section citations.** References to "§15"–"§18" of 0.1 are now §16–§19.
- **Declared version.** Documents MAY declare `legaldown: "0.2"`; 0.1 documents that pass the
  points above remain valid unchanged.

### Files touched

- `spec/legaldown-spec.md` — new §15 Templates; new §16.12 and §17.6; updates across §1.3, §3,
  §4–§8, §10–§14, §16–§17, §19; sections 15–18 renumbered 16–19; version 0.2
- `llm/legaldown-spec-llm.md` — new Templates section; directives, identifiers, validation summary,
  and "Not in the language" updated
- `fixtures/` — rule fixtures for every new rule id, `assembly/` cases, `verify.py`,
  `coverage.json`, README
- `examples/advanced/` — `template/` reworked as a full template with an answers set and a
  conditional LegalDown attachment; the other advanced examples declare `legaldown: "0.2"`;
  `examples/README.md`
- `README.md`, `CONTRIBUTING.md` — templates overview, version, section numbers, fixture guidance
- `proposals/templates.md` — the design proposal
- `.gitattributes`, `.gitignore` — YAML normalized to LF; Python caches ignored

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

[Unreleased]: https://github.com/ForLegalAI/LegalDown/compare/v0.2...HEAD
[0.2]: https://github.com/ForLegalAI/LegalDown/releases/tag/v0.2
[0.1]: https://github.com/ForLegalAI/LegalDown/releases/tag/v0.1
