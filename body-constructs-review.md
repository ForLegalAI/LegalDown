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
4. **Defined-term references in headings** — permit `{{term:}}` in heading text.
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
  plain bullets — an anchor implies the item needs a stable label. (Alternatively the renderer MAY
  emit a warning and fall back to the section number; the MUST-enumerate rule is preferred.)
- Ordered (`1.`) and unordered (`-`) lists both map to labels by level via §13.2, so anchoring works
  regardless of marker.

**Optional extension — paragraph anchors.** The same `{#id}`-at-end-of-block rule MAY apply to a
standalone paragraph. Because a paragraph has no enumeration label, a reference to it renders just the
containing section number (e.g. `7.3`) with a precise hyperlink. Useful for linking, weak for display
(two paragraphs in 7.3 both show "7.3"). Recommended only where a hyperlink, not a distinct label, is
the goal. List items remain the primary, fully-labeled mechanism.

### Validation (additions to §15.2/§15.3)

| Check | Level |
|---|---|
| List-item/paragraph `{#id}` is unique across the whole identifier namespace | Error |
| List-item/paragraph `{#id}` follows the identifier format | Error |
| `{{ref:}}` to a list-item id resolves (already covered by broken-ref) | Error |
| A list containing an anchored item is rendered with enumeration active | Error (or Warning, per the enumeration rule above) |

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
template/enumeration-scheme concern (§13.2). To let the renderer apply the recital style, the
RECOMMENDED convention is a section with id `recitals` (or `background`); the style template MAY key
recital enumeration off that id. (A heavier alternative — a section-level role marker — is noted as an
open question, not proposed.)

**Block quotes remain valid** for narrative, non-referenced recitals. This proposal makes the
*anchorable, lettered* form available, and recommends it where recitals must be referenced.

---

## Proposal 4 — Defined-term references in headings

### Problem

§4.2 forbids **all** inline directives in heading text, including `{{term:}}`. But a heading
sometimes needs to display a defined term — e.g. *"Scope of the Services"* where *Services* is a
defined term that should link to its definition and stay consistent.

### Design

Relax §4.2 to **permit `{{term:}}`** in heading text. All other restrictions stay: no hardcoded
numbering, and (for now) no other directives or Markdown emphasis.

```markdown
## Scope of the {{term: services}} {#scope-of-services}
```

**Auto-id interaction (§5.3).** When a heading has no explicit `{#id}`, the auto-id algorithm MUST
first replace any `{{term:}}` with its **resolved display term text**, then slug the result — e.g.
*"Scope of the {{term: services}}"* → "Scope of the Services" → `scope-of-the-services`. Explicit ids
are RECOMMENDED for headings that contain a term, to avoid the resolution dependency.

**Rendering.** The term renders as its display text and hyperlinks to the definition, but inherits the
**heading's** styling (the template decides; the term's usual defined-term styling does not override
heading style).

**Validation.** A `{{term:}}` in a heading resolves like any other (undefined → error). Hardcoded
numbers and other directives in headings remain errors.

**Open sub-question:** whether to also allow `{{ref:}}` in headings (a section number inside a title
is unusual and risks circularity) and/or `*italic*` for foreign phrases (*force majeure*). Not
proposed now; `{{term:}}` only, per the request.

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

```yaml
references:
  - id: gdpr-6
    title: "Article 6(1)(b) of Regulation (EU) 2016/679 (GDPR)"
    url: "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
  - id: civil-code-2079
    title: "Section 2079 of Act No. 89/2012 Coll., the Civil Code"
```

```markdown
Processing is lawful under {{cite: gdpr-6}}.
The purchase contract is governed by {{cite: civil-code-2079}}.
```

**Object fields:**

| Field | Status | Description |
|---|---|---|
| `id` | REQUIRED | Identifier; unique within the shared identifier namespace |
| `title` | REQUIRED | Citation text, rendered **verbatim** — author controls the form |
| `url` | OPTIONAL | Link target |

Additional fields permitted and ignored if unknown (forward-compatible, like party fields).

**`{{cite: id}}` behavior:**

- Resolves to the object's `title`, rendered verbatim (no formatting imposed).
- Hyperlinks to `url` when present.
- Unknown id → `[UNKNOWN REFERENCE: id]` + error (mirrors `{{attach:}}`).

This is **not a citation-formatting directive** — it neither parses nor reformats the citation; it is
only a referenceable, reusable handle to author-written text. That directly answers the "different
form" concern: the form lives in the object, written by the lawyer.

**Open questions:**
- Directive name: `{{cite:}}` vs `{{ref:}}`-with-namespace vs folding into a generalized references
  concept. (`{{ref:}}` is reserved for internal sections; a distinct handle is clearer.)
- Whether a bare handle directive is acceptable given the "no citation directive" preference — it is a
  reference handle, not a formatter, but worth confirming.
- Frontmatter key name: `references` vs `authorities` vs `external_references`.

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
| 4 | `{{term:}}` in a heading resolves to a declared definition | Error |
| 4 | Heading contains hardcoded numbering or a non-`{{term:}}` directive | Error |
| 5 | External reference `id` unique; `title` non-empty | Error |
| 5 | `{{cite:}}` resolves to a declared external reference | Error |

## Summary

| # | Proposal | Mechanism | New surface |
|---|---|---|---|
| 1 | Anchorable list items | `{#id}` on list items; `{{ref:}}` → `7.3(b)(ii)` | Reuses `{#id}`/`{{ref:}}`; path resolution |
| 2 | Lead-in + tail text | Specify rendering of CommonMark multi-block items | None — rendering rules only |
| 3 | Recitals | Compose 1 + 2; recommended `recitals` section | None beyond 1 + 2 |
| 4 | Term in headings | Permit `{{term:}}` in heading text | Relaxes one §4.2 rule |
| 5 | External references | Frontmatter objects + `{{cite: id}}` | One frontmatter array + one handle directive |

**Headline:** Proposal 1 is the one that matters most — it unblocks references to sub-clauses, the
biggest body-level gap. Proposals 2 and 3 fall out of it almost for free; 4 and 5 are small,
self-contained relaxations.

## Open questions for decision

1. **Enumeration-forcing (Proposal 1):** MUST a list with an anchored item be enumerated (Error if
   not), or fall back to the section number with a Warning?
2. **Paragraph anchors (Proposal 1):** include now, or list items only?
3. **Recital style signal (Proposal 3):** rely on a recommended `recitals` section id, or add a
   light section-role marker later?
4. **Headings (Proposal 4):** `{{term:}}` only, or also `{{ref:}}` and/or `*italic*`?
5. **External references (Proposal 5):** confirm the handle directive is acceptable; pick the
   directive name and the frontmatter key.
