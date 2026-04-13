# LegalDown Specification
## Version 0.1 DRAFT

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
- Language block directives for bilingual documents
- File inclusion directives
- Validation requirements for legal-specific constraints

### 1.4 Relationship to LeGit

LegalDown is the document format. LeGit is the Git-based legal document versioning and negotiation platform. LegalDown documents are the native format of LeGit repositories, but LegalDown can be used independently of LeGit with any compatible renderer or validator.

### 1.5 Conformance

Throughout this specification:

- **MUST** / **MUST NOT** — absolute requirement / prohibition
- **SHOULD** / **SHOULD NOT** — recommended but not mandatory
- **MAY** — optional feature

Implementations claiming LegalDown conformance MUST support all MUST requirements at their claimed conformance level (see Section 16).

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

> **Note:** Signature blocks are NOT defined in LegalDown markup. Renderers SHOULD generate signature blocks automatically from frontmatter. For contracts, from all sides. For unilateral acts, from the issuer side. For collective acts, from the issuer side and `adopted_by`.

---

## 3. Metadata (Frontmatter)

### 3.1 Format

Documents SHOULD include YAML frontmatter as the first element, delimited by triple dashes:

```yaml
---
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

| Field | Status | Description |
|---|---|---|
| `title` | REQUIRED | Document title |
| `subtitle` | OPTIONAL | Document subtitle |
| `version` | OPTIONAL | Document version identifier |
| `document_type` | OPTIONAL | Document type. Valid values: `contract`, `unilateral_act`, `collective_act`. Default: `contract` |
| `effective_date` | OPTIONAL | Document effective date (ISO 8601) |
| `field_types` | OPTIONAL | Map of custom field type declarations for `{{field:}}` (type name → description) |
| `sides` | RECOMMENDED | Array of sides, each containing a non-empty `parties` array (see Section 3.3) |
| `governing_law` | OPTIONAL | Applicable law |
| `language` | RECOMMENDED | Primary language (ISO 639-1) |
| `translations` | OPTIONAL | Map of translation files (see Section 14) |
| `authoritative` | OPTIONAL | Authoritative language for disputes (ISO 639-1) |
| `adopted_by` | OPTIONAL | Body or authority that adopted the document |
| `adoption_date` | OPTIONAL | Adoption date (ISO 8601) |
| `supersedes` | OPTIONAL | Prior document or version superseded by this document |
| `amends` | OPTIONAL | Object identifying the original document this document amends (see Section 3.8) |
| `tags` | OPTIONAL | Classification tags array |

If `field_types` is present, it MUST be a YAML map where each entry is `type-name: description`.

- Each `type-name` MUST follow the identifier format `[a-z][a-z0-9-]*`
- Each description MUST be plain text describing the custom value type
- `type-name` values MUST NOT collide with built-in directive names `date`, `money`, `duration`, or `party`
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

- Side `label` is used for display; if absent, renderers SHOULD title-case and pluralize `name` as a fallback
- Party `label` is used for display; if absent, renderers MUST fall back to `legal_name`
- `legal_name` MUST always appear on signature blocks
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

---

## 4. Document Structure

### 4.1 Heading Hierarchy

LegalDown uses Markdown heading syntax to define legal document hierarchy:

```
# Document Title                    (Level 1 — Document root)
## Top-level Provision              (Level 2 — Articles / Sections)
### Second-level Provision          (Level 3 — Subsections)
#### Third-level Provision          (Level 4)
##### Fourth-level Provision        (Level 5)
###### Fifth-level Provision        (Level 6)
```

**Rules:**

- Level 1 (`#`) MUST appear exactly once in the document as the document title
- Level 2 (`##`) represents top-level provisions (articles, sections)
- Heading levels MUST NOT skip levels — jumping from `##` to `####` without an intervening `###` is invalid
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

---

## 5. Section Identifiers

### 5.1 Purpose

Section identifiers (anchors) provide stable targets for cross-references that remain valid regardless of section numbering changes.

### 5.2 Explicit Identifiers

