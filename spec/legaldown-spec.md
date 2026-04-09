# LegalDown Specification
## Version 0.1 DRAFT

---

## 1. Introduction

### 1.1 Purpose

LegalDown is a plain text markup language for authoring legal contracts and agreements. It extends standard Markdown with legal-specific constructs enabling structured authoring, automated validation, intelligent rendering, and version control integration. LegalDown is the document format standard of the LeGit contract management ecosystem, but is designed as an open, independent standard usable with any compatible tooling.

### 1.2 Design Principles

**Human-readable first.** Legal professionals must be able to read and edit LegalDown source files without specialized tools. A contract in LegalDown should be immediately comprehensible to any lawyer opening it in a plain text editor.

**Separation of content and presentation.** Document structure, hierarchy, and content are defined independently of visual formatting, numbering, and styling. A LegalDown document contains no hardcoded section numbers. All numbering is generated at render time by the renderer according to a configurable scheme. This means sections can be freely added, removed, or reordered without any manual renumbering.

**Machine-parseable.** Document structure must be unambiguous for automated processing, validation, transformation, and AI analysis.

**Simplicity through standardization.** LegalDown intentionally encourages simpler contract structures. The format does not attempt to reproduce every complexity found in traditional legal drafting. Standardized templates and enforced structure make contracts easier to read, compare, and negotiate.

**Version control native.** Plain text format is optimized for meaningful diffs, intelligent merging, and collaborative editing through Git-based tooling.

**Minimal extensions.** LegalDown extends standard Markdown only where strictly necessary for legal-specific needs. Where standard Markdown constructs are sufficient, they are used unchanged.

**Open standard.** LegalDown is not proprietary. The specification is publicly available and any tooling may implement it.

### 1.3 Relationship to Standard Markdown

LegalDown is a superset of CommonMark (standard Markdown). All valid CommonMark constructs are valid LegalDown. LegalDown adds:

- YAML frontmatter for document metadata
- Section identifier syntax
- Cross-reference directives
- Definition declaration and reference directives
- Language block directives for bilingual documents
- File inclusion directives
- Validation requirements for legal-specific constraints

### 1.4 Relationship to LeGit

LegalDown is the document format. LeGit is the Git-based contract versioning and negotiation platform. LegalDown documents are the native format of LeGit repositories, but LegalDown can be used independently of LeGit with any compatible renderer or validator.

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

> **Note:** Signature blocks are NOT defined in LegalDown markup. Renderers SHOULD generate signature blocks automatically from the contract's structured data (e.g., party information in frontmatter).

---

## 3. Metadata (Frontmatter)

### 3.1 Format

Documents SHOULD include YAML frontmatter as the first element, delimited by triple dashes:

```yaml
---
title: Master Service Agreement
subtitle: Between Acme Corporation and Beta Industries Inc.
version: 1.0
effective_date: 2026-02-01
sides:
  - name: Providers
    legal_entity:
      - name: Acme Corporation
        short_name: Provider
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
        representatives:
          - name: John Smith
            title: Chief Executive Officer
  - name: Clients
    legal_entity:
      - name: Beta Industries Inc.
        short_name: Client 1
        identification_number: TX-87654321
        address: 456 Oak Avenue, Austin, TX 78701
        representatives:
          - name: Jane Doe
            title: General Counsel
      - name: Gamma Solutions Ltd.
        short_name: Client 2
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
| `effective_date` | OPTIONAL | Contract effective date (ISO 8601) |
| `sides` | RECOMMENDED | Array of sides, each containing parties keyed by type (see Section 3.3) |
| `governing_law` | OPTIONAL | Applicable law |
| `language` | RECOMMENDED | Primary language (ISO 639-1) |
| `translations` | OPTIONAL | Map of translation files (see Section 14) |
| `authoritative` | OPTIONAL | Authoritative language for disputes (ISO 639-1) |
| `tags` | OPTIONAL | Classification tags array |

### 3.3 Sides and Parties

Parties to a contract are organized under **sides**. Each side is a named grouping that contains one or more parties. Sides represent the opposing or distinct groups in a contractual relationship (e.g., "Buyers" vs. "Sellers", "Licensors" vs. "Licensees").

Parties within a side are listed under keys that correspond to their type: `legal_entity` or `natural_person`. This makes the party type implicit from the key, rather than requiring a separate `party_type` field on each party.

```yaml
sides:
  - name: Sellers
    legal_entity:
      - name: ...
  - name: Buyers
    legal_entity:
      - name: Buyer 1 Ltd.
        ...
    natural_person:
      - name: Buyer 2
        ...
