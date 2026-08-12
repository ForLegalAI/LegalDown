# LegalDown Spec — LLM Reference

LegalDown is a plain-text markup language for legal documents, including contracts, unilateral acts, and collective acts. It is a CommonMark superset with legal-specific directives. This document is a condensed technical reference for reading, understanding, and generating LegalDown documents.

## File Format

- Extension: `.lgd` or `.legaldown` (`.legal.md` for Markdown tooling compatibility)
- Encoding: UTF-8
- Line endings: LF preferred, CRLF accepted

## Document Structure

A document has two parts in order:

1. **Frontmatter** (optional) — YAML metadata block delimited by `---`
2. **Body** (required) — LegalDown markup

## Frontmatter

YAML block at the top of the file:

```yaml
---
legaldown: "0.1"                        # OPTIONAL: spec version targeted (quote it)
title: Document Title                    # REQUIRED
subtitle: Optional Subtitle             # OPTIONAL
version: 1.0                            # OPTIONAL
document_type: contract                 # OPTIONAL: contract | unilateral_act | collective_act
effective_date: 2026-02-01              # OPTIONAL, ISO 8601
field_types:                            # OPTIONAL: custom {{field:}} type declarations
  invoice-id: Invoice identifier
  case-number: Court case reference number
sides:                                  # RECOMMENDED
  - name: providers
    label: Providers                    # OPTIONAL
    parties:
      - name: acme-corporation          # REQUIRED, unique identifier
        label: Acme                     # OPTIONAL
        type: legal_entity              # REQUIRED
        legal_name: Acme Corporation    # REQUIRED
        identification_number: ID-123   # RECOMMENDED for legal_entity
        address: Full Address           # RECOMMENDED
        representatives:                # RECOMMENDED for legal_entity
          - name: Person Name           # REQUIRED
            title: Role Title           # OPTIONAL
  - name: issuer
    parties:
      - name: john-novak
        type: natural_person
        legal_name: John Novak
        date_of_birth: 1985-03-15       # RECOMMENDED for natural_person
        address: Full Address
governing_law: Jurisdiction             # OPTIONAL
language: en                            # RECOMMENDED, ISO 639-1
translations:                           # OPTIONAL
  fr: document-fr.lgd
authoritative: en                       # OPTIONAL, ISO 639-1; marks the primary of a translation group (recommended with translations)
adopted_by: Board of Directors          # OPTIONAL
adoption_date: 2026-03-15               # OPTIONAL, ISO 8601
supersedes: Prior policy v1             # OPTIONAL: string or {title, file} object
amends:                                  # OPTIONAL: amendment metadata
  title: Original Document Title         # REQUIRED when amends is present
  file: ../original/document.lgd         # OPTIONAL: relative path to original
attachments:                             # OPTIONAL: array of attachment objects
  - id: schedule-a                       # REQUIRED: unique identifier
    title: "Schedule A: Service Description"  # REQUIRED: rendered verbatim
    file: attachments/service-description.lgd # REQUIRED: relative path
  - id: exhibit-1
    title: "Exhibit 1: Prior Agreements"
    file: attachments/prior-agreements.pdf
tags: [tag1, tag2]                      # OPTIONAL
---
```