Any heading MAY include an explicit identifier:

```markdown
## Payment Terms {#payment-terms}
### Late Payment Fees {#payment-late-fees}
#### Monthly Calculation {#payment-late-fees-monthly}
```

**Rules for identifiers:**

- Specified using `{#identifier}` syntax placed immediately after heading text, separated by a single space
- MUST be unique within the document
- MUST contain only lowercase letters, numbers, and hyphens
- MUST start with a letter
- MUST NOT contain spaces or special characters

### 5.3 Automatic Identifier Generation

If no explicit identifier is provided, implementations MUST auto-generate one using the following algorithm:

1. Take heading text
2. Convert to lowercase
3. Replace spaces and underscores with hyphens
4. Remove all characters that are not letters, numbers, or hyphens
5. Remove leading and trailing hyphens
6. Truncate to maximum 64 characters

Example: "Confidential Information & Trade Secrets" → `confidential-information-trade-secrets`

### 5.4 Identifier Scope

Section identifiers are document-global. Each section MUST have a unique identifier within the document, whether the identifier is provided explicitly or auto-generated.

Implementations MUST resolve cross-references by matching the referenced identifier directly. Implementations MUST NOT construct, require, or interpret hierarchical dot-separated paths based on heading nesting.

### 5.5 Duplicate Identifier Handling

If the same identifier would be auto-generated for two different headings, implementations MUST:

1. Emit a validation error
2. Append a numeric suffix to the second identifier (`-2`, `-3`, etc.) to ensure uniqueness
3. Warn the author to add explicit identifiers to resolve the conflict

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

### 6.3 Reference Rendering

Renderers MUST:

1. Locate the target section by identifier
2. Determine the rendered section number based on the active numbering scheme
3. Replace the reference with the section number (e.g., "3.2")
4. Create a hyperlink to the target section in formats that support hyperlinking (HTML, PDF, DOCX)
5. If the target identifier does not exist, insert `[BROKEN REF: identifier]` in output and emit a validation error

---

## 7. Definitions

### 7.1 Purpose

Defined terms are a fundamental feature of legal contracts. LegalDown provides structured syntax for declaring definitions and referencing them consistently throughout a document.

### 7.2 Definition Declaration

Definitions are declared using the `{{def:}}` directive placed at the start of a paragraph, immediately before the defined term:

```markdown
## Definitions {#definitions}

{{def: confidential-info}}
**"Confidential Information"** means any non-public information disclosed by
one party to the other, including technical data, business plans, customer
information, and any other information designated as confidential.

{{def: services}}
**"Services"** means the software development services described in Section
{{ref: scope-of-work}}.
```

**Rules:**

- `{{def: id}}` MUST appear on its own line immediately preceding the definition text paragraph
- Definition IDs follow the same rules as section identifiers
- Definition IDs MUST be unique within the document
- The defined term SHOULD be formatted as bold quoted text: `**"Term Name"**`
- All definitions MUST be placed in a single Definitions section
- The Definitions section MUST be the first level 2 (`##`) heading in the document body (i.e., the first `##` after the document title)
- The Definitions section MUST NOT contain any subheadings (level 3 or deeper) — all `{{def:}}` declarations appear directly under the `##` heading as consecutive paragraphs

### 7.3 Definition Reference

Defined terms are referenced using the `{{term:}}` directive:

```markdown
{{term: definition-id}}
{{term: definition-id, label=Custom Display Text}}
```

