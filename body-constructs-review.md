# Contract Body — Constructs Review & Proposal

**Status:** Design proposal. No spec changes have been made yet. This document proposes body-level
constructs to remove the biggest practical blockers for legal drafting, in line with the project's
reuse-first, standardization-minded philosophy.

**Scope:** §4 (Document Structure), §5 (Section Identifiers), §6 (Cross-References), §8 (Text
Formatting / lists / block quotes), §13 (Rendering / enumeration) of
[spec/legaldown-spec.md](spec/legaldown-spec.md).

### What this proposes

1. **Anchorable list items** — `{#id}` on a list item, with `{{ref:}}` resolving to the full
   enumerated path (e.g. `7.3(b)(ii)`). The headline fix.
2. **Lead-in and concluding (tail) text** — specify "flush language" after an enumerated list as a
   first-class part of the clause, reusing CommonMark multi-block list items.
3. **Recitals** — model recitals as *lead-in + anchorable list + tail* (reusing 1 and 2) so they can
   be lettered `(A) (B)` and referenced, instead of un-anchorable block quotes.
4. **References in headings** — permit `{{term:}}` and `{{ref:}}` in heading text.
5. **External references as frontmatter objects** — declare outside authorities as author-formatted
   objects and reference them by a lightweight handle, instead of an inline citation directive.

**Explicitly out of scope:** conditional / optional / alternative clauses (document-assembly logic).
That is an application layer *above* LegalDown, not a markup concern, and is intentionally not
specified here.

---

## Proposal 1 — Anchorable list items (and paragraphs)

### Problem

Identifiers attach only to headings (§5.2) and `{{ref:}}` resolves to a section number (§6.3). List
items get render-time legal enumeration `(a) (b) (i) (ii)` (§8.2, §13.2) but **carry no identifier
and cannot be referenced**. Yet legal drafting constantly references lettered sub-clauses —
*"subject to Section 7.3(b)"*, *"the indemnity in Clause 9.2(a)(ii)"*. Today that is impossible
without hardcoding `(b)`, which breaks on reorder and violates the no-hardcoded-numbers principle
(§1.2). Promoting every sub-point to a heading fails too: headings are plain-text-only (§4.2) and
produce `7.3.1`-style numbering, not the `7.3(b)` lawyers expect.

### Design

Allow an explicit `{#id}` anchor on a **list item**. The reference resolves to the item's full
rendered path: the containing section number followed by the enumeration labels from the top of the
list down to the item.

```markdown
## Provider Obligations {#provider-obligations}

Provider shall:

- maintain professional liability insurance {#cov-insurance}
- comply with all applicable laws, including:
  - data-protection law {#cov-dp}
  - anti-bribery law {#cov-bribery}
```

Then, anywhere in the document:

```markdown
Breach of {{ref: cov-dp}} entitles the Client to terminate.
```

renders as *"Breach of 7.3(b)(i) entitles the Client to terminate."* (assuming the section renders
as 7.3 and the enumeration scheme yields `(b)` and `(i)`).

**Anchor placement and parsing:**

- `{#id}` is written at the **end of the list item's leaf text** (its first paragraph), separated by
  a single space, mirroring the heading anchor rule (§5.2). It is removed from rendered output.
- If a list item has multiple block children (a paragraph, then a nested list, then tail text — see
  Proposal 2), the anchor attaches to the **item** and is written at the end of the item's first
  paragraph.
- An anchor is **explicit only**. List-item ids are never auto-generated (unlike headings, §5.3) —
  you add one only where you intend to reference it. This keeps the identifier namespace clean.

**Identifier rules (reused from §5):**

- Same format as section identifiers: `[a-z][a-z0-9-]*`.
- **Document-global and unique** across the entire identifier namespace — section ids, attachment
  ids, and list-item ids all share one namespace; collisions are an error.

**Reference resolution (extends §6.3):**

1. Locate the anchored block by identifier (heading *or* list item).
2. If it is a **heading**, resolve to the section number as today.
3. If it is a **list item**, resolve to `<section-number><enumeration-path>`, where the enumeration
   path is the concatenation of the active enumeration labels (§13.2) for each list level from the
   top-level list down to the item — e.g. `7.3` + `(b)` + `(i)` → `7.3(b)(i)`.
4. The join format (parenthesized labels, no separating space) is the legal default and SHOULD be
   template-configurable.
5. Hyperlink to the item; broken target → `[BROKEN REF: id]` + error, as today.

**Enumeration interaction:**

- A list that contains an anchored item **MUST be enumerated** even if the template otherwise renders
  plain bullets — an anchor implies the item needs a stable label. An anchored item in a
  non-enumerated list is an error. *(Decided.)*
