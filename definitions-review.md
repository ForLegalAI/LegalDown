# Definitions — Implementation Review & Proposal

**Status:** Design rationale (adopted). This document reviews how LegalDown handled defined terms
prior to the definitions overhaul, explains why the old model was too rigid for real legal
drafting, and records the replacement now incorporated into the spec. See [`CHANGELOG.md`](CHANGELOG.md)
for the change summary and migration guide.

**Scope:** Section 7 (Definitions) of [spec/legaldown-spec.md](spec/legaldown-spec.md), plus the
related validation rules (§15.2, §15.3, §15.4), the LLM reference, and the README.

### Decisions locked in (this review)

1. **One syntax:** the term is written in quotes and the `{{def: id}}` tag is placed **immediately
   after** it. The term is extracted from the preceding quoted span. No block vs. inline split.
2. **Format-agnostic source:** defined terms carry **no emphasis markers** (`**`, `__`). Quotation
   marks are the only delimiter. **All styling — including how the defining occurrence vs. later
   references look — is a renderer/template concern; the spec does not prescribe it.**
3. **Reference by location, not body:** a `{{def:}}` records only *(id, term, location)*. References
   and glossaries point to the **clause/section**. No "definition text" is stored or extracted.
   Optional glossary previews use the containing **paragraph**; sentence-level extraction is avoided.
4. **Name-based ids retained** (not numbered), but **the id MAY be omitted and auto-derived** from
   the quoted term via the §5.3 slug algorithm. Explicit ids remain recommended for stability. See §5.
5. **All delimiter pairs in §3 are accepted by default** — double and single forms (single forms keep
   the apostrophe caveat; double quotes recommended).
6. **Definitions may appear anywhere**, including inside attachment files (attachments MAY introduce
   terms). There is no mandatory Definitions section; a top "Definitions" article is a recommended
   convention only, not enforced.
7. **Breaking change accepted** — LegalDown is v0.1 DRAFT.

---

## 1. How definitions work today

The current model (spec §7) has three moving parts:

| Part | Directive | Where it lives today |
|---|---|---|
| **Declaration** | `{{def: id}}` on its own line, before a paragraph | Only inside *the* Definitions section |
| **Term text** | `**"Term Name"**` extracted from the following paragraph | Same paragraph as the body |
| **Reference** | `{{term: id}}` / `{{term: id, label=...}}` | Anywhere in the body |

And it imposes four structural constraints (§7.2):

1. If the document has **any** `{{def:}}`, **all** definitions MUST be in a single Definitions section.
2. That section MUST be the **first** level‑1 (`#`) heading in the body.
3. That section MUST NOT contain subheadings (level 2+).
4. Every `{{def:}}` appears directly under the `#` heading as consecutive paragraphs.