The optional `label` parameter specifies text to display in place of the canonical defined term name. This is useful when the defined term must appear in a grammatically inflected form (e.g., declension, conjugation, or other morphological variation required by the document's language).

**Examples:**

```markdown
Each party shall protect the {{term: confidential-info}} from unauthorized disclosure.

Provider shall deliver the {{term: services}} in accordance with the agreed specifications.

Client may use the {{term: services, label=Hosted Services}} solely for its internal business operations.
```

In the last example, the defined term is "Services" but the label `Hosted Services` is displayed in the rendered output, allowing the text to use a context-appropriate English label.

**Rules:**

- The `label` parameter is OPTIONAL
- When `label` is present, renderers MUST display the label text instead of the canonical term name
- The label value MUST NOT contain commas or closing braces (`}}`)
- The `label` value is plain text — it MUST NOT contain Markdown formatting or nested directives

**Rendering:**

Renderers MUST:

1. Locate the definition by identifier
2. If a `label` parameter is provided, use the label text as the display text
3. Otherwise, extract the defined term text from within `**"..."**`
4. Replace `{{term: id}}` (or `{{term: id, label=...}}`) with the display text
5. Create a hyperlink to the definition in formats that support hyperlinking
6. If the definition is not found, insert `[UNDEFINED: id]` and emit a validation error

### 7.4 Optional Automatic Term Recognition

Implementations MAY support automatic recognition of defined terms without explicit `{{term:}}` directives, linking any occurrence of a defined term's text to its definition automatically. When this is enabled:

- Implementations SHOULD make this behavior configurable
- The feature SHOULD be disabled by default to avoid false positives
- Explicit `{{term:}}` is RECOMMENDED for precision

### 7.5 Definition Resolution in Amendments

When a document contains an `amends` key in frontmatter, definition validation follows special resolution rules based on whether the original document is available and in LegalDown format:

**When `amends.file` points to a LegalDown file (`.lgd`, `.legaldown`):**

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

- `**bold**` or `__bold__` — Bold text (used for defined terms)
- `*italic*` or `_italic_` — Italic text (used for emphasis)
- `` `code` `` — Monospace/code (used for technical specifications)

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
- Renderers MAY convert unordered lists to legal enumeration styles (a), (b), (c) at configured heading levels
- Renderers MAY convert nested unordered lists to legal sub-enumeration (i), (ii), (iii)

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

## Limitation of Liability {#liability-limitations}
```

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

All field specs MAY include an optional `note` parameter to provide a plain-text explanation of the value for automation or machine-processing purposes. The `note` value MUST NOT affect rendered output, MUST NOT contain commas or closing braces (`}}`), and MUST be preserved in structured output formats when present.

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
- Renderers MUST format the date according to the document's locale or render template settings (e.g., "June 1, 2026", "1 June 2026", "2026-06-01")
- The raw ISO 8601 value and `note` (if present) MUST be preserved in structured output formats for machine processing

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

- The amount MUST be a numeric value (integer or decimal, using period `.` as the decimal separator)
- The amount MUST NOT include grouping separators, currency symbols, or whitespace
- The optional `currency` parameter specifies the currency using an ISO 4217 three-letter code (e.g., `USD`, `EUR`, `CZK`, `GBP`)
- If `currency` is omitted, the renderer SHOULD use a default currency from the document metadata or render template, or emit a validation warning
- Renderers MUST format the amount according to the document's locale or render template settings (e.g., "$10,000.00", "USD 10,000.00", "€500.00")
- The raw numeric value, currency code, and `note` (if present) MUST be preserved in structured output formats for machine processing

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

{{party: board-of-directors, label=the Board, note=Collective body adopting the policy}} may amend this Policy from time to time.
```

**Rules:**

- The `party-name` value MUST be a non-empty string matching the identifier format `[a-z][a-z0-9-]*` (a lowercase ASCII letter followed by zero or more lowercase ASCII letters, digits, or hyphens)
- The directive MUST resolve against a party `name` in the frontmatter `sides[].parties[]` arrays
- The optional `label` parameter specifies display text for rendering; if omitted, the renderer MUST use the party's `label` and fall back to `legal_name`
- The `label` value is plain text — it MUST NOT contain commas or closing braces (`}}`)
- Renderers MUST format the resolved party reference according to the document's locale or render template settings
- The raw `party-name` value, `label` (if present), and `note` (if present) MUST be preserved in structured output formats for machine processing

### 10.5 Duration Directive

The `{{duration:}}` directive represents a time duration inline in document text. It specifies a numeric value and a time unit.

**Syntax:**

