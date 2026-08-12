<div align="center">

# LegalDown 📄

### Markdown for Legal Documents

**Write contracts in plain text. Render to PDF or DOCX. Track changes with Git.**

LegalDown is an open specification that extends Markdown with legal-specific constructs —
structured sections, cross-references, defined terms, and party references —
so legal documents are human-readable, machine-parseable, and AI-friendly.

[Specification](spec/legaldown-spec.md) · [Examples](llm) · [Discussions](../../discussions)

</div>

---

### The Problem

Legal documents live in Word files — a mess of hidden formatting, inconsistent structure, and binary noise. This makes them hard to version-control, hard for AI to process, and fragile to edit. Move one section and half your cross-references break.

### The Fix

A LegalDown document is a **plain text file** you can read in any editor, diff with Git, and feed directly to an LLM. Write once, render anywhere — all section numbering, cross-references, and defined-term links are generated automatically at render time.

---

### Why LegalDown? 🤔

LegalDown is built on a few core ideas:

📝 **Write in plain text.** Documents are readable in any text editor without
proprietary software, plugins, or compatibility concerns. If you can read
this README, you can read a LegalDown document.

🔢 **Never write section numbers.** There are no hardcoded numbers in LegalDown
source. Move, add, or remove sections freely — all numbering and cross-references
update automatically when you render.

🎨 **Content and presentation are separate.** Write the document once. Render
it to PDF, DOCX, or HTML using any style template you want. Change fonts, margins,
and numbering style without ever touching the document text.

✅ **Errors are caught before you send.** Broken cross-references, undefined
terms, and structural mistakes are validated automatically. The document
either passes or it tells you exactly what is wrong and where.

🔀 **Built for version control.** Plain text works naturally with Git. Every
change is tracked, every version is recoverable, and comparing two versions
produces a meaningful, readable diff — not a corrupted Track Changes mess.

✂️ **Simpler by design.** LegalDown encourages clearer, shorter legal documents.
The format does not try to replicate every complexity found in traditional
legal drafting - it forces legal drafting to simplify. Standardized structure makes documents easier to read,
compare, and negotiate.

---

### A Simple Example

Below is a short excerpt from a mutual NDA written in LegalDown:

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
field_types:
  invoice-id: Invoice identifier
  case-number: Court case reference number
governing_law: Delaware
language: en
---

# Definitions {#definitions}

"Confidential Information" {{def: confidential-info}} means any non-public information disclosed
by one side to the other, whether orally or in writing, that is designated
as confidential or that reasonably should be understood to be confidential.

# Confidentiality Obligations {#confidentiality}

{{party: beta, label=the Receiving Party}} shall protect the
{{term: confidential-info}} using at least the same degree of care it uses
for its own confidential information.

# Exceptions {#confidentiality-exceptions}

The obligations in {{ref: confidentiality}} do not apply to information
that was publicly known at the time of disclosure.
```

This source renders automatically as a professionally formatted document with:

- 🔢 Section numbers generated (1., 1.1, 2., 2.1, 2.2...) according to your chosen style
- 🔗 "Confidential Information" linked to its definition wherever `{{term:}}` appears (with optional custom display text via `label`)
- 📌 "Section 2" resolved and hyperlinked wherever `{{ref:}}` appears
- 🎨 Professional typography and layout applied from a style template

The source file itself remains clean, readable, and numbering-free.

---

### Core Concepts 🧠

**Headings define structure.** The Markdown heading hierarchy directly maps
to the legal document structure. The document title lives in frontmatter.
`#` is a top-level provision. `##`, `###` and deeper are nested provisions.
Heading levels must not skip — no jumping from `#` to `###`.

**Identifiers make references stable.** Add `{#payment-terms}` after any
heading to give it a stable identifier. Cross-references use this identifier,
not the section number, so they never break when sections move. Anchors also
work below headings — at the end of a list item or paragraph — so clause-level
references like "Section 4.2(b)" stay stable too, and reorder just as safely.

**Cross-references always resolve.** Write `{{ref: payment-terms}}` in your
text. The renderer looks up the section, finds its number, and outputs
"Section 5" (or whatever number it is). Rearrange the document and it
just works.