```

**Side rules:**

- `sides` is an array of side objects
- Each side object MUST contain a `name` field identifying the side (e.g., "Buyers", "Sellers")
- Each side object MUST contain at least one party object in total across the `legal_entity` and/or `natural_person` arrays
- If a side object includes `legal_entity` and/or `natural_person`, each present type key MUST map to a non-empty array of party objects
- A side MAY contain multiple parties of the same or different types (e.g., two legal entities and one natural person acting jointly on the same side)

### 3.4 Party Structure

Each party object describes an individual or organization that is a party to the contract. The party type is determined by the key under which it is listed (`natural_person` or `legal_entity`), not by a field on the party itself.

**Common party fields:**

| Field | Status | Description |
|---|---|---|
| `name` | REQUIRED | Full legal name of the party |
| `short_name` | OPTIONAL | Short name used in document text |

Additional custom fields MAY be included on any party object. Implementations MUST ignore unknown party fields rather than failing. This allows organizations to include jurisdiction-specific information, tax identifiers, or any other relevant party metadata.

#### 3.4.1 Natural Person

When a party is listed under the `natural_person` key, it represents an individual.

**Required fields for `natural_person`:**

| Field | Status | Description |
|---|---|---|
| `name` | REQUIRED | Full legal name |
| `date_of_birth` | REQUIRED | Date of birth in ISO 8601 format |
| `address` | REQUIRED | Residential address |

**Example:**

```yaml
sides:
  - name: Buyer
    natural_person:
      - name: Jan Novák
        short_name: Buyer
        date_of_birth: 1985-03-15
        address: 456 Oak Avenue, Austin, TX 78701
        nationality: Czech  # custom field
```

#### 3.4.2 Legal Entity

When a party is listed under the `legal_entity` key, it represents a corporation, LLC, partnership, or other legal organization.

**Required fields for `legal_entity`:**

| Field | Status | Description |
|---|---|---|
| `name` | REQUIRED | Full legal name of the entity |
| `identification_number` | REQUIRED | Entity identification or registration number |
| `address` | REQUIRED | Registered address of the entity |
| `representatives` | REQUIRED | Array of at least one representative object (see Section 3.5) |

**Example:**

```yaml
sides:
  - name: Providers
    legal_entity:
      - name: Acme Corporation
        short_name: Provider
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
        tax_id: 12-3456789  # custom field
        representatives:
          - name: John Smith
            title: Chief Executive Officer
```

### 3.4.3 Full Example with Custom Fields

```yaml
sides:
  - name: Sellers
    legal_entity:
      - name: Acme Corporation
        short_name: Seller
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
        tax_id: 12-3456789
        representatives:
          - name: John Smith
            title: Chief Executive Officer
  - name: Buyers
    natural_person:
      - name: Jan Novák
        short_name: Buyer 1
        date_of_birth: 1985-03-15
        address: 456 Oak Avenue, Austin, TX 78701
        nationality: Czech
      - name: Marie Nováková
        short_name: Buyer 2
        date_of_birth: 1990-07-22
        address: 456 Oak Avenue, Austin, TX 78701