```markdown
{{duration: value, unit=UNIT}}
{{duration: value, unit=UNIT, note=text}}
```

Where `UNIT` is one of: `S` (seconds), `M` (minutes), `H` (hours), `D` (days), `MO` (months), `Y` (years).

**Examples:**

```markdown
This Agreement shall remain in effect for {{duration: 12, unit=MO}}.

The notice period shall be {{duration: 30, unit=D}}.

The service level response time shall not exceed {{duration: 4, unit=H, note=Critical incident response target}}.
```

**Rules:**

- The `value` MUST be a positive numeric value (integer or decimal, using period `.` as the decimal separator); zero and negative values are not allowed
- The `unit` parameter is REQUIRED and MUST be one of: `S`, `M`, `H`, `D`, `MO`, `Y`
- Renderers MUST format the duration according to the document's locale or render template settings (e.g., "12 months", "30 days", "4 hours", "1 year")
- The raw numeric value, unit code, and `note` (if present) MUST be preserved in structured output formats for machine processing

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
- Because commas separate directive parameters and `}}` terminates the directive, the `value` MUST NOT contain a comma (`,`) or the sequence `}}`
- Optional whitespace immediately after `{{field:` and optional whitespace surrounding parameter separators is directive syntax and is not part of the `value`
- After parsing, implementations MUST preserve the `value` exactly as parsed, with no trimming, normalization, character escaping/unescaping, or locale-aware formatting
- The `type` parameter is REQUIRED and MUST follow the identifier format `[a-z][a-z0-9-]*`
- If frontmatter `field_types` is present, the `type` SHOULD match a declaration in `field_types`
- If `field_types` is absent entirely, implementations MUST accept any `type` value that follows the identifier format without emitting a warning
- Renderers MUST pass the parsed `value` through unchanged
- The raw parsed `value`, `type`, and `note` (if present) MUST be preserved in structured output formats for machine processing

### 10.7 Placeholder Directive

The `{{placeholder:}}` directive represents a fillable inline blank. Placeholders are declared directly where they are used in document text and MUST NOT require any frontmatter declaration.

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
- All occurrences of the same `placeholder-id` MUST use the same effective `type`
- When the same `placeholder-id` appears multiple times with type-specific parameters, those parameters SHOULD remain consistent across occurrences; validators MAY emit a warning when they differ
- Renderers MUST preserve the raw `placeholder-id`, effective `type`, any type-specific parameters, and `note` (if present) in structured output formats for machine processing

---

## 11. Directives Summary

All LegalDown-specific extensions use double-brace directive syntax `{{directive: argument}}` to clearly distinguish them from standard Markdown and avoid ambiguity.

### 11.1 Core Directives

| Directive | Status | Purpose |
|---|---|---|
| `{{ref: id}}` | REQUIRED | Cross-reference to section |
| `{{def: id}}` | REQUIRED | Declare a definition |
| `{{term: id}}` | REQUIRED | Reference a defined term |
| `{{term: id, label=text}}` | OPTIONAL | Reference a defined term with custom display text |
| `{{date: YYYY-MM-DD}}` | OPTIONAL | Inline date value |
| `{{money: amount}}` | OPTIONAL | Inline monetary amount |
| `{{money: amount, currency=CODE}}` | OPTIONAL | Inline monetary amount with currency |
| `{{party: role}}` | OPTIONAL | Inline party reference by role |
| `{{party: role, label=text}}` | OPTIONAL | Inline party reference with display text |
| `{{duration: value, unit=UNIT}}` | OPTIONAL | Inline time duration with unit |
| `{{field: value, type=type-name}}` | OPTIONAL | Inline custom typed value with pass-through rendering |
| `{{placeholder: placeholder-id}}` | OPTIONAL | Inline fillable blank (defaults to `type=text`) |
| `{{placeholder: placeholder-id, type=money, currency=CODE}}` | OPTIONAL | Inline typed blank with type-specific parameters |
| `{{include: path}}` | OPTIONAL | Include external file |

### 11.2 Directive Rules