**Definitions are tracked.** Declare a defined term by writing it in quotes
and placing `{{def: id}}` right after it — in a Definitions section or inline
at first use — then reference it anywhere with `{{term: id}}`. An optional
`label` parameter — `{{term: id, label=Custom Text}}` — lets you display a
different form of the term (e.g., a grammatically inflected form).
The renderer validates that every referenced term is actually defined,
links it back to its definition, and formats it consistently throughout
the document.

**Metadata lives in frontmatter.** Party names, effective dates, and
document type are declared in a YAML block at the top of the file.
Parties are organized under named sides, with each side containing a
`parties` array of party objects with explicit `type` values (`legal_entity`
or `natural_person`). Structured data stays structured — not buried in
paragraph text.

**Placeholders stay inline.** Write `{{placeholder: closing-date}}` or
`{{placeholder: fee, type=money, currency=EUR}}` directly in the text when a
document needs a fillable blank. No frontmatter declaration is required.

**Custom fields stay structured.** Declare reusable custom value types in
frontmatter under `field_types`, then reference them inline with
`{{field: value, type=type-name}}`. Renderers pass the value through as-is.

**Numbering is never in the source.** This is worth repeating. Section
numbers, list enumeration (a), (b), (i), (ii), and cross-reference text
like "Section 3.2" are all generated at render time. The source file
contains none of them.

---

### Document Structure at a Glance 🗂️

```
# Top-level Provision {#identifier}      ← Article / Section
## Subsection                            ← Nested provision
### Further detail                       ← Deeper nesting (up to 5 levels)

- provision text {#item-id}              ← Anchor a list item (clause-level reference target)

"Defined Term" {{def: term-id}} means... ← Declare a defined term (term in quotes, tag after)

{{term: term-id}}                        ← Use a defined term
{{term: term-id, label=Alt Text}}        ← Use a defined term with custom display text
{{ref: identifier}}                      ← Cross-reference a section
{{date: 2026-06-01}}                     ← Inline date value
{{money: 10000, currency=CZK}}          ← Inline monetary amount
{{field: INV-2026-0042, type=invoice-id}} ← Inline custom typed value
{{placeholder: governing-law}}          ← Inline fillable blank (`type=text` by default)
{{placeholder: fee, type=money, currency=EUR}} ← Typed inline blank
{{party: acme}}                          ← Inline party reference
{{include: schedules/pricing.lgd}}       ← Include an external file
{{lang: fr}} ... {{/lang}}              ← Bilingual language block
```

---

### File Format 📁

LegalDown files use the `.lgd` extension (short for LegalDown). The
alternative `.legaldown` extension is also supported. Files must be UTF-8
encoded.

---

### Specification 📖

The full specification is in [`spec/legaldown-spec.md`](spec/legaldown-spec.md).

It covers document structure, frontmatter format, all directive syntax,
validation rules, rendering requirements, bilingual support, and conformance
levels in detail.

| Version | Status | Document |
|---------|--------|----------|
| v0.1 | 🚧 DRAFT | [spec/legaldown-spec.md](spec/legaldown-spec.md) |

The specification is in early draft. It is not yet stable and may change
before v1.0. Do not build production tooling against a draft version without
following this repository for changes.

---

### Project Status 🚀

LegalDown is in early draft stage. Current priorities:

- [ ] Finalize v0.1 specification
- [ ] Publish reference examples for common document types
- [ ] Release reference parser and validator
- [ ] Release CLI rendering tool
- [ ] Gather community feedback and publish v0.2

Watch this repository and follow [Discussions](../../discussions) to stay
informed.

---

### Contributing 🤝

LegalDown is an open standard. Contributions are welcome at any level.

💬 **Have a question about the spec?**
Open a [Discussion](../../discussions). This is the right place for
questions, ideas, and broader conversations.

🐛 **Found an error or ambiguity?**
Open an [Issue](../../issues). Describe what is unclear and what you
expected.

🛠️ **Want to propose a change?**
Start in [Discussions](../../discussions) first to gather feedback, then
submit a pull request against [`spec/legaldown-spec.md`](spec/legaldown-spec.md).
Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting.

---

### License

The LegalDown specification document is released under
Creative Commons Attribution 4.0 International (CC BY 4.0).

This license applies to the specification document itself.
It does not govern software implementations of the specification.
Parsers, renderers, editors, and other tools implementing LegalDown
may be released under any license their authors choose.
