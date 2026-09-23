# Proposal: Template Language for LegalDown

| | |
|---|---|
| **Status** | Accepted — specified in [`spec/legaldown-spec.md`](../spec/legaldown-spec.md) §15 for v0.2 |
| **Targets** | v0.2 |
| **Tracks** | [ForLegalAI/LegalDown#38](https://github.com/ForLegalAI/LegalDown/issues/38) — Conditional content for templates |
| **Date** | 2026-09-23 |

This is a design proposal, not specification text; it is kept as a record of the design and its
rationale. The normative text is §15 of [`spec/legaldown-spec.md`](../spec/legaldown-spec.md).

> **Superseded in detail by the specification.** Review of the specification refined several
> points after this proposal was accepted, and the specification wins wherever the two differ.
> Most notably: includes in a template are restricted (only in the template's own body, each
> fragment included once, no conditions or drafting notes in fragments); inserted text must be
> kept apart from surrounding Markdown punctuation (`insertion-boundary`); a defined term may not
> contain a blank; the assembly procedure and its escaping rules are specified byte for byte; and
> several open questions below were settled (section 11: `!` for negation, single-value conditions, final
> check as a job option). See the [0.2 changelog entry](../CHANGELOG.md).

References written with § (§5.3) point to the v0.1 specification; references written as
"section 3" point to this proposal.

---

## Summary

v0.1 already supports fillable blanks in templates: `{{placeholder:}}` (§10.7, §3.10). This
proposal adds the four things templates still lack, plus one validation option:

| | Addition | Syntax |
|---|---|---|
| 1 | **Questions**: optional declarations that give blanks a prompt and a default, and declare the yes/no and multiple-choice decisions a template depends on | `questions:` in frontmatter |
| 2 | **Conditions**: optional and alternative sections, list items, paragraphs, and attachments | `{#id when=...}`, reusing the anchor marker |
| 3 | **Inline choices**: a word or phrase that varies with a decision, inside a sentence | `{{choose:}}` directive |
| 4 | **Drafting notes**: guidance for the person using the template, removed from the finished document | `> [!DRAFTING]` block quote |
| 5 | **Final check**: a validator option that rejects anything unfinished | no syntax |

It also defines **assembly**: how a template plus a set of answers becomes an ordinary
LegalDown document.

Two decisions keep this simple:

- **Conditions attach only to whole structural units.** These are a section with its
  subsections, a list item, a paragraph, an included file, and an attachment. They never
  attach to arbitrary spans of text. The one inline exception, `{{choose:}}`, picks between
  plain-text phrases and cannot contain structure.
- **A condition is a single test on a single answer.** There are no `and`/`or` operators and
  no expression language. Nesting gives "and", and alternatives cover most uses of "or".

Together they give the property that matters most:

> **A template that validates without Errors assembles into a document without Errors, for
> every possible set of answers.**

This works because LegalDown never hardcodes numbers (§1.2). Removing a clause from a Word
template breaks every "see clause 9.2". Removing a section from a LegalDown template only
changes what the renderer numbers.

---

## 1. Design goals

1. **Simple to write and read.** A lawyer should understand a template in a plain text editor
   without learning a programming language.
2. **Language agnostic.** The syntax uses symbols and identifiers, never English phrases. Every
   human-facing text (prompts, choice labels, drafting notes) is written in the document's own
   language. Labels a renderer adds come from the style template, not from fixed English
   strings.
3. **Validate once, assemble any.** Static checks on the template guarantee an Error-free
   result for every answer set (section 5.4).
4. **Deterministic.** The same template and answers produce byte-identical output in every
   conforming implementation.
5. **Reuse what exists.** The anchor marker, block quotes, placeholders, and the directive
   grammar are reused. The only new directive is `{{choose:}}`.
6. **Visible degradation.** A v0.1 tool must never silently drop or silently keep conditional
   content (§16.5).

---

## 2. Template, draft, final

A template is not a new file type. It is a LegalDown document that declares `questions` or
uses `when=` or `{{choose:}}`.

| State | `questions`, `when=`, `{{choose:}}` | Placeholders | Drafting notes |
|---|---|---|---|
| **Template** | Yes | MAY | MAY |
| **Draft** | No | MAY | MAY |
| **Final** | No | No | No |

**Assembly** (section 6) turns a template and an answers file into a draft. When every blank
is answered, the draft is final. A draft is exactly what v0.1 already calls a draft, so v0.1
documents are unaffected.

---

## 3. Questions

```yaml
questions:
  fee:
    type: money
    prompt: Fixed fee, excluding VAT
  non-solicit:
    type: boolean
    prompt: Include a non-solicitation covenant?
    default: true
  forum:
    type: choice
    prompt: How are disputes resolved?
    choices:
      courts: State courts
      arbitration: ICC arbitration
    default: courts
```

| Field | Status | Description |
|---|---|---|
| `type` | REQUIRED | `text`, `date`, `money`, `duration`, `boolean`, or `choice` |
| `prompt` | RECOMMENDED | The question as shown to the person filling the template, in the document's language |
| `default` | OPTIONAL | Used when the answers file omits the answer |
| `choices` | REQUIRED for `choice` | Map of value id → label. At least two entries. Value ids use the identifier format (§5.2). Labels are free text in the document's language |

The question id (the map key) follows the identifier format, `[a-z][a-z0-9-]*`.

**Questions and placeholders are the same thing.** A placeholder id is a question id:

- `text`, `date`, `money`, and `duration` questions are **blanks**, filled through
  `{{placeholder:}}`. Declaring them is **optional** and only adds a prompt and a default. An
  undeclared placeholder behaves exactly as in v0.1.
- `boolean` and `choice` questions are **decisions**. They are used only by `when=` and
  `{{choose:}}`, and must be declared, because both need to know the possible values.
- When a placeholder's question is declared, the inline `type` may be omitted. If it is
  written, it must match the declaration.

**New placeholder type `duration`**, mirroring `{{duration:}}` (§10.5):
`{{placeholder: term, type=duration, unit=MO}}`.

---

## 4. Conditions

### 4.1 Syntax

The anchor marker gains one optional attribute, `when=`:

```markdown
# Non-Solicitation {#non-solicit when=non-solicit}

- processing of personal data under {{attach: dpa}} {#scope-data when=personal-data}

The Client may terminate for convenience on thirty days' notice. {when=!fixed-term}

# Dispute Resolution {#disputes when=forum:arbitration}
```

A condition is one test:

| Condition | True when |
|---|---|
| `when=non-solicit` | Boolean question `non-solicit` is `true` |
| `when=!non-solicit` | Boolean question `non-solicit` is `false` |
| `when=forum:arbitration` | Choice question `forum` is `arbitration` |
| `when=!forum:arbitration` | Choice question `forum` is anything other than `arbitration` |

```ebnf
marker    ::= "{" attribute ( ws+ attribute )* "}"
attribute ::= "#" identifier | "when=" condition
condition ::= [ "!" ] identifier [ ":" identifier ]
```

- `{#id}` alone is exactly the v0.1 anchor. `{when=...}` alone is also valid: it makes the unit
  conditional without creating an anchor, and a heading then gets its usual auto-generated
  identifier (§5.3).
- A condition contains no spaces, no quoting, and no words, so it reads the same in a Czech,
  French, or English document.

### 4.2 What can be conditional

The same positions where v0.1 allows an anchor (§5.2, §5.7), plus three more:

| Unit | Where the marker goes | What is included or removed |
|---|---|---|
| Section | After the heading text | The section, **with all its subsections and content** |
| List item | End of the item's first paragraph | The item, with its nested lists |
| Paragraph | End of a top-level paragraph | The paragraph |
| Preamble paragraph | End of the paragraph | The paragraph. Only `when=` is allowed here: §4.4 still rules out anchors in the preamble |
| Included file | End of the paragraph holding `{{include:}}` | The whole included fragment |
| Attachment | `when:` on the entry in `attachments` | The attachment |

A unit inside another conditional unit is present only if **both** conditions are true. This
is how conditions combine. No `and` operator is needed:

```markdown
# Data Protection {#data when=personal-data}

- sub-processors may be engaged only with the Client's prior written consent {#data-consent when=!sub-processors}
```

### 4.3 Alternatives

Two units MAY share an identifier if their conditions can never both be true. Exactly one of
them survives assembly, and references to the shared identifier always resolve to the survivor:

```markdown
# Dispute Resolution {#disputes when=forum:courts}

Disputes are resolved exclusively by the courts of {{placeholder: forum-city}}.

# Dispute Resolution {#disputes when=forum:arbitration}

Disputes are finally settled under the ICC Rules by a sole arbitrator seated in
{{placeholder: forum-city}}.
```

`{{ref: disputes}}` can then be written anywhere. It works because `forum` has exactly those
two values. A `{{def:}}` may be declared twice in the same way.

### 4.4 Why whole units only

If a condition could cover any span of text (#38's shape B, `{{if:}} … {{endif}}`), removing
that span could leave a `###` directly under a `#`. Checking for that would mean checking every
combination of answers.

Whole units cannot cause the problem. Removing a section together with its subsections never
breaks the heading hierarchy (§4.1): the next heading is never deeper than the removed one. List
items and paragraphs contain no headings. The hierarchy therefore holds for every answer set,
and the validator only has to check it once.

There is a drafting benefit too. A clause that switches wording on and off mid-sentence is hard
to review. Putting each variant in its own paragraph, item, or section is clearer for the reader
of the template and of the finished document. When only a word or phrase varies, the one inline
form, `{{choose:}}` (section 4.5), picks between plain-text phrases. It cannot hide headings,
anchors, or definitions, so it cannot break anything section 5 checks.

### 4.5 Inline choices — `{{choose:}}`

A phrase that varies with a decision, inside an otherwise fixed sentence:

```markdown
Nothing in Section {{ref: disputes}} prevents interim relief from
{{choose: forum, courts="a competent court", arbitration="a competent court or an emergency arbitrator"}}.

The fee is payable within thirty days of invoice{{choose: vat, true=", plus VAT", false=""}}.
```

**Syntax.** The directive follows the v0.1 directive grammar (§11.2) unchanged:

- The positional value is the id of a declared `boolean` or `choice` question.
- There is one named parameter per possible answer. The parameter names are the choice's value
  ids, or `true` and `false` for a boolean.
- **Every possible answer must be listed.** Use `""` to produce no text. If a template later
  adds a choice value, every `{{choose:}}` for that question fails validation until it covers
  the new value, so no phrase can go missing silently.
- Values are plain text in the document's language, quoted when they contain a comma (§11.3).
  They cannot contain directives: a `{{term:}}` or `{{ref:}}` inside a value would be literal
  text, and `{{` draws `brace-stray` (§15.2). When a variant needs a defined term, a reference,
  or a blank, write it as a paragraph or item alternative (section 4.3) instead.

**Where it may appear.** Anywhere v0.1 recognizes directives in body text (§11.4): paragraphs,
list items, table cells, and block quotes. It may not appear in headings, which stay plain
text (§4.2), or in frontmatter.

**Language neutrality.** The only fixed tokens are the directive name and, for booleans,
`true`/`false`, the same literals the answers file uses. Value ids are the author's own
identifiers, and the phrases are in the document's language. A translation mirrors the
parameter names and translates only the phrases.

`{{choose:}}` is the inline counterpart of `when=`. Use `when=` when a whole unit appears or
disappears, and `{{choose:}}` when only words change.

---

## 5. Validation

### 5.1 How the checks work

Every check below needs only the template. Conditions are single tests over questions with a
few possible values each (`true`/`false`, or the declared choices). A validator can therefore
check a rule by **trying every combination of the questions involved**, which in practice means
two or three questions and a handful of combinations.

### 5.2 Refined v0.1 rules

`anchor-duplicate`, `def-duplicate-id`, and `attachment-id-duplicate` keep their ids and their
meaning. They now count two declarations of the same id as duplicates only if **both can be
present at the same time**. This is what permits alternatives (section 4.3).

### 5.3 New rules

| ID | Check | Level |
|---|---|---|
| `question-invalid` | A question declaration is malformed: bad id, unknown `type`, a `choice` with fewer than two choices, or a `default` that does not fit the type | Error |
| `question-unused` | A declared question is never used | Warning |
| `placeholder-question-mismatch` | A placeholder's `type` conflicts with its declared question, or the placeholder uses a `boolean` or `choice` question | Error |
| `condition-invalid` | A `when=` names an undeclared question, uses `:value` with a boolean, omits the value for a choice, or names an undeclared choice value | Error |
| `condition-never-true` | A unit can never be present, because its condition contradicts an enclosing one | Warning |
| `condition-reference-unsafe` | A `{{ref:}}`, `{{term:}}`, or `{{attach:}}` may point to a unit that is absent while the reference itself is present | Error |
| `choose-invalid` | A `{{choose:}}` names an undeclared or non-decision question, names a value the question does not have, or leaves a possible answer unlisted | Error |
| `drafting-note-def` | A `{{def:}}` appears inside a drafting note, where assembly would remove it | Error |

All eight are **Core** (§16.2). They need the document only. A question used only by
`{{choose:}}` counts as used for `question-unused`.

### 5.4 The guarantee

If a template has no Errors, then every assembly of it has no Errors:

| What could go wrong after assembly | Prevented by |
|---|---|
| Skipped heading levels | Whole units only (section 4.4) |
| Broken references, terms, or attachments | `condition-reference-unsafe` |
| Duplicate anchors or definitions | Refined duplicate rules (section 5.2) |
| Invalid dates, amounts, or durations | Answer checks at assembly (section 6.2) |
| A phrase missing for some answer | `choose-invalid` requires every answer to be listed |
| Answer text or chosen phrases interpreted as Markdown or directives | Escaping (section 6.2) |

Warnings can still appear, for example `def-unreferenced` when a term was only used in a removed
section. That is acceptable, because a Warning only asks for review.

---

## 6. Assembly

### 6.1 Answers file

```yaml
fee: "48000.00"
non-solicit: true
forum: arbitration
forum-city: Vienna
effective-date: 2026-10-01
```

A flat map of question id → value:

| Type | Value |
|---|---|
| `text` | A single-line string |
| `date` | An ISO 8601 date (`2026-10-01`) |
| `money` | `{amount, currency}`, with the amount a string in §10.3 format (a string avoids floating-point rounding). The bare amount string is enough when the placeholder already fixes `currency` |
| `duration` | `{value, unit}`, or the bare value when the placeholder already fixes `unit` |
| `boolean` | `true` / `false` |
| `choice` | One of the declared value ids |

Every value except `text` is language-neutral. For the same case, a Czech and an English
version of a template take the same answers file.

### 6.2 Steps

1. **Decisions.** Take each `boolean` and `choice` answer from the answers file, or else its
   `default`. If a decision has neither, report `answer-missing` (Error). Report values of the
   wrong type as `answer-invalid` (Error), and ids that match no question as `answer-unknown`
   (Warning).
2. **Conditions.** Remove every unit whose condition is false, with everything inside it.
   Delete the `when=` attribute from the units that remain, and delete markers left empty.
   Replace each `{{choose:}}` with the phrase for the given answer.
3. **Blanks.** Replace each answered placeholder with the matching v0.1 construct: the text
   itself, `{{date:}}`, `{{money:}}`, or `{{duration:}}`. In frontmatter, the plain value is
   inserted. Unanswered placeholders stay as they are.

   Text answers and chosen phrases are escaped (backslash escapes, `\{` before `{{`, §11.4), so
   that they render exactly as written.
4. **Clean-up.** Remove drafting notes and the `questions` block.
5. **Identifiers.** Identifiers stay as they were in the template. If removing content would
   change an auto-generated identifier, write that identifier out explicitly.

Nothing else is changed. The result is an ordinary LegalDown document that can be diffed,
negotiated, and rendered. **Section numbering happens at render time, after assembly.**

### 6.3 Conformance

Assembly reads an answers file, not another document, so it does not belong to any of the
three levels (§16). It is a **named capability**, *Assembly*, which an implementation MAY claim
alongside any level. For example, "Core + Assembly" describes a document-generation backend, and
"Rendering + Assembly" describes an editor with a live preview.

---

## 7. Drafting notes and rendering templates

### 7.1 Drafting notes

```markdown
# Non-Solicitation {#non-solicit when=non-solicit}

> [!DRAFTING]
> Twelve months is the firm's standard. Do not extend beyond twenty-four months without
> partner approval.

During the engagement and for {{duration: 12, unit=MO}} after it ends, neither party shall
solicit ...
```

- A block quote whose first line is exactly `[!DRAFTING]` is a drafting note. It is written in
  the document's language and may have several paragraphs.
- Assembly removes drafting notes. HTML comments (§8.6) remain what they are in v0.1: notes to
  whoever edits the *source*, never rendered.
- Directives inside a note are validated like any others, so a `{{ref:}}` in a note cannot go
  stale. A `{{def:}}` inside a note is an Error.
- `[!DRAFTING]` is a fixed keyword, like directive names, and is never rendered as-is. The
  renderer shows the note in a distinct style and labels it in the document's language, taking
  the label from the style template (§13.7).

The syntax follows the GitHub-flavoured Markdown alert form (`> [!NOTE]`), so ordinary Markdown
viewers still show the note, as a quote.

### 7.2 Rendering a template without answers

When a renderer renders a template without answers, it:

- MUST mark every conditional unit visibly, together with its condition. The label and layout
  come from the style template, not from fixed English strings.
- MUST show every phrase of a `{{choose:}}`, the way paper templates show alternatives. The
  RECOMMENDED form uses symbols only, so it needs no translation:
  `[a competent court / a competent court or an emergency arbitrator]`.
- SHOULD show drafting notes in a distinct style.
- renders placeholders as in v0.1 (§13.5), and MAY show their `prompt`.

Numbering in this view is implementation-defined. Alternatives that share an identifier SHOULD
share a number.

Rendering *with* answers means assembling first, then rendering as usual.

### 7.3 In v0.1 tools

Nothing is dropped or kept without a trace. A marker with `when=` is not a valid v0.1 anchor,
so it stays in the text, visibly. `{{choose:}}` renders as `[UNKNOWN DIRECTIVE: choose]`
(§11.5); under a declared `legaldown: "0.2"` it is a Warning rather than an Error. A drafting
note renders as an ordinary quote with its label showing. `questions` is ignored as unknown
metadata (§3.7).

---

## 8. Final check

v0.1 has no notion of a finished document. A contract that still contains a placeholder
validates cleanly and prints `[_____]` in the signature copy.

Validators and renderers SHOULD offer a **final** option, for example `--final` or a render-job
setting. With it enabled, two more checks apply:

| ID | Check | Level |
|---|---|---|
| `placeholder-unfilled` | A `{{placeholder:}}` remains, in the body or frontmatter | Error |
| `template-construct-present` | A `questions` block, a `when=` attribute, a `{{choose:}}`, or a drafting note remains | Error |

Whether a document is final is a property of the job ("render this for signature"), not of the
document, so no frontmatter field is needed.

---

## 9. Bilingual templates

Language versions of a template work like language versions of a document (§14). Identifiers
are mirrored from the primary document, and only human text is translated:

- Question ids, `type`, choice value ids, and every `when=` condition MUST be identical across
  linked files. This extends the existing `translation-hierarchy-mismatch` and
  `translation-anchor-mismatch` checks. No new rule is needed.
- `prompt`, choice labels, and `{{choose:}}` phrases are translated in each file. The
  `{{choose:}}` parameter names are value ids, so they stay the same.
- One answers file assembles every language version. Only `text` answers may need per-language
  values, which is open question 3.

---

## 10. Worked example

This is the existing
[`examples/advanced/template/consulting-agreement-template.lgd`](../examples/advanced/template/consulting-agreement-template.lgd),
reworked:

```markdown
---
legaldown: "0.2"
title: Consulting Agreement
document_type: contract
effective_date: "{{placeholder: effective-date, type=date}}"
questions:
  fee:
    type: money
    prompt: Fixed fee, excluding VAT
  non-solicit:
    type: boolean
    prompt: Include a non-solicitation covenant?
    default: true
  personal-data:
    type: boolean
    prompt: Will the Consultant process personal data for the Client?
    default: false
  forum:
    type: choice
    prompt: How are disputes resolved?
    choices:
      courts: State courts
      arbitration: ICC arbitration
    default: courts
sides:
  - name: consultants
    label: Consultant
    parties:
      - name: acme
        label: Acme
        type: legal_entity
        legal_name: Acme Corporation
        identification_number: DE-12345678
        address: 123 Main Street, Dover, DE 19901
  - name: clients
    label: Client
    parties:
      - name: client
        type: legal_entity
        legal_name: "{{placeholder: client-name}}"
        address: "{{placeholder: client-address}}"
governing_law: "{{placeholder: governing-law}}"
language: en
attachments:
  - id: dpa
    title: "Schedule 1: Data Processing Agreement"
    file: attachments/data-processing.lgd
    when: personal-data
---

This Consulting Agreement (this "Agreement" {{def: agreement}}) is entered into on
{{placeholder: effective-date, type=date}} between {{party: acme}} and {{party: client}}.

> [!DRAFTING]
> For fixed-fee advisory engagements only. Use the time-and-materials template otherwise.

# Definitions {#definitions}

"Services" {{def: services}} means the advisory services described in Section {{ref: scope}}.

"Client Data" {{def: client-data}} means personal data processed by the Consultant on behalf of
the Client. {when=personal-data}

# Scope {#scope}

The Consultant shall provide the {{term: services}}, comprising:

- a review of the Client's operations {#scope-review}
- a written recommendations report {#scope-report}
- processing of {{term: client-data}} in accordance with {{attach: dpa}} {#scope-data when=personal-data}

# Fees {#fees}

The Client shall pay {{placeholder: fee, currency=EUR}} for the {{term: services}}, payable
within {{duration: 30, unit=D}} of invoice.

# Non-Solicitation {#non-solicit when=non-solicit}

> [!DRAFTING]
> Twelve months is the firm's standard. Do not extend beyond twenty-four.

For {{duration: 12, unit=MO}} after the engagement ends, neither party shall solicit any
employee of the other who was involved in the {{term: services}}.

# Dispute Resolution {#disputes when=forum:courts}

Disputes are resolved exclusively by the courts of {{placeholder: forum-city}}.

# Dispute Resolution {#disputes when=forum:arbitration}

Disputes are finally settled under the ICC Rules by a sole arbitrator seated in
{{placeholder: forum-city}}.

# Governing Law {#governing-law}

The {{term: agreement}} is governed by the laws of {{placeholder: governing-law}}. Nothing in
Section {{ref: disputes}} prevents interim relief from
{{choose: forum, courts="a competent court", arbitration="a competent court or an emergency arbitrator"}}.
```

`client-name`, `client-address`, `effective-date`, `governing-law`, and `forum-city` are not
declared. They work as v0.1 placeholders. Only the decisions, and the fee (to give it a prompt),
are declared.

What the validator confirms:

- `{{term: client-data}}` and `{{attach: dpa}}` appear only where `personal-data` is true, which
  is exactly when their targets exist. ✓
- The two `{#disputes}` sections can never both be present. ✓
- `{{ref: disputes}}` is unconditional, and one of the two targets is always present. ✓
- The `{{choose:}}` lists a phrase for both `forum` values. ✓

With the answers file from section 6.1 (`personal-data` defaults to `false`), assembly
produces:

```markdown
# Scope {#scope}

The Consultant shall provide the {{term: services}}, comprising:

- a review of the Client's operations {#scope-review}
- a written recommendations report {#scope-report}

# Fees {#fees}

The Client shall pay {{money: 48000.00, currency=EUR}} for the {{term: services}}, payable
within {{duration: 30, unit=D}} of invoice.

# Non-Solicitation {#non-solicit}

For {{duration: 12, unit=MO}} after the engagement ends, ...

# Dispute Resolution {#disputes}

Disputes are finally settled under the ICC Rules by a sole arbitrator seated in Vienna.

# Governing Law {#governing-law}

The {{term: agreement}} is governed by the laws of {{placeholder: governing-law}}. Nothing in
Section {{ref: disputes}} prevents interim relief from
a competent court or an emergency arbitrator.
```

The assembled document also:

- drops the "Client Data" definition, the `dpa` attachment, and the drafting notes
- keeps `client-name`, `client-address`, and `governing-law` as placeholders, because the
  answers file does not supply them. It is therefore a **draft**, and the final check would
  list those three blanks.

---

## 11. Open questions

1. **`!` for negation**, or a second attribute such as `unless=`?
2. **Several values in one condition**, for example `when=forum:courts|mediation`? It is left
   out for now. The same result is possible with separate alternatives.
3. **Per-language text answers** for bilingual templates, such as a scope description that
   differs by language.
4. **Provenance.** Should assembly record the template it came from (for example
   `assembled_from: consulting-agreement.lgd`), so that tooling can re-assemble when the
   template changes?
5. **Final check as an option, or a frontmatter field** such as `status: final`?
6. **Directives inside `{{choose:}}` phrases.** Phrases are plain text for now, so "the
   {{term: services}}" cannot vary inline. Allowing nested directives would need a change to
   the v0.1 directive grammar. Is the gap big enough in real templates to justify one?

## 12. Deliberately left out

- **Conditional spans of rich text.** `{{choose:}}` covers plain-text phrases. Anything with
  directives, formatting, or structure goes in its own paragraph, item, or section.
- **Combined conditions** (`and`, `or`, named conditions). Nesting and alternatives cover the
  common cases, and an expression language would bring English keywords or programmer syntax.
- **Conditions on text, money, or date answers** (for example `fee > 100000`). Model the
  threshold as a `choice` question instead.
- Repetition and loops, computed values, conditional parties or table rows, and template
  inheritance. All are consistent with #38's out-of-scope list.

## 13. Alternatives considered

| Alternative | Why not |
|---|---|
| Delimited regions `{{if:}} … {{endif}}` (#38 shape B) | Can break the heading hierarchy, adds paired and nested blocks to the parser, and invites mid-sentence logic that is hard to review |
| Conditions named in frontmatter (#38 shape C) | Adds a layer of indirection that single-test conditions do not need |
| An expression language (`forum is arbitration and not x`) | Uses English words (or symbols foreign to lawyers) and needs precedence rules. Structure already provides "and" |
| Jinja, Liquid, or Handlebars | Unreadable for lawyers, behaves differently across engines, and cannot be checked statically |
| A separate template file type | A template is a document. One file type means one set of tools |
| Drafting notes as HTML comments | Never rendered, which hides them exactly when the template is being reviewed |

## 14. Implementation plan

The work follows the [CONTRIBUTING](../CONTRIBUTING.md) checklist:

- **Spec**
  - Add a `questions` field to §3.2, with a new subsection describing it.
  - Add the `duration` type to §10.7.
  - Add the `when=` attribute to §5.2 and §5.7.
  - Add `{{choose:}}` to the §11.1 directive table, at the Core level.
  - Add a new section, "Templates", covering conditions, alternatives, inline choices,
    assembly, and drafting notes.
  - Add a template row to the §5.6 namespaces table.
  - Add the rows from section 5.3 and section 8 to §15.
  - Add the Assembly capability to §16.
  - Where the spec says "template" but means a style template (§6.3, §13.2, §13.3), change it
    to "style template".
- **Fixtures**
  - Add one fixture per new rule id.
  - Add `fixtures/valid/` cases consisting of a template, an answers file, and the expected
    assembled output. These test the byte-identical claim.
- **Examples**: update `examples/advanced/template/` to match section 10.
- **LLM reference, README, and CHANGELOG**: update them to match.