- Directives are case-sensitive — always lowercase
- Directives MUST NOT span multiple lines
- Unknown directives SHOULD generate a warning and be passed through to output as-is
- Implementations MUST NOT fail silently on unknown directives

---

## 12. File Inclusion

### 12.1 Syntax

Implementations MAY support including external LegalDown files:

```markdown
## Schedule A — Service Description {#schedule-a}

{{include: schedules/service-description.lgd}}

## Schedule B — Pricing {#schedule-b}

{{include: schedules/pricing.lgd}}
```

### 12.2 Rules

If file inclusion is supported:

- Included files MUST be valid LegalDown documents
- Include paths MUST be relative to the including document
- Circular includes MUST be detected and rejected with an error
- Section identifiers from included files MUST be checked for conflicts with the main document
- Included file frontmatter SHOULD be ignored (main document frontmatter applies)
- Validation of the combined document (including all inclusions) is REQUIRED

---

## 13. Rendering

### 13.1 Section Numbering

Because LegalDown source contains no hardcoded numbers, renderers MUST generate all section numbering at render time. Numbering MUST follow the heading hierarchy (`##`, `###`, `####`, etc.).

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

Numbering scheme MUST be configurable per render job and SHOULD be specifiable in document metadata or renderer configuration file. Default scheme is decimal.

### 13.2 List Enumeration

Renderers SHOULD convert Markdown lists to legal enumeration based on nesting level and active template:

| List Level | Decimal Style | Outline Style | Mixed Style |
|---|---|---|---|
| 1st level | (a), (b), (c) | (a), (b), (c) | (a), (b), (c) |
| 2nd level | (i), (ii), (iii) | (i), (ii), (iii) | (i), (ii), (iii) |
| 3rd level | (A), (B), (C) | (A), (B), (C) | (A), (B), (C) |

This behavior MUST be configurable and MAY be disabled to preserve plain bullet points.

### 13.3 Reference Resolution

When rendering `{{ref: id}}`:

1. Locate target section by identifier
2. Determine the section number generated under the active numbering scheme
3. Replace directive with the section number (e.g., "3.2")
4. Create hyperlink to target section in formats supporting links
5. If target not found, insert `[BROKEN REF: id]` and emit validation error

### 13.4 Definition Resolution

When rendering `{{term: id}}` or `{{term: id, label=text}}`:

1. Locate definition by identifier
2. If a `label` parameter is provided, use the label text as the display text
3. Otherwise, extract defined term from `**"..."**` formatting
4. Replace directive with the display text and hyperlink
5. If definition not found, insert `[UNDEFINED: id]` and emit validation error

### 13.5 Field Spec Resolution

When rendering `{{date: value}}` or `{{date: value, note=text}}`:

1. Validate the date value is a valid ISO 8601 date
2. Format the date according to the active locale or render template
3. Ignore any `note` parameter for rendered output
4. Replace the directive with the formatted date text
5. If the date is invalid, insert `[INVALID DATE: value]` and emit a validation error

When rendering `{{money: amount}}`, `{{money: amount, note=text}}`, `{{money: amount, currency=CODE}}`, or `{{money: amount, currency=CODE, note=text}}`:

1. Validate the amount is a valid numeric value
2. If a `currency` parameter is provided, validate it is a recognized ISO 4217 code
3. Format the amount according to the active locale or render template, including the currency symbol or code
4. Ignore any `note` parameter for rendered output
5. Replace the directive with the formatted monetary value
6. If the amount is invalid, insert `[INVALID AMOUNT: amount]` and emit a validation error
7. If the currency code is unrecognized, insert `[UNKNOWN CURRENCY: CODE]` and emit a validation warning

When rendering `{{party: role}}`, `{{party: role, note=text}}`, `{{party: role, label=text}}`, or `{{party: role, label=text, note=text}}`:

1. If a `label` parameter is provided, use it as the display text
2. If no `label` is provided, use the `role` value as the display text
3. Format the display text according to the active locale or render template
4. Ignore any `note` parameter for rendered output
5. Replace the directive with the formatted party reference text
6. If the `role` value is empty or malformed, insert `[INVALID PARTY: role]` and emit a validation error

