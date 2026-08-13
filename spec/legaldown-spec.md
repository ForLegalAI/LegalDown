# LegalDown Specification
## Version 0.1 DRAFT

**Revision:** 2026-08-12 — change history in [CHANGELOG.md](../CHANGELOG.md)

---

## 1. Introduction

### 1.1 Purpose

LegalDown is a plain text markup language for authoring legal documents — including contracts, unilateral acts (notices, declarations, powers of attorney), and collective acts (internal regulations, bylaws, policies). It extends standard Markdown with legal-specific constructs enabling structured authoring, automated validation, intelligent rendering, and version control integration. LegalDown is the document format standard of the LeGit legal document management ecosystem, but is designed as an open, independent standard usable with any compatible tooling.

### 1.2 Design Principles

**Human-readable first.** Legal professionals must be able to read and edit LegalDown source files without specialized tools. A document in LegalDown should be immediately comprehensible to any lawyer opening it in a plain text editor.

**Separation of content and presentation.** Document structure, hierarchy, and content are defined independently of visual formatting, numbering, and styling. A LegalDown document contains no hardcoded section numbers. All numbering is generated at render time by the renderer according to a configurable scheme. This means sections can be freely added, removed, or reordered without any manual renumbering.

**Machine-parseable.** Document structure must be unambiguous for automated processing, validation, transformation, and AI analysis.

**Simplicity through standardization.** LegalDown intentionally encourages simpler legal document structures. The format does not attempt to reproduce every complexity found in traditional legal drafting. Standardized templates and enforced structure make documents easier to read, compare, and review.

**Version control native.** Plain text format is optimized for meaningful diffs, intelligent merging, and collaborative editing through Git-based tooling.

**Minimal extensions.** LegalDown extends standard Markdown only where strictly necessary for legal-specific needs. Where standard Markdown constructs are sufficient, they are used unchanged.

**Open standard.** LegalDown is not proprietary. The specification is publicly available and any tooling may implement it.

### 1.3 Relationship to Standard Markdown

LegalDown is a superset of CommonMark (standard Markdown). All valid CommonMark constructs are valid LegalDown. LegalDown adds:

- YAML frontmatter for document metadata
- Section identifier syntax
- Cross-reference directives
- Definition declaration and reference directives
- Placeholder directives
- File inclusion directives
- Validation requirements for legal-specific constraints

### 1.4 Relationship to LeGit

LegalDown is the document format. LeGit is the Git-based legal document versioning and negotiation platform. LegalDown documents are the native format of LeGit repositories, but LegalDown can be used independently of LeGit with any compatible renderer or validator.

### 1.5 Conformance

Throughout this specification:

- **MUST** / **MUST NOT** — absolute requirement / prohibition
- **SHOULD** / **SHOULD NOT** — recommended but not mandatory
- **MAY** — optional feature

Implementations claiming LegalDown conformance MUST support all MUST requirements within the scope of their claimed conformance level — Core, Rendering, or Full (see Section 16).

---

## 2. File Format

### 2.1 Encoding and Extension

LegalDown documents:

- MUST be encoded in UTF-8
- MUST use file extension `.legaldown` or `.lgd`
- MAY use `.legal.md` for compatibility with Markdown tooling
- SHOULD use Unix-style line endings (LF) but MAY use CRLF

### 2.2 Document Sections

A LegalDown document consists of two parts in order:

1. **Frontmatter** (OPTIONAL) — YAML metadata block
2. **Body** (REQUIRED) — Document content in LegalDown markup

> **Note:** Signature blocks are NOT defined in LegalDown markup, and their generation is **implementation-defined** in this version of the specification. Renderers SHOULD generate signature blocks automatically from frontmatter — for contracts from all sides, for unilateral acts from the issuer side, for collective acts from the issuer side and `adopted_by` — but the content and layout of generated blocks (signing lines, representatives, dates, places, capacities) are left to the implementation and its style template (§13.7). Where an implementation generates signature blocks, party `legal_name` MUST appear on them (§3.6).

### 2.3 File References

LegalDown documents reference external files in several places: `{{include:}}` (§12), `attachments[].file` (§3.9), `amends.file` (§3.8), `translations` (§14), and image paths (§8.7). All such paths:

- MUST be relative paths — absolute paths are a validation Error
- MUST resolve to a location within the **document root** — a boundary directory that implementations MUST enforce and MUST allow to be configured (typically the repository or workspace root; it MUST NOT default to anything wider than the working tree). A path that escapes the document root (e.g., via `../` traversal) is a validation Error
- The relative-form check is syntactic and applies at Core (§16.2); root containment is checked against the configured root; file **existence** checks remain Full-level (§16.4) per each feature's validation table

This is a safety boundary for hosted validators and renderers: a document must never be able to read files outside the tree it belongs to.

---

## 3. Metadata (Frontmatter)

### 3.1 Format

Documents SHOULD include YAML frontmatter as the first element, delimited by triple dashes:

```yaml
---
legaldown: "0.1"
title: Master Service Agreement
subtitle: Between Acme Corporation and Beta Industries Inc.
version: 1.0
document_type: contract
effective_date: 2026-02-01
field_types:
  invoice-id: Invoice identifier
  cadastral-id: Cadastral territory identifier
sides:
  - name: providers
    label: Providers
    parties:
      - name: acme-corporation
        label: Acme
        type: legal_entity
        legal_name: Acme Corporation
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
        representatives:
          - name: John Smith
            title: Chief Executive Officer
  - name: clients
    label: Clients
    parties:
      - name: beta-industries
        label: Beta
        type: legal_entity
        legal_name: Beta Industries Inc.
        identification_number: TX-87654321
        address: 456 Oak Avenue, Austin, TX 78701
        representatives:
          - name: Jane Doe
            title: General Counsel
      - name: gamma-solutions
        label: Gamma
        type: legal_entity
        legal_name: Gamma Solutions Ltd.
        identification_number: CA-11223344
        address: 789 Pine Road, San Jose, CA 95101
        representatives:
          - name: Bob Johnson
            title: Managing Director
governing_law: Delaware
language: en
tags:
  - SaaS
  - B2B
  - standard
---
```

### 3.2 Standard Metadata Fields

Frontmatter is OPTIONAL as a block (§2.2) but RECOMMENDED (§3.1). The Status column below applies **when frontmatter is present**: a document without frontmatter is valid, but has no title, parties, or other metadata, and validators SHOULD emit a Warning (§15.6).

| Field | Status | Description |
|---|---|---|
| `title` | REQUIRED | Document title |
| `subtitle` | OPTIONAL | Document subtitle |
| `version` | OPTIONAL | Document version identifier |
| `legaldown` | OPTIONAL | LegalDown specification version the document targets (e.g., `"0.1"`) |
| `document_type` | OPTIONAL | Document type. Valid values: `contract`, `unilateral_act`, `collective_act`. Default: `contract` |
| `effective_date` | OPTIONAL | Document effective date (ISO 8601) |
| `field_types` | OPTIONAL | Map of custom field type declarations for `{{field:}}` (type name → description) |
| `sides` | RECOMMENDED | Array of sides, each containing a non-empty `parties` array (see Section 3.3) |
| `governing_law` | OPTIONAL | Applicable law |
| `language` | RECOMMENDED | Primary language (ISO 639-1) |
| `translations` | OPTIONAL | Map of translation files (see Section 14) |
| `authoritative` | OPTIONAL | Authoritative language for disputes (ISO 639-1); also identifies the primary document of a translation group (§14.2). RECOMMENDED when `translations` is present |
| `adopted_by` | OPTIONAL | Body or authority that adopted the document |
| `adoption_date` | OPTIONAL | Adoption date (ISO 8601) |
| `supersedes` | OPTIONAL | Prior document or version superseded by this document — a plain string, or an object with the same fields as `amends` (§3.8) |
| `amends` | OPTIONAL | Object identifying the original document this document amends (see Section 3.8) |
| `attachments` | OPTIONAL | Array of attachment objects declaring documents attached to this document (see Section 3.9) |
| `tags` | OPTIONAL | Classification tags array |

If `legaldown` is present, it declares the specification version the document was authored against. The value SHOULD be written as a quoted string (unquoted, YAML would parse `0.1` as a number). Implementations SHOULD emit a Warning when the declared version is newer than the version they implement, and MUST NOT fail solely because the declared version is unknown. When the field is absent, implementations process the document under the version they implement. A newer declared version also softens unknown-directive handling — see §11.5.

If `supersedes` is present, it MAY be either a plain string describing the superseded document, or an object with the same fields as `amends` (`title` REQUIRED, `file` OPTIONAL — §3.8).

If `field_types` is present, it MUST be a YAML map where each entry is `type-name: description`.

- Each `type-name` MUST follow the identifier format `[a-z][a-z0-9-]*`
- Each description MUST be plain text describing the custom value type
- `type-name` values MUST NOT collide with the reserved value-type names `date`, `money`, `duration`, `party`, or `text` (the built-in field specs and placeholder types, reserved so a custom type can never be confused with them)
- If `field_types` is absent entirely, implementations MUST still accept all `{{field:}}` type names that follow the identifier format

### 3.3 Sides and Parties

Parties to a document are organized under **sides**. Each side is a named grouping that contains one or more parties acting together in the document. Contracts typically have multiple sides (for example, "Providers" and "Clients"). Unilateral acts and collective acts typically include a side named `issuer`.

**Side object:**

| Field | Status | Description |
|---|---|---|
| `name` | REQUIRED | ASCII identifier (`[a-z][a-z0-9-]*`), starting with a lowercase ASCII letter and then containing only lowercase ASCII letters, digits, or hyphens; unique across sides |
| `label` | OPTIONAL | Display name (free-form Unicode, any language) |
| `parties` | REQUIRED | Non-empty array of party objects |

```yaml
sides:
  - name: providers
    label: Providers
    parties:
      - name: acme-corporation
        label: Acme
        type: legal_entity
        legal_name: Acme Corporation
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
        representatives:
          - name: John Smith
            title: Chief Executive Officer
  - name: clients
    label: Clients
    parties:
      - name: beta-industries
        label: Beta
        type: legal_entity
        legal_name: Beta Industries Inc.
        identification_number: TX-87654321
        address: 456 Oak Avenue, Austin, TX 78701
      - name: john-novak
        type: natural_person
        legal_name: John Novak
        date_of_birth: 1985-03-15
        address: 456 Oak Avenue, Austin, TX 78701
```

**Side rules:**

- `sides` is an array of side objects
- Each side object MUST contain a unique `name`
- Each side object MAY contain a `label`
- Each side object MUST contain a `parties` array with at least one party object

### 3.4 Party Structure

Each party object describes an individual or organization that appears in the document's structured metadata.

**Universal party fields:**

| Field | Status | Description |
|---|---|---|
| `name` | REQUIRED | ASCII identifier (`[a-z][a-z0-9-]*`), starting with a lowercase ASCII letter and then containing only lowercase ASCII letters, digits, or hyphens; unique across ALL parties in the document |
| `label` | OPTIONAL | Display name (free-form Unicode) |
| `type` | REQUIRED | `legal_entity` or `natural_person` |
| `legal_name` | REQUIRED | Full legal name as it appears on official documents |
| `address` | RECOMMENDED | Address |

**Additional fields for `legal_entity`:**

| Field | Status | Description |
|---|---|---|
| `identification_number` | RECOMMENDED | Registration or identification number |
| `representatives` | RECOMMENDED | Array of representative objects (see Section 3.5) |

**Additional fields for `natural_person`:**

| Field | Status | Description |
|---|---|---|
| `date_of_birth` | RECOMMENDED | Date of birth in ISO 8601 format |

A `natural_person` MAY also include `identification_number` (OPTIONAL) when the individual has a registration or national identification number (national ID, birth number, passport, etc.). `identification_number` is the reserved field name for this value across **all** party types — prefer it over a custom field so tooling can locate the identifier consistently. It is never required for a natural person, since not every individual has such a number.

Additional custom fields MAY be included on any party object. Implementations MUST ignore unknown party fields rather than failing. This allows organizations to include jurisdiction-specific information, tax identifiers, or any other relevant party metadata.

### 3.5 Representatives

Representatives are the individuals authorized to act on behalf of a party. The `representatives` field is an array of representative objects, allowing multiple representatives per party. It is RECOMMENDED for `legal_entity` parties and MAY be used for any party where such information is relevant.

```yaml
representatives:
  - name: John Smith
    title: Chief Executive Officer
  - name: Jane Doe
    title: General Counsel
```

**Representative fields:**

| Field | Status | Description |
|---|---|---|
| `name` | REQUIRED | Full name of the representative |
| `title` | OPTIONAL | Title or role of the representative |

### 3.6 Rendering Rules

