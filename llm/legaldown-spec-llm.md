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
title: Document Title                    # REQUIRED
subtitle: Optional Subtitle             # OPTIONAL
version: 1.0                            # OPTIONAL
document_type: contract                 # OPTIONAL: contract | unilateral_act | collective_act
effective_date: 2026-02-01              # OPTIONAL, ISO 8601
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
authoritative: en                       # OPTIONAL, ISO 639-1
adopted_by: Board of Directors          # OPTIONAL
adoption_date: 2026-03-15               # OPTIONAL, ISO 8601
supersedes: Prior policy v1             # OPTIONAL
tags: [tag1, tag2]                      # OPTIONAL
---
```

### Sides and Parties

- `sides` is an array of side objects
- Each side has a unique ASCII `name` (lowercase letter, then lowercase letters/digits/hyphens), optional `label`, and non-empty `parties` array
- Each party has a unique document-wide ASCII `name` (lowercase letter, then lowercase letters/digits/hyphens), optional `label`, `type`, and `legal_name`
- Party `type` is explicit: `legal_entity` or `natural_person`
- Unknown party fields are allowed and must be ignored by implementations
- Display fallback: side `label` → title-cased/pluralized `name`; party `label` → `legal_name`

## Heading Hierarchy

```
# Document Title              ← Exactly one per document
## Top-level Provision         ← Articles / Sections (level 2)
### Subsection                 ← Level 3
#### Sub-subsection            ← Level 4
##### Level 5
###### Level 6
```

**Rules:**
- `#` must appear exactly once (document title)
- Heading levels must not skip (no `##` → `####` without `###`)
- Heading text must be plain text only — no numbering, no directives, no Markdown formatting
- All section numbering is generated at render time — never write numbers in headings

## Section Identifiers

Explicit identifier syntax appended to headings:

```markdown
## Payment Terms {#payment-terms}
```

**Identifier rules:**
- Lowercase letters, numbers, and hyphens only
- Must start with a letter
- Must be unique within the document
- Auto-generated if omitted: lowercase → spaces/underscores to hyphens → strip non-alphanumeric → truncate to 64 chars

**Identifier scope:**
- Each section identifier must be unique within the document
- Cross-references resolve the exact identifier directly
- Dot-separated hierarchical paths are not used

## Directives

All directives use `{{directive: argument}}` syntax. Case-sensitive, always lowercase. Must not span multiple lines.

### Cross-References

```markdown
{{ref: identifier}}
```

Resolves to the section number (e.g., "3.2"). Links to the target section.
Broken references render as `[BROKEN REF: identifier]`.

### Definitions

**Declare** a defined term (on its own line before the definition paragraph):

```markdown
{{def: term-id}}
**"Term Name"** means ...
```

**Rules:**

- All definitions MUST be placed in a single Definitions section
- The Definitions section MUST be the first `##` heading in the document body
- The Definitions section MUST NOT contain any subheadings (level 3 or deeper)
- All `{{def:}}` declarations appear directly under the `##` heading as consecutive paragraphs

**Reference** a defined term inline:

```markdown
{{term: term-id}}
{{term: term-id, label=Alternative Display Text}}
```

- `label` is optional; when present, displays that text instead of the canonical term name
- `label` must not contain commas or `}}`
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

- `party-name`: lowercase ASCII identifier starting with a letter, then lowercase letters/digits/hyphens; resolves against `sides[].parties[].name`
- `label`: optional inline display override
- Without `label`, render the party `label` and fall back to `legal_name`
- `note`: optional plain-text explanation for automation

### Duration

```markdown
{{duration: 30, unit=D}}
{{duration: 30, unit=D, note=Standard notice period}}
```

- Value: positive numeric
- `unit` (required): `S` | `M` | `H` | `D` | `MO` | `Y`
- `note`: optional plain-text explanation for automation

### File Inclusion

```markdown
{{include: schedules/pricing.lgd}}
```

Path is relative to the including document. Circular includes are invalid.

## Text Formatting

Standard CommonMark:
- `**bold**` — used for defined terms as `**"Term"**`
- `*italic*`
- Lists (ordered and unordered) with blank lines before/after
- Tables (standard Markdown pipe tables with header row)
- Block quotes (used for recitals/WHEREAS clauses)
- HTML comments `<!-- ... -->` — stripped from rendered output
- Horizontal rules `---` — for major document divisions

## Bilingual Documents

Separate files per language with identical heading structure and section identifiers. Linked via `translations` and `authoritative` in frontmatter.

## Validation Summary

**Errors** (must fix):
- Not exactly one `#` heading
- Skipped heading levels
- Duplicate or malformed section identifiers
- Definitions section is not the first `##` heading
- Definitions section contains subheadings
- `{{def:}}` declarations outside the Definitions section
- Broken `{{ref:}}` or `{{term:}}` targets
- Duplicate `{{def:}}` declarations
- Invalid `document_type`, side names, party names, or party `type` values
- Too few sides or parties for the selected `document_type`
- Missing `issuer` side for `unilateral_act` or `collective_act`
- Invalid `{{date:}}`, `{{money:}}`, or `{{duration:}}` values
- Mismatched bilingual structure

**Warnings** (should fix):
- Hardcoded numbering in headings
- Defined terms not following `**"Term"**` format
- Declared definitions never referenced
- Missing `currency` on `{{money:}}`

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

# Mutual Non-Disclosure Agreement

## Definitions {#definitions}

{{def: confidential-info}}
**"Confidential Information"** means any non-public information disclosed
by one side to the other, whether orally or in writing, that is designated
as confidential.

{{def: effective-date}}
**"Effective Date"** means the date first written above.

## Confidentiality Obligations {#confidentiality}

{{party: beta, label=the Receiving Party}} shall protect the
{{term: confidential-info}} using at least the same degree of care it uses
for its own confidential information.

## Term and Termination {#term}

This Agreement commences on the {{term: effective-date}} and continues
until {{date: 2028-02-01}} unless earlier terminated by either party upon
{{duration: 30, unit=D}} written notice.
```