Frontmatter is optional as a block but recommended: without it the document is valid but untitled (validators warn). REQUIRED/RECOMMENDED/OPTIONAL statuses apply when frontmatter is present; frontmatter must parse as valid YAML (Error otherwise), `title` must be non-empty, date fields must be valid ISO 8601, and language codes valid ISO 639-1. A `{{placeholder:}}` value satisfies a required field's presence and is exempt from that field's format checks (the placeholder's own checks apply instead).

### Sides and Parties

- `sides` is an array of side objects
- `field_types`, when present, is a map of `type-name: description` entries for custom `{{field:}}` directives
- Custom field type names use the same lowercase identifier format as side and party names and must not be `date`, `money`, `duration`, `party`, or `text` (reserved value-type names)
- Each side has a unique ASCII `name` (lowercase letter, then lowercase letters/digits/hyphens), optional `label`, and non-empty `parties` array
- Each party has a unique document-wide ASCII `name` (lowercase letter, then lowercase letters/digits/hyphens), optional `label`, `type`, and `legal_name`
- Party `type` is explicit: `legal_entity` or `natural_person`
- Unknown party fields are allowed and must be ignored by implementations
- Display fallback: side `label` → title-cased `name` (no pluralization — provide a `label`); party `label` → `legal_name`
- `identification_number` is the reserved field for a registration/national ID — RECOMMENDED for `legal_entity`, OPTIONAL for `natural_person` (not every individual has one); prefer it over a custom field when present
- Template/draft frontmatter MAY use `{{placeholder:}}` as a **quoted** string in value fields (e.g. `legal_name: "{{placeholder: client-name}}"`), but NOT in identifier/structural fields (any `name`, `type`, `document_type`, `legaldown`, `sides`/`parties` structure); same id in frontmatter and body means the same blank

### Amendments

When `amends` is present in frontmatter, the document is an amendment to an existing document:

- `amends.title` (required): non-empty string identifying the original document
- `amends.file` (optional): relative path to the original document (`.lgd`, `.legaldown`, `.pdf`, `.docx`, etc.)
- The amendment follows the same structure rules as any other LegalDown document
- An amendment MAY declare its own `{{def:}}` definitions for new terms

**Definition resolution in amendments:**

- If `amends.file` points to a `.lgd`, `.legaldown`, or `.legal.md` file: import original definitions; `{{term:}}` resolves against both amendment and original definitions; redeclaring a definition from the original emits a Warning
- If `amends.file` points to a non-LegalDown file other than `.lgd`, `.legaldown`, or `.legal.md`, or is absent: unresolved `{{term:}}` references emit Info (not Error)

### Attachments

When `attachments` is present in frontmatter, the document has attached files (schedules, annexes, exhibits) that are integral parts of the document.

- Each attachment has `id` (required, unique identifier), `title` (required, rendered verbatim), and `file` (required, relative path)
- Attachment ids share the same namespace as section identifiers — collisions are not allowed
- The `title` is author-written; the renderer does not generate labels like "Schedule" or "Annex"
- `.lgd`, `.legaldown`, and `.legal.md` files: rendered inline after the main body, content validated, body-only format (must not contain frontmatter or level 1 heading)
- Other file types (`.pdf`, `.docx`, etc.): tracked for referencing and numbering but not rendered inline
- Attachments are rendered in declared order after the main body
- LegalDown attachment files inherit the parent document's context (definitions, field types, metadata)
- Section identifiers in attachment files must be unique across the entire combined document

## Heading Hierarchy

```
# Top-level Provision          ← Articles / Sections (level 1)
## Subsection                  ← Level 2
### Sub-subsection             ← Level 3
#### Level 4
##### Level 5
```

**Rules:**
- Heading levels must not skip (no `#` → `###` without `##`)
- Maximum depth is 5 (`#####`); `######` is an Error. Setext headings (`===`/`---` underlines) are valid and map to levels 1–2; ATX `#` style recommended
- Heading text must be plain text only — no numbering, no directives, no Markdown formatting
- All section numbering is generated at render time — never write numbers in headings
- Content before the first heading is a valid, unnumbered **preamble** — all directives allowed there (including `{{def:}}`), but no anchors and not referenceable

## Section Identifiers

Explicit identifier syntax appended to headings:

```markdown
# Payment Terms {#payment-terms}
```

**Identifier rules:**
- Lowercase ASCII letters (`a-z`), ASCII digits (`0-9`), and hyphens only
- Must start with a lowercase ASCII letter
- Must be unique within the document
- Auto-generated if omitted, via a **fully deterministic** algorithm (identical output across implementations): Unicode NFKD + strip combining marks (`é`→`e`, `ř`→`r`) → apply the fixed transliteration table (`ß`→`ss`, `æ`→`ae`, `œ`→`oe`, `ø`→`o`, `đ`/`ð`→`d`, `þ`→`th`, `ł`→`l`, `ħ`→`h`, `ı`→`i` — exhaustive, no other mappings) → remove remaining non-ASCII (Cyrillic/Greek/CJK are removed, **not** romanized) → lowercase → spaces/tabs/underscores to hyphens → remove other characters → collapse hyphen runs → trim hyphens → truncate to 64 chars → trim trailing hyphen → use `section` if empty → prefix `section-` if not starting with a lowercase letter (prefix exempt from the 64-char cap — no re-truncation)
- If the removal step dropped letters or digits (non-transliterable script), validators warn and recommend an explicit identifier; removed punctuation and symbols (em dashes, curly apostrophes) do not warn. The same applies to auto-derived definition ids
- Duplicate-collision suffixes (`-2`, `-3`) are appended after the algorithm, in document order, exempt from the 64-char cap

**Identifier scope:**
- Each section identifier must be unique within the document
- Cross-references resolve the exact identifier directly
- Dot-separated hierarchical paths are not used

**Item and paragraph anchors:** `{#id}` may also be placed at the very end of a list item's first paragraph (any list depth, but not in lists inside block quotes/tables) or at the very end of a top-level paragraph directly inside a section (not before the first heading). Explicit only — never auto-generated. Same format/uniqueness rules; they join the anchor namespace and are targeted with plain `{{ref:}}`. Rendered designation = containing section number + item enumeration path or paragraph number (`3.1(a)`, `3.1(b)(ii)`, `5.2`); if the template doesn't enumerate that list or number paragraphs, the ref falls back to the section number alone (Warning). Templates may render first-level items or top-level paragraphs as section-qualified decimals (5.1, 5.2) for continental numbered-paragraph drafting. A `{#id}`-like marker anywhere else is literal text (Warning — likely misplaced).

**Identifier namespaces:** all identifiers share one format but live in separate namespaces — each directive resolves only against its own:
- **Anchor:** section identifiers + item/paragraph anchors + attachment ids share one namespace (collisions are Errors); `{{ref:}}` resolves section identifiers and item/paragraph anchors, `{{attach:}}` only attachment ids — a `{{ref:}}` targeting an attachment id is an Error (use `{{attach:}}`)
- **Definitions:** `{{def:}}` ids are unique among definitions only; a definition id may equal a section id (e.g., both `services`) — not a collision
- **Placeholders:** own namespace; repeated ids = the same logical blank; may coincide with any other identifier
- Side names, party names, and `field_types` keys are frontmatter namespaces with their own uniqueness rules
- Renderers disambiguate output anchors themselves (e.g., `def-services` vs `services`)

## Directives

All directives use `{{directive: argument}}` syntax. Case-sensitive, always lowercase. Must not span multiple lines.

**Shared syntax rules (all directives):**

- Form: `{{name: positional, param=value, ...}}` — at most one positional value, always first; named parameters are order-insensitive; the same parameter must not appear twice (Error); a parameter unknown to the directive is ignored with a Warning
- No whitespace between `{{` and the name or between the name and `:`; whitespace after `:`, around commas, and before `}}` is syntax, not value content
- **Quoting:** any value may be wrapped in straight double quotes (`"`, U+0022) to include commas or `}}`: `label="Smith, Jones & Co."`, `{{field: "Smith, Jones & Co. v. Doe", type=case-name}}`. Inside quotes, `\"` = literal quote, `\\` = literal backslash. Unquoted values must not contain `,`, `}}`, or line breaks (leading/trailing whitespace trimmed); quoted and unquoted spellings parse to the same value. Straight quotes only — typographic quotes (`“ ” „ « »`) do not delimit values (validators warn when an unquoted value starts with one)
- Directives are recognized in body text (paragraphs, lists, table cells, block quotes) and in frontmatter only as quoted placeholder strings; they are **not** recognized inside code spans, code blocks, or HTML comments
- Literal `{{` in text: escape the first brace — `\{{ref: x}}` renders as literal `{{ref: x}}` (CommonMark backslash escape)
- A `{{` followed by a name and `:` that cannot be completed as a directive on the same line is malformed (Error); a stray `{{` not followed by `name:` is literal text (Warning)
- An unknown directive name is an Error and renders as `[UNKNOWN DIRECTIVE: name]` — it is never printed verbatim into output (pass-through exists only as an explicit non-default permissive mode)

### Cross-References

```markdown
{{ref: identifier}}
```

Resolves to the section number (e.g., "3.2"). Links to the target section.
Broken references render as `[BROKEN REF: identifier]`. Only section identifiers and item/paragraph anchors are valid targets — referencing an attachment id with `{{ref:}}` is an Error (use `{{attach:}}`). Under a template with no section numbering ("None" scheme), refs render the target's heading text; refs crossing attachment numbering restarts are qualified with the attachment title ("Schedule A: …, Section 2").

### Definitions

**Declare** a defined term by writing it in quotation marks and placing `{{def: id}}` immediately after it. The defined term is the text inside the quotes. The same syntax works in a Definitions section or inline at first use:

```markdown
"Term Name" {{def: term-id}} means ...

The Provider performs marketing services (the "Services" {{def: services}}).
```

**Rules:**

- `{{def:}}` MUST be on the same line as, and immediately preceded by, a quoted span (only optional spaces/tabs — no line break — in between); the term is the text inside the quotation marks
- Defined terms carry NO emphasis markers in source (`**bold**`); styling is applied by the renderer. The quotation marks are a source-only delimiter and are NOT rendered — at neither the definition nor any `{{term:}}` reference
- Accepted quotation pairs (all on by default; double quotes recommended): `"…"` (U+0022), `“…”` (U+201C/D), `«…»`, `»…«`, `„…“`, `‘…’`, `‚…‘`, `‹…›`. Single-quote forms are accepted but ambiguous with apostrophes — validators warn
- The `id` follows section-identifier format rules and MUST be unique **among definitions** (definitions are their own namespace — a def id may equal a section id without conflict); it MAY be omitted and is then auto-derived from the term via the §5.3 slug algorithm (`"Services" {{def:}}` → `services`). Explicit ids are recommended and required to break slug collisions
- A `{{def:}}` MAY appear anywhere in the body — there is no required, single, or first-positioned Definitions section. A top "Definitions" heading is a recommended convention only
- Definitions MAY be introduced inside attachment files (they register document-wide terms)
- A definition records (id, term, location); no "definition text" is stored. A `{{term:}}` link targets the definition's location (the `{{def:}}` anchor); a generated glossary entry points to the section/clause containing it

**Reference** a defined term inline:

```markdown
{{term: term-id}}
{{term: term-id, label=Alternative Display Text}}
```

- `label` is optional; when present, displays that text instead of the defined term (used for inflected forms; authoring tools may generate the `label` automatically)
- Unquoted `label` values must not contain commas or `}}`; use the quoted form to include them (`label="Services, as amended"`)
- Undefined references render as `[UNDEFINED: id]`

### Date

```markdown
{{date: 2026-06-01}}
{{date: 2026-06-01, note=Execution date}}
```

Value must be valid ISO 8601 (`YYYY-MM-DD`). Optional `note` provides an automation-facing explanation and is not rendered.

### Money

```markdown
{{money: 10000, currency=USD}}
{{money: 500}}
{{money: 500, note=Estimated onboarding fee}}
{{money: 500, currency=EUR, note=Base monthly service fee}}
```

- Amount: numeric (period decimal separator), no grouping separators or symbols
- `currency`: optional, ISO 4217 code
- `note`: optional plain-text explanation for automation

### Party

```markdown
{{party: party-name}}
{{party: party-name, label=Display Text}}
{{party: party-name, note=Primary signing contact}}
{{party: party-name, label=Display Text, note=Primary signing contact}}
```

- `party-name`: lowercase ASCII identifier starting with a lowercase ASCII letter, then lowercase letters/digits/hyphens; resolves against `sides[].parties[].name`
- `label`: optional inline display override
- Without `label`, render the party `label` and fall back to `legal_name`
- If the `party-name` does not match any party in frontmatter, render as `[UNKNOWN PARTY: party-name]`
- `note`: optional plain-text explanation for automation

### Duration

```markdown
{{duration: 30, unit=D}}
{{duration: 30, unit=D, note=Standard notice period}}
```

- Value: positive numeric
- `unit` (required): `S` | `M` | `H` | `D` | `MO` | `Y`
- `note`: optional plain-text explanation for automation

### Custom Field

```markdown
{{field: INV-2026-0042, type=invoice-id}}
{{field: 25 Cdo 1234/2025, type=case-number, note=Relevant precedent}}
```

- `value`: required raw value; preserved exactly (after unquoting) and rendered as-is; quote it (`"..."`) when it contains a comma or `}}`
- `type` (required): lowercase ASCII identifier starting with a letter, then lowercase letters/digits/hyphens
- If frontmatter `field_types` exists, undeclared custom field types should trigger a warning
- If `field_types` is absent entirely, any well-formed custom field type is accepted without warning
- `note`: optional plain-text explanation for automation

### Placeholder

```markdown
{{placeholder: governing-jurisdiction}}
{{placeholder: delivery-date, type=date}}
{{placeholder: fee, type=money, currency=EUR, note=Base monthly fee}}
```

- No separate declaration needed; appears in document text, and MAY also appear as a quoted string value in frontmatter value fields (not identifier/structural fields) for templates and drafts
- `type`: optional, defaults to `text`
- Supported types: `text` | `date` | `money`
- Same placeholder id used multiple times means the same logical blank
- Repeated uses of the same placeholder id must keep the same effective type
- Render as a visible blank such as `[_____]`; if unavailable, fall back to `[TBD: id]`
- `note`: optional plain-text explanation for automation

### File Inclusion

```markdown
{{include: schedules/pricing.lgd}}
```

Path is relative to the including document. The target is a **body-only LegalDown fragment** — the same file model as attachment files: must be `.lgd`/`.legaldown`/`.legal.md`, no frontmatter, no level 1 heading (write the surrounding heading in the including document). Content splices verbatim at the directive position with no heading re-basing — the combined document must not skip heading levels. A `{{def:}}` in a fragment registers a document-wide term; section ids must be unique across the combined document. Fragments may nest further `{{include:}}`s; circular chains are invalid.

### Attachment Reference

```markdown
{{attach: attachment-id}}
```

- Resolves to the attachment `title` from frontmatter
- Creates a hyperlink to the attachment (rendered section for LegalDown files, external file for others)
- If the id is not found, renders as `[UNKNOWN ATTACHMENT: id]`

## Text Formatting

Standard CommonMark:
- `**bold**` — emphasis (NOT used for defined terms; terms use quotes + `{{def:}}`, styled by the renderer)
- `*italic*`
- Lists (ordered and unordered) with blank lines before/after
- Tables (standard Markdown pipe tables with header row)
- Block quotes (used for recitals/WHEREAS clauses)
- HTML comments `<!-- ... -->` — stripped from rendered output
- Horizontal rules `---` — for major document divisions

## Bilingual Documents

Separate files per language with identical heading structure and section identifiers. Linked via `translations` and `authoritative` in frontmatter. Linked files must declare the same set of languages (each file's `language` + `translations` keys); structural or language-set mismatches are Errors.

A translation is a **secondary** document: the **primary** is the linked file whose `language` equals `authoritative` (declaring it is recommended). Identifiers originate in the primary and are mirrored **explicitly** into translations — every heading and `{{def:}}` in a translation file must carry an explicit id (its counterpart's id from the primary); auto-generation is never relied on in translation files. Updating a translation = mirror the primary's change under the same id + translate the text. Without `authoritative`, validators check symmetrically and warn on auto-generated ids in linked files.

## Validation Summary

**Errors** (must fix):
- Skipped heading levels
- Heading depth beyond level 5
- Unknown directive name (renders as `[UNKNOWN DIRECTIVE: name]`)
- Circular definitions (scoped to each definition's containing paragraph)
- Duplicate explicit anchors (section identifiers, item/paragraph anchors — one shared namespace)
- Malformed section identifiers
- Malformed directive after a `{{name:` opener (grammar violation, including an unterminated quoted value)
- Duplicate named parameter in a directive
- `{{def:}}` not immediately preceded by a recognized quoted span
- Two definitions auto-generate the same identifier (omitted ids)
- Broken `{{ref:}}` or `{{term:}}` targets
- `{{ref:}}` targeting an attachment id (attachments are referenced with `{{attach:}}`)
- Duplicate `{{def:}}` identifiers (within the definitions namespace)
- Invalid `document_type`, side names, party names, or party `type` values
- Too few sides or parties for the selected `document_type` (checked only when `sides` is present)
- Missing `issuer` side for `unilateral_act` or `collective_act` (checked only when `sides` is present)
- Heading or `{{def:}}` without an explicit identifier in a translation file (non-authoritative linked file)
- Invalid `{{date:}}`, `{{money:}}`, or `{{duration:}}` values
- `{{party:}}` `party-name` is empty, malformed, or does not match any party declared in frontmatter
- `field_types` keys that are malformed or collide with the reserved value-type names (`date`, `money`, `duration`, `party`, `text`)
- Missing or malformed `type` on `{{field:}}`
- Invalid `{{placeholder:}}` identifiers or inconsistent placeholder types across repeated uses
- `{{placeholder:}}` in a frontmatter identifier or structural field (any `name`, `type`, `document_type`, `legaldown`, `sides`/`parties` structure)
- Frontmatter present but not valid YAML
- Missing or empty `title` when frontmatter is present
- Invalid `effective_date`, `adoption_date`, or `date_of_birth` (not a valid ISO 8601 date; placeholders exempt)
- Empty attachment `title` or representative `name`
- Include target missing, not a LegalDown file, or part of a circular include chain
- Included fragment contains frontmatter or a level 1 heading
- Section identifiers in included fragments not unique across the combined document, or the combined document skips heading levels
- Mismatched bilingual structure (heading hierarchy, section ids, definition ids, or declared language sets)
- `amends.title` is empty or missing when `amends` is present
- `amends.file` path does not exist when specified
- `{{term:}}` references id not found in amendment or imported original (when original is a LegalDown file)
- Attachment `id` is not unique across document
- Attachment `id` collides with a section identifier or item/paragraph anchor
- Attachment `file` path does not exist
- LegalDown attachment file contains frontmatter
- LegalDown attachment file contains level 1 heading
- Section identifiers in attachment files are not unique across entire combined document
- `{{attach:}}` references undeclared attachment id

**Warnings** (should fix):
- Hardcoded numbering in headings
- Named parameter not defined for the directive (ignored for rendering)
- Stray `{{` in body text that does not begin a well-formed directive
- Unquoted directive value beginning with a typographic quotation mark (auto-curled quote)
- `{#id}`-like marker outside an anchor position (likely misplaced anchor)
- `{{ref:}}` to an item/paragraph anchor the active template does not enumerate (falls back to section number)
- Duplicate auto-generated section identifiers (implementations append `-2`, `-3` suffixes for rendering)
- Auto-generated section or definition identifier lost non-transliterable letters or digits (removed punctuation does not warn; explicit id recommended)
- Defined term wrapped in emphasis markers (`**`, `__`) in source
- Single-quoted term ambiguous with an apostrophe (U+2019)
- Declared definitions never referenced
- Missing `currency` on `{{money:}}`
- Undeclared `{{field:}}` type when `field_types` frontmatter is present
- Attachment declared but never referenced via `{{attach:}}`
- Document has no frontmatter
- `sides` absent entirely — `document_type` structural constraints cannot be verified (single warning; the per-rule Errors apply only when `sides` is present)
- Invalid ISO 639-1 code in `language`, `authoritative`, or `translations` keys; `authoritative` not among the document's languages
- Auto-generated identifiers in bilingual linked files when `authoritative` is absent (primary cannot be determined)
- Declared `legaldown` spec version newer than the implementation supports (implementations must not fail on an unknown version)
- Unknown currency on `{{placeholder: ..., type=money}}`
- Amendment declares `{{def:}}` with same id as definition in original LegalDown source

**Info** (suggestions):
- `{{term:}}` references id not found in amendment (when original is not available or not a LegalDown file)
- Definition used before its declaration point in the document

## Minimal Example

```markdown
---
title: Mutual Non-Disclosure Agreement
document_type: contract
sides:
  - name: disclosers
    label: Disclosing Parties
    parties:
      - name: acme
        label: Acme
        type: legal_entity
        legal_name: Acme Corporation
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
        representatives:
          - name: John Smith
            title: Chief Executive Officer
  - name: recipients
    label: Receiving Parties
    parties:
      - name: beta
        label: Beta
        type: legal_entity
        legal_name: Beta Industries Inc.
        identification_number: TX-87654321
        address: 456 Oak Avenue, Austin, TX 78701
        representatives:
          - name: Jane Doe
            title: General Counsel
effective_date: 2026-02-01
governing_law: Delaware
language: en
---

This Mutual Non-Disclosure Agreement (this "Agreement" {{def: agreement}}) is entered into
between {{party: acme}} and {{party: beta}}.

# Definitions {#definitions}

"Confidential Information" {{def: confidential-info}} means any non-public information disclosed
by one side to the other, whether orally or in writing, that is designated as confidential.

"Effective Date" {{def: effective-date}} means the date first written above.

# Confidentiality Obligations {#confidentiality}

{{party: beta, label=the Receiving Party}} shall protect the
{{term: confidential-info}} using at least the same degree of care it uses
for its own confidential information.

# Term and Termination {#term}

The {{term: agreement}} commences on the {{term: effective-date}} and continues
until {{date: 2028-02-01}} unless earlier terminated by either party upon
{{duration: 30, unit=D}} written notice.
```