```

### 3.5 Representatives

Representatives are the individuals authorized to act on behalf of a party. The `representatives` field is an array of representative objects, allowing multiple representatives per party. It is REQUIRED for parties listed under `legal_entity` (with at least one representative) and OPTIONAL for parties listed under `natural_person`.

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

### 3.6 Party References in Text

Party `short_name` values from frontmatter MAY be used directly in document body text. Renderers SHOULD NOT automatically substitute or link these unless explicitly configured. The author is responsible for using party names consistently.

### 3.7 Metadata Extensions

Additional metadata fields in frontmatter are permitted. Implementations MUST ignore unknown metadata fields rather than failing. This allows forward compatibility and custom extensions.

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

### 5.4 Hierarchical Identifier Paths

Cross-references use hierarchical dot-separated paths to identify sections unambiguously:

```
## Payment Terms {#payment-terms}
### Late Payment Fees {#late-fees}
#### Monthly Calculation {#monthly}
```

Full hierarchical paths:
- `payment-terms`
- `payment-terms.late-fees`
- `payment-terms.late-fees.monthly`

When using cross-references, authors SHOULD use the full hierarchical path to avoid ambiguity, especially when section names may repeat across the document.

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
{{ref: hierarchical.identifier.path}}
```

**Examples:**

```markdown
As described in Section {{ref: definitions}}, terms have specific meanings.

Subject to Clause {{ref: liability.limitations.cap}}, Provider shall indemnify Client.

The payment schedule in Article {{ref: payment-terms.schedule}} applies from the Effective Date.
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

### Confidential Information {#def-confidential-info}

{{def: confidential-info}}
**"Confidential Information"** means any non-public information disclosed by
one party to the other, including technical data, business plans, customer
information, and any other information designated as confidential.

### Services {#def-services}

{{def: services}}
**"Services"** means the software development services described in Section
{{ref: scope-of-work}}.
```

**Rules:**

- `{{def: id}}` MUST appear on its own line immediately preceding the definition text paragraph
- Definition IDs follow the same rules as section identifiers
- Definition IDs MUST be unique within the document
- The defined term SHOULD be formatted as bold quoted text: `**"Term Name"**`
- Definitions SHOULD be grouped in a dedicated Definitions section
- Definitions MAY appear in other sections where contextually appropriate

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

Jednateli náleží za {{term: services, label=Výkon funkcí}}&nbsp;odměna ve výši 10.000,- Kč měsíčně.
```

In the last example, the defined term is "Services" but the label `Výkon funkcí` is displayed in the rendered output, allowing the text to use the grammatically correct form.

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

Field specs are typed inline directives that represent structured values — such as dates and monetary amounts — within the document text. They enable renderers to format values consistently according to locale and template settings, and validators to verify that values are well-formed.

### 10.2 Date Directive

The `{{date:}}` directive represents a calendar date inline in document text.

**Syntax:**

```markdown
{{date: YYYY-MM-DD}}
```

**Examples:**

```markdown
This Agreement shall terminate on {{date: 2026-06-01}}.

Provider shall deliver the final report no later than {{date: 2027-03-31}}.
```

**Rules:**

- The date value MUST be in ISO 8601 format (`YYYY-MM-DD`)
- The date MUST be a valid calendar date (e.g., `2026-02-30` is invalid)
- Renderers MUST format the date according to the document's locale or render template settings (e.g., "June 1, 2026" in `en-US`, "1. Juni 2026" in `de-DE`, "1. 6. 2026" in `cs-CZ`)
- The raw ISO 8601 value MUST be preserved in structured output formats for machine processing

### 10.3 Money Directive

The `{{money:}}` directive represents a monetary amount inline in document text.

**Syntax:**

```markdown
{{money: amount}}
{{money: amount, currency=CODE}}
```

**Examples:**

```markdown
Provider shall pay a penalty of {{money: 10000, currency=CZK}} for each day of delay.

The total contract value shall not exceed {{money: 1000000, currency=USD}}.

The monthly fee is {{money: 500, currency=EUR}}.
```

**Rules:**

- The amount MUST be a numeric value (integer or decimal, using period `.` as the decimal separator)
- The amount MUST NOT include grouping separators, currency symbols, or whitespace
- The optional `currency` parameter specifies the currency using an ISO 4217 three-letter code (e.g., `USD`, `EUR`, `CZK`, `GBP`)
- If `currency` is omitted, the renderer SHOULD use a default currency from the document metadata or render template, or emit a validation warning
- Renderers MUST format the amount according to the document's locale or render template settings (e.g., "$10,000.00", "10 000,00 Kč", "€500.00")
- The raw numeric value and currency code MUST be preserved in structured output formats for machine processing

### 10.4 Party Directive

The `{{party:}}` directive represents a reference to a contract party inline in document text. It identifies a party by their role (such as a representative function) and provides an optional display label for rendering.

**Syntax:**

```markdown
{{party: role}}
{{party: role, label=text}}
```

**Examples:**

```markdown
Za společnost jedná {{party: jednatel, label=Jednatelem}} na základě plné moci.

