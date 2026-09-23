# Proposal: Template Language for LegalDown

| | |
|---|---|
| **Status** | Draft for discussion |
| **Targets** | v0.2 |
| **Tracks** | [ForLegalAI/LegalDown#38](https://github.com/ForLegalAI/LegalDown/issues/38) — Conditional content for templates |
| **Date** | 2026-09-23 |

This is a design proposal, not specification text. Nothing here is normative until it lands in
[`spec/legaldown-spec.md`](../spec/legaldown-spec.md) through the process in
[CONTRIBUTING.md](../CONTRIBUTING.md). References written with § (§5.3) point to the v0.1
specification; references written as "section 5.3" point to this proposal.

---

## Summary

v0.1 gives templates one primitive: the fillable blank, `{{placeholder:}}` (§10.7, §3.10).
Real-world legal templates need more. They need **questions** asked of the person filling them,
**optional clauses**, **one-of-N alternatives**, **drafting guidance** that never reaches the
signed document, a defined way to **turn a template into a document**, and a way to tell
whether a document is **finished**.

This proposal adds six things, in two phases:

| # | Addition | Syntax | Phase |
|---|---|---|---|
| 1 | Declared answers — the template's questions, with types, prompts, and defaults | `template.answers` in frontmatter | 1 |
| 2 | Drafting notes — guidance for the drafter, removed on assembly | `> [!DRAFTING]` block quote | 1 |
| 3 | Completeness profile — "is this document finished?" | validator/renderer option, no syntax | 1 |
| 4 | Conditional content — optional and alternative sections, items, paragraphs, attachments | `when=` on the existing `{#id}` marker | 2 |
| 5 | Inline alternative wording | `{{choose:}}` directive | 2 |
| 6 | Assembly — a deterministic template + answers → document transformation | defined process, `assembled_from` provenance | 2 |

The central design decision, answering the main question in #38: **conditions attach to
structural units only** — sections (with their subsections), list items, top-level paragraphs,
and attachments. They never attach to arbitrary regions of text. This single constraint buys
the most valuable property in the proposal:

> **A template that validates without Errors assembles into a document without Errors, for
> every possible set of answers.** Validate once; assemble any.

This works because v0.1 already refuses hardcoded numbers (§1.2). Deleting clause 7 from a Word
template breaks every "see clause 9.2". Deleting a section from a LegalDown template only
changes what the renderer numbers. The rest of this proposal makes sure the same holds for
headings, identifiers, definitions, and references.

---

## 1. Motivation

### 1.1 What templates need, and what v0.1 offers

| Need | v0.1 | Proposed |
|---|---|---|
| Fillable blank | `{{placeholder:}}` — `text`, `date`, `money` | Unchanged, plus a `duration` type and optional declaration |
| Questions for a form or questionnaire UI | — | `template.answers` with `prompt`, `help`, `default` |
| Optional clause | — (split into two templates) | `# Heading {#id when=...}` |
| One-of-N alternative clauses | — | Mutually exclusive `when=` conditions sharing one identifier |
| Alternative wording inside a sentence | — | `{{choose:}}` |
| Optional schedule or annex | — | `attachments[].when` |
| Guidance for the drafter | HTML comments (§8.6), which are invisible when the template is rendered | `> [!DRAFTING]` notes |
| Producing a document from a template | Left to tooling | Assembly, specified |
| "Is this ready to sign?" | — | Completeness profile |
| "Which template did this come from?" | — | `assembled_from` provenance |

### 1.2 Why this belongs in the format

As #38 puts it: if the logic of a template lives in the tool that assembles it, a user who can
take their `.lgd` files elsewhere has not really taken their templates. Placeholders made the
*blanks* portable in v0.1. This proposal makes the *logic* and the *guidance* portable too.

---

## 2. Design goals

1. **Validate once, assemble any.** Static checks on the template guarantee that every
   assembly is Error-free (section 7.5). This needs condition domains to be finite, which is why
   conditions range only over `boolean` and `choice` answers.
2. **Structure-aligned conditionality.** Only whole structural units are optional. This keeps
   the heading hierarchy intact under any answers, and it fits LegalDown's commitment to
   *simplicity through standardization* (§1.2): drafting that switches words mid-sentence on
   and off is hard to review, and the format should push back on it.
3. **Total and deterministic.** The expression language has no functions, no arithmetic, and no
   side effects. It always terminates. Two conforming implementations produce byte-identical
   assembled documents from the same template and answers.
4. **Human-readable first.** A lawyer opening a template in a plain text editor should see the
   clause, its condition in words (`forum is arbitration`), and the drafting note, with no
   code-shaped noise.
5. **Graceful degradation.** A v0.1 implementation that meets a v0.2 template must never
   *silently* drop or keep conditional content (§16.5). Section 10 shows that the proposed
   syntax degrades visibly.
6. **Minimal extensions.** The proposal reuses the anchor marker, block quotes, the directive
   grammar, and the placeholder mechanism, and adds exactly one directive.

---

## 3. Document states

A template is not a separate file type. It is a LegalDown document with a `template` block in
its frontmatter. Three states follow from what a document contains:

| State | `template` block | Conditions, `{{choose:}}` | Placeholders | Drafting notes |
|---|---|---|---|---|
| **Template** | Yes | MAY | MAY | MAY |
| **Draft** | No | MUST NOT | MAY | MAY |
| **Final** | No | MUST NOT | MUST NOT | MUST NOT |

```
                       ┌──────────────┐
  template.lgd ───────►│              │      draft.lgd                final.lgd
                       │   assemble   ├───►  (blanks may      ──►     (complete)  ──► render
  answers.yaml ───────►│  (section 7) │       remain)     fill rest
                       └──────────────┘
```

A partially answered template assembles into a draft: conditions are all resolved, and
unanswered value blanks stay as `{{placeholder:}}` directives. That is exactly the v0.1 notion
of a draft, so nothing changes for v0.1 drafts.

Answers to #38's question 5: a template **is** a valid LegalDown document. It follows every
v0.1 rule, plus the template rules below, and it validates and renders with the same tooling.

---

## 4. Declared answers — `template` frontmatter block *(phase 1)*

### 4.1 Schema

```yaml
template:
  id: acme-consulting-agreement
  version: "2.0"
  answers:
    client-legal-name:
      type: text
      prompt: Client's full registered name
    effective-date:
      type: date
      prompt: Date the agreement takes effect
    fee-amount:
      type: money
      currency: EUR
      prompt: Fixed fee for the engagement
      help: Excluding VAT. Use the amount approved in the engagement letter.
    engagement-term:
      type: duration
      unit: MO
      prompt: Length of the engagement, in months
      default: 6
    include-non-solicit:
      type: boolean
      prompt: Include a non-solicitation covenant?
      default: true
    personal-data:
      type: boolean
      prompt: Will Acme process personal data on the Client's behalf?
    forum:
      type: choice
      prompt: How are disputes resolved?
      choices:
        courts: State courts
        arbitration: ICC arbitration
      default: courts
  conditions:
    arbitration-with-data: forum is arbitration and personal-data
```

**`template` fields:**

| Field | Status | Description |
|---|---|---|
| `id` | RECOMMENDED | Template identifier (`[a-z][a-z0-9-]*`), recorded in `assembled_from` (section 7.4) |
| `version` | OPTIONAL | Template version string, recorded in `assembled_from` |
| `answers` | OPTIONAL | Map of answer id → answer declaration |
| `conditions` | OPTIONAL | Map of condition name → condition expression (§5.2) |

**Answer declaration fields:**

| Field | Status | Description |
|---|---|---|
| `type` | REQUIRED | `text`, `date`, `money`, `duration`, `boolean`, or `choice` |
| `prompt` | RECOMMENDED | Question shown to the person filling the template (plain text) |
| `help` | OPTIONAL | Longer guidance for that person (plain text) |
| `default` | OPTIONAL | Value used when the answers set omits this answer. Its form follows section 7.1 |
| `choices` | REQUIRED for `choice` | Map of value id (`[a-z][a-z0-9-]*`) → display label. At least two entries. Order is presentation order |
| `currency` | OPTIONAL, `money` only | Fixed ISO 4217 currency. The answer then supplies only the amount |
| `unit` | OPTIONAL, `duration` only | Fixed §10.5 unit. The answer then supplies only the value |

Answer types fall into two families:

- **Value answers** (`text`, `date`, `money`, `duration`) fill blanks and are read by
  `{{placeholder:}}`.
- **Decision answers** (`boolean`, `choice`) drive conditions and `{{choose:}}`. They never
  appear as blanks.

### 4.2 Relationship to placeholders

A placeholder id **is** an answer id. When `template.answers` declares an id:

- `{{placeholder: fee-amount}}` takes the declared type and type-specific parameters
  (`currency`, `unit`), so inline occurrences can stay short. An inline `type` that conflicts
  with the declaration is an Error.
- A placeholder that references a decision answer (`boolean`, `choice`) is an Error.
- A placeholder id that is not declared, in a document whose template declares answers, is a
  Warning (a questionnaire UI cannot ask for it). v0.1 behaviour is unchanged: undeclared
  placeholders are implicitly `text` unless typed inline.

A declaration is optional: §10.7's "placeholders MUST NOT require any separate frontmatter
declaration" still holds. Every v0.1 template remains valid.

### 4.3 New placeholder type: `duration`

```markdown
The engagement runs for {{placeholder: engagement-term, type=duration, unit=MO}}.
```

This mirrors `{{duration:}}` (§10.5), and assembly produces a `{{duration:}}` directive. `unit`
is OPTIONAL on the placeholder. When it is absent, the answer supplies both value and unit.

### 4.4 Namespace

Answer ids and condition names share one new **template namespace** (added to the §5.6
table). The two maps must not share a key. Placeholder ids resolve against this namespace
whenever `template.answers` is present.

---

## 5. Conditional content *(phase 2)*

### 5.1 The `when=` attribute

The v0.1 anchor marker `{#id}` becomes an **attribute marker** that can also carry a condition:

```markdown
# Non-Solicitation {#non-solicit when=include-non-solicit}

- processing of personal data under {{attach: dpa}} {#scope-data when=personal-data}

The Client may terminate for convenience on thirty days' notice. {when="not fixed-term"}
```

**Marker grammar** (extends §5.2 and §5.7):

```ebnf
marker     ::= "{" ws* attribute ( ws+ attribute )* ws* "}"
attribute  ::= "#" identifier | "when=" condition-value
condition-value ::= identifier | quoted-value        ; quoted-value per §11.3
```

- Each attribute appears at most once. Writing `#id` first is RECOMMENDED.
- A marker with only `when=` is valid. It makes the unit conditional without creating an
  anchor. On a heading, the identifier is then auto-generated as usual (§5.3).
- A bare identifier is the name of a condition or a boolean answer. Any other expression is
  quoted: `when="forum is arbitration"`.
- `{#id}` alone is exactly the v0.1 anchor, so existing documents are unchanged.

**Where a condition may appear.** Everywhere v0.1 permits an anchor marker, plus two places:

| Unit | Position | What is conditional |
|---|---|---|
| Heading | After heading text (§5.2) | The section **and its entire subtree** of subsections and content |
| List item | End of the item's first paragraph (§5.7) | The item and its nested blocks |
| Top-level paragraph | End of the paragraph (§5.7) | The paragraph |
| Preamble paragraph | End of the paragraph | The paragraph. `when=` only: §4.4 still forbids preamble anchors |
| `{{include:}}` paragraph | End of the paragraph holding the directive | The whole included fragment |
| Attachment | `attachments[].when` in frontmatter | The attachment and every reference target inside it |

A unit's **presence condition** is the conjunction of its own `when=` and the conditions of
every enclosing unit: its section and ancestor sections, its parent list items, the include
paragraph that brought it in, and the attachment containing it.

### 5.2 Condition expressions

The language is intentionally small. It is boolean-only and total, and every operand has a
finite domain:

```ebnf
expression ::= or-expr | and-expr | unary
or-expr    ::= unary ( ws+ "or" ws+ unary )+
and-expr   ::= unary ( ws+ "and" ws+ unary )+
unary      ::= "not" ws+ unary | atom
atom       ::= "(" ws* expression ws* ")" | test
test       ::= name                                    ; boolean answer or named condition
             | name ws+ "is" ws+ value                 ; choice answer equals value
             | name ws+ "is" ws+ "not" ws+ value       ; choice answer differs from value
             | name ws+ "in" ws* "(" ws* value ( ws* "," ws* value )* ws* ")"
name       ::= identifier
value      ::= identifier                              ; a declared choice value
```

- **`and` and `or` cannot be mixed without parentheses.** `a and b or c` is malformed and must
  be written `(a and b) or c`. The rule removes the one precedence question a non-programmer
  reader would otherwise get wrong. `not` binds tightest.
- **Operands** are boolean answers, choice answers compared with a declared value, and named
  conditions. There are no literals besides choice values, no text or number comparisons, no
  arithmetic, and no functions.
- **Named conditions** (`template.conditions`) may refer to other named conditions. The
  reference graph must be acyclic.
- **Evaluation** is total. Every name resolves to a boolean once the decision answers are fixed
  (answered, or taken from `default`).

Words were chosen over symbols (`is`, `in`, `and`, `not`, rather than `==`, `!=`, `&&`, `!`)
because the audience is lawyers: `forum is arbitration and not include-non-solicit` reads as
the rule it states.

### 5.3 Alternatives: one of N, sharing an identifier

Two units MAY carry the **same explicit identifier** if their presence conditions are mutually
exclusive. Only one can survive assembly, so a reference to that identifier resolves to
whichever alternative is chosen:

```markdown
# Dispute Resolution {#disputes when="forum is courts"}

Any dispute arising out of the {{term: agreement}} shall be resolved exclusively by the courts
of {{placeholder: forum-city}}.

# Dispute Resolution {#disputes when="forum is arbitration"}

Any dispute arising out of the {{term: agreement}} shall be finally settled under the Rules of
Arbitration of the International Chamber of Commerce by a sole arbitrator seated in
{{placeholder: forum-city}}.
```

Elsewhere, `{{ref: disputes}}` is valid wherever `forum is courts or forum is arbitration` is
guaranteed. Because `forum` is a required choice with exactly those two values, that is
everywhere.

There is no `else` keyword. The alternative to `when=x` is `when="not x"`, and the alternative
to one choice value is another choice value. One-of-N is therefore expressed with the same
mechanism as include/omit, which answers #38's question 2.

The same relaxation applies to `{{def:}}` identifiers. A defined term such as "Arbitration
Rules" may be defined differently in two exclusive alternatives.

### 5.4 Why structural units, and why not delimited regions

Delimited regions (#38 shape B: `{{if:}} … {{else}} … {{endif}}`) could wrap any span, for
example the second half of one section and the first half of the next. Removing such a span can
leave a `###` directly under a `#`. The validator would then have to check the heading hierarchy
under every combination of answers, and that number grows exponentially.

Structural units avoid this entirely. **Removing any section subtree never breaks §4.1.** If the
removed heading is at level *k*, the heading before it is at some level *p* with *k* ≤ *p*+1.
The next heading after the subtree is at some level *n* ≤ *k*, and therefore *n* ≤ *p*+1. List
items and paragraphs contain no headings. So the hierarchy holds under all answers without any
per-combination analysis.

Structural units also keep diffs line-oriented, need no pairing or nesting logic in the parser
(the marker is a single token on a line that already exists), and round-trip byte for byte.

What gets lost is conditional *arbitrary* spans. Section 6 covers the inline case with plain
text only. For block-level content, the answer is to make the optional content its own
paragraph, item, or section, which is usually better drafting anyway.

### 5.5 Identifiers under conditions

Auto-generated identifiers (§5.3) and collision suffixes (§5.5) depend on document order, and
assembly changes the document. To keep identifiers stable across template and assembled output:

1. Identifiers are computed over the **template** with all conditional content present. The one
   exception: two headings whose presence conditions are mutually exclusive never collide with
   each other.
2. Assembly MUST keep the template's identifiers. When re-deriving an identifier in the
   assembled document would give a different result, assembly writes that identifier out
   explicitly. This is the same "identifiers originate once and are mirrored explicitly" rule
   §14.2 uses for translations.
3. Validators SHOULD warn when a conditional heading has no explicit identifier
   (`template-implicit-id`). Identifiers inside optional content are the ones most likely to be
   referenced from elsewhere.

### 5.6 Static guarantees: exclusivity and reference safety

Two checks carry the "validate once, assemble any" property. Both reduce to evaluating
conditions over finite domains:

- **Per-configuration uniqueness.** `anchor-duplicate`, `def-duplicate-id`, and
  `attachment-id-duplicate` are refined. Two declarations with the same id are an Error only if
  their presence conditions can **both** be true.
- **Reference safety** (`template-ref-conditional`). For every `{{ref:}}`, `{{term:}}`, and
  `{{attach:}}`, the presence condition of the referring site must **imply** the presence
  condition of the target (or the disjunction of its alternatives). Otherwise some answers
  produce a `[BROKEN REF]`, and that is an Error in the template.

**Decision procedure.** Collect the decision answers named by the two conditions (named
conditions expanded) and enumerate the Cartesian product of their domains: `{true, false}` for
booleans, the declared values for choices. `default` values play no part, since any answer is
possible. The check is exact and deterministic, and in practice it touches two or three answers.
To keep implementations in agreement, the limit is fixed by the specification: when the product
exceeds 65,536 assignments, validators MUST skip that check and emit `condition-too-complex`
(Warning) instead.

---

## 6. Inline alternative wording — `{{choose:}}` *(phase 2)*

```markdown
Nothing in {{ref: disputes}} prevents either party from seeking interim relief from
{{choose: forum, courts="any competent court", arbitration="any competent court or an emergency arbitrator"}}.

The fee is payable {{choose: include-vat, yes="plus VAT at the applicable rate", no=""}} within
thirty days of invoice.
```

**Rules:**

- The positional value names a `choice` answer, a `boolean` answer, or a named condition.
- For a `choice` answer, each named parameter is a declared value id, and **every** value
  MUST be covered. The empty string `""` is allowed. For a boolean answer or named condition,
  the parameters are exactly `yes` and `no`.
- Values are **plain text**, following §11.3. They cannot contain directives: the grammar
  prevents nesting, and `{{` inside a quoted value is literal and draws `brace-stray`.
  Alternatives that need defined terms or references must be structural (section 5).
- Assembly replaces the directive with the selected text, escaped as literal text (section 7.3).

This deliberately narrow directive covers the most common inline need, a phrase that depends
on a decision, without bringing back arbitrary conditional spans.

---

## 7. Assembly *(phase 2)*

Assembly turns a template and an answers set into a LegalDown document. It is a
**source-to-source transformation**: the output is ordinary LegalDown with no template
constructs left, so it can be diffed, versioned, negotiated, validated, and rendered like any
other document. Numbering and reference resolution happen afterwards, at render time. That
answers #38's question 4 normatively: **numbering runs after assembly**.

### 7.1 The answers set

Answers are portable along with the template, so the format specifies their shape (answering
#38's question 3). YAML or JSON:

```yaml
template: acme-consulting-agreement   # OPTIONAL; if present, MUST equal template.id
version: "2.0"                        # OPTIONAL; a mismatch with template.version is a Warning
answers:
  client-legal-name: Northwind Trading s.r.o.
  effective-date: "2026-10-01"
  fee-amount: "48000.00"              # currency fixed by the declaration
  engagement-term: 6                  # unit fixed by the declaration
  include-non-solicit: true
  forum: arbitration
  forum-city: Vienna
  personal-data: false
```

| Type | Answer value |
|---|---|
| `text` | String, single line |
| `date` | ISO 8601 `YYYY-MM-DD` string (a YAML date is accepted) |
| `money` | Amount as a **string** in §10.3 format, or `{amount, currency}` when currency is not fixed. A string avoids binary floating-point drift |
| `duration` | Number, or `{value, unit}` when unit is not fixed |
| `boolean` | `true` / `false` |
| `choice` | One declared value id |

### 7.2 Algorithm

Given a template *T* with no Errors and an answers set *A*:

1. **Resolve decision answers.** Every `boolean` and `choice` answer that any condition or
   `{{choose:}}` depends on takes its value from *A*, or from `default`. If neither exists,
   assembly fails with `answer-missing`. Value answers may be absent.
2. **Validate *A*.** Values must match their types (`answer-value-invalid`, Error). Keys that
   are not declared draw `answer-unknown` (Warning).
3. **Evaluate presence** for every conditional unit. Remove each absent unit with its whole
   subtree, and remove absent attachments from `attachments`. On surviving units, delete the
   `when=` attribute, and delete any marker left empty (`{}`).
4. **Resolve `{{choose:}}`** to the selected text (section 7.3).
5. **Fill placeholders** that have an answer:
   - `text` → the text, escaped (section 7.3)
   - `date` → `{{date: 2026-10-01}}`
   - `money` → `{{money: 48000.00, currency=EUR}}`
   - `duration` → `{{duration: 6, unit=MO}}`

   A placeholder's `note` carries over to the resulting directive. In frontmatter, a value that
   is exactly one placeholder becomes the plain scalar (a date string or text). A placeholder
   embedded in a longer frontmatter string must be `text`. Unanswered placeholders stay as
   they are, which makes the output a draft.
6. **Remove drafting notes** (section 8).
7. **Stabilize identifiers** per section 5.5, rule 2.
8. **Replace the `template` block with provenance** (section 7.4).

Output formatting is deterministic. Assembly changes only the bytes these steps touch, and
every other byte of *T*, including line wrapping and comments, is preserved.

### 7.3 Escaping inserted text

Text answers and `{{choose:}}` values are literal. Assembly MUST escape them so that the
assembled document renders exactly that text: CommonMark backslash escapes for ASCII punctuation
that would otherwise open inline syntax, and `\{` before any `{{` (§11.4). A company named
`*Star* Holdings {{Ltd}}` must not come out in italics, and must not become a directive.

### 7.4 Provenance

```yaml
assembled_from:
  template: acme-consulting-agreement
  version: "2.0"
```

The field is informational. v0.1 implementations ignore it as an unknown field (§3.7). It lets
tooling such as LeGit find every document built from a template version, and it enables
*re-assembly*: produce the document again from a newer template version and the same answers,
then diff.

### 7.5 The guarantee

If *T* has no Errors, then for **every** *A* that passes steps 1–2, the assembled document has
no Errors at the levels *T* was validated at:

| Could fail after assembly | Prevented by |
|---|---|
| Heading skips | Structural units (section 5.4) |
| Broken `{{ref:}}`, `{{term:}}`, `{{attach:}}` | `template-ref-conditional` (section 5.6) |
| Duplicate anchors or definitions | Per-configuration uniqueness (section 5.6) |
| Invalid dates, amounts, durations | Answer type validation (step 2) |
| Directive or Markdown injection through answers | Escaping (section 7.3) |
| Shifted auto-generated identifiers | Identifier stabilization (section 5.5) |

Warnings can still appear. For example, `def-unreferenced` fires when the only use of a term
was in an omitted section. Warnings flag something to review, and they are acceptable in an
assembled document.

---

## 8. Drafting notes *(phase 1)*

Templates need guidance addressed to the drafter: when to use a clause, what to negotiate, what
never to change. v0.1 has only HTML comments, which are stripped from all output (§8.6), so a
template rendered for review hides exactly the guidance its reader needs.

The proposal reuses the block quote with the alert marker popularised by GitHub-flavoured
Markdown:

```markdown
# Non-Solicitation {#non-solicit when=include-non-solicit}

> [!DRAFTING]
> Twelve months is the firm's standard. Do not extend beyond twenty-four months without
> partner approval. Delete for clients in jurisdictions where the covenant is unenforceable.

During the engagement and for {{duration: 12, unit=MO}} after it ends, neither party shall
solicit for employment any employee of the other who was involved in the
{{term: consulting-services}}.
```

**Rules:**

- A block quote whose first line is exactly `[!DRAFTING]` is a **drafting note**. It may span
  several paragraphs and use inline formatting.
- Drafting notes MAY appear in templates and drafts. Assembly removes them, and the completeness
  profile (section 9) rejects any that remain.
- Renderers SHOULD show them in a visually distinct style, labelled as drafting notes, when
  rendering templates and drafts.
- Directives inside a note are recognized and validated, so a `{{ref:}}` in a note cannot go
  stale unnoticed. A `{{def:}}` inside a note is an Error (`drafting-note-def`): the definition
  would disappear on assembly.
- Drafting notes are not structural units, carry no anchors or conditions, and are never
  numbered.

This form is familiar and uses no new syntax class. It also degrades well: any Markdown viewer
shows it as a visible quote, and GitHub shows the label.

HTML comments keep their v0.1 role: notes to whoever edits the *source*. Drafting notes are
for whoever *uses the template*.

---

## 9. Completeness profile *(phase 1)*

v0.1 has no notion of a finished document. A contract with a `{{placeholder:}}` still validates
cleanly and renders `[_____]` in the signed PDF.

Validators and renderers SHOULD offer a **completeness profile**, for example a `--final`
option or a render-job setting, which adds these Errors:

| ID | Check |
|---|---|
| `placeholder-unfilled` | No `{{placeholder:}}` remains (body or frontmatter) |
| `drafting-note-present` | No drafting note remains |
| `template-unassembled` | No `template` block, `when=` attribute, or `{{choose:}}` remains |

Outside the profile, these rows are not reported. The profile is a property of the *job*
("render this for signature"), not of the document, so no frontmatter field is needed. A
frontmatter `status` field is listed as an open question (section 14).

---

## 10. Rendering an unassembled template

A template opened in an editor or rendered for internal review has no answers yet. Renderers
at the Rendering level rendering a template without answers (*template view*):

- MUST render every conditional unit with a visible marker that shows the condition's source
  text. The RECOMMENDED form is `[IF: forum is arbitration]` at the head of the unit.
- MUST render `{{choose:}}` with all alternatives visible. RECOMMENDED form:
  `[courts: any competent court | arbitration: any competent court or an emergency arbitrator]`.
- SHOULD render drafting notes distinctly (section 8).
- Render placeholders as in v0.1 (§13.5). Renderers MAY show the `prompt` text.
- Numbering in template view is implementation-defined. Alternatives that share an identifier
  SHOULD share a number, so that `{{ref:}}` renders one designation.

Rendering *with* answers is assembly followed by ordinary rendering. No second rendering model
is needed.

**Degradation in v0.1 implementations.** Nothing is silently dropped or silently kept:

| Construct | What a v0.1 implementation does |
|---|---|
| `{#id when=...}` on a heading | Not a valid v0.1 anchor, so it stays in the heading text: visible |
| `{when=...}` on an item or paragraph | Literal text plus `anchor-misplaced` Warning: visible |
| `{{choose:}}` | `[UNKNOWN DIRECTIVE: choose]`: visible (§11.5) |
| `> [!DRAFTING]` | Rendered as a block quote with the label: visible |
| `template`, `assembled_from` | Ignored as unknown metadata (§3.7): harmless |
| `legaldown: "0.2"` | `legaldown-version-newer` Warning, with unknown directives softened to Warnings (§11.5) |

---

## 11. Validation rules

New rule ids, following §15.1. Each needs a fixture under `fixtures/invalid/<rule-id>/`.

| ID | Check | Level | Conformance |
|---|---|---|---|
| `answer-id-format` | `template.answers` and `template.conditions` keys follow `[a-z][a-z0-9-]*` and are distinct across both maps | Error | Core |
| `answer-type-invalid` | Answer `type` is one of `text`, `date`, `money`, `duration`, `boolean`, `choice` | Error | Core |
| `answer-choices-invalid` | `choice` answer declares ≥ 2 choices with identifier-format value ids | Error | Core |
| `answer-default-invalid` | `default` is a valid value for the answer's type (a declared value for `choice`) | Error | Core |
| `answer-unused` | Declared answer is never referenced by a placeholder, condition, or `{{choose:}}` | Warning | Core |
| `placeholder-undeclared` | Placeholder id not declared, when `template.answers` is present | Warning | Core |
| `placeholder-answer-mismatch` | Placeholder's inline type or parameters conflict with its declaration, or it references a decision answer | Error | Core |
| `placeholder-frontmatter-type` | A non-`text` placeholder is embedded in a longer frontmatter string | Error | Core |
| `condition-malformed` | Condition expression parses per §5.2, including the no-mixed-`and`/`or` rule | Error | Core |
| `condition-unknown-name` | Every name in a condition resolves to a boolean answer, choice answer, or named condition | Error | Core |
| `condition-type-mismatch` | `is`/`in` applied only to choice answers with declared values; bare names are boolean answers or named conditions | Error | Core |
| `condition-cycle` | Named conditions do not reference each other cyclically | Error | Core |
| `condition-outside-template` | `when=` or `{{choose:}}` used in a document without a `template` block | Error | Core |
| `condition-unsatisfiable` | A unit's presence condition can never be true (dead content) | Warning | Core |
| `condition-too-complex` | A section 5.6 check exceeds 65,536 assignments and was skipped | Warning | Core |
| `template-ref-conditional` | A `{{ref:}}`, `{{term:}}`, or `{{attach:}}` target may be absent where the reference is present | Error | Core |
| `template-implicit-id` | A conditional heading has no explicit identifier | Warning | Core |
| `choose-invalid-subject` | `{{choose:}}` subject is a choice answer, boolean answer, or named condition | Error | Core |
| `choose-incomplete` | `{{choose:}}` covers every value (or `yes`/`no`), with no undeclared values | Error | Core |
| `drafting-note-def` | `{{def:}}` inside a drafting note | Error | Core |
| `answer-missing` | A decision answer needed for assembly has neither an answer nor a `default` | Error | Assembly |
| `answer-value-invalid` | An answer value does not match its declared type | Error | Assembly |
| `answer-unknown` | Answers set contains an undeclared answer id | Warning | Assembly |
| `placeholder-unfilled` | Placeholder remains | Error (profile only) | Core |
| `drafting-note-present` | Drafting note remains | Error (profile only) | Core |
| `template-unassembled` | Template constructs remain | Error (profile only) | Core |

**Refined v0.1 rules** (same ids, same checks, now evaluated per configuration, section 5.6):
`anchor-duplicate`, `def-duplicate-id`, `attachment-id-duplicate`, `attachment-id-collision`,
`anchor-autogen-collision`, `def-autogen-collision`.

---

## 12. Conformance

Every template check listed above needs only the document itself, so they are **Core**.
Enumerating conditions is analysis of that single file.

Assembly reads an answers set rather than another LegalDown document, so it does not fit the
Full level's "other files" scope. Following #38's suggestion, the proposal defines it as a
**named capability**, *Assembly*, which an implementation MAY claim at any level:

| Claim | Typical implementation |
|---|---|
| Core + Assembly | A form-filling or document-generation backend |
| Rendering + Assembly | An editor with a live preview of the answered template |
| Full + Assembly | A complete toolchain, including conditional includes and attachments |

An implementation without Assembly that is asked to render a template follows section 10 (template
view) and §16.5. It never silently resolves conditions.

---

## 13. Worked example

The existing [`examples/advanced/template/consulting-agreement-template.lgd`](../examples/advanced/template/consulting-agreement-template.lgd),
rewritten for v0.2. It shows every feature in the proposal: declared answers, an optional
section, two alternative sections sharing an identifier, a conditional list item and definition,
a conditional attachment, `{{choose:}}`, and drafting notes.

### 13.1 Template

```markdown
---
legaldown: "0.2"
title: "Consulting Agreement with {{placeholder: client-short-name}}"
document_type: contract
effective_date: "{{placeholder: effective-date}}"
template:
  id: acme-consulting-agreement
  version: "2.0"
  answers:
    client-short-name:
      type: text
      prompt: Client's short name, as it should appear in the title
    client-legal-name:
      type: text
      prompt: Client's full registered name
    client-id:
      type: text
      prompt: Client's registration number
    client-address:
      type: text
      prompt: Client's registered address
    effective-date:
      type: date
      prompt: Date the agreement takes effect
    engagement-term:
      type: duration
      unit: MO
      prompt: Length of the engagement, in months
      default: 6
    fee-amount:
      type: money
      currency: EUR
      prompt: Fixed fee, excluding VAT
    governing-law:
      type: text
      prompt: Governing law
    forum-city:
      type: text
      prompt: City of the courts or the arbitral seat
    include-non-solicit:
      type: boolean
      prompt: Include a non-solicitation covenant?
      default: true
    personal-data:
      type: boolean
      prompt: Will Acme process personal data on the Client's behalf?
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
        legal_name: "{{placeholder: client-legal-name}}"
        identification_number: "{{placeholder: client-id}}"
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
{{placeholder: effective-date}} between {{party: acme}} and {{party: client}}.

> [!DRAFTING]
> Use this template for fixed-fee advisory engagements only. For time-and-materials work, use
> the Acme T&M template.

# Definitions {#definitions}

"Consulting Services" {{def: consulting-services}} means the advisory services described in
Section {{ref: scope}}.

"Client Personal Data" {{def: client-personal-data}} means personal data processed by
{{party: acme, label=the Consultant}} on behalf of the Client under the {{term: agreement}}. {when=personal-data}

# Scope of Engagement {#scope}

{{party: acme, label=the Consultant}} shall provide the {{term: consulting-services}},
comprising:

- a strategic review of the Client's operations {#scope-review}
- a written recommendations report {#scope-report}
- processing of {{term: client-personal-data}} strictly in accordance with {{attach: dpa}} {#scope-data when=personal-data}

The engagement runs for {{placeholder: engagement-term}} from {{placeholder: effective-date}}.

# Fees {#fees}

The Client shall pay {{placeholder: fee-amount}} for the {{term: consulting-services}}, payable
within {{duration: 30, unit=D}} of invoice.

# Non-Solicitation {#non-solicit when=include-non-solicit}

> [!DRAFTING]
> Twelve months is the firm's standard. Do not extend beyond twenty-four months without partner
> approval.

During the engagement and for {{duration: 12, unit=MO}} after it ends, neither party shall
solicit for employment any employee of the other who was involved in the
{{term: consulting-services}}.

# Dispute Resolution {#disputes when="forum is courts"}

Any dispute arising out of the {{term: agreement}} shall be resolved exclusively by the courts of
{{placeholder: forum-city}}.

# Dispute Resolution {#disputes when="forum is arbitration"}

Any dispute arising out of the {{term: agreement}} shall be finally settled under the Rules of
Arbitration of the International Chamber of Commerce by a sole arbitrator. The seat of
arbitration is {{placeholder: forum-city}}.

# Governing Law {#governing-law}

The {{term: agreement}} is governed by the laws of {{placeholder: governing-law}}. Nothing in
Section {{ref: disputes}} prevents either party from seeking interim relief from
{{choose: forum, courts="any competent court", arbitration="any competent court or an emergency arbitrator"}}.
```

What the validator proves statically:

- `{{term: client-personal-data}}` and `{{attach: dpa}}` sit in an item whose presence is
  `personal-data`, and both targets are present exactly when `personal-data` holds. The
  implication holds. ✓
- The two `{#disputes}` headings have presence conditions `forum is courts` and
  `forum is arbitration`, which are exclusive. The anchor is unique in every configuration. ✓
- `{{ref: disputes}}` in Governing Law is unconditional, and its target's presence is
  `forum is courts or forum is arbitration`, which always holds. ✓
- Removing the Non-Solicitation section, or either Dispute Resolution section, cannot break the
  heading hierarchy (section 5.4). ✓

### 13.2 Answers

```yaml
template: acme-consulting-agreement
version: "2.0"
answers:
  client-short-name: Northwind
  client-legal-name: Northwind Trading s.r.o.
  client-id: CZ-27082440
  client-address: Na Příkopě 12, 110 00 Prague 1, Czech Republic
  effective-date: "2026-10-01"
  fee-amount: "48000.00"
  governing-law: Austria
  forum-city: Vienna
  include-non-solicit: true
  personal-data: false
  forum: arbitration
  # engagement-term omitted: default 6 applies
```

### 13.3 Assembled document (body excerpt)

```markdown
---
legaldown: "0.2"
title: Consulting Agreement with Northwind
document_type: contract
effective_date: 2026-10-01
assembled_from:
  template: acme-consulting-agreement
  version: "2.0"
sides:
  # ... placeholders replaced with the answers ...
governing_law: Austria
language: en
---

This Consulting Agreement (this "Agreement" {{def: agreement}}) is entered into on
{{date: 2026-10-01}} between {{party: acme}} and {{party: client}}.

# Definitions {#definitions}

"Consulting Services" {{def: consulting-services}} means the advisory services described in
Section {{ref: scope}}.

# Scope of Engagement {#scope}

{{party: acme, label=the Consultant}} shall provide the {{term: consulting-services}},
comprising:

- a strategic review of the Client's operations {#scope-review}
- a written recommendations report {#scope-report}

The engagement runs for {{duration: 6, unit=MO}} from {{date: 2026-10-01}}.

# Fees {#fees}

The Client shall pay {{money: 48000.00, currency=EUR}} for the {{term: consulting-services}},
payable within {{duration: 30, unit=D}} of invoice.

# Non-Solicitation {#non-solicit}

During the engagement and for {{duration: 12, unit=MO}} after it ends, ...

# Dispute Resolution {#disputes}

Any dispute arising out of the {{term: agreement}} shall be finally settled under the Rules of
Arbitration of the International Chamber of Commerce by a sole arbitrator. The seat of
arbitration is Vienna.

# Governing Law {#governing-law}

The {{term: agreement}} is governed by the laws of Austria. Nothing in Section
{{ref: disputes}} prevents either party from seeking interim relief from any competent court or
an emergency arbitrator.
```

The assembled document is plain v0.1-style LegalDown. It passes the completeness profile, the
`attachments` key is gone (its only entry was conditional), and the renderer numbers it 1–6.

---

## 14. Open questions

1. **Attribute name.** This proposal uses `when=`, following #38's sketch. `if=` is shorter and
   more familiar to developers, while `when=` reads more naturally to lawyers.
2. **Operators.** Words (`is`, `in`, `and`, `not`) or symbols (`==`, `!=`, `and`, `not`)? Words
   are proposed.
3. **Completeness as a job option or a frontmatter field.** Should a document be able to declare
   `status: final` so that every tool applies the profile without being told to?
4. **`number` answer type** for percentages, counts, and interest rates (`{{placeholder: rate, type=number}}`).
   v0.1 has no `{{number:}}` directive to assemble into, so it would render as pass-through text.
5. **Conditional parties.** An optional guarantor is a common need, but parties are referenced
   by `{{party:}}` and counted by `sides-minimum`. Deferred unless a simple rule emerges.
6. **Bilingual templates.** Presumably each linked file is assembled with the same answers, and
   §14.3's structural checks extend to `when=` (identical conditions on mirrored units). Prompts
   would need per-language text.
7. **`{{choose:}}` in phase 2, or later?** It is the only piece that touches inline text. It
   could be deferred to keep 0.2 purely structural.
8. **Answers-set versioning.** Should a mismatched `version` be a Warning (as proposed) or
   ignored entirely?

## 15. Out of scope (deferred)

These are consistent with #38's out-of-scope list:

- Repetition and loops: one clause per property, or a variable number of parties or items
- Arithmetic and computed values, such as a fee of rate × days
- Conditions over `text`, `money`, or `date` answers (`fee > 100000`). These would make condition
  domains infinite and break the exhaustive checks in section 5.6. Model the threshold as a `choice`.
- Conditional table rows
- Clause libraries, template inheritance, or overriding parts of another template
- External data lookups

## 16. Alternatives considered

| Alternative | Why not |
|---|---|
| **Delimited regions** (`{{if:}} … {{endif}}`, #38 shape B) | Arbitrary spans break the heading-hierarchy guarantee (section 5.4), need pairing and nesting in an otherwise flat block model, and invite hard-to-review mid-sentence logic |
| **Named variants only** (#38 shape C) | Kept as the optional `template.conditions` layer. Requiring it for even a single boolean adds indirection with no benefit |
| **Embedding Jinja, Liquid, or Handlebars** | Not total, differs between engines, makes source unreadable to lawyers, and cannot be validated statically |
| **A separate template file type (`.lgdt`)** | A template is a document. One file type means one set of tools, and the `template` block already shows the state |
| **Drafting notes as HTML comments** | Invisible when the template is rendered for review, which is when the notes are needed |
| **Drafting notes as a directive** (`{{guidance: …}}`) | Single-line and plain text only, and `note` already means something else (§10.1) |

## 17. Implementation plan

Following the [CONTRIBUTING](../CONTRIBUTING.md) checklist, split so phase 1 can ship even if
phase 2 needs more discussion.

**Phase 1: answers, drafting notes, completeness** (low risk, no change to parsing structure)

- Spec: §3.2 `template` field. New §3.11 "Template Metadata". §10.7 declared placeholders and
  the `duration` type. New drafting-note subsection in §8. §5.6 template namespace row.
  §15 rows for the phase 1 ids and the completeness profile.
- Terminology: the spec says "template" in several places where it means *style template*
  (§6.3, §13.2, §13.3). Normalize those to "style template" before "template" gains its new
  meaning.
- Fixtures: one per phase 1 rule id. `placeholder-unfilled` and the other profile rules need a
  profile flag in the fixture expectation format.
- Examples: update `examples/advanced/template/` with declared answers and a drafting note.
- LLM reference, README "at a glance" block, CHANGELOG.

**Phase 2: conditions, `{{choose:}}`, assembly**

- Spec: §5.2/§5.7 attribute marker. New section "Conditional Content" (expressions,
  presence, alternatives, identifier stability, static checks). `{{choose:}}` in §11.1. New
  section "Assembly". §13 template view. §16 Assembly capability. §15 rows.
- Fixtures: `fixtures/valid/` pairs of template, answers, and expected assembled output. These
  are the strongest conformance test for the byte-identical assembly claim.
- Examples: the §13 worked example as `examples/advanced/template/`, with answers and assembled
  output kept alongside.
- LLM reference: move "conditional content" out of *Not in the language*.