- Side `label` is used for display; if absent, renderers SHOULD derive a fallback from the `name` by replacing hyphens with spaces and capitalizing each word (`disclosing-parties` → "Disclosing Parties") — no pluralization or other language-dependent transformation is applied, so providing a `label` is RECOMMENDED
- Party `label` is used for display; if absent, renderers MUST fall back to `legal_name`
- Where an implementation generates signature blocks (§2.2), party `legal_name` MUST appear on them
- `{{party: <party-name>}}` resolves against party `name` and renders `label`, falling back to `legal_name`

### 3.7 Metadata Extensions

Additional metadata fields in frontmatter are permitted. Implementations MUST ignore unknown metadata fields rather than failing. This allows forward compatibility and custom extensions.

### 3.8 Amendments Metadata

When the `amends` key is present, the document is an amendment to an existing document.

The `amends` object has the following fields:

| Field | Status | Description |
|---|---|---|
| `title` | REQUIRED | Title of the amended document |
| `file` | OPTIONAL | Relative path to the original document file |

**Rules:**

- The `amends.title` field MUST be a non-empty string
- The `amends.file` field, if present, is a relative path to the original document
- The original file MAY be a LegalDown file (`.lgd`, `.legaldown`, `.legal.md`) or a non-LegalDown file (`.pdf`, `.docx`, etc.)
- The amendment document itself follows the same structure rules as any other LegalDown document — all existing features (headings, section identifiers, cross-references, definitions, field specs, etc.) work unchanged
- An amendment MAY declare its own definitions using `{{def:}}` for new terms introduced by the amendment
- **Referencing the original's provisions:** `{{ref:}}` resolves only within the amendment itself (§6); references to the original's sections are written as literal text (e.g., "Section 5.1 of the Agreement"), citing the original's **executed rendering**. Because rendered numbers depend on the numbering scheme active at render time (§13.1), parties SHOULD pin the numbering scheme used for the executed original — for example in repository or template configuration — so such citations remain accurate. Qualified cross-document references are a Roadmap candidate (§18)

**Example:**

```yaml
---
title: First Amendment to Master Service Agreement
amends:
  title: Master Service Agreement
  file: ../original/msa.lgd
effective_date: 2026-06-01
sides:
  - name: providers
    label: Providers
    parties:
      - name: acme-corporation
        label: Acme
        type: legal_entity
        legal_name: Acme Corporation
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
        representatives:
          - name: John Smith
            title: Chief Executive Officer
  - name: clients
    label: Clients
    parties:
      - name: beta-industries
        label: Beta
        type: legal_entity
        legal_name: Beta Industries Inc.
        identification_number: TX-87654321
        address: 456 Oak Avenue, Austin, TX 78701
        representatives:
          - name: Jane Doe
            title: General Counsel
governing_law: Delaware
language: en
---
```

### 3.9 Attachments Metadata

The `attachments` key declares files that form an integral part of the document.

Each attachment object has the following fields:

| Field | Status | Description |
|---|---|---|
| `id` | REQUIRED | Identifier following standard identifier rules |
| `title` | REQUIRED | Full attachment title as it should appear in rendered output |
| `file` | REQUIRED | Relative path to the attachment file |

**Rules:**

- `attachments` is an OPTIONAL array in frontmatter
- Attachment ids MUST be unique within the document
- Attachment ids share the anchor namespace with section identifiers (§5.6) — collisions are not allowed
- The `title` is author-written and rendered verbatim — the renderer does not generate labels such as "Schedule" or "Annex" (to remain language-agnostic)
- The `file` path MAY point to a LegalDown file (`.lgd`, `.legaldown`, `.legal.md`) or a non-LegalDown file (`.pdf`, `.docx`, etc.)

**Two modes based on file type:**

| File type | Rendered inline | Content validated | Keeps order position |
|---|---|---|---|
| `.lgd` / `.legaldown` / `.legal.md` | Yes | Yes | Yes |
| Any other (`.pdf`, `.docx`, etc.) | No | No | Yes |

**Example:**

```yaml
---
title: Master Service Agreement
attachments:
  - id: schedule-a
    title: "Schedule A: Service Description"
    file: attachments/service-description.lgd
  - id: schedule-b
    title: "Schedule B: Pricing"
    file: attachments/pricing.lgd
  - id: schedule-c
    title: "Schedule C: Technical Specifications"
    file: attachments/tech-specs.pdf
---
```

### 3.10 Placeholders in Frontmatter

Frontmatter value fields MAY use the `{{placeholder:}}` directive (§10.7) to mark unfilled values in template and draft documents. This reuses the placeholder mechanism unchanged — same identifiers, types, and rendering — rather than introducing a separate "draft" concept.

```yaml
sides:
  - name: clients              # identifier — stays concrete
    parties:
      - name: client           # identifier — stays concrete
        type: legal_entity     # structural — stays concrete
        legal_name: "{{placeholder: client-legal-name}}"
        identification_number: "{{placeholder: client-id}}"
        address: "{{placeholder: client-address}}"
effective_date: "{{placeholder: effective-date, type=date}}"
```

**Rules:**

- A placeholder in frontmatter MUST be written as a quoted YAML string, because an unquoted `{{` begins a YAML flow mapping and is not valid YAML
- Placeholders MAY appear in **value** fields (for example `title`, `legal_name`, `address`, `identification_number`, `effective_date`, `governing_law`)
- Placeholders MUST NOT appear in **identifier** or **structural** fields — any side or party `name` (these must satisfy the identifier format; a party `name` is additionally referenced by `{{party:}}`), party `type`, `document_type`, `legaldown`, or the `sides`/`parties` array structure
- Type-specific placeholders follow §10.7 (for example `"{{placeholder: effective-date, type=date}}"`)
- A required field whose value is a placeholder satisfies that field's presence requirement; the document is treated as a template or draft with unfilled values
- A placeholder id used in both frontmatter and body refers to the same logical blank (§10.7)
- Renderers render frontmatter placeholders as a visible blank, consistent with §13.5 (for example `[_____]`, or `[TBD: id]` when no visual blank is available)

---

## 4. Document Structure

### 4.1 Heading Hierarchy

LegalDown uses Markdown heading syntax to define legal document hierarchy:

```
# Top-level Provision               (Level 1 — Articles / Sections)
## Second-level Provision            (Level 2 — Subsections)
### Third-level Provision            (Level 3)
#### Fourth-level Provision          (Level 4)
##### Fifth-level Provision          (Level 5)
```

**Rules:**

- Level 1 (`#`) represents top-level provisions (articles, sections)
- Heading levels MUST NOT skip levels — jumping from `#` to `###` without an intervening `##` is invalid
- The maximum heading depth is 5 (`#####`); level 6 headings (`######`) are invalid
- Setext headings (text underlined with `===` or `---`) are valid CommonMark and are treated as level 1 and level 2 headings respectively — they participate in hierarchy, numbering, and identifier generation exactly like ATX headings; ATX (`#`) style is RECOMMENDED
- Heading text MUST NOT contain hardcoded section numbers — numbering is generated at render time
- Headings SHOULD be concise and descriptive

### 4.2 Heading Text

Heading text MUST be plain text only. Heading text MUST NOT contain:

- Hardcoded numbering ("1.", "1.1", "Article I")
- Inline directives (`{{ref:}}`, `{{term:}}` etc.)
- Markdown formatting (`**bold**`, `*italic*`)

Section identifiers (anchors) in `{#id}` syntax are permitted after heading text (see Section 5).

### 4.3 Body Text

Between headings, the document body consists of standard Markdown paragraphs, lists, tables, and block elements. LegalDown-specific directives (`{{ref:}}`, `{{term:}}`, `{{def:}}` etc.) may appear within body text.

### 4.4 Preamble Content

Body content MAY appear before the first heading. Such content is the document's **preamble** — typically an introductory paragraph identifying the parties and the act (see the §17 examples).

- The preamble is valid and unnumbered — section numbering (§13.1) begins at the first heading
- All body-level directives are valid in the preamble, including `{{def:}}` declarations and field specs
- Preamble paragraphs cannot carry paragraph anchors (§5.7) and cannot be targeted by `{{ref:}}`
- Renderers place the preamble after the title block and before the first numbered provision

---

## 5. Identifiers and Anchors

### 5.1 Purpose

Section identifiers (anchors) provide stable targets for cross-references that remain valid regardless of section numbering changes. Anchors MAY also be attached to list items and top-level paragraphs (§5.7), extending the same stability to clause-level references ("Section 4.2(b)") below heading level.

### 5.2 Explicit Identifiers

Any heading MAY include an explicit identifier:

```markdown
# Payment Terms {#payment-terms}
## Late Payment Fees {#payment-late-fees}
### Monthly Calculation {#payment-late-fees-monthly}
```

**Rules for identifiers:**

- Specified using `{#identifier}` syntax placed immediately after heading text, separated by one or more spaces or tabs
- MUST be unique within the document
- MUST contain only lowercase ASCII letters (`a-z`), ASCII digits (`0-9`), and hyphens (`-`)
- MUST start with a lowercase ASCII letter
- MUST NOT contain characters outside `a-z`, `0-9`, and `-`

### 5.3 Automatic Identifier Generation

If no explicit identifier is provided, implementations MUST auto-generate one using the following algorithm. The algorithm is **fully deterministic**: two conformant implementations MUST produce the identical identifier for the same input text. It is used for section identifiers and, via §7.2, for auto-derived definition identifiers.

1. Take the heading text
2. Apply Unicode NFKD normalization, then remove all combining marks (Unicode general category `Mn`). This reduces accented Latin letters to their ASCII base letter (e.g., `é` → `e`, `ř` → `r`, `ü` → `u`)
3. Replace each occurrence of a character in the **transliteration table** below with its ASCII replacement (running after normalization, so that decomposed forms such as `ǿ` → `ø` are caught by the table)
4. Remove every remaining non-ASCII character. No other transliteration or romanization is applied — text in scripts without an ASCII decomposition (Cyrillic, Greek, CJK, etc.) is removed, not romanized (see the warning rule below)
5. Convert to lowercase
6. Replace spaces, tabs, and underscores with hyphens
7. Remove all characters that are not ASCII letters (`a-z`), ASCII digits (`0-9`), or hyphens
8. Collapse each run of consecutive hyphens into a single hyphen
9. Remove leading and trailing hyphens
10. Truncate to a maximum of 64 characters
11. Remove any trailing hyphen left by truncation
12. If the result is empty, use `section` as the identifier
13. If the result does not start with a lowercase ASCII letter (e.g., starts with a digit), prefix with `section-`; like the §5.5 collision suffixes, the prefix is exempt from the step 10 maximum — implementations MUST NOT re-truncate after prefixing

**Transliteration table.** This table is exhaustive: implementations MUST apply exactly these mappings and MUST NOT apply additional ones. It covers the Latin-script letters that NFKD normalization cannot reduce to an ASCII base.

| Character | Replacement |
|---|---|
| `ß`, `ẞ` | `ss` |
| `æ`, `Æ` | `ae` |
| `œ`, `Œ` | `oe` |
| `ø`, `Ø` | `o` |
| `đ`, `Đ` | `d` |
| `ð`, `Ð` | `d` |
| `þ`, `Þ` | `th` |
| `ł`, `Ł` | `l` |
| `ħ`, `Ħ` | `h` |
| `ı` | `i` |

**Warning rule:** If step 4 removes at least one **letter or digit** (Unicode general categories `L*` or `N*`), validators MUST emit a Warning recommending an explicit identifier — the auto-generated identifier has lost information and may be empty or collide (§5.5). Removed punctuation and symbols (em dashes, typographic apostrophes and quotation marks, etc.) do not trigger the warning, and accented Latin text transliterates deterministically without triggering it — so ordinary professionally typeset Latin-script headings stay silent.

**Examples:**

- "Confidential Information & Trade Secrets" → `confidential-information-trade-secrets`
- "Définitions Générales" → `definitions-generales`
- "Smluvní pokuta" → `smluvni-pokuta`
- "Haftungsausschluß" → `haftungsausschluss`
- "Определения" → all characters removed → `section` (with a Warning recommending an explicit identifier)

### 5.4 Identifier Scope

Section identifiers are document-global. Each section MUST have a unique identifier within the document, whether the identifier is provided explicitly or auto-generated. Section identifiers share the anchor namespace with attachment ids (§3.9, §5.6).

Implementations MUST resolve cross-references by matching the referenced identifier directly. Implementations MUST NOT construct, require, or interpret hierarchical dot-separated paths based on heading nesting.

### 5.5 Duplicate Identifier Handling

If the same identifier would be auto-generated for two different headings, implementations MUST:

1. Emit a validation warning recommending that the author add explicit identifiers to resolve the conflict
2. Append a numeric suffix to the second and subsequent identifiers (`-2`, `-3`, etc.) to ensure uniqueness for rendering purposes

Suffixes are assigned in document order, are appended after the §5.3 algorithm completes, and are exempt from the 64-character maximum.