- Ordered (`1.`) and unordered (`-`) lists both map to labels by level via §13.2, so anchoring works
  regardless of marker.

**Optional extension — paragraph anchors.** The same `{#id}`-at-end-of-block rule MAY apply to a
standalone paragraph. Because a paragraph has no enumeration label, a reference to it renders just the
containing section number (e.g. `7.3`) with a precise hyperlink. Useful for linking, weak for display
(two paragraphs in 7.3 both show "7.3"). Recommended only where a hyperlink, not a distinct label, is
the goal. List items remain the primary, fully-labeled mechanism. *(Status: deferred — the initial
implementation covers list items only; see Open question 2.)*

### Validation (additions to §15.2/§15.3)

| Check | Level |
|---|---|
| List-item/paragraph `{#id}` is unique across the whole identifier namespace | Error |
| List-item/paragraph `{#id}` follows the identifier format | Error |
| `{{ref:}}` to a list-item id resolves (already covered by broken-ref) | Error |
| A list containing an anchored item is rendered with enumeration active | Error |

### Edge cases

- **Cross-section references** work unchanged — ids are document-global.
- **Anchored item inside an attachment** resolves across the combined document (§12.4), same as
  section ids.
- **Reordering** items recomputes `(b)` automatically — the entire point.
- **An item that is both anchored and has anchored sub-items** — each id refers to its own level.

---

## Proposal 2 — Lead-in and concluding (tail / flush) text

### Problem

Legal clauses routinely take the shape *lead-in → enumerated items → concluding wrap-up*:

> Provider shall: (a) do X; (b) do Y; and (c) do Z, **in each case subject to {{ref: payment}}.**

The concluding "in each case…" (flush language / tail) grammatically governs all items and is part of
the same clause. In Markdown, text after a list becomes a *separate* paragraph, visually and
semantically detaching it from the clause.

### Design — specify, don't invent

No new syntax is needed: CommonMark already lets a list item (or a section) contain a paragraph, a
nested list, and then another paragraph. LegalDown should **define how that trailing paragraph
renders** so it behaves as legal flush language.

```markdown
- Provider shall:

  - do X
  - do Y
  - do Z

  in each case subject to {{ref: payment}}.
- Client shall cooperate in good faith.
```

**Definitions (new §8 subsection):**

- The **lead-in (chapeau)** is the first paragraph of a list item (or the paragraph introducing a
  list under a heading) that precedes the item's nested list.
- **Concluding (tail) text** is a block in a list item that *follows* the item's nested list, or a
  paragraph that follows a list under a heading.

**Rendering rules:**

- Tail text MUST render **flush at the clause level** — aligned with the lead-in, not indented to the
  sub-item level.
- Tail text MUST NOT receive an enumeration label (it is not a list item).
- Lead-in text likewise carries the parent item's label (or the section number) and introduces the
  sub-enumeration.

This makes the *lead-in + list + tail* a single rendered clause, which is exactly the legal pattern,
using only structure LegalDown already accepts.

### Related note (not proposed) — conjunctive/disjunctive connectors

Whether enumerated items are joined by "; and" vs "; or" is legally significant and currently must be
typed into the penultimate item, which misplaces on reorder. A future option could let the template
insert the connector. Flagged for awareness; **not** part of this proposal to keep scope tight.

---

## Proposal 3 — Recitals as lead-in + anchorable list + tail

### Problem

§8.4 models recitals (WHEREAS clauses) as **block quotes**, which cannot be lettered `(A) (B) (C)`
or anchored. So the common *"as set out in Recital (B)"* can be neither auto-enumerated nor
referenced, and recital order can't be changed without manual relettering.

### Design — compose Proposals 1 and 2

A recitals block is just a clause: a lead-in, an **anchorable list** of background statements, and a
concluding transition ("NOW, THEREFORE…"). No recital-specific syntax is required.

```markdown
# Background {#recitals}

WHEREAS the parties agree as follows:

- Provider possesses expertise in software development. {#recital-expertise}
- Client wishes to engage Provider for the Services. {#recital-engagement}

NOW, THEREFORE, in consideration of the mutual covenants below, the parties agree:
```

- Each recital is a list item → gains a stable anchor (Proposal 1) and renders `(A) (B)` per the
  enumeration scheme.
- "WHEREAS…" is the lead-in; "NOW, THEREFORE…" is the tail (Proposal 2).
- `{{ref: recital-expertise}}` → "Recital (A)" / "(A)" per template.

**Recital enumeration style.** Recitals conventionally use uppercase letters `(A) (B)`. This is a
template/enumeration-scheme concern (§13.2). The convention is a section with id `recitals`; the style
template keys recital enumeration (uppercase letters `(A) (B)`) off that id. *(Decided — rely on the
`recitals` id; no section-role marker.)*