When rendering `{{duration: value, unit=UNIT}}` or `{{duration: value, unit=UNIT, note=text}}`:

1. Validate the value is a positive numeric value
2. Validate the `unit` parameter is one of: `S`, `M`, `H`, `D`, `MO`, `Y`
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
- Table formatting
- Paragraph spacing and indentation
- Cover page format

Templates SHOULD be defined in a separate configuration file (e.g., YAML or JSON) completely independent of document content. The same LegalDown source SHOULD render correctly with any compatible template.

---

## 14. Bilingual Documents

### 14.1 Overview

LegalDown supports bilingual and multilingual contracts via **separate files** — one document per language, with metadata linking them

### 14.2 Separate File 

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

# Service Agreement {#agreement}

## Definitions {#definitions}

{{def: confidential-info}}
**"Confidential Information"** means any non-public information...
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

# Accord de service {#agreement}

## Définitions {#definitions}

{{def: confidential-info}}
**« Information confidentielle »** désigne toute information non publique...
```

**Rules for separate file approach:**

- Linked translation files MUST have identical heading hierarchy
- Linked translation files MUST use identical section identifiers
- Validators MUST check structural consistency between linked files
- Cross-references resolve to section numbers (same in both versions)

### 14.3 Bilingual Validation

The `legaldown validate --sync` command MUST check:

- Both files have identical heading hierarchy
- All section identifiers match between files
- All `{{def:}}` declarations exist in both files
- Both files declare the same languages in metadata
- Warns on structural differences

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
| Document contains exactly one level 1 heading | Error |
| Heading levels do not skip | Error |
| Section identifiers are unique within document | Error |
| Section identifiers follow naming rules | Error |
| Headings do not contain hardcoded numbering | Warning |
| Directives are well-formed | Error |
| Definitions section is the first level 2 heading | Error |
| Definitions section contains no subheadings (level 3 or deeper) | Error |

### 15.3 Reference Validation

| Check | Level |
|---|---|
| All `{{ref: id}}` point to existing sections | Error |
| All `{{term: id}}` point to declared definitions | Error |
| Circular definitions detected | Error |
| Definitions used before declaration | Warning |
| Sections with no references (possible orphaned content) | Info |

### 15.4 Definition Validation

| Check | Level |
|---|---|
| All `{{def: id}}` declarations are unique | Error |
| All `{{def: id}}` declarations appear in the Definitions section | Error |
| Defined terms follow `**"Term"**` formatting | Warning |
| Declared definitions never referenced with `{{term:}}` | Warning |

### 15.5 Field Spec Validation

| Check | Level |
|---|---|
| `{{date:}}` value is valid ISO 8601 date | Error |
| `{{money:}}` amount is a valid numeric value | Error |
| `{{money:}}` `currency` parameter is a recognized ISO 4217 code | Warning |
| `{{money:}}` used without `currency` parameter and no default configured | Warning |
| `{{party:}}` `role` value is non-empty and matches identifier format | Error |
| `{{duration:}}` value is a positive numeric value | Error |
| `{{duration:}}` `unit` parameter is one of `S`, `M`, `H`, `D`, `MO`, `Y` | Error |
| `field_types` keys follow the identifier format `[a-z][a-z0-9-]*` | Error |
| `field_types` keys do not collide with built-in directive names `date`, `money`, `duration`, `party` | Error |
| `{{field:}}` `type` parameter is present and matches identifier format | Error |
| `{{field:}}` uses a type declared in `field_types` when `field_types` is present | Warning |
| `{{placeholder:}}` `placeholder-id` value is non-empty and matches identifier format | Error |
| `{{placeholder:}}` `type` parameter, when present, is one of `text`, `date`, or `money` | Error |
| Repeated `{{placeholder:}}` occurrences with the same `placeholder-id` use the same effective `type` | Error |
| `{{placeholder:}}` `currency` parameter for `type=money` is a recognized ISO 4217 code | Warning |
| Field spec `note` parameter is plain text and does not contain commas or closing braces | Error |

### 15.6 Document Metadata Validation

If `document_type` is omitted, validators MUST treat it as `contract` when applying the following checks:

| Rule | `contract` | `unilateral_act` | `collective_act` |
|---|---|---|---|
| Minimum distinct sides | ≥ 2 | ≥ 1 | ≥ 1 |
| Side named `issuer` required | No | Yes | Yes |
| Minimum total parties | ≥ 2 | ≥ 1 | ≥ 1 |
| `document_type` is valid value | Error if not | Error if not | Error if not |

Violations of the following additional checks MUST be reported as **Error**:

- Every party `name` is unique across the entire document
- Every side `name` is unique
- All side and party `name` values follow the identifier format `[a-z][a-z0-9-]*` (a lowercase ASCII letter followed by zero or more lowercase ASCII letters, digits, or hyphens)
- Every party `type` is `legal_entity` or `natural_person`

### 15.7 Bilingual Validation (when translations metadata present)

| Check | Level |
|---|---|
| Translation files exist at declared paths | Error |
| Heading hierarchy matches between translations | Error |
| Section identifiers match between translations | Error |
| Definition IDs match between translations | Error |

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

## 16. Complete Examples

### 16.1 Contract Example

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
---

# Mutual Non-Disclosure Agreement

This Mutual Non-Disclosure Agreement (this "Agreement") is entered into on
{{date: 2026-02-01}} between {{party: acme}} and {{party: beta}}.

## Definitions {#definitions}

{{def: confidential-info}}
**"Confidential Information"** means any non-public information disclosed by
one side to the other in connection with evaluating a potential business
relationship.

## Confidentiality Obligations {#confidentiality}

Each party shall protect the {{term: confidential-info}} using at least
reasonable care.

## Use Restrictions {#use}

{{party: beta, label=the Receiving Party}} may use the
{{term: confidential-info}} solely for evaluating a potential business
relationship with {{party: acme, label=the Disclosing Party}}.

## Governing Law {#governing-law}

This Agreement is governed by the laws of Delaware.
```