The same handling applies when an auto-generated identifier would collide with an **explicit** anchor elsewhere in the document (a section identifier, item/paragraph anchor, or attachment id): the explicit identifier always wins, the auto-generated one receives the numeric suffix, and the warning is emitted.

### 5.6 Identifier Namespaces

All LegalDown identifiers share one format (§5.2) but live in separate **namespaces**. Uniqueness is enforced within a namespace; the same identifier text MAY appear in different namespaces without conflict, and each directive resolves only against its own namespace.

| Namespace | Members | Uniqueness | Resolved by |
|---|---|---|---|
| Anchor | Section identifiers (§5.2), item and paragraph anchors (§5.7), and attachment ids (§3.9) | Shared — unique across all | `{{ref:}}` (sections, items, paragraphs), `{{attach:}}` (attachment ids only) |
| Definition | `{{def:}}` identifiers (§7.2) | Unique among definitions | `{{term:}}` |
| Placeholder | `{{placeholder:}}` ids (§10.7) | Not applicable — repeated ids denote the same logical blank | — |
| Side | Side `name` values (§3.3) | Unique among sides | `{{side:}}` |
| Party | Party `name` values (§3.4) | Unique among all parties | `{{party:}}` |
| Field type | `field_types` keys (§3.2) | Unique keys | `{{field:}}` `type` parameter |

**Rules:**

- Section identifiers, item and paragraph anchors (§5.7), and attachment ids share the anchor namespace because all are link targets in rendered output; collisions are Errors (§15.2, §15.10). Within the shared namespace, the directives remain type-specific: `{{ref:}}` MUST resolve only against section identifiers and item/paragraph anchors, and `{{attach:}}` only against attachment ids. A `{{ref:}}` whose target is an attachment id is a broken reference (§6.3); the validator SHOULD suggest `{{attach:}}` in its diagnostic message
- Definition identifiers are unique **among definitions only**. A definition identifier MAY equal a section identifier — this is common and benign (a "Services" section and a defined term "Services" both auto-generate `services`) and is not a collision
- Placeholder ids form their own namespace; a placeholder id MAY coincide with any other identifier without relation. Repeated use of the same placeholder id denotes the same logical blank (§10.7)
- Side names, party names, and field type names are frontmatter namespaces with their own uniqueness rules (§3.3, §3.4, §3.2); they are unrelated to body identifiers
- Renderers MUST keep generated link targets unambiguous in output formats with a single anchor space (e.g., HTML) — for example by prefixing definition anchors (`def-services`) so they cannot collide with section anchors (`services`). The disambiguation scheme is implementation-defined; the source format is unaffected

### 5.7 Item and Paragraph Anchors

An explicit identifier MAY also be attached below heading level:

- To a **list item** — placed at the very end of the item's first paragraph, before any nested blocks. Permitted at any list nesting depth, but not in lists inside block quotes or tables
- To a **top-level paragraph** — a paragraph directly inside a section (not inside a list, block quote, or table, and not before the first heading), placed at the very end of the paragraph

```markdown
# Suspension {#suspension}

Provider may suspend the Services if:

- payment is overdue by more than thirty (30) days {#suspension-overdue}
- Client breaches confidentiality {#suspension-breach}
  - and the breach is material {#suspension-breach-material}
```

**Rules:**

- Item and paragraph anchors follow the identifier format and uniqueness rules of §5.2 and join the anchor namespace (§5.6); `{{ref:}}` resolves them like any other anchor
- They are **never auto-generated** — automatic generation (§5.3) applies to headings only; anchors below heading level are always explicit and opt-in
- The anchor marker is source-only and MUST NOT appear in rendered output
- The rendered designation of an anchored item or paragraph is produced by the renderer under the active template (§6.3, §13.2, §13.3) — the source never contains item letters or paragraph numbers
- A `{#id}`-like marker in any other position (mid-paragraph, in a table cell, on a block quote, before the first heading) is not an anchor and is treated as literal text; validators SHOULD emit a Warning, since it usually indicates a misplaced anchor

---

## 6. Cross-References

### 6.1 Purpose

Cross-references create links between sections within a document. Because section numbers are generated at render time, cross-references use section identifiers rather than hardcoded numbers. The renderer resolves identifiers to actual section numbers in output.

### 6.2 Reference Syntax

```markdown
{{ref: identifier}}
```

**Examples:**

```markdown
As described in Section {{ref: definitions}}, terms have specific meanings.

Subject to Clause {{ref: liability-cap}}, Provider shall indemnify Client.

The payment schedule in Article {{ref: payment-schedule}} applies from the Effective Date.
```

**Rules:**

- The identifier MUST be a section identifier or an item/paragraph anchor (§5.7). `{{ref:}}` resolves against those members of the anchor namespace (§5.6); attachments are referenced with `{{attach:}}` (§6.4). A `{{ref:}}` targeting an attachment id is a broken reference, and validators SHOULD suggest `{{attach:}}` in the diagnostic message

> **Note:** The word before a reference ("Section", "Article", "Clause") is ordinary body text chosen by the author, while the number comes from the render-time numbering scheme (§13.1). Changing the scheme can make the author's word read unconventionally — e.g., "Section I.A" under the legal outline scheme, where "Article I.A" is customary. Authors SHOULD choose wording compatible with the schemes the document will render under; a template-supplied reference label is a Roadmap candidate (§18).

### 6.3 Reference Rendering

Renderers MUST:

1. Locate the target section by identifier
2. Determine the rendered section number based on the active numbering scheme
3. Replace the reference with the section number (e.g., "3.2")
4. Create a hyperlink to the target section in formats that support hyperlinking (HTML, PDF, DOCX)
5. If the target identifier does not exist, insert `[BROKEN REF: identifier]` in output and emit a validation error

When the target is an **item or paragraph anchor** (§5.7), the rendered designation is the containing section's number followed by the item's enumeration path or the paragraph's number under the active template (e.g., "3.1(a)", "3.1(b)(ii)", "5.2" — §13.2). If the active template does not enumerate the containing list or does not number paragraphs, the renderer MUST fall back to the containing section's number alone and emit a validation Warning.

Rendering under the "None" numbering scheme and across attachment numbering restarts is defined in §13.3.

### 6.4 Attachment References

**Syntax:**

```markdown
{{attach: attachment-id}}
{{attach: attachment-id, label=text}}
```

**Examples:**

```markdown
Services are described in {{attach: schedule-a}}.

Pricing is set out in {{attach: schedule-b, label=Schedule B}}.

Technical requirements per {{attach: schedule-c}} shall apply.
```

**Rendering rules:**

- Resolves to the attachment `title` from frontmatter; the optional `label` parameter (plain text, §11.3 value rules) overrides the displayed text — useful mid-sentence, where the full title reads awkwardly
- Creates a hyperlink to the attachment in formats that support linking
- For LegalDown attachments — links to the rendered attachment section
- For non-LegalDown attachments — links to the external file
- If the id is not found, insert `[UNKNOWN ATTACHMENT: id]` in output and emit a validation error

---

## 7. Definitions

### 7.1 Purpose

Defined terms are a fundamental feature of legal contracts. LegalDown provides structured syntax for declaring definitions and referencing them consistently throughout a document.

### 7.2 Definition Declaration

A definition is declared by placing the `{{def:}}` directive **immediately after the quoted term** being defined. The defined term is the text inside the quotation marks of the quoted span that the directive follows. The same syntax is used everywhere — whether the term is introduced in a dedicated Definitions section or inline at its first use.

```markdown
# Definitions {#definitions}

"Confidential Information" {{def: confidential-info}} means any non-public information disclosed by
one party to the other, including technical data, business plans, customer information, and any
other information designated as confidential.

"Services" {{def: services}} means the software development services described in Section
{{ref: scope-of-work}}.
```

The directive marks the preceding quoted span as a defined term, registers its identifier, and produces no visible output of its own. It MAY also appear inline at the point a term is first used:

```markdown
The Provider shall perform the marketing services described in this Article
(the "Services" {{def: services}}).
```

**Term extraction:**

- The defined term is the text inside the quotation marks of the quoted span that immediately precedes the directive
- The directive MUST be on the same line as the quoted span; only optional spaces or tabs (no line break) may appear between the closing quotation mark and the directive. If any other character intervenes, the directive is not attached to that span
- A `{{def:}}` not immediately preceded by a recognized quoted span is an error
- Defined terms MUST NOT carry emphasis markers in source (e.g., `**bold**`); how a defined term is displayed (bold, underline, small caps) is determined at render time by the style template (§13.7)
- The quotation marks are a source-only delimiter: they are NOT part of the defined term and MUST NOT be rendered. At both the defining occurrence and every `{{term:}}` reference, the term is rendered as the text inside the marks, without the marks. A template marks defined terms visually through styling (e.g., bold), never by re-adding quotation marks

**Accepted quotation marks:**

A quoted span is delimited by one of the recognized opening/closing quotation-mark pairs below. By default all pairs are accepted; the active set MAY be narrowed or extended per document `language` or by renderer/validator configuration.

| Pair | Opening | Closing | Code points |
|---|---|---|---|
| Straight double | `"` | `"` | U+0022 / U+0022 |
| Curly double | `“` | `”` | U+201C / U+201D |
| Guillemets | `«` | `»` | U+00AB / U+00BB |
| Reversed guillemets | `»` | `«` | U+00BB / U+00AB |
| Low-high double | `„` | `“` | U+201E / U+201C |
| Curly single | `‘` | `’` | U+2018 / U+2019 |
| Low-high single | `‚` | `‘` | U+201A / U+2018 |
| Single guillemets | `‹` | `›` | U+2039 / U+203A |

- The parser matches the closing delimiter immediately preceding the directive, then scans back to the corresponding opening delimiter to delimit the term. For symmetric pairs (where opening and closing are the same character) it pairs with the nearest prior identical mark on the same line.
- This matching is deterministic only because **no character in the active set serves as the closing mark of two different pairs**. Configured sets — narrowed or extended per document `language` or implementation configuration — MUST preserve that property. When the backward scan fails to find the opening mark, the §15.4 no-quoted-span Error applies; the diagnostic SHOULD mention mismatched or typo'd quotation marks as a likely cause.
- Double-quote forms are RECOMMENDED. Single-quote forms are accepted, but because the right single quotation mark (U+2019) also serves as an apostrophe, a single-quoted term containing an apostrophe may be mis-delimited; validators SHOULD emit a warning in that case.

**Identifiers:**

- Definition identifiers follow the same format rules as section identifiers (§5.2) and MUST be unique among definitions within the document. Definitions form their own namespace (§5.6): a definition identifier MAY equal a section identifier without conflict
- The identifier MAY be omitted; when omitted, implementations MUST auto-generate it from the defined term using the algorithm in §5.3 (e.g., `"Services" {{def:}}` → `services`)
- Explicit identifiers are RECOMMENDED for stability, and are REQUIRED to disambiguate when two different terms would auto-generate the same identifier

**Placement:**

- A `{{def:}}` MAY appear anywhere in the document body — in a dedicated Definitions section, or inline at the point a term is first used
- There is no required, single, or first-positioned Definitions section
- Authors MAY collect stipulative definitions under a conventional "Definitions" heading; this is RECOMMENDED for readability but not required
- Definitions MAY also be introduced inside attachment files (§12.4) and included fragments (§12.2); such definitions register document-wide terms

**Scope (for tooling):** A definition records its identifier, term text, and location. LegalDown does not store a separate "definition text." For purposes such as circular-reference detection and optional glossary previews, a definition's scope is the paragraph containing the `{{def:}}` directive. A `{{term:}}` link targets the definition's location (the `{{def:}}` anchor); a generated glossary entry points to the section or clause containing it.

### 7.3 Definition Reference

Defined terms are referenced using the `{{term:}}` directive:

```markdown
{{term: definition-id}}
{{term: definition-id, label=Custom Display Text}}
```