The obligations of {{party: director}} under this Agreement shall include...

{{party: ceo, label=Chief Executive Officer}} shall have the authority to...
```

**Rules:**

- The `role` value MUST be a non-empty string identifying the party's role or function (e.g., `jednatel`, `director`, `ceo`)
- The `role` value MUST match the identifier format: lowercase ASCII letters, digits, and hyphens (`[a-z0-9]+(-[a-z0-9]+)*`)
- The optional `label` parameter specifies a display text for rendering; if omitted, the renderer SHOULD use the `role` value as the display text
- Renderers MUST format the party reference according to the document's locale or render template settings
- The raw `role` value and `label` (if present) MUST be preserved in structured output formats for machine processing

### 10.5 Duration Directive

The `{{duration:}}` directive represents a time duration inline in document text. It specifies a numeric value and a time unit.

**Syntax:**

```markdown
{{duration: value, unit=UNIT}}
```

Where `UNIT` is one of: `S` (seconds), `M` (minutes), `H` (hours), `D` (days), `MO` (months), `Y` (years).

**Examples:**

```markdown
This Agreement shall remain in effect for {{duration: 12, unit=MO}}.

The notice period shall be {{duration: 30, unit=D}}.

The service level response time shall not exceed {{duration: 4, unit=H}}.
```

**Rules:**

- The `value` MUST be a positive numeric value (integer or decimal, using period `.` as the decimal separator); zero and negative values are not allowed
- The `unit` parameter is REQUIRED and MUST be one of: `S`, `M`, `H`, `D`, `MO`, `Y`
- Renderers MUST format the duration according to the document's locale or render template settings (e.g., "12 months", "30 days", "4 hours", "12 měsíců")
- The raw numeric value and unit code MUST be preserved in structured output formats for machine processing

### 10.6 Percentage Directive

The `{{pct:}}` directive represents a percentage value inline in document text.

**Syntax:**

```markdown
{{pct: value}}
```

**Examples:**

```markdown
The interest rate shall be {{pct: 0.5}} per annum.

Provider shall receive a commission of {{pct: 15}} on all sales.