### 16.2 Unilateral Act Example

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

# Notice of Termination

This notice is issued by {{party: acme}}.

## Definitions {#definitions}

{{def: termination-date}}
**"Termination Date"** means {{date: 2026-06-01}}.

## Notice {#notice}

{{party: acme, label=the Issuer}} hereby terminates the Services Agreement
effective on the {{term: termination-date}}.

## Delivery {#delivery}

This notice shall be delivered in accordance with the notice provisions of the
Services Agreement.
```

### 16.3 Collective Act Example

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

# Remote Work Policy

This Policy is adopted by the Board of Directors of {{party: acme}} and takes
effect on {{date: 2026-04-01}}.

## Definitions {#definitions}

{{def: remote-work}}
**"Remote Work"** means performance of assigned duties at a location other
than the Issuer's premises.

## Eligibility {#eligibility}

Employees of {{party: acme}} may perform {{term: remote-work}} when approved
by their manager and consistent with applicable law.

## Equipment {#equipment}

The Issuer may issue equipment and security requirements needed to support
{{term: remote-work}}.
```

### 16.4 Amendment Example

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

# First Amendment to Master Service Agreement

The parties hereby agree to amend the Master Service Agreement
dated {{date: 2025-01-15}} (the "Agreement") as follows:

## Payment Terms {#payment-terms}

Section 5.1 of the Agreement is amended to read as follows:

Client shall pay Provider within fifteen (15) days of invoice
date. Late payments shall bear interest at {{money: 500, currency=USD}}
per day of delay.

## Data Protection {#data-protection}

The following new section is added after Section 8 of the Agreement:

Provider shall process all {{term: confidential-info}} in
accordance with applicable data protection laws.

## Unchanged Provisions {#unchanged}

All other terms and conditions of the Agreement remain in full
force and effect.
```