The optional `label` parameter specifies text to display in place of the defined term. This is useful when the defined term must appear in a grammatically inflected form (e.g., declension, conjugation, or other morphological variation required by the document's language). LegalDown does not encode morphological variants in the schema; supplying the correct inflected `label` is left to authoring tools, which MAY generate it automatically.

**Examples:**

```markdown
Each party shall protect the {{term: confidential-info}} from unauthorized disclosure.

Provider shall deliver the {{term: services}} in accordance with the agreed specifications.

Client may use the {{term: services, label=Hosted Services}} solely for its internal business operations.
```

In the last example, the defined term is "Services" but the label `Hosted Services` is displayed in the rendered output, allowing the text to use a context-appropriate English label.

**Rules:**

- The `label` parameter is OPTIONAL
- When `label` is present, renderers MUST display the label text instead of the defined term
- The label value follows the value rules in §11.3: unquoted, it MUST NOT contain commas or closing braces (`}}`); the quoted form MAY contain both (e.g., `label="Services, as amended"`)
- The `label` value is plain text — it MUST NOT contain Markdown formatting or nested directives

**Rendering:**

Renderers MUST:

1. Locate the definition by identifier
2. If a `label` parameter is provided, use the label text as the display text
3. Otherwise, use the defined term text — the text inside the quotation marks at the definition site, without the delimiting marks (§7.2)
4. Replace `{{term: id}}` (or `{{term: id, label=...}}`) with the display text
5. Create a hyperlink to the definition's location (the `{{def:}}` anchor) in formats that support hyperlinking
6. If the definition is not found, insert `[UNDEFINED: id]` and emit a validation error

### 7.4 Optional Automatic Term Recognition

Implementations MAY support automatic recognition of defined terms without explicit `{{term:}}` directives, linking any occurrence of a defined term's text to its definition automatically. When this is enabled:

- Implementations SHOULD make this behavior configurable
- The feature SHOULD be disabled by default to avoid false positives
- Explicit `{{term:}}` is RECOMMENDED for precision

### 7.5 Definition Resolution in Amendments

When a document contains an `amends` key in frontmatter, definition validation follows special resolution rules based on whether the original document is available and in LegalDown format:

**When `amends.file` points to a LegalDown file (`.lgd`, `.legaldown`, `.legal.md`):**

- The validator MUST load the original document and import its `{{def:}}` declarations into the amendment's validation scope
- `{{term:}}` directives in the amendment resolve against both the amendment's own definitions and the imported definitions from the original
- Imported definitions do not need to be redeclared in the amendment
- If the amendment declares a `{{def:}}` with the same id as a definition in the original, the validator MUST emit a Warning (intentional override of original definition)

**When `amends.file` points to a non-LegalDown file (`.pdf`, `.docx`, etc.):**

- The validator cannot import definitions from the original
- `{{term:}}` directives referencing ids not declared in the amendment itself MUST emit an Info-level message rather than a validation Error; this amendment-specific rule overrides the general missing-definition validation error requirement (including Section 7.3 Rendering step 6)

**When `amends.file` is absent:**

- No cross-validation is possible
- `{{term:}}` directives referencing ids not declared in the amendment itself MUST emit an Info-level message rather than a validation Error; this amendment-specific rule overrides the general missing-definition validation error requirement (including Section 7.3 Rendering step 6)

---

## 8. Text Formatting

### 8.1 Inline Formatting

All standard CommonMark inline formatting is supported:

- `**bold**` or `__bold__` — Bold text (used for emphasis)
- `*italic*` or `_italic_` — Italic text (used for emphasis)
- `` `code` `` — Monospace/code (used for technical specifications)

> **Note:** Defined terms are not marked with emphasis in source. A defined term is written in quotation marks followed by `{{def:}}` (see §7.2); its visual styling is applied by the renderer, and the delimiting quotation marks themselves are not rendered.

### 8.2 Lists

Unordered and ordered lists follow standard Markdown syntax.

**Unordered list:**
```markdown
Provider shall:

- perform the Services diligently
- maintain adequate professional insurance
- comply with all applicable laws and regulations
```

**Ordered list:**
```markdown
Termination shall proceed as follows:

1. The terminating party provides written notice
2. A cure period of thirty (30) days commences
3. If uncured, termination takes effect at period end
```

**Rules:**

- Lists MUST have a blank line before and after
- Nested lists are supported with consistent indentation (2 or 4 spaces)
- Renderers SHOULD convert unordered lists to legal enumeration — (a), (b), (c); (i), (ii), (iii) — and MAY apply the same enumeration to ordered lists, per §13.2; ordered-list numbers in source are never authoritative (items are renumbered at render time)

### 8.3 Nested Lists

```markdown
The following restrictions apply:

- Restriction A
  - Sub-restriction 1
  - Sub-restriction 2
- Restriction B
  - Sub-restriction 3
    - Further detail
```

Renderers SHOULD apply appropriate legal enumeration at each nesting level based on the active style template.

### 8.4 Block Quotes

Block quotes are used for recitals, WHEREAS clauses, preambles, and quoted text:

```markdown
> WHEREAS, Provider possesses expertise in software development services; and
>
> WHEREAS, Client desires to engage Provider for certain technology services;
>
> NOW, THEREFORE, in consideration of the mutual covenants herein, the parties agree as follows:
```

### 8.5 Horizontal Rules

Horizontal rules (`---`) MAY be used to visually separate major document divisions such as between the main agreement and schedules.

### 8.6 Comments

HTML-style comments are valid in LegalDown and MUST be stripped from all rendered output:

```markdown
<!-- Internal note: this clause was revised on 2026-01-15 per partner review -->

# Limitation of Liability {#liability-limitations}
```

### 8.7 Inherited CommonMark Features

As a CommonMark superset (§1.3), LegalDown documents may contain constructs to which this specification assigns no legal-drafting semantics. They are handled as follows:

- **Raw HTML** (inline or block), other than comments (§8.6): ignored for rendered output by default — renderers MUST NOT emit it into output — and a validation Warning is emitted. Implementations MAY support the extended-table exception of §9.2 as a documented extension
- **Links** (`[text](url)` and autolinks): valid. Renderers MUST render them as hyperlinks in formats that support linking; in print-oriented output, style templates MAY additionally render the URL visibly (e.g., in parentheses or a note)
- **Images** (`![alt](path)`): valid. The path follows the file-reference rules of §2.3; the image is rendered where the output format supports images and replaced by its alt text where it does not. Existence checking of image paths is a Full-level capability (§16.4)

---

## 9. Tables

### 9.1 Standard Tables

LegalDown supports standard Markdown tables for pricing schedules, comparison matrices, and structured data:

```markdown
| Service Tier | Monthly Volume | Unit Price |
|---|---|---|
| Standard | 0 – 1,000 units | $0.50 |
| Professional | 1,001 – 5,000 units | $0.40 |
| Enterprise | 5,000+ units | $0.30 |
```

**Rules:**

- Tables MUST include a header row
- Alignment MAY be specified using colons in the separator row
- Renderers SHOULD format tables professionally in PDF and DOCX output

### 9.2 Table Limitations

Standard Markdown tables do not support merged cells or complex formatting. For complex tables, implementations MAY:

- Support extended table syntax as a documented extension
- Allow raw HTML `<table>` elements within LegalDown
- Support inclusion of tables from external files via `{{include:}}`

---

## 10. Field Specs

### 10.1 Purpose

Field specs are typed inline directives that represent structured values — including dates, monetary amounts, pass-through custom values, and fillable placeholders — within the document text. They enable renderers to format values consistently according to locale and template settings, and validators to verify that values are well-formed.

The **active locale** used for formatting (date order, decimal and grouping separators, etc.) is a render-time setting — part of the style template or renderer configuration (style templates list the locale among their settings, §13.7) — not a frontmatter field. LegalDown documents do not declare a formatting locale. Renderers MAY use the document `language` as a hint. The underlying value (ISO date, numeric amount) is stored canonically, so only its display varies by locale.

All field specs MAY include an optional `note` parameter to provide a plain-text explanation of the value for automation or machine-processing purposes. The `note` value MUST NOT affect rendered output. It follows the value rules in §11.3: unquoted, it MUST NOT contain commas or closing braces (`}}`); the quoted form MAY contain both.

The LegalDown source file is itself the canonical machine-readable representation of a document — the raw values of all field specs (and their `note` annotations) are always available by parsing the source. LegalDown defines no export or interchange format.

### 10.2 Date Directive

The `{{date:}}` directive represents a calendar date inline in document text.

**Syntax:**

```markdown
{{date: YYYY-MM-DD}}
{{date: YYYY-MM-DD, note=text}}
```

**Examples:**

```markdown
This Agreement shall terminate on {{date: 2026-06-01}}.

Provider shall deliver the final report no later than {{date: 2027-03-31, note=Final delivery deadline}}.
```

**Rules:**

- The date value MUST be in ISO 8601 format (`YYYY-MM-DD`)
- The date MUST be a valid calendar date (e.g., `2026-02-30` is invalid)
- Renderers MUST format the date according to the active locale or render template settings (e.g., "June 1, 2026", "1 June 2026", "2026-06-01")

### 10.3 Money Directive

The `{{money:}}` directive represents a monetary amount inline in document text.

**Syntax:**

```markdown
{{money: amount}}
{{money: amount, note=text}}
{{money: amount, currency=CODE}}
{{money: amount, currency=CODE, note=text}}
```

**Examples:**

```markdown
Provider shall pay a penalty of {{money: 10000, currency=USD}} for each day of delay.

The total contract value shall not exceed {{money: 1000000, currency=USD}}.

The monthly fee is {{money: 500, currency=EUR, note=Base monthly service fee}}.
```

**Rules:**

- The amount MUST be a non-negative numeric value (integer or decimal, using period `.` as the decimal separator); negative amounts are invalid — express reductions, credits, or deductions in the surrounding prose
- The amount MUST NOT include grouping separators, currency symbols, or whitespace
- Renderers MUST NOT round, truncate, or otherwise alter the numeric value. Display formatting — separators, currency symbol, and padding to the currency's conventional minor units (e.g., "10000" → "$10,000.00") — follows the active locale and template settings per the formatting rule below
- The optional `currency` parameter specifies the currency using an ISO 4217 three-letter code (e.g., `USD`, `EUR`, `CZK`, `GBP`)
- If `currency` is omitted, the renderer MAY apply a default currency configured in the render template or renderer configuration; if none is configured, it MUST emit a validation warning. LegalDown defines no document-level default currency — currency is specified per `{{money:}}` directive
- Renderers MUST format the amount according to the active locale or render template settings (e.g., "$10,000.00", "USD 10,000.00", "€500.00")

### 10.4 Party Directive

The `{{party:}}` directive represents a reference to a party declared in frontmatter. It identifies a party by its `name` identifier and allows an optional inline display override for grammatical or stylistic inflection.

**Syntax:**

```markdown
{{party: party-name}}
{{party: party-name, label=text}}
{{party: party-name, note=text}}
{{party: party-name, label=text, note=text}}
```

**Examples:**

```markdown
The Company acts through {{party: acme-corporation, label=the Company}} under this Agreement.

Notices under this Agreement shall be delivered to {{party: beta-industries}}.

{{party: acme-corporation, label=the Company, note=Adopting entity}} may amend this Policy from time to time.
```

**Rules:**

- The `party-name` value MUST be a non-empty string matching the identifier format `[a-z][a-z0-9-]*` (a lowercase ASCII letter followed by zero or more lowercase ASCII letters, digits, or hyphens)
- The directive MUST resolve against a party `name` in the frontmatter `sides[].parties[]` arrays
- The optional `label` parameter specifies display text for rendering; if omitted, the renderer MUST use the party's `label` and fall back to `legal_name`
- The `label` value is plain text — it MUST NOT contain Markdown formatting or nested directives; per §11.3, the unquoted form MUST NOT contain commas or closing braces (`}}`), while the quoted form MAY (e.g., `label="Smith, Jones & Co."`)
- Renderers MUST format the resolved party reference according to the active locale or render template settings

### 10.5 Duration Directive

The `{{duration:}}` directive represents a time duration inline in document text. It specifies a numeric value and a time unit.

**Syntax:**

```markdown
{{duration: value, unit=UNIT}}
{{duration: value, unit=UNIT, note=text}}
```

Where `UNIT` is one of: `S` (seconds), `MIN` (minutes), `H` (hours), `D` (days), `W` (weeks), `MO` (months), `Y` (years).

**Examples:**

```markdown
This Agreement shall remain in effect for {{duration: 12, unit=MO}}.

The notice period shall be {{duration: 30, unit=D}}.

The cure period shall be {{duration: 2, unit=W}}.

The service level response time shall not exceed {{duration: 4, unit=H, note=Critical incident response target}}.
```

**Rules:**

- The `value` MUST be a positive numeric value (integer or decimal, using period `.` as the decimal separator); zero and negative values are not allowed
- The `unit` parameter is REQUIRED and MUST be one of: `S`, `MIN`, `H`, `D`, `W`, `MO`, `Y`. The bare unit `M` is deliberately not defined — in ISO 8601 it denotes months while earlier drafts used it for minutes; validators MUST reject it with a diagnostic suggesting `MIN` (minutes) or `MO` (months)
- Renderers MUST format the duration according to the active locale or render template settings (e.g., "12 months", "30 days", "4 hours", "1 year")

### 10.6 Custom Field Directive

The `{{field:}}` directive represents a custom structured value inline in document text. It uses a caller-defined type name and passes the raw value through unchanged for rendering.

**Syntax:**

```markdown
{{field: value, type=type-name}}
{{field: value, type=type-name, note=text}}
```

**Examples:**

```markdown
The property {{field: CZ0100000001, type=cadastral-id}} is transferred...

Pursuant to {{field: 25 Cdo 1234/2025, type=case-number}}...

Invoice {{field: INV-2026-0042, type=invoice-id}} remains unpaid.
```

**Relationship to built-ins:**

| Directive | Formatting | Validation | Declaration needed |
|---|---|---|---|
| `{{date:}}` | Locale-aware | Built-in | No |
| `{{money:}}` | Locale-aware | Built-in | No |
| `{{duration:}}` | Locale-aware | Built-in | No |
| `{{field:}}` | Pass-through | By declaration | Optional (recommended when using `field_types`) |

**Rules:**

- The `value` is REQUIRED
- The `value` is the first positional parameter of the directive
- Because commas separate directive parameters and `}}` terminates the directive, an unquoted `value` MUST NOT contain a comma (`,`) or the sequence `}}`. A quoted `value` (§11.3) MAY contain both: `{{field: "Smith, Jones & Co. v. Doe", type=case-name}}`
- Optional whitespace immediately after `{{field:` and optional whitespace surrounding parameter separators is directive syntax and is not part of the `value`; so is the quoting of a quoted `value`
- After parsing (including removal of value quoting and application of the §11.3 escape sequences), implementations MUST preserve the resulting `value` exactly, with no further trimming, normalization, character escaping/unescaping, or locale-aware formatting
- The `type` parameter is REQUIRED and MUST follow the identifier format `[a-z][a-z0-9-]*`
- If frontmatter `field_types` is present, the `type` SHOULD match a declaration in `field_types`
- If `field_types` is absent entirely, implementations MUST accept any `type` value that follows the identifier format without emitting a warning
- Renderers MUST pass the parsed `value` through unchanged

### 10.7 Placeholder Directive

The `{{placeholder:}}` directive represents a fillable inline blank. Placeholders are declared directly where they are used and MUST NOT require any separate frontmatter declaration. They appear in document text and MAY also appear as quoted string values in frontmatter (see §3.10).

**Syntax:**

```markdown
{{placeholder: placeholder-id}}
{{placeholder: placeholder-id, type=text}}
{{placeholder: placeholder-id, type=date}}
{{placeholder: placeholder-id, type=money, currency=EUR}}
{{placeholder: placeholder-id, note=text}}
{{placeholder: placeholder-id, type=money, currency=EUR, note=text}}
```

**Examples:**

```markdown
The purchase price shall be {{placeholder: purchase-price, type=money}}.

Delivery by {{placeholder: delivery-date, type=date}}.

Governed by the laws of {{placeholder: governing-jurisdiction}}.
```

**Rules:**

- The `placeholder-id` value MUST be a non-empty string matching the identifier format `[a-z][a-z0-9-]*` (a lowercase ASCII letter followed by zero or more lowercase ASCII letters, digits, or hyphens)
- The `type` parameter is OPTIONAL; if omitted, implementations MUST treat it as `text`
- Implementations MUST support placeholder types `text`, `date`, and `money`
- Additional type-specific parameters MAY be provided when defined for the selected `type`; for `type=money`, `currency` MAY be provided using an ISO 4217 three-letter code
- The `note` parameter is OPTIONAL and follows the general field spec rules in Section 10.1
- Multiple occurrences using the same `placeholder-id` refer to the same logical blank
- Placeholder ids form their own namespace (§5.6) — a `placeholder-id` MAY coincide with a section, attachment, or definition identifier without any relation between them
- All occurrences of the same `placeholder-id` MUST use the same effective `type`
- When the same `placeholder-id` appears multiple times with type-specific parameters, those parameters SHOULD remain consistent across occurrences; validators MAY emit a warning when they differ

### 10.8 Side Directive

The `{{side:}}` directive references a **side** declared in frontmatter (§3.3) — the collective grouping of parties — by its `name` identifier, with an optional inline display override. It is the collective counterpart of `{{party:}}` (§10.4).

**Syntax:**

```markdown
{{side: side-name}}
{{side: side-name, label=text}}
{{side: side-name, note=text}}
{{side: side-name, label=text, note=text}}
```

**Examples:**

```markdown
The {{side: clients, label=Clients}} shall be jointly and severally liable for the fees.

Notices to the {{side: providers}} shall be delivered to each of its parties.
```

**Rules:**

- The `side-name` value MUST be a non-empty string matching the identifier format `[a-z][a-z0-9-]*`
- The directive MUST resolve against a side `name` in the frontmatter `sides[]` array
- The optional `label` parameter specifies display text for rendering; if omitted, the renderer MUST use the side's `label`, falling back to the §3.6 derivation from `name` (hyphens replaced by spaces, each word capitalized)
- The `label` and `note` values are plain text and follow the value rules in §11.3

---

## 11. Directives

All LegalDown-specific extensions use double-brace directive syntax `{{directive: argument}}` to clearly distinguish them from standard Markdown and avoid ambiguity. This section defines the directive vocabulary (§11.1), the formal syntax shared by all directives (§11.2), value quoting (§11.3), and where directives are recognized (§11.4).

### 11.1 Core Directives

| Directive | Level | Purpose |
|---|---|---|
| `{{ref: id}}` | Core | Cross-reference to section |
| `{{def: id}}` | Core | Mark the preceding quoted term as a definition (`id` optional; auto-derived from the term when omitted) |
| `{{term: id}}` | Core | Reference a defined term |
| `{{term: id, label=text}}` | Core | Reference a defined term with custom display text |
| `{{date: YYYY-MM-DD}}` | Core | Inline date value |
| `{{money: amount}}` | Core | Inline monetary amount |
| `{{money: amount, currency=CODE}}` | Core | Inline monetary amount with currency |
| `{{party: party-name}}` | Core | Inline party reference by name |
| `{{party: party-name, label=text}}` | Core | Inline party reference with display text |
| `{{side: side-name}}` | Core | Inline side (collective) reference by name |
| `{{side: side-name, label=text}}` | Core | Inline side reference with display text |
| `{{duration: value, unit=UNIT}}` | Core | Inline time duration with unit |
| `{{field: value, type=type-name}}` | Core | Inline custom typed value with pass-through rendering |
| `{{placeholder: placeholder-id}}` | Core | Inline fillable blank (defaults to `type=text`) |
| `{{placeholder: placeholder-id, type=money, currency=CODE}}` | Core | Inline typed blank with type-specific parameters |
| `{{include: path}}` | Full | Include external file |
| `{{attach: id}}` | Core | Reference a declared attachment |
| `{{attach: id, label=text}}` | Core | Attachment reference with display text |

The **Level** column states the conformance level (Section 16) at which implementations MUST support the directive. `{{include:}}` expansion is a Full capability, and rendering the *content* of attachment files referenced via `{{attach:}}` is likewise Full (§16.4); resolving `{{attach:}}` to its declared `title` is Core. The column says nothing about documents: no directive is ever required to appear in a document — which directives to use is an authoring choice.

### 11.2 Formal Grammar

Every directive conforms to the following grammar (EBNF):

```ebnf
directive        ::= "{{" name ":" ws* [ argument ( ws* "," ws* argument )* ] ws* "}}"
name             ::= lowercase+
argument         ::= named-parameter | positional-value
named-parameter  ::= parameter-name "=" value
parameter-name   ::= lowercase ( lowercase | digit | "-" )*
positional-value ::= value
value            ::= quoted-value | unquoted-value
quoted-value     ::= '"' ( escape | quoted-char )* '"'
escape           ::= "\" ( '"' | "\" )
quoted-char      ::= any character except '"' and line breaks
unquoted-value   ::= any run of characters not containing ",", the sequence "}}",
                     or line breaks, and not beginning with '"'; leading and
                     trailing whitespace is trimmed
ws               ::= " " | tab
lowercase        ::= "a" ... "z"
digit            ::= "0" ... "9"
```

**Rules:**

- No whitespace is permitted between `{{` and the name, or between the name and `:`. Whitespace after the `:`, around commas, and before `}}` is optional directive syntax and never part of a value
- The entire directive MUST appear on a single line (§11.5)
- A directive takes **at most one positional value**, which MUST precede all named parameters
- An argument is a **named parameter** if and only if it begins with a `parameter-name` immediately followed by `=` (no intervening whitespace); every other argument is positional. An unquoted positional value whose text would match that pattern MUST be written as a quoted value (§11.3) to avoid misinterpretation
- Named parameters are **order-insensitive**. The examples in this specification show a conventional order (type-specific parameters first, `note` last), which is RECOMMENDED for readability but not required
- A directive MUST NOT contain the same named parameter more than once — validators MUST report a duplicate as an Error
- A named parameter whose name is not defined for the directive MUST be ignored for rendering and reported as a validation Warning (consistent with §13.5, placeholder rule 7)
- Which arguments a directive requires or permits — and any constraints on their values beyond this grammar — are defined in that directive's own section (§6, §7, §10, §12)

### 11.3 Value Quoting

Any positional value or named-parameter value MAY be enclosed in straight double quotes (U+0022). Quoting is part of directive syntax, not of the value: after parsing, a quoted and an unquoted spelling of the same value are indistinguishable, and all downstream rules (rendering, `{{field:}}` pass-through preservation) apply to the decoded value.

Quoting exists to carry characters that are otherwise directive syntax:

```markdown
{{term: services, label="Services, as amended"}}

{{field: "Smith, Jones & Co. v. Doe", type=case-name}}

{{party: sjc, label="Smith, Jones & Co."}}
```

**Rules:**

- An **unquoted** value MUST NOT contain a comma (`,`), the sequence `}}`, or a line break, and MUST NOT begin with `"`; its leading and trailing whitespace is trimmed
- A value whose first non-whitespace character is `"` MUST be parsed as a quoted value. If its closing quote is missing, the directive is malformed (§15.2) — it never falls back to an unquoted parse
- A **quoted** value MAY contain commas, the sequence `}}`, `=`, and leading or trailing spaces (all preserved exactly); it MUST NOT contain a line break
- Within a quoted value, `\"` denotes a literal double quote and `\\` denotes a literal backslash; the `escape` alternative is matched preferentially over `quoted-char`. A backslash followed by any other character is not an escape sequence — it is an ordinary `quoted-char` and is preserved as written (e.g., `{{field: "C:\Users\doe", type=path}}` is valid, and the value is `C:\Users\doe`)
- A quoted value MUST be terminated by a closing `"` on the same line, followed only by optional whitespace and then `,` or `}}`; anything else makes the directive malformed (§15.2)
- Only the straight double quote (U+0022) delimits quoted values. Typographic quotation marks (`“ ” „ « »` etc.) are ordinary value characters — validators SHOULD emit a Warning when an unquoted value begins with one, since it usually means an editor auto-curled an intended quote

### 11.4 Recognition Contexts and Escaping

Directives are recognized in body text — paragraphs, list items, table cells, and block quotes — and in frontmatter only as specified in §3.10. Heading text MUST NOT contain directives (§4.2).

Directives are **not** recognized inside:

- Inline code spans (`` ` ``)
- Fenced or indented code blocks
- HTML comments (`<!-- -->`) — their content is stripped from output regardless (§8.6)

In those contexts, directive-like text is literal text.

**Escaping a literal `{{`:** LegalDown inherits CommonMark backslash escapes for punctuation, so escaping the first brace (`\{`) prevents the sequence from forming a directive opener — `\{{ref: x}}` renders as the literal text `{{ref: x}}`.

**Opener commitment:** In a recognized context, an unescaped `{{` immediately followed by a `name` and `:` begins a directive; if the directive cannot be completed according to the grammar on the same line (including an unterminated quoted value), it is malformed — a validation Error (§15.2). An unescaped `{{` **not** followed by a `name` and `:` is literal text; validators SHOULD emit a Warning, since stray double braces usually indicate a typo.

### 11.5 General Directive Rules

- Directives are case-sensitive — always lowercase
- Directives MUST NOT span multiple lines
- An unknown directive (well-formed per §11.2, but with a name this specification does not define) is a validation **Error**. Renderers MUST replace it with `[UNKNOWN DIRECTIVE: name]` — consistent with the other bracketed failure markers — and MUST NOT print the directive source verbatim into rendered output (a typo like `{{trem: services}}` must never leak into an executed document)
- Implementations MAY offer an explicit, non-default permissive mode that instead emits a Warning and passes unknown directives through as-is (forward compatibility with future directive names)
- When the document declares a `legaldown` version newer than the implementation supports (§3.2), validators SHOULD report unknown directives as Warnings rather than Errors — they may be constructs introduced by the newer version, and §3.2 promises processing does not fail solely on an unknown version; the `[UNKNOWN DIRECTIVE: name]` rendering marker still applies
- Implementations MUST NOT fail silently on unknown directives

---

## 12. File Inclusion

### 12.1 Syntax

File inclusion inserts the content of an external LegalDown fragment at the position of the directive. Include processing is a Full-level capability (§16.4).

```markdown
# Schedule A — Service Description {#schedule-a}

{{include: schedules/service-description.lgd}}

# Schedule B — Pricing {#schedule-b}

{{include: schedules/pricing.lgd}}
```

### 12.2 Include Fragments

Include targets use the same file model as LegalDown attachment files (§12.4): they are **body-only LegalDown fragments**, not standalone documents.

- The include target MUST be a LegalDown file (`.lgd`, `.legaldown`, or `.legal.md`); non-LegalDown files cannot be included
- The included fragment MUST NOT contain YAML frontmatter — the main document's frontmatter applies
- The included fragment MUST NOT contain a level 1 heading (`#`) — the author writes the surrounding heading in the including document, as in the §12.1 example
- Include paths MUST be relative to the including document
- Content is spliced verbatim at the directive position; heading levels are **not** re-based. The combined document MUST satisfy the heading hierarchy rules (§4.1) — a fragment whose headings would skip a level at its insertion point is invalid
- A fragment MAY itself contain `{{include:}}` directives; circular includes MUST be detected across the entire include chain and rejected with an error
- A `{{def:}}` inside an included fragment registers a document-wide term, exactly as in attachment files (§7.2, §12.4)
- Section identifiers in included fragments MUST be unique across the entire combined document
- Validation of the combined document (including all inclusions) is REQUIRED (§15.11)

### 12.3 Distinction from Attachments

| Aspect | `{{include:}}` | Attachments |
|---|---|---|
| Purpose | Inline content insertion at directive position | Structurally distinct appendix to the document |
| Position in output | Where the directive appears in body | After main body, in declared order |
| Heading | Author writes it in body | Renderer generates from frontmatter `title` |
| Metadata | None | `id`, `title`, `file` in frontmatter |
| File model | Body-only fragment — no frontmatter, no `#` (§12.2) | Body-only fragment — no frontmatter, no `#` (§12.4) |
| Referenceable by | Section ids and item/paragraph anchors (§5.7) | `{{attach: id}}` directive |
| Non-LegalDown files | Not supported | Supported (tracked but not rendered) |

### 12.4 Attachment Files

LegalDown attachment files are body-only LegalDown content fragments included by a parent LegalDown document. They MUST NOT contain frontmatter. They MUST NOT contain a level 1 heading (`#`). They inherit the parent document's context — definitions, field types, metadata. Attachment files are not standalone LegalDown documents for purposes of §4.1 and §15.2 validation. Instead, attachment files are validated using the attachment-specific rules in this section and §15.10, plus any validation that applies across the combined document such as identifier uniqueness.

**What attachment files can use:**

- All standard LegalDown body syntax, except standalone-document structure requirements (for example, frontmatter)
- `{{term:}}` referencing definitions declared in the main document
- `{{ref:}}` referencing sections in the main document or other attachments
- `{{attach:}}` referencing other attachments
- All field spec directives (`{{date:}}`, `{{money:}}`, `{{duration:}}`, `{{field:}}`, etc.)
- Their own section identifiers (validated for uniqueness across the entire combined document)

**What attachment files MUST NOT contain:**

- YAML frontmatter (delimited by `---`)
- Level 1 heading (`#`) — the renderer generates the attachment heading from the `title` in frontmatter

**Example attachment file (attachments/service-description.lgd):**

(assumes the parent document declares `{{def: services}}` and `{{def: business-hours}}` in its body)

```markdown
Provider shall deliver the following {{term: services}}:

- Platform hosting and maintenance
- Technical support during {{term: business-hours}}
- Monthly performance reporting

## Service Levels {#service-levels}

Provider shall maintain system uptime of 99.9% measured monthly.
Response time for critical issues shall not exceed {{duration: 4, unit=H}}.
```

**Non-LegalDown attachment files:**

- Declared in frontmatter identically to LegalDown attachments
- Referenceable via `{{attach: id}}`
- Occupy their declared position in the attachment order
- Validators check that the file exists but perform no content validation
- Renderers MAY insert a placeholder page showing the title, or omit from rendered output depending on style template configuration

---

## 13. Rendering

### 13.1 Section Numbering

Because LegalDown source contains no hardcoded numbers, renderers MUST generate all section numbering at render time. Numbering MUST follow the heading hierarchy (`#`, `##`, `###`, etc.).

**Supported numbering schemes:**

**Decimal (default):**
```
1. First Provision
   1.1 Subprovision
       1.1.1 Further Detail
   1.2 Another Subprovision
2. Second Provision
```

**Legal outline:**
```
I. First Provision
   A. Subprovision
      1. Further Detail
         a. Even Further
   B. Another Subprovision
```

**Mixed legal style:**
```
1. First Provision
   (a) Subprovision
       (i) Further Detail
   (b) Another Subprovision
```

**None (heading text only):**
```
First Provision
   Subprovision
       Further Detail
```

Numbering scheme MUST be configurable per render job and SHOULD be specifiable in the style template or renderer configuration file (§13.7). Default scheme is decimal.

### 13.2 List Enumeration

Renderers SHOULD convert Markdown lists to legal enumeration based on nesting level and the active template. The default enumeration sequence, shared by all built-in numbering schemes (§13.1), is:

| List Level | Default enumeration |
|---|---|
| 1st level | (a), (b), (c) |
| 2nd level | (i), (ii), (iii) |
| 3rd level | (A), (B), (C) |

Style templates MAY define different sequences per level (§13.7). This behavior MUST be configurable and MAY be disabled to preserve plain bullet points.

**Ordered lists.** Renderers MUST renumber ordered list items sequentially at render time — the numbers written in source are not authoritative, consistent with §1.2 — and MAY apply the active enumeration scheme to ordered lists the same way as to unordered lists.

**Section-qualified decimal items.** As an alternative to letter and roman markers, a template MAY render first-level list items as section-qualified decimal numbers (5.1, 5.2, …) — the continental drafting convention for numbered, untitled provisions.

**Paragraph numbering.** A template MAY number the top-level paragraphs within each section (5.1, 5.2, …) for the same purpose. Paragraph numbering is off by default and is a style template setting (§13.7). Together with item and paragraph anchors (§5.7), this lets `{{ref:}}` target untitled numbered provisions ("čl. 5 odst. 2" style) without fake headings.

### 13.3 Reference Resolution

When rendering `{{ref: id}}`:

1. Locate target section by identifier
2. Determine the section number generated under the active numbering scheme
3. Replace directive with the section number (e.g., "3.2")
4. Create hyperlink to target section in formats supporting links
5. If target not found, insert `[BROKEN REF: id]` and emit validation error

For targets that are item or paragraph anchors (§5.7), render the containing section's number plus the item enumeration path or paragraph number under the active template (e.g., "3.1(a)", "5.2"); when the template does not enumerate the containing list or number paragraphs, fall back to the containing section's number and emit a validation Warning (§6.3).

**Numbering scheme "None":** under the None scheme (§13.1) there is no section number; `{{ref:}}` MUST instead render the target's heading text, hyperlinked as usual. When the target is an item or paragraph anchor (§5.7), render the containing section's heading text followed by the item enumeration path or paragraph number — e.g., "Termination (a)"; if the template does not enumerate the containing list or number paragraphs, fall back to the heading text alone with the §6.3 Warning.

**References across attachment boundaries:** when the reference and its target lie in different numbering scopes (main body vs. an attachment, or two different attachments) and the active template restarts numbering per attachment (§13.8), the renderer MUST qualify the designation with the **target's** scope: the attachment `title` when the target lies in an attachment (e.g., "Schedule A: Service Description, Section 2"), or the document `title` when the target lies in the main body (e.g., "Master Service Agreement, Section 5"). Under continuous numbering, or within the same scope, the plain designation is used.

### 13.4 Definition Resolution

When rendering `{{term: id}}` or `{{term: id, label=text}}`:

1. Locate definition by identifier
2. If a `label` parameter is provided, use the label text as the display text
3. Otherwise, use the defined term — the text inside the quotation marks at the definition site, without the delimiting marks (§7.2)
4. Replace directive with the display text and hyperlink it to the definition's location (the `{{def:}}` anchor)
5. If definition not found, insert `[UNDEFINED: id]` and emit validation error

### 13.5 Field Spec Resolution

When rendering `{{date: value}}` or `{{date: value, note=text}}`:

1. Validate the date value is a valid ISO 8601 date
2. Format the date according to the active locale or render template
3. Ignore any `note` parameter for rendered output
4. Replace the directive with the formatted date text
5. If the date is invalid, insert `[INVALID DATE: value]` and emit a validation error

When rendering `{{money: amount}}`, `{{money: amount, note=text}}`, `{{money: amount, currency=CODE}}`, or `{{money: amount, currency=CODE, note=text}}`:

1. Validate the amount is a valid, non-negative numeric value
2. If a `currency` parameter is provided, validate it is a recognized ISO 4217 code
3. Format the amount according to the active locale or render template, including the currency symbol or code
4. Ignore any `note` parameter for rendered output
5. Replace the directive with the formatted monetary value
6. If the amount is invalid, insert `[INVALID AMOUNT: amount]` and emit a validation error
7. If the currency code is unrecognized, insert `[UNKNOWN CURRENCY: CODE]` and emit a validation warning

When rendering `{{party: party-name}}`, `{{party: party-name, note=text}}`, `{{party: party-name, label=text}}`, or `{{party: party-name, label=text, note=text}}`:

1. If a `label` parameter is provided, use it as the display text
2. If no `label` is provided, resolve the party from frontmatter `sides[].parties[]` by matching the `party-name` against party `name` fields; use the party's `label` field as the display text, falling back to `legal_name` if `label` is absent
3. Format the display text according to the active locale or render template
4. Ignore any `note` parameter for rendered output
5. Replace the directive with the formatted party reference text
6. If the `party-name` value is empty or malformed, insert `[INVALID PARTY: party-name]` and emit a validation error
7. If the `party-name` does not match any party declared in frontmatter, insert `[UNKNOWN PARTY: party-name]` and emit a validation error

When rendering `{{side: side-name}}`, `{{side: side-name, note=text}}`, `{{side: side-name, label=text}}`, or `{{side: side-name, label=text, note=text}}`:

1. If a `label` parameter is provided, use it as the display text
2. If no `label` is provided, resolve the side from frontmatter `sides[]` by matching the `side-name` against side `name` fields; use the side's `label` field as the display text, falling back to the §3.6 derivation from `name` if `label` is absent
3. Format the display text according to the active locale or render template
4. Ignore any `note` parameter for rendered output
5. Replace the directive with the formatted side reference text
6. If the `side-name` value is empty or malformed, insert `[INVALID SIDE: side-name]` and emit a validation error
7. If the `side-name` does not match any side declared in frontmatter, insert `[UNKNOWN SIDE: side-name]` and emit a validation error

When rendering `{{duration: value, unit=UNIT}}` or `{{duration: value, unit=UNIT, note=text}}`:

1. Validate the value is a positive numeric value
2. Validate the `unit` parameter is one of: `S`, `MIN`, `H`, `D`, `W`, `MO`, `Y` (a bare `M` is rejected with a diagnostic suggesting `MIN` or `MO`, §10.5)
3. Format the duration according to the active locale or render template (e.g., "12 months", "30 days", "1 year")
4. Ignore any `note` parameter for rendered output
5. Replace the directive with the formatted duration text
6. If the value is invalid, insert `[INVALID DURATION: value]` and emit a validation error
7. If the unit is missing or unrecognized, insert `[INVALID DURATION UNIT: UNIT]` and emit a validation error

When rendering `{{field: value, type=type-name}}` or `{{field: value, type=type-name, note=text}}`:

1. Validate the `type` parameter value matches the identifier format
2. If `field_types` is present, check whether the `type` value is declared there
3. Ignore any `note` parameter for rendered output
4. Replace the directive with the raw `value` exactly as provided
5. If the `type` parameter is missing or malformed, insert `[INVALID FIELD]` or `[INVALID FIELD: value]` when the `value` can be determined, and emit a validation error
6. If `field_types` is present and the `type` value is not declared, keep rendering the raw `value` and emit a validation warning

When rendering `{{placeholder: id}}` or `{{placeholder: id, ...}}`:

1. Validate the `id` value and determine the effective `type`, defaulting to `text` when `type` is omitted
2. Validate any type-specific parameters provided for the effective `type`
3. Treat repeated occurrences of the same `id` as the same logical blank
4. Ignore any `note` parameter for rendered output
5. Replace the directive with a visible blank marker according to renderer settings, such as `[_____]`
6. If the renderer cannot emit a visual blank, it MUST fall back to `[TBD: id]`
7. If a type-specific parameter name is not defined for the effective `type`, implementations MUST ignore that parameter for rendered output and emit a validation warning
8. If a type-specific parameter value is invalid, unrecognized, or a required type-specific parameter is missing, implementations MUST apply the rendering fallback and validation severity defined for that type-specific rule when such a rule exists; for example, for `type=money`, an unrecognized `currency` MUST render as `[UNKNOWN CURRENCY: CURRENCY]` and emit a validation warning, consistent with `{{money: ...}}`
9. If no type-specific fallback is defined for an invalid, unrecognized, or missing required type-specific parameter, insert `[INVALID PLACEHOLDER]` or `[INVALID PLACEHOLDER: id]` when the `id` can be determined, and emit a validation error
10. If the `id` is malformed, the `type` is unsupported, or repeated occurrences use inconsistent types, insert `[INVALID PLACEHOLDER]` or `[INVALID PLACEHOLDER: id]` when the `id` can be determined, and emit a validation error

### 13.6 Output Formats

Implementations SHOULD support:

| Format | Status | Notes |
|---|---|---|
| PDF | RECOMMENDED | Primary legal format, styled per template |
| DOCX | RECOMMENDED | Compatibility with law firm workflows |
| HTML | RECOMMENDED | Web viewing with interactive hyperlinks |
| Plain text | OPTIONAL | Stripped output for comparison |

### 13.7 Style Templates

Renderers SHOULD support external style templates specifying:

- Font family, size, and weight per heading level
- Page layout (margins, headers, footers, page numbers)
- Section numbering scheme
- List enumeration scheme
- Paragraph numbering within sections (off by default)
- Table formatting
- Paragraph spacing and indentation
- Cover page format
- Signature block layout (generation is implementation-defined, §2.2)
- Locale for value formatting (date order, number and decimal separators, currency display)

Templates SHOULD be defined in a separate configuration file (e.g., YAML or JSON) completely independent of document content. The same LegalDown source SHOULD render correctly with any compatible template.

### 13.8 Attachment Rendering

Attachments are rendered after the main document body, in the order declared in frontmatter.

**Rendering rules:**

- The renderer outputs the attachment `title` as the attachment heading — verbatim, with no generated labels
- A separator (e.g., horizontal rule, page break) SHOULD be inserted before each attachment
- Section numbering within LegalDown attachments follows the active numbering scheme — either continuing from the main body or restarting per attachment, configurable in the style template
- Non-LegalDown attachments MAY render as a placeholder page (showing the title) or be omitted from rendered output, depending on style template configuration
- Non-LegalDown attachments keep their declared position in the attachment order even when omitted from rendered output

---

## 14. Bilingual Documents

### 14.1 Overview

LegalDown supports bilingual and multilingual contracts via **separate files** — one document per language, with metadata linking them.

A translation is a **secondary document** derived from a **primary document**: structure and identifiers originate in the primary and are mirrored into each translation; only the text is translated (§14.2).

### 14.2 Separate File Approach

Maintain separate LegalDown documents per language with identical heading structure and section identifiers:

**contract-en.lgd:**
```yaml
---
title: Service Agreement
language: en
translations:
  fr: contract-fr.lgd
authoritative: en
---

# Definitions {#definitions}

"Confidential Information" {{def: confidential-info}} means any non-public information...
```

**contract-fr.lgd:**
```yaml
---
title: Accord de service
language: fr
translations:
  en: contract-en.lgd
authoritative: en
---

# Définitions {#definitions}

« Information confidentielle » {{def: confidential-info}} désigne toute information non publique...
```

**Rules for the separate file approach:**

- Linked translation files MUST have identical heading hierarchy
- Linked translation files MUST use identical section identifiers
- Validators MUST check structural consistency between linked files
- Cross-references resolve to section numbers (same in both versions)

**Primary and translations:**

- The **primary** document is the linked file whose `language` equals the declared `authoritative` language. Declaring `authoritative` is RECOMMENDED whenever `translations` is present
- Identifiers originate in the primary — including any auto-generated there (§5.3 is deterministic, so tooling can compute them) — and are mirrored into each translation **explicitly**. Updating a translation means mirroring the primary's structural change under the same identifier and translating the text
- In a translation file, every heading and every `{{def:}}` MUST therefore carry an explicit identifier (its counterpart's identifier from the primary). Auto-generation MUST NOT be relied upon in translation files — translated text would produce different identifiers and break the matching rules above
- When `authoritative` is absent, implementations cannot distinguish the primary from its translations; validators check the linked files symmetrically and SHOULD warn about auto-generated identifiers in any linked file

### 14.3 Bilingual Validation

Bilingual synchronization validation — a Full-level capability (§16.4) — MUST check:

- Linked files have identical heading hierarchy
- All section identifiers match between the linked files
- All `{{def:}}` identifiers exist in both files
- The linked files declare the same set of languages (each file's `language` plus its `translations` keys)

Violations are Errors; the per-rule severities are defined in §15.7.

---

## 15. Validation

### 15.1 Validation Levels

Validators MUST categorize issues at three levels:

- **Error** — Prevents rendering or indicates broken document (MUST be reported)
- **Warning** — Potential issue that should be reviewed (SHOULD be reported)
- **Info** — Suggestion for improvement (MAY be reported)

### 15.2 Structure Validation

| Check | Level |
|---|---|
| Heading levels do not skip | Error |
| Heading depth does not exceed level 5 | Error |
| Explicit anchors (section identifiers, item and paragraph anchors) are unique within the anchor namespace | Error |
| `{#id}`-like marker outside an anchor position (likely misplaced anchor, §5.7) | Warning |
| Auto-generated section identifiers would collide (implementations append numeric suffixes) | Warning |
| Auto-generated identifier lost non-transliterable letters or digits (§5.3 — explicit identifier recommended) | Warning |
| Section identifiers follow naming rules | Error |
| Headings do not contain hardcoded numbering | Warning |
| Directives are well-formed per the §11.2 grammar (including quoted-value termination and escapes, §11.3) | Error |
| Directive contains the same named parameter more than once | Error |
| Directive name is defined by this specification (unknown names render as `[UNKNOWN DIRECTIVE: name]`; Warning instead under §11.5's permissive mode or a newer declared `legaldown` version) | Error |
| Named parameter not defined for the directive (ignored for rendering) | Warning |
| Unescaped `{{` in body text that does not begin a well-formed directive | Warning |
| Unquoted directive value begins with a typographic quotation mark (possible auto-curled quote) | Warning |
| File-reference paths are relative (§2.3) | Error |
| File-reference paths resolve within the configured document root (§2.3) | Error |
| Raw HTML other than comments present (ignored for rendered output, §8.7) | Warning |

### 15.3 Reference Validation

| Check | Level |
|---|---|
| All `{{ref: id}}` point to existing sections | Error |
| `{{ref: id}}` targets an attachment id — attachments are referenced with `{{attach:}}` (§5.6) | Error |
| `{{ref: id}}` targets an item or paragraph anchor whose containing list or paragraphs the active template does not enumerate (renders as the containing section number; template-dependent — evaluated from the Rendering level, §16.3) | Warning |
| All `{{term: id}}` point to declared definitions | Error |
| Circular definitions detected (scoped to each definition's containing paragraph, see §7.2) | Warning |
| Definitions used before declaration | Info |

### 15.4 Definition Validation

| Check | Level |
|---|---|
| All `{{def: id}}` identifiers are unique among definitions (§5.6) | Error |
| `{{def:}}` is immediately preceded by a recognized quoted span | Error |
| Two definitions auto-generate the same identifier (omitted ids) | Error |
| Auto-derived definition identifier lost non-transliterable letters or digits (§5.3 — explicit id recommended) | Warning |
| Defined term wrapped in emphasis markers (`**`, `__`) in source | Warning |
| Single-quoted term ambiguous with an apostrophe (U+2019) | Warning |
| Declared definitions never referenced with `{{term:}}` (may yield false positives when §7.4 automatic term recognition is enabled) | Warning |

### 15.5 Field Spec Validation

| Check | Level |
|---|---|
| `{{date:}}` value is valid ISO 8601 date | Error |
| `{{money:}}` amount is a valid, non-negative numeric value | Error |
| `{{money:}}` `currency` parameter is a recognized ISO 4217 code | Warning |
| `{{money:}}` used without `currency` parameter and no default configured | Warning |
| `{{party:}}` `party-name` value is non-empty and matches identifier format | Error |
| `{{party:}}` `party-name` references a party declared in frontmatter `sides[].parties[]` | Error |
| `{{side:}}` `side-name` value is non-empty and matches identifier format | Error |
| `{{side:}}` `side-name` references a side declared in frontmatter `sides[]` | Error |
| `{{duration:}}` value is a positive numeric value | Error |
| `{{duration:}}` `unit` parameter is one of `S`, `MIN`, `H`, `D`, `W`, `MO`, `Y` (bare `M` rejected with a `MIN`/`MO` hint) | Error |
| `field_types` keys follow the identifier format `[a-z][a-z0-9-]*` | Error |
| `field_types` keys do not collide with the reserved value-type names `date`, `money`, `duration`, `party`, `text` | Error |
| `{{field:}}` `type` parameter is present and matches identifier format | Error |
| `{{field:}}` uses a type declared in `field_types` when `field_types` is present | Warning |
| `{{placeholder:}}` `placeholder-id` value is non-empty and matches identifier format | Error |
| `{{placeholder:}}` `type` parameter, when present, is one of `text`, `date`, or `money` | Error |
| Repeated `{{placeholder:}}` occurrences with the same `placeholder-id` use the same effective `type` | Error |
| `{{placeholder:}}` `currency` parameter for `type=money` is a recognized ISO 4217 code | Warning |
| `{{placeholder:}}` in frontmatter appears in an identifier or structural field (any `name`, `type`, `document_type`, `legaldown`, `sides`/`parties` structure) | Error |
| Field spec `note` parameter is plain text and satisfies the value rules in §11.3 (unquoted: no commas or closing braces) | Error |

### 15.6 Document Metadata Validation

If `document_type` is omitted, validators MUST treat it as `contract` when applying the following checks:

| Rule | `contract` | `unilateral_act` | `collective_act` |
|---|---|---|---|
| Minimum distinct sides | ≥ 2 | ≥ 1 | ≥ 1 |
| Side named `issuer` required | No | Yes | Yes |
| Minimum total parties | ≥ 2 | ≥ 1 | ≥ 1 |
| `document_type` is valid value | Error if not | Error if not | Error if not |

**Severities for the table above:** an invalid `document_type` value is always an **Error**. When `sides` is present, violations of the minimum-sides, `issuer`-side, and minimum-parties rows are **Errors**. When frontmatter is present but `sides` is absent entirely, those structural rows cannot be verified: validators MUST NOT report them as violated and MUST instead emit a single **Warning** stating that the `document_type` constraints cannot be verified without `sides` — keeping `sides` genuinely RECOMMENDED (§3.2) rather than effectively required. A document with no frontmatter at all draws only the no-frontmatter Warning (see the general metadata checks below), not this one.

Violations of the following additional checks MUST be reported as **Error**:

- Every party `name` is unique across the entire document
- Every side `name` is unique
- All side and party `name` values follow the identifier format `[a-z][a-z0-9-]*` (a lowercase ASCII letter followed by zero or more lowercase ASCII letters, digits, or hyphens)
- Every party `type` is `legal_entity` or `natural_person`

**General metadata checks:**

| Check | Level |
|---|---|
| Frontmatter, when present, parses as valid YAML | Error |
| Document includes frontmatter (§3.1) | Warning |
| `title` is present and non-empty when frontmatter is present | Error |
| `effective_date` and `adoption_date`, when present, are valid ISO 8601 dates | Error |
| Party `date_of_birth`, when present, is a valid ISO 8601 date | Error |
| `language`, `authoritative`, and `translations` keys, when present, are valid ISO 639-1 codes | Warning |
| `authoritative`, when present, equals the document `language` or a `translations` key | Warning |
| `legaldown`, when present, does not declare a version newer than the implementation supports | Warning |
| Representative `name` is non-empty | Error |

Where §3.10 permits a placeholder in a value field, a placeholder value satisfies that field's presence requirement and is **exempt from the field's format checks** above (for example, `effective_date: "{{placeholder: effective-date, type=date}}"` does not fail the ISO 8601 check); the placeholder's own checks (§15.5) apply instead.

### 15.7 Bilingual Validation (when translations metadata present)

| Check | Level |
|---|---|
| Translation files exist at declared paths | Error |
| Heading hierarchy matches between translations | Error |
| Section identifiers match between translations | Error |
| Definition IDs match between translations | Error |
| Linked files declare the same set of languages (`language` + `translations` keys) | Error |
| Every heading and `{{def:}}` in a translation file (a linked file whose `language` differs from `authoritative`) carries an explicit identifier | Error |
| Auto-generated identifiers used in linked files when `authoritative` is absent (primary cannot be determined) | Warning |

### 15.8 Amendment Validation (when amends metadata present)

| Check | Level |
|---|---|
| `amends.title` is non-empty when `amends` is present | Error |
| `amends.file` path exists when specified | Error |
| `{{term:}}` references id not found in amendment or imported original (original LegalDown source available, e.g. `.lgd`, `.legaldown`, or `.legal.md`) | Error |
| `{{term:}}` references id not found in amendment (original not available or not LegalDown source) | Info |
| Amendment declares `{{def:}}` with same id as definition in original LegalDown source | Warning |

### 15.9 Validation Output

Validators MUST produce structured output indicating file, line number, identifier (if applicable), issue level, and human-readable message. Validators SHOULD support output in plain text and JSON formats for integration with tooling.

### 15.10 Attachment Validation

| Check | Level |
|---|---|
| Attachment `id` is unique across document | Error |
| Attachment `id` does not collide with any other anchor (section identifier or item/paragraph anchor, §5.6) | Error |
| Attachment `title` is non-empty | Error |
| Attachment `file` path exists | Error |
| LegalDown attachment file contains frontmatter | Error |
| LegalDown attachment file contains level 1 heading | Error |
| Section identifiers in LegalDown attachment files are unique across entire combined document (main + all attachments) | Error |
| Attachment declared but never referenced via `{{attach:}}` | Warning |
| `{{attach:}}` references undeclared attachment id | Error |

Non-LegalDown attachments: only file existence is checked.

### 15.11 Include Validation

| Check | Level |
|---|---|
| Include target path exists | Error |
| Include target is a LegalDown file (`.lgd`, `.legaldown`, `.legal.md`) | Error |
| Circular include chain detected | Error |
| Included fragment contains frontmatter | Error |
| Included fragment contains a level 1 heading | Error |
| Section identifiers in included fragments are unique across the entire combined document | Error |
| Combined document (after all inclusions) satisfies the heading hierarchy rules (§4.1) | Error |

All other §15 checks apply to the combined document after inclusion (§12.2). Include processing is a Full-level capability (§16.4); the file-extension check on the include path is determinable from the document alone and applies at Core (§16.2).

---

## 16. Conformance Levels

### 16.1 Model

LegalDown defines three cumulative conformance levels. Each level includes every requirement of the levels below it. An implementation claims a level and MUST satisfy every MUST requirement within that level's scope.

| Level | Name | Summary |
|---|---|---|
| 1 | Core | Parse and validate a single document |
| 2 | Rendering | Core, plus rendered output per Section 13 |
| 3 | Full | Rendering, plus all multi-file processing |

**General rules:**

- Conformance levels describe **implementation** obligations only. They impose nothing on documents or authors: no construct is ever mandatory in a document, and a document MAY use any LegalDown construct regardless of the conformance level of the implementation that will process it.
- A claimed level is a floor, not a ceiling. An implementation MAY support individual capabilities from a higher level (for example, a Core validator that also performs bilingual validation per §15.7) without claiming that level.
- Within a level's scope, the conformance keywords keep their §1.5 meanings — SHOULD and MAY features (for example, automatic term recognition, §7.4) remain non-mandatory at every level.

### 16.2 Level 1 — Core

Scope: everything that can be determined from the document file alone. A Core implementation MUST support:

- File format requirements (§2) and frontmatter metadata (§3), including the `amends` (§3.8), `attachments` (§3.9), and frontmatter placeholder (§3.10) schemas
- Document structure (§4) and identifiers (§5), including automatic identifier generation (§5.3) and item/paragraph anchors (§5.7)
- Recognition and validation of all directives in §11.1: cross-references (§6), definitions and term references (§7), field specs (§10), and attachment references (§6.4)
- Standard text formatting (§8) and tables (§9)
- Validation (§15): §15.1–§15.6 and §15.9 in full — excluding the template-dependent §15.3 row on refs to non-enumerated item/paragraph anchors, which is evaluated from the Rendering level (§16.3) — plus the rows of §15.7, §15.8, §15.10, and §15.11 that need only the document itself:
  - §15.7 — the single-file translation rows: every heading and `{{def:}}` carries an explicit identifier when the document itself is a translation (its `language` differs from its declared `authoritative`), and the auto-generated-identifier Warning when the document declares `translations` without `authoritative`
  - §15.8 — `amends.title` is non-empty; unresolved `{{term:}}` references are handled per §7.5's "original not available" rules (a Core implementation never loads the original, so that branch always applies)
  - §15.10 — attachment `id` uniqueness, attachment `id` collisions with other anchors (§5.6), attachment `title` is non-empty, `{{attach:}}` references a declared id, attachment declared but never referenced
  - §15.11 — the `{{include:}}` target path has a LegalDown file extension

A Core implementation is not required to open any file other than the document itself. Checks that involve another file — existence of declared paths, attachment or include content, imported definitions, translation synchronization — belong to Full (§16.4).

### 16.3 Level 2 — Rendering

Everything in Core, plus rendering (Section 13) of a single document. A Rendering implementation MUST additionally support:

- Section numbering generation (§13.1), configurable per render job
- Resolution and rendering of all §11.1 directives except `{{include:}}` (Full, §16.4) per §6.3, §7.3, and §13.3–§13.5, including all bracketed failure markers (`[BROKEN REF: ...]`, `[UNDEFINED: ...]`, etc.); a Rendering implementation encountering `{{include:}}` follows §16.5
- Party and side display rules (§3.6)
- At least one of the RECOMMENDED output formats in §13.6 (PDF, DOCX, or HTML)
- Comment stripping (§8.6)

List enumeration (§13.2), style templates (§13.7), and signature block generation (§2.2) remain SHOULD. Rendering the content of attachment files (§13.8) is a Full capability; a Rendering implementation resolves `{{attach:}}` to the declared `title` (§6.4) without reading the attachment file.

### 16.4 Level 3 — Full

Everything in Rendering, plus all processing that reads files beyond the document itself. A Full implementation MUST additionally support:

- File inclusion (§12.1–§12.3) and the remaining §15.11 checks (target exists, circular chains, fragment content rules, combined-document validation)
- Attachment file processing: content rules (§12.4), attachment rendering (§13.8), and the remaining §15.10 checks (attachment file exists, contains no frontmatter and no level 1 heading, identifier uniqueness across the combined document)
- Amendment processing: loading a LegalDown original and importing its definitions (§7.5), and the remaining §15.8 checks (`amends.file` exists, `{{term:}}` resolution against the imported original)
- Bilingual documents: Section 14 and the remaining §15.7 checks (cross-file structure, identifier, and language-set matching)
- Existence checks for every path declared in frontmatter (`attachments[].file`, `amends.file`, `translations`) and for image paths (§8.7)

### 16.5 Constructs Beyond the Claimed Level

An implementation that encounters a construct whose processing lies beyond its claimed level MUST NOT ignore it silently:

- Validators MUST emit a Warning identifying each check category they did not perform (for example, "translations declared; bilingual validation not performed at this conformance level") and MUST NOT report the document as passing checks they did not run.
- Renderers MUST NOT produce output that silently omits unprocessed content. Where content cannot be processed (for example, `{{include:}}` below Full), the renderer MUST either refuse to render or insert a visible marker in place of the construct — `[NOT PROCESSED: include schedules/pricing.lgd]` — and emit a Warning.

---

## 17. Complete Examples

### 17.1 Contract Example

```markdown
---
title: Mutual Non-Disclosure Agreement
document_type: contract
effective_date: 2026-02-01
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
governing_law: Delaware
language: en
attachments:
  - id: schedule-a
    title: "Schedule A: Categories of Confidential Information"
    file: attachments/confidential-categories.lgd
  - id: exhibit-1
    title: "Exhibit 1: Prior Agreements"
    file: attachments/prior-agreements.pdf
---

This Mutual Non-Disclosure Agreement (this "Agreement" {{def: agreement}}) is entered into on
{{date: 2026-02-01}} between {{party: acme}} and {{party: beta}}.

# Definitions {#definitions}

"Confidential Information" {{def: confidential-info}} means any non-public information disclosed by
one side to the other in connection with evaluating a potential business relationship.

# Confidentiality Obligations {#confidentiality}

Each party shall protect the {{term: confidential-info}} using at least
reasonable care.

# Use Restrictions {#use}

{{party: beta, label=the Receiving Party}} may use the
{{term: confidential-info}} solely for evaluating a potential business
relationship with {{party: acme, label=the Disclosing Party}}.

Categories of {{term: confidential-info}} are described in {{attach: schedule-a}}.

The {{term: agreement}} supersedes all prior agreements listed in {{attach: exhibit-1}}.

# Governing Law {#governing-law}

The {{term: agreement}} is governed by the laws of Delaware.
```

**attachments/confidential-categories.lgd:**

```markdown
The following categories of information shall constitute
{{term: confidential-info}} under the {{term: agreement}}:

- Technical data and trade secrets
- Business plans and financial information
- Customer and supplier lists
- Product development roadmaps

## Exclusions {#exclusions}

{{term: confidential-info}} does not include information that is publicly
available or independently developed by the receiving party.
```

### 17.2 Unilateral Act Example

```markdown
---
title: Notice of Termination
document_type: unilateral_act
effective_date: 2026-05-01
sides:
  - name: issuer
    label: Issuer
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
language: en
---

This notice is issued by {{party: acme}}.

# Definitions {#definitions}

"Termination Date" {{def: termination-date}} means {{date: 2026-06-01}}.

# Notice {#notice}

{{party: acme, label=the Issuer}} hereby terminates the Services Agreement
effective on the {{term: termination-date}}.

# Delivery {#delivery}

This notice shall be delivered in accordance with the notice provisions of the
Services Agreement.
```

### 17.3 Collective Act Example

```markdown
---
title: Remote Work Policy
document_type: collective_act
effective_date: 2026-04-01
adopted_by: Board of Directors of Acme Corporation
adoption_date: 2026-03-15
supersedes: Remote Work Policy adopted on 2025-01-10
sides:
  - name: issuer
    label: Issuer
    parties:
      - name: acme
        label: Acme
        type: legal_entity
        legal_name: Acme Corporation
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
language: en
---

This Policy is adopted by the Board of Directors of {{party: acme}} and takes
effect on {{date: 2026-04-01}}.

# Definitions {#definitions}

"Remote Work" {{def: remote-work}} means performance of assigned duties at a location other
than the Issuer's premises.

# Eligibility {#eligibility}

Employees of {{party: acme}} may perform {{term: remote-work}} when approved
by their manager and consistent with applicable law.

# Equipment {#equipment}

The Issuer may issue equipment and security requirements needed to support
{{term: remote-work}}.
```

### 17.4 Amendment Example

```markdown
---
title: First Amendment to Master Service Agreement
amends:
  title: Master Service Agreement
  file: ../original/msa.lgd
effective_date: 2026-06-01
sides:
  - name: providers
    label: Providers
    parties:
      - name: acme-corporation
        label: Acme
        type: legal_entity
        legal_name: Acme Corporation
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
        representatives:
          - name: John Smith
            title: Chief Executive Officer
  - name: clients
    label: Clients
    parties:
      - name: beta-industries
        label: Beta
        type: legal_entity
        legal_name: Beta Industries Inc.
        identification_number: TX-87654321
        address: 456 Oak Avenue, Austin, TX 78701
        representatives:
          - name: Jane Doe
            title: General Counsel
governing_law: Delaware
language: en
---

The parties hereby agree to amend the Master Service Agreement
dated {{date: 2025-01-15}} (the "Agreement" {{def: agreement}}) as follows:

# Payment Terms {#payment-terms}

Section 5.1 of the {{term: agreement}} is amended to read as follows:

Client shall pay Provider within fifteen (15) days of invoice
date. Late payments shall bear interest at {{money: 500, currency=USD}}
per day of delay.

# Data Protection {#data-protection}

The following new section is added after Section 8 of the {{term: agreement}}:

Provider shall process all {{term: confidential-info}} in
accordance with applicable data protection laws.

# Unchanged Provisions {#unchanged}

All other terms and conditions of the {{term: agreement}} remain in full
force and effect.
```

---

## 18. Roadmap and Known Limitations (Non-Normative)

Candidates considered during the v0.1 draft and deliberately deferred. Their absence from this version is a decision, not an oversight:

- **Qualified cross-document references for amendments** — a `{{ref: id, doc=amends}}` form resolving against the imported original (§3.8, §7.5); v0.1 instead provides authoring guidance in §3.8
- **`{{meta:}}` field insertion** — rendering frontmatter values (e.g., `effective_date`) in body text, removing the duplication between frontmatter and `{{date:}}` directives
- **Structured `adopted_by` / an organ party type** — so collective acts can reference their adopting body through a directive rather than plain text
- **Template-generated attachment labels** — so attachment titles need not hardcode ordinals ("Schedule A", "Schedule B") that require manual renaming on reorder
- **A structured signature model** — per-representative signing lines, date and place, signing capacities; signature block generation is implementation-defined in v0.1 (§2.2)
- **Template-supplied reference label words** — e.g., `{{ref: id, style=full}}` rendering "Article I.A" with the label word chosen by the style template (§6.2 note)
- **Machine-readable export** — a JSON document model as a companion specification; the source file remains the canonical machine-readable representation (§10.1)
