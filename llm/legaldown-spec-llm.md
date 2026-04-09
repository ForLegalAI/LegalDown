# LegalDown Spec — LLM Reference

LegalDown is a plain-text markup language for legal contracts. It is a CommonMark superset with legal-specific directives. This document is a condensed technical reference for reading, understanding, and generating LegalDown documents.

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
title: Contract Title                    # REQUIRED
subtitle: Optional Subtitle             # OPTIONAL
version: 1.0                            # OPTIONAL
effective_date: 2026-02-01              # OPTIONAL, ISO 8601
sides:                                  # RECOMMENDED
  - name: Side Name
    legal_entity:
      - name: Full Legal Name           # REQUIRED
        short_name: ShortRef            # OPTIONAL
        identification_number: ID-123   # REQUIRED for legal_entity
        address: Full Address           # REQUIRED
        representatives:                # REQUIRED for legal_entity (≥1)
          - name: Person Name           # REQUIRED
            title: Role Title           # OPTIONAL
    natural_person:
      - name: Full Legal Name           # REQUIRED
        short_name: ShortRef            # OPTIONAL
        date_of_birth: 1985-03-15       # REQUIRED for natural_person
        address: Full Address           # REQUIRED
governing_law: Jurisdiction             # OPTIONAL
language: en                            # RECOMMENDED, ISO 639-1
translations:                           # OPTIONAL
  fr: contract-fr.lgd
authoritative: en                       # OPTIONAL, ISO 639-1
tags: [tag1, tag2]                      # OPTIONAL
---
```

### Sides and Parties

- `sides` is an array of side objects (e.g., Buyers vs. Sellers)
- Each side has a `name` and contains parties under `legal_entity` and/or `natural_person` keys
- Each key maps to a non-empty array of party objects
- Unknown party fields are allowed and must be ignored by implementations

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

**Hierarchical paths** (dot-separated):
```
payment-terms
payment-terms.late-fees
payment-terms.late-fees.monthly
```

## Directives

All directives use `{{directive: argument}}` syntax. Case-sensitive, always lowercase. Must not span multiple lines.

### Cross-References

```markdown
{{ref: identifier}}
{{ref: identifier, format=with-title}}    ← optional format variant
{{ref: identifier, format=title-only}}
```

Resolves to the rendered section number (e.g., "3.2"). Links to the target section.
Broken references render as `[BROKEN REF: identifier]`.

### Definitions

**Declare** a defined term (on its own line before the definition paragraph):

```markdown
{{def: term-id}}
**"Term Name"** means ...
```

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
```

Value must be valid ISO 8601 (`YYYY-MM-DD`). Rendered per locale.

### Money

```markdown
{{money: 10000, currency=USD}}
{{money: 500}}
```

- Amount: numeric (period decimal separator), no grouping separators or symbols
- `currency`: optional, ISO 4217 code

### Party

```markdown
{{party: role}}
{{party: role, label=Display Text}}
```

- `role`: lowercase ASCII, digits, hyphens
- `label`: optional display text

### Duration

```markdown
{{duration: 30, unit=D}}
```

- Value: positive numeric
- `unit` (required): `S` | `M` | `H` | `D` | `MO` | `Y`

### Percentage

```markdown
{{pct: 15}}
```

Value is the percentage directly (15 = 15%). No `%` symbol.

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
- Broken `{{ref:}}` or `{{term:}}` targets
- Duplicate `{{def:}}` declarations
- Invalid `{{date:}}`, `{{money:}}`, `{{duration:}}`, `{{pct:}}` values
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
effective_date: 2026-02-01
governing_law: Delaware
language: en
---

# Mutual Non-Disclosure Agreement

## Definitions {#definitions}

### Confidential Information {#def-confidential-info}

{{def: confidential-info}}
**"Confidential Information"** means any non-public information disclosed
by one party to the other, whether orally or in writing, that is designated
as confidential.

### Effective Date {#def-effective-date}

{{def: effective-date}}
**"Effective Date"** means the date first written above.

## Confidentiality Obligations {#confidentiality}

### Protection of Information {#confidentiality-protection}

Each party shall protect the {{term: confidential-info}} using at least
the same degree of care it uses for its own confidential information.

### Exceptions {#confidentiality-exceptions}

The obligations in {{ref: confidentiality-protection}} do not apply to
information that was publicly known at the time of disclosure.

## Term and Termination {#term}

This Agreement commences on the {{term: effective-date}} and continues
until {{date: 2028-02-01}} unless earlier terminated by either party upon
{{duration: 30, unit=D}} written notice.

## Remedies {#remedies}

The breaching party shall pay liquidated damages of
{{money: 50000, currency=USD}} per breach, not to exceed
{{money: 500000, currency=USD}} total.

## Governing Law {#governing-law}

This Agreement is governed by the laws of the State of Delaware.
```