A late payment penalty of {{pct: 0.05}} per day shall apply.
```

**Rules:**

- The `value` MUST be a numeric value (integer or decimal, using period `.` as the decimal separator)
- The `value` represents the percentage directly (e.g., `0.5` means 0.5%, `15` means 15%)
- The `value` MUST NOT include a percent sign (`%`) or other symbols
- Renderers MUST format the percentage according to the document's locale or render template settings (e.g., "0.5 %", "15%", "0,5 %")
- The raw numeric value MUST be preserved in structured output formats for machine processing

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
| `{{pct: value}}` | OPTIONAL | Inline percentage value |
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

1. Locate target section by identifier using hierarchical path resolution
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

When rendering `{{date: value}}`:

1. Validate the date value is a valid ISO 8601 date
2. Format the date according to the active locale or render template
3. Replace the directive with the formatted date text
4. If the date is invalid, insert `[INVALID DATE: value]` and emit a validation error

When rendering `{{money: amount}}` or `{{money: amount, currency=CODE}}`:

1. Validate the amount is a valid numeric value
2. If a `currency` parameter is provided, validate it is a recognized ISO 4217 code
3. Format the amount according to the active locale or render template, including the currency symbol or code
4. Replace the directive with the formatted monetary value
5. If the amount is invalid, insert `[INVALID AMOUNT: amount]` and emit a validation error
6. If the currency code is unrecognized, insert `[UNKNOWN CURRENCY: CODE]` and emit a validation warning

When rendering `{{party: role}}` or `{{party: role, label=text}}`:

1. If a `label` parameter is provided, use it as the display text
2. If no `label` is provided, use the `role` value as the display text
3. Format the display text according to the active locale or render template
4. Replace the directive with the formatted party reference text
5. If the `role` value is empty or malformed, insert `[INVALID PARTY: role]` and emit a validation error

When rendering `{{duration: value, unit=UNIT}}`:

1. Validate the value is a positive numeric value
2. Validate the `unit` parameter is one of: `S`, `M`, `H`, `D`, `MO`, `Y`
3. Format the duration according to the active locale or render template (e.g., "12 months", "30 days", "12 měsíců")
4. Replace the directive with the formatted duration text
5. If the value is invalid, insert `[INVALID DURATION: value]` and emit a validation error
6. If the unit is missing or unrecognized, insert `[INVALID DURATION UNIT: UNIT]` and emit a validation error

When rendering `{{pct: value}}`:

1. Validate the value is a valid numeric value
2. Format the percentage according to the active locale or render template (e.g., "0.5 %", "15%")
3. Replace the directive with the formatted percentage text
4. If the value is invalid, insert `[INVALID PERCENTAGE: value]` and emit a validation error

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

### Confidential Information {#def-confidential-info}

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

### Information confidentielle {#def-confidential-info}

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
| `{{pct:}}` value is a valid numeric value | Error |

### 15.6 Bilingual Validation (when translations metadata present)

| Check | Level |
|---|---|
| Translation files exist at declared paths | Error |
| Heading hierarchy matches between translations | Error |
| Section identifiers match between translations | Error |
| Definition IDs match between translations | Error |

### 15.7 Validation Output

Validators MUST produce structured output indicating file, line number, identifier (if applicable), issue level, and human-readable message. Validators SHOULD support output in plain text and JSON formats for integration with tooling.

## 16. Complete Example

```markdown
---
title: Mutual Non-Disclosure Agreement
effective_date: 2026-02-01
sides:
  - name: Disclosing Party
    legal_entity:
      - name: Acme Corporation
        short_name: Provider
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
        representatives:
          - name: John Smith
            title: Chief Executive Officer
  - name: Receiving Party
    legal_entity:
      - name: Beta Industries Inc.
        short_name: Client
        identification_number: TX-87654321
        address: 456 Oak Avenue, Austin, TX 78701
        representatives:
          - name: Jane Doe
            title: General Counsel
governing_law: Delaware
language: en
---

# Mutual Non-Disclosure Agreement

This Mutual Non-Disclosure Agreement (this "Agreement") is entered into as
of the Effective Date by and between the parties identified above.

## Recitals

> WHEREAS, the parties wish to explore a potential business relationship
> and may disclose certain confidential information to each other; and
>
> WHEREAS, the parties wish to protect such confidential information from
> unauthorized use or disclosure;
>
> NOW, THEREFORE, in consideration of the mutual covenants herein, the
> parties agree as follows:

## Definitions {#definitions}

### Confidential Information {#def-confidential-info}