**Block quotes remain valid** for narrative, non-referenced recitals. This proposal makes the
*anchorable, lettered* form available, and recommends it where recitals must be referenced.

---

## Proposal 4 — Defined-term references in headings

### Problem

§4.2 forbids **all** inline directives in heading text, including `{{term:}}`. But a heading
sometimes needs to display a defined term — e.g. *"Scope of the Services"* where *Services* is a
defined term that should link to its definition and stay consistent.

### Design

Relax §4.2 to **permit `{{term:}}` and `{{ref:}}`** in heading text. The other restrictions stay:
**no hardcoded numbering**, no field-spec directives, and **no Markdown emphasis in source** — any
italics (e.g. for a foreign phrase such as *force majeure*) are a render-time styling choice, not
source markup, consistent with §1.2.

```markdown
## Scope of the {{term: services}} {#scope-of-services}
## Indemnities under {{ref: liability-cap}} {#indemnities}
```

**Auto-id interaction (§5.3).** When a heading has no explicit `{#id}`:

- A `{{term:}}` is replaced by its **resolved display term text** before slugging — e.g. *"Scope of
  the {{term: services}}"* → "Scope of the Services" → `scope-of-the-services`.
- A `{{ref:}}` is **omitted** from the slug, because it resolves to a section number that changes on
  reorder and would make the id unstable. A heading containing `{{ref:}}` therefore SHOULD carry an
  explicit `{#id}`.

**Rendering.** The term/reference renders as its display text/number and hyperlinks to its target, but
inherits the **heading's** styling (the template decides; defined-term styling does not override
heading style).

**Validation.** `{{term:}}` / `{{ref:}}` in a heading resolve like anywhere else (undefined target →
error). Hardcoded numbers, field-spec directives, and source emphasis in headings remain errors.

---

## Proposal 5 — External references as frontmatter objects

### Problem