These are enforced as **errors** in validation (§15.2: "Definitions section is the first level 1
heading", "Definitions section contains no subheadings"; §15.4: "All `{{def:}}` appear in the
Definitions section").

So today a definition is really *one thing*: a glossary entry of the form **"Term"** means …,
collected into a mandatory front-of-document section.

---

## 2. Why this is too rigid for legal workflows

Real legal drafting uses **two** distinct kinds of defined terms, and the current model only
supports the first:

### (a) Stipulative / glossary definitions
A term with an explicit meaning: *"**"Confidential Information"** means any non‑public
information…"*. These naturally live in a Definitions article. The current model handles these
well.

### (b) Labeling / "first-use" definitions
A short label introduced **at the point of first use**, where the surrounding sentence *is* the
definition:

> Acme Corporation ("**Provider**") …
> … the services described in Schedule A (the "**Services**") …
> … Intellectual Property Rights ("**IP Rights**") …

This is one of the most common patterns in actual contracts. The current model **cannot express
it**: to define `provider` you must hoist a `**"Provider"** means …` entry up into the front
Definitions section, away from the place where the term is actually introduced. That is unnatural
for naming definitions and produces awkward, redundant glossary entries.

### Other friction points

- **"Definitions must be the first heading."** Many documents open with Recitals / Background /
  Interpretation / Parties before any defined terms. Forcing Definitions to be the first `#`
  fights that ordering.
- **"Single section, no subheadings."** Long agreements often group definitions ("Financial
  Terms", "Technical Terms") or interleave a handful of local definitions into the relevant
  article. Both are currently illegal.
- **Amendments.** When an amendment adds one clause, it is natural to define the new term *in that
  clause*, not to reopen a central Definitions article. Inline support makes amendments cleaner.

**Net:** the format optimizes for a tidy front glossary at the cost of forbidding the single most
common real-world definition pattern. We can support both with *less* structure, not more.

---

## 3. Proposal A — one definition syntax: term, then tag

`{{def: id}}` is placed **immediately after** the quoted term it defines. The defined term is the
text inside the quotation marks of the span that immediately precedes the directive. There is no
block vs. inline distinction — the same rule applies wherever a definition appears.

```markdown
"Confidential Information" {{def: confidential-information}} means any non-public information
disclosed by one side to the other.

The Provider shall perform marketing services (the "Services" {{def: services}}).
```

Both register a defined term that is referenced the same way everywhere:

```markdown
Client shall pay for the {{term: services}} within thirty days.
```

### Extraction rule

> `{{def: id}}` MUST be immediately preceded, on the same line, by a quoted span — separated only
> by optional whitespace. The **defined term** is the text inside that span's quotation marks. If
> no quoted span immediately precedes, emit an **Error**. The directive emits no visible output of
> its own — it anchors the preceding term and registers the id.

Because each tag binds to the quoted span right before it, **multiple definitions in one sentence**
work naturally — something the old one-`{{def:}}`-per-paragraph block form could not do:

```markdown
The "Services" {{def: services}} and the "Deliverables" {{def: deliverables}} are invoiced monthly.
```

### Accepted term delimiters

A "quoted span" is a run of text enclosed by a recognized opening/closing quotation-mark pair. The
**default accepted set** below covers the major Western legal languages. The active set MAY be
narrowed or extended per document `language` or via template/validator configuration.

| Pair | Open | Close | Code points | Typical languages |
|---|---|---|---|---|
| Straight double | `"` | `"` | U+0022 / U+0022 | ASCII / universal |
| Curly double | `“` | `”` | U+201C / U+201D | English (typographic) |
| Guillemets | `«` | `»` | U+00AB / U+00BB | French, Italian, Spanish, Portuguese, Russian |
| Reversed guillemets | `»` | `«` | U+00BB / U+00AB | German, Danish, Croatian |
| German double | `„` | `“` | U+201E / U+201C | German, Czech, Slovak, Polish |
| Curly single | `‘` | `’` | U+2018 / U+2019 | English (nested) |
| German single | `‚` | `‘` | U+201A / U+2018 | German (nested) |
| Single guillemets | `‹` | `›` | U+2039 / U+203A | French, Swiss (nested) |

**Matching rules:**

- The parser matches the **closing** delimiter immediately preceding the directive (after optional
  whitespace), then scans back to the corresponding **opening** delimiter to delimit the term.
- For symmetric pairs (straight double/single, where open = close) it pairs with the nearest prior
  identical mark on the same line.
- **All pairs above are accepted by default.** **Double-quote forms are RECOMMENDED** for defined
  terms; single-quote forms are accepted but carry a caveat: the right single quote (U+2019) doubles
  as an apostrophe, so a single-quoted term containing an apostrophe can be mis-delimited. Validators
  SHOULD warn in that ambiguous case and recommend double quotes.
- Whitespace between the closing quote and the directive is allowed; anything else (punctuation, a
  word, a closing paren) between them means the directive is **not** attached → **Error**.

> **Note — this fixes an existing latent inconsistency.** §7.3 currently says the term is extracted
> from `**"…"**` (straight quotes), but the French bilingual example (spec line 1292) uses
> guillemets: `**« Information confidentielle »**`. Today's spec never actually defines which quote
> characters are valid. Specifying the set above resolves that regardless of this proposal.

### Format-agnostic — no emphasis markers in source

The term is delimited by **quotation marks only**. Authors do **not** write `**bold**` (or any
emphasis) around defined terms; whether a defined term renders bold, underlined, small-caps, or
quoted is a **render-time** decision driven by the style template (§13.7). This applies the
separation-of-content-and-presentation principle (§1.2) to definitions: the source marks *what* is
a term, the template decides *how* it looks. The quotation marks are the parser's delimiter; the
renderer MAY keep or drop them in output per template.

### No extracted "definition body" — reference the location

A `{{def:}}` records only **(id, term, location)**. The format does **not** store or require a
"definition text." The authoritative answer to "where is this defined?" is the **section/clause**
containing the directive — that is what `{{term:}}` back-links and generated glossaries point to.

For machine purposes (circular-reference detection, optional glossary previews) a definition's
**scope is its containing paragraph** — a deterministic, blank-line-delimited unit. Renderers MAY
optionally surface that paragraph as a glossary preview, but it is best-effort, not authoritative.

> **Sentence-level extraction is deliberately avoided.** Reliable sentence segmentation in legal,
> multilingual text (abbreviations, citations like `25 Cdo 1234/2025`, decimals, enumerations) is
> fragile and locale-dependent, which conflicts with the machine-parseable principle (§1.2). The
> deterministic units are *paragraph* (for previews and circular checks) and *section* (for
> back-links). Prefer those over guessing sentence boundaries.

### Why this supersedes earlier drafts

Simpler than a `term=` parameter or a block/inline split: one rule (term precedes tag), no new
parameters, no paired tags. The old stipulative-vs-labeling distinction disappears *at the format
level* — a `… means …` sentence and a `(the "Services")` first-use label use the exact same
mechanism; the difference is purely authoring style.

---

## 4. Proposal B — drop the "single / first Definitions section" constraint

Once `{{def:}}` can appear anywhere, the special **Definitions section** stops being a structural
element and becomes just an ordinary section that authors *conventionally* use for stipulative
definitions.

**Recommended change:** a `{{def:}}` MAY appear anywhere in the body. There is no required,
single, or first-positioned Definitions section.

This is both **more flexible and simpler** — it removes three special-case structural rules and
two validation errors rather than adding any:

| Rule today | Proposed |
|---|---|
| All defs in one Definitions section (error) | Removed — defs may appear anywhere |
| Definitions section is first `#` heading (error) | Removed |
| Definitions section has no subheadings (error) | Removed — grouping allowed |

**Preserve the convention without mandating it.** A "Definitions" article at the top is still good
practice for stipulative terms, so:

- Keep it as a **RECOMMENDED** convention in the spec.
- Renderers SHOULD be able to **generate a glossary/index** from *all* `{{def:}}` declarations
  regardless of location (each entry links back to the clause where the term is defined).

The one thing we give up is "a reader can assume every definition is in one place." Glossary
generation with clause back-links recovers that for readers. (A strict "all defs in one section"
house-style linter is intentionally left out of the format — any team that wants it can add it as a
tooling rule, but the spec neither defines nor requires it.)

---

## 5. The ID question — name-based vs numbered

**Recommendation: keep author-chosen, name-based ids (`{{def: confidential-information}}`). Do not
move to numbered ids.**

Numbered ids (`{{def: 1}}`, or auto-assigned `def-1`, `def-2`) directly contradict LegalDown's
foundational design principle (§1.2): *"A LegalDown document contains no hardcoded section
numbers… sections can be freely added, removed, or reordered without any manual renumbering."*

| Dimension | Name-based id (current) | Numbered id |
|---|---|---|
| Reorder / insert a definition | References unaffected | Every later number shifts → references silently point to the wrong term |
| Source readability | `{{term: confidential-information}}` is self-explanatory | `{{term: 7}}` is meaningless |
| Git diffs | Meaningful, local | A renumber touches every reference |
| Consistency with rest of spec | Matches section ids, party `name`, attachment `id` (all kebab) | New, inconsistent convention |
| Bilingual / amendment matching (§14, §7.5) | Robust — matched by stable id across files | Fragile — numbers must line up across files |

Numbered ids reintroduce exactly the brittleness the whole format exists to remove. Name-based ids
are also what make Proposals A and B safe: because references bind to a stable id, a definition can
move (glossary ↔ inline) without touching a single `{{term:}}`.

**Addressing the real concern behind the question — the burden of inventing ids — this review
adopts id auto-derivation:**

1. **Auto-derive the id from the term (adopted).** The id MAY be omitted; when it is, derive it from
   the preceding quoted term with the existing §5.3 slug algorithm (`"Services" {{def:}}` →
   `services`). Explicit ids remain RECOMMENDED for stability (so a later wording change to the term
   doesn't change the id) and are REQUIRED to disambiguate when two different terms would slug to the
   same id.
2. **Editor/tooling support** can suggest ids and flag collisions — a tooling concern, not a spec
   change.

> Note on staleness: an id is an *anchor*, not the display text. If the term's wording later
> changes (`confidential-information` while the term becomes "Proprietary Information"), the id may
> read stale but nothing breaks — the same trade-off section identifiers already make.

---

## 6. Knock-on changes to validation

Most validation survives unchanged; a few rules relax or move. Intended end state:

**Removed (structural constraints that no longer exist):**
- "Definitions section is the first level‑1 heading" (§15.2) — removed.
- "Definitions section contains no subheadings" (§15.2) — removed.
- "All `{{def:}}` declarations appear in the Definitions section" (§15.4) — removed.

**Kept (still meaningful):**
- All `{{def: id}}` ids are unique — **Error**.
- All `{{term: id}}` resolve to a declared definition — **Error**.
- Declared but never referenced with `{{term:}}` — **Warning**.

**New / adjusted:**
- `{{def:}}` not immediately preceded by a recognized quoted span — **Error** (the term cannot be
  determined). This replaces the old `**"Term"**`-formatting warning (quotes are now the sole
  delimiter).
- Id omitted → auto-derived from the quoted term (§5). Two definitions auto-deriving to the same id —
  **Error** (add an explicit id to disambiguate).
- Emphasis markers (`**`, `__`) wrapping a defined term in source — **Warning/Info** (discouraged;
  defined-term styling is render-time, §13.7).
- Single-quote-delimited term while single quotes are not in the active set, or an ambiguous
  apostrophe match — **Warning** (recommend double quotes).
- **Circular-definition check (§15.3)** — scope it to the containing **paragraph** (deterministic):
  if def A's paragraph references `{{term: B}}` and B's paragraph references `{{term: A}}`, flag it.
  Alternatively downgrade to **Warning**, since with scattered inline defs "circular" is softer.
- "Definition used before declaration" (§15.3) — **downgrade to Info, or drop.** With first-use
  inline definitions, using a term where it is introduced is normal.
- Optional strict house-style lint: "definitions not collected in a Definitions section" —
  **Info / off by default.**

---

## 7. Interactions to confirm

- **Amendments (§7.5).** Unaffected in principle — definition import/override is matched by **id**,
  not position, so anywhere-placed defs import and override exactly as today. Inline defs make
  "add a clause that introduces a term" cleaner.
- **Bilingual (§14, §15.7).** "Definition ids match between translations" still works — it is
  id-based. Each language file uses its own language's quotation marks (the accepted-delimiter set
  in §3 makes that explicit); structural-sync checks remain id-driven, not text-driven.
- **Attachments (§12.4).** Attachment files already reference parent definitions via `{{term:}}`.
  Definitions may now also be **introduced inside attachment files** — a `{{def:}}` in an attachment
  registers a document-wide term like any other (ids stay unique across the combined document, per
  §15.10).
- **Glossary generation.** New, recommended renderer capability: collect all `{{def:}}` into an
  optional generated glossary, each entry linking back to the clause where the term is defined
  (optionally previewing the containing paragraph). This preserves "find every defined term in one
  place" once the mandatory section is gone.

---

## 8. Deliberately out of scope (to keep the schema simple)

Considered during review, **not** recommended now:

- **Section-local / scoped definitions** (a term meaning one thing only within an article). Keep all
  definitions document-global; scoping complicates resolution for little benefit.
- **Paired/enclosing definition syntax** (`{{def: id}}Services{{/def}}`). The term-precedes-tag rule
  achieves the same with a single directive and no parameters; a closing-tag form is unnecessary.
- **Sentence-level body extraction.** Deterministic units are paragraph and section; sentence
  segmentation in legal/multilingual text is too fragile to be normative (see §3).
- **Emphasis markup in source for terms.** Presentation is render-time; the source uses quotes only.
- **Definition "kinds"/typing** (means vs includes vs has-the-meaning-given-in). Expressible in body
  text already; no schema support needed.

---

## 9. Summary of recommendations

| # | Recommendation | Effect on schema |
|---|---|---|
| A | **One syntax:** term in quotes, then `{{def: id}}`; term taken from the preceding quoted span (delimiter set in §3) | Net **simpler** — removes block/inline split, no new parameters |
| B | **Remove** the single/first/no-subheading Definitions-section constraints; make the section a recommended convention | Net **simpler** (−3 rules) |
| C | **Keep name-based ids**; reject numbered ids | No change |
| D | **Auto-derive ids** from the quoted term when omitted (explicit ids still recommended) | +1 optional behavior |
| E | Add **glossary generation** with clause back-links (no strict-section linter in the format) | Renderer, not format |

**Headline:** support the way lawyers actually define terms (in quotes, at first use) by *removing*
structural constraints rather than adding syntax, keeping the source format-agnostic (no emphasis
markup), and keeping the stable, name-based id system that makes everything else in LegalDown
reorder-safe.

---

## 10. Resolved decisions

All open questions from the prior draft are now settled:

1. **Strict-section lint** — **dropped.** The format does not define or require a "collect all defs
   in one section" linter; house-style enforcement is left entirely to third-party tooling.
   ("Strict section lint" earlier meant an optional validator rule that flagged definitions placed
   outside a single front Definitions section — a way to keep the old discipline by choice. We are
   not building it into the spec.)
2. **Styling** — **renderer concern only.** The spec does not prescribe how a defining occurrence or
   a reference looks (bold, underline, quotes, small-caps). Source carries quotes only.
3. **Auto-derived ids** — **adopted.** Id MAY be omitted and is slugged from the quoted term;
   explicit ids recommended for stability and required to disambiguate slug collisions.
4. **Attachments introducing definitions** — **allowed.** A `{{def:}}` inside an attachment file
   registers a document-wide term.
5. **Delimiters** — **all pairs in §3 accepted by default** (double and single forms); double quotes
   recommended, single-quote ambiguity warned.

With these settled, the design is ready to be written into the spec, the LLM reference, and the
README. The remaining work is editing, not deciding.