{{def: confidential-info}}
**"Confidential Information"** means any non-public information disclosed
by one party (the "Disclosing Party") to the other party (the "Receiving
Party"), whether orally or in writing, that is designated as confidential
or that reasonably should be understood to be confidential given the nature
of the information and circumstances of disclosure.

### Effective Date {#def-effective-date}

{{def: effective-date}}
**"Effective Date"** means the date first written above.

### Representative {#def-representative}

{{def: representative}}
**"Representative"** means a party's employees, officers, directors, and
professional advisors who have a need to know the {{term: confidential-info}}
for the purposes contemplated by this Agreement.

## Confidentiality Obligations {#confidentiality}

### Protection of Information {#confidentiality-protection}

The Receiving Party shall:

- hold the {{term: confidential-info}} in strict confidence
- not disclose the {{term: confidential-info}} to any person other than its
  {{term: representative}} without prior written consent of the Disclosing Party
- use the {{term: confidential-info}} solely for evaluating the potential
  business relationship between the parties
- protect the {{term: confidential-info}} using at least the same degree of
  care it uses to protect its own confidential information, but in no event
  less than reasonable care

### Exceptions {#confidentiality-exceptions}

The obligations in {{ref: confidentiality-protection}} do not apply to
information that:

- was publicly known at the time of disclosure to the Receiving Party
- becomes publicly known after disclosure through no act or omission of the
  Receiving Party
- was rightfully in the Receiving Party's possession prior to disclosure
  without restriction on disclosure
- is independently developed by the Receiving Party without use of the
  {{term: confidential-info}}
- is required to be disclosed by applicable law or court order, provided that
  the Receiving Party gives prompt written notice to the Disclosing Party

## Term and Termination {#term}

This Agreement commences on the {{term: effective-date}} and continues
until {{date: 2028-02-01}} unless earlier terminated by either party upon
thirty (30) days written notice to the other party. Obligations under
{{ref: confidentiality}} survive termination for a period of three (3) years.

## Remedies {#remedies}

In the event of a breach of this Agreement, the breaching party shall pay
the non-breaching party liquidated damages in the amount of
{{money: 50000, currency=USD}} per breach. The total liability under this
section shall not exceed {{money: 500000, currency=USD}}.

## Return of Materials {#return}

Upon termination of this Agreement or upon written request of the Disclosing
Party, the Receiving Party shall promptly return or destroy all
{{term: confidential-info}} in its possession and certify such return or
destruction in writing within ten (10) business days.

## Miscellaneous {#misc}

### Governing Law {#governing-law}

This Agreement shall be governed by and construed in accordance with the
laws of the State of Delaware, without regard to its conflicts of law
principles.

### Entire Agreement {#entire-agreement}

This Agreement constitutes the entire agreement between the parties with
respect to the subject matter hereof and supersedes all prior and
contemporaneous agreements, understandings, and negotiations.

### Amendment {#amendment}

This Agreement may only be amended by a written instrument signed by
authorized representatives of both parties.

### Severability {#severability}

If any provision of this Agreement is found invalid or unenforceable, the
remaining provisions shall remain in full force and effect.

---

**IN WITNESS WHEREOF**, the parties have executed this Agreement as of the
{{term: effective-date}}.
```

**The above source renders with decimal numbering as:**

```
MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement...

RECITALS

WHEREAS, the parties wish to explore...

1. DEFINITIONS

1.1 Confidential Information

"Confidential Information" means any non-public information...

1.2 Effective Date

"Effective Date" means the date first written above.

1.3 Representative

"Representative" means a party's employees...

2. CONFIDENTIALITY OBLIGATIONS

2.1 Protection of Information

The Receiving Party shall:

(a) hold the Confidential Information in strict confidence;
(b) not disclose the Confidential Information to any person...
(c) use the Confidential Information solely for evaluating...
(d) protect the Confidential Information using at least the same...

2.2 Exceptions

The obligations in Section 2.1 do not apply to information that:

(a) was publicly known at the time of disclosure...
...

3. TERM AND TERMINATION

This Agreement commences on the Effective Date and continues
until February 1, 2028... Obligations under Section 2 survive...

4. REMEDIES

In the event of a breach of this Agreement, the breaching party shall pay
the non-breaching party liquidated damages in the amount of $50,000.00 per
breach. The total liability under this section shall not exceed $500,000.00.

[etc.]
```

---

## 19. Future Considerations

The following features are under consideration for future specification versions:

- **Variable substitution** — Insert party names and metadata values directly into text using `{{var: parties.0.name}}` syntax
- **Conditional clauses** — Include or exclude sections based on metadata values
- **Mathematical expressions** — Payment calculations and financial formulas
- **Amendment markup** — Standard syntax for amendments referencing original documents
- **Clause library** — Standard identifiers for common clause types across documents
- **Schema validation** — JSON Schema for frontmatter validation
- **Digital signature integration** — Metadata fields for cryptographic signatures
- **Multi-language glossary** — Shared definition libraries across documents
- **AI annotation layer** — Standard syntax for automated clause analysis metadata

---

**Specification:** LegalDown v0.1 DRAFT
**Date:** 2026-04-08
**Status:** Draft for Comment