Contracts cite outside authorities — statutes, regulations, case law, other agreements ("Art. 6
GDPR", "§ 2079 of the Civil Code", "the Lease dated …"). An inline citation **directive** is the
wrong tool: citation form varies wildly by jurisdiction and source, and LegalDown should not try to
parse or format it.

### Design — declare objects, reference a handle (mirrors attachments)

Declare external references as **frontmatter objects** whose display text is fully author-controlled
(so any citation form is allowed), and reference them inline by id with a lightweight handle — exactly
the `attachments` + `{{attach:}}` pattern, but for outside authorities rather than attached files.

**Object fields:**

| Field | Status | Description |
|---|---|---|
| `id` | REQUIRED | Identifier; unique within the shared identifier namespace |
| `title` | REQUIRED | Full citation text, rendered **verbatim** — author controls the form |
| `short` | OPTIONAL | A short form for repeat citations (e.g. "GDPR", "the Lease") |
| `url` | OPTIONAL | Link target |

Additional fields permitted and ignored if unknown (forward-compatible, like party fields).

**`{{cite:}}` syntax:**

```markdown
{{cite: id}}                          → the object's title, verbatim
{{cite: id, short}}                   → the object's short form (the `short` field)
{{cite: id, pinpoint=text}}           → title + an author-written locator
{{cite: id, label=text}}              → custom inline text (overrides title/short)
{{cite: id, pinpoint=text, short}}    → short form + locator
```

**Behavior:**

- `{{cite: id}}` → renders `title` verbatim; hyperlinks to `url` if present.
- `short` (bare flag) → renders the object's `short` field instead of `title`; error if the object
  has no `short`.
- `pinpoint=` → an author-written locator (article/section/paragraph) appended to the citation. Plain
  text; appended per template (default: a space, then the pinpoint). One object can serve many
  pinpoint cites.
- `label=` → overrides the displayed text entirely with author text (e.g. an inflected or contextual
  form), like `{{term: ..., label=}}`. Plain text; no commas or `}}`.
- Unknown id → `[UNKNOWN REFERENCE: id]` + error (mirrors `{{attach:}}`).

`{{cite:}}` is **not a citation-formatting directive** — it never parses or reformats a citation.
`title`, `short`, `pinpoint`, and `label` are all author-written text. That directly answers the
"different form" concern: the form lives in the object, written by the lawyer.

**Worked example.**

Frontmatter:

```yaml
references:
  - id: gdpr
    title: "Regulation (EU) 2016/679 (General Data Protection Regulation)"
    short: "GDPR"
    url: "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
  - id: civil-code
    title: "Act No. 89/2012 Coll., the Civil Code"
    short: "the Civil Code"
  - id: novak-v-acme
    title: "Supreme Court judgment of 14 March 2025, No. 25 Cdo 1234/2025"
  - id: master-lease
    title: "the Lease Agreement dated 1 March 2024 between the parties"
    short: "the Lease"
```

Body:

```markdown
Processing is lawful only under {{cite: gdpr, pinpoint=Art. 6(1)(b)}}.

Thereafter, {{cite: gdpr, short}} applies to all personal data.

Title passes on delivery per {{cite: civil-code, pinpoint=§ 2079}}.

The principle in {{cite: novak-v-acme}} governs.

Rent is set out in {{cite: master-lease, label=the Lease}}, Schedule 2.
```

Renders (illustratively; each hyperlinked where a `url` exists):

- "…lawful only under Regulation (EU) 2016/679 (General Data Protection Regulation) Art. 6(1)(b)."
- "Thereafter, GDPR applies…"
- "Title passes on delivery per Act No. 89/2012 Coll., the Civil Code § 2079."
- "The principle in Supreme Court judgment of 14 March 2025, No. 25 Cdo 1234/2025 governs."
- "Rent is set out in the Lease, Schedule 2."

**Optional — generated table of authorities.** As with the definitions glossary, a renderer MAY
generate a "References" / "Table of Authorities" list from the cited `references` objects, each linking
to its `url`. Off by default; template-controlled.

**Confirmed / open sub-decisions:**

- Directive `{{cite:}}` — **confirmed**.
- Frontmatter key — `references` proposed (vs `authorities`); confirm.
- Short-form mechanism — proposed as both a reusable object `short` field and an inline `label=`
  override. Confirm whether you want both, or just `label=`.
- First-full-then-short rendering convention is left to the author (via `short` / `label`); not
  automated.

---

## Out of scope — conditional / optional / alternative clauses

Document assembly (include/exclude clauses, Option A/B variants, variable-driven logic) is **not**
proposed and is intentionally excluded. It belongs to an application layer above LegalDown
(template/assembly engines), not the markup specification. `{{placeholder:}}` covers fill-in blanks;
anything conditional is out of band.

---

## Consolidated validation additions

| Area | Check | Level |
|---|---|---|
| 1 | List-item/paragraph `{#id}` unique across the identifier namespace | Error |
| 1 | List-item/paragraph `{#id}` follows identifier format | Error |
| 1 | List containing an anchored item is rendered with enumeration active | Error/Warning |
| 4 | `{{term:}}` / `{{ref:}}` in a heading resolves to its target | Error |
| 4 | Heading contains hardcoded numbering, a field-spec directive, or source emphasis | Error |
| 5 | External reference `id` unique; `title` non-empty | Error |
| 5 | `{{cite:}}` resolves to a declared external reference | Error |
| 5 | `{{cite: id, short}}` used but the object has no `short` field | Error |
| 5 | `{{cite:}}` `label` / `pinpoint` are plain text (no commas or `}}`) | Error |

## Summary

| # | Proposal | Mechanism | New surface |
|---|---|---|---|
| 1 | Anchorable list items | `{#id}` on list items; `{{ref:}}` → `7.3(b)(ii)` | Reuses `{#id}`/`{{ref:}}`; path resolution |
| 2 | Lead-in + tail text | Specify rendering of CommonMark multi-block items | None — rendering rules only |
| 3 | Recitals | Compose 1 + 2; recommended `recitals` section | None beyond 1 + 2 |
| 4 | Term/ref in headings | Permit `{{term:}}` and `{{ref:}}` in heading text | Relaxes one §4.2 rule |
| 5 | External references | Frontmatter objects + `{{cite: id}}` | One frontmatter array + one handle directive |

**Headline:** Proposal 1 is the one that matters most — it unblocks references to sub-clauses, the
biggest body-level gap. Proposals 2 and 3 fall out of it almost for free; 4 and 5 are small,
self-contained relaxations.

## Decisions and remaining questions

**Decided:**

1. **Enumeration-forcing (Proposal 1)** — a list with an anchored item MUST be enumerated; an anchored
   item in a non-enumerated list is an error.
3. **Recitals (Proposal 3)** — rely on the recommended `recitals` section id; no section-role marker.
4. **Headings (Proposal 4)** — allow **`{{term:}}` and `{{ref:}}`**; no source emphasis (italics are a
   renderer/template choice).
5. **External references (Proposal 5)** — the `{{cite:}}` handle is accepted; details worked out above.

**Still open:**

2. **Paragraph anchors (Proposal 1)** — allow `{#id}` on standalone paragraphs, or list items only? A
   paragraph has no enumeration label, so its reference renders only the section number — useful as a
   hyperlink, ambiguous as a displayed locator. *Recommendation: list items only for now.*
5a. **External-reference naming** — frontmatter key `references` (vs `authorities`); and whether to
   keep both `short` (object field) and `label=` (inline override), or just `label=`.
