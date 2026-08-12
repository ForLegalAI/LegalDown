# LegalDown v0.1 — Release Readiness & Consistency Review

**Status:** Living review, updated after implementation round 1. Originally issued 2026-08-12
against commit `d05a8b8`; round 1 (same day) resolved **all release-blocking and major gaps
(G1–G11)** — see Part 0 for what was implemented. Remaining open work: the consistency cleanup pass
(I-items), practical improvements (P-items), minor editorial items (E-items), and the deferred
ecosystem work (G12).

**Scope:** [`spec/legaldown-spec.md`](spec/legaldown-spec.md), [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md),
[`README.md`](README.md), [`CHANGELOG.md`](CHANGELOG.md), [`LICENSE`](LICENSE). Detailed change
records for every resolved item are in [`CHANGELOG.md`](CHANGELOG.md) under *Unreleased*.

---

## Issue Index

| ID | Status | Issue |
|---|---|---|
| G1 | ✅ Resolved | Conformance levels referenced but never defined |
| G2 | ✅ Resolved | No formal directive grammar; no escaping mechanism |
| G3 | ✅ Resolved | Identifier namespace model ambiguous |
| G4 | ✅ Resolved | Auto-identifier transliteration non-deterministic |
| G5 | ✅ Removed | "Structured output formats" invoked by MUSTs but never defined |
| G6 | ✅ Resolved | Missing frontmatter validation rules |
| G7 | ✅ Resolved | No validation table for `{{include:}}` |
| G8 | ✅ Resolved | Include semantics underspecified |
| G9 | ✅ Resolved | No anchors below heading level |
| G10 | ✅ Descoped | Signature block generation invoked but unspecified |
| G11 | ✅ Resolved | No spec-version declaration in documents |
| G12 | ⏸ Deferred | Ecosystem: examples dir, CONTRIBUTING.md, test corpus |
| I1 | ⬜ Open | Ghost feature: `{{lang:}}` language blocks |
| I2 | ⬜ Open | Numbering scheme "specifiable in document metadata" — field doesn't exist |
| I3 | ⬜ Open | §15.6 minimum-sides rules contradict `sides: RECOMMENDED`; severities unstated |
| I4 | ⬜ Open | §14.3 embeds a CLI, conflicts with §15.7 severities, has an orphan check |
| I5 | ⬜ Open | Bilingual id-matching incompatible with auto-generated ids |
| I6 | ⬜ Open | §13.2 enumeration table columns identical; MAY/SHOULD conflict |
| I7 | ⬜ Open | Attachment "numbering position" contradicts verbatim titles |
| I8 | ⬜ Open | `{{ref:}}` undefined under "None" scheme and across attachment restarts |
| I9 | ⬜ Open | Unknown directives pass through into rendered legal text |
| I10 | ⬜ Open | Body text before the first heading never specified |
| I11 | ⬜ Open | README / LLM-reference drift (remaining items) |
| I12 | ⬜ Open | LICENSE points to wrong repository URL |
| P1 | ⬜ Open | No way to reference a side collectively |
| P2 | ⬜ Open | `{{attach:}}` lacks a `label` override |
| P3 | ⬜ Open | Duration units: no weeks; `M`/`MO` footgun |
| P4 | ⬜ Open | Amendments cannot reference the original's sections stably |
| P5 | ⬜ Open | Circular-definition Error will false-positive |
| P6 | ⬜ Open | "Sections with no references" Info check is noise |
| P7 | ⬜ Open | Money: sign and precision unspecified |
| P8 | ⬜ Open | Quoted-span matching: determinism invariant unstated |
| P9 | ⬜ Open | No path-safety rule for file references |
| P10 | ⬜ Open | Raw HTML, links, and images policy absent |
| P11 | ⬜ Open | "Section"/"Article" label words couple content to numbering scheme |
| P12 | ⬜ Open | Frontmatter/body value duplication (no `{{meta:}}`) |
| P13 | ⬜ Open | `{{party: board-of-directors}}` example doesn't fit the type model |
| E1 | ✅ Resolved | §5.3 truncation/trim ordering (fixed with G4) |
| E2–E10, E12, E13 | ⬜ Open | Minor editorial items (see Part 3) |
| E11 | ✅ Resolved | Missing `---` before Complete Examples (fixed with G1) |

---

## Part 0 — Resolved in Round 1

Short implementation notes; full details per item in [`CHANGELOG.md`](CHANGELOG.md).

### G1 ✅ Conformance levels — new spec §16

Three cumulative levels: **Core** (parse + validate a single document — everything determinable
from the file alone, including the single-file rows of §15.8/§15.10/§15.11), **Rendering** (Core +
§13, at least one of PDF/DOCX/HTML), **Full** (Rendering + all multi-file processing: includes,
attachment content, amendment import, bilingual). Levels bind implementations only; a claimed level
is a floor, not a ceiling. §16.5 forbids silent degradation: validators must warn about checks they
did not run; renderers must refuse or emit a visible `[NOT PROCESSED: ...]` marker. Complete
Examples renumbered §16 → §17 (fixing §1.5's dangling pointer); §11.1's ambiguous Status column
replaced by a conformance **Level** column.

### G2 ✅ Directive grammar and quoted values — new spec §11.2–§11.4

§11 restructured around a formal EBNF grammar: at most one positional value (first), named
parameters order-insensitive, duplicate parameter = Error, unknown parameter = Warning + ignored.
**Quoted values**: any value may be wrapped in straight double quotes to carry commas or `}}`
(`label="Smith, Jones & Co."`, `{{field: "Smith, Jones & Co. v. Doe", type=case-name}}`); `\"` and
`\\` escapes; typographic quotes never delimit (Warning on auto-curled quotes). Recognition
contexts defined: directives are inert in code spans, code blocks, and HTML comments; literal `{{`
via the inherited CommonMark backslash escape; "well-formed" defined by opener commitment. The old
absolute comma/`}}` bans in §7.3/§10.1/§10.4/§10.6 are rescoped to the unquoted form. Backward
compatible.

### G3 ✅ Identifier namespaces — new spec §5.6

One identifier format, separate namespaces, each directive resolves only against its own: **anchor**
(section ids + item/paragraph anchors + attachment ids; shared uniqueness), **definitions** (unique
among definitions only — a def id may equal a section id, explicitly benign), **placeholders**
(repeats = same blank), frontmatter names (sides/parties/field types). `{{ref:}}` targeting an
attachment id is an Error with a suggest-`{{attach:}}` diagnostic. Renderers must disambiguate
emitted anchors (e.g., `def-services`).

### G4 ✅ Deterministic identifier generation — spec §5.3 rewritten

Fully pinned pipeline: NFKD + combining-mark stripping → exhaustive 10-entry transliteration table
(`ß`→`ss`, `æ`→`ae`, `ø`→`o`, `þ`→`th`, …) → remove remaining non-ASCII (**no romanization** of
Cyrillic/Greek/CJK — removal + Warning recommending an explicit id) → mechanical slug steps.
Identical output across implementations is now a MUST. Fixed two latent bugs (missing
hyphen-collapse step; trim-before-truncate) and specified §5.5 suffix behavior (document order,
after the algorithm, exempt from the 64-char cap). Also resolved **E1**.

### G5 ✅ Resolved by removal

The six "raw value MUST be preserved in structured output formats" clauses (§10.2–§10.7) are
deleted. §10.1 now states the position explicitly: the source file is the canonical
machine-readable representation; LegalDown defines no export or interchange format. §15.9 validator
diagnostics (a different, self-defined use) unaffected.

### G6 ✅ Frontmatter validation completeness — §3.2, §15.6

Optionality model clarified: frontmatter optional as a block but recommended; field statuses apply
when present; no frontmatter → Warning. New §15.6 general checks: YAML parses (Error), `title`
non-empty (Error), `effective_date`/`adoption_date`/`date_of_birth` valid ISO 8601 (Error),
language codes valid ISO 639-1 (Warning), `authoritative` among the document's languages (Warning),
representative `name` non-empty (Error), attachment `title` non-empty (Error, §15.10). Placeholder
values satisfy presence and are exempt from format checks (§3.10 interplay made explicit).

### G7 ✅ Include validation — new spec §15.11

Seven Error rows: target exists, target is a LegalDown file, circular chain, fragment contains
frontmatter, fragment contains `#`, combined-document id uniqueness, combined-document hierarchy.
The extension check is string-only and applies at Core; the rest at Full.

### G8 ✅ Include semantics — §12.2 unified with attachment files

Include targets are now **body-only fragments** (no frontmatter, no `#`, LegalDown extensions only)
— the same file model as attachment files; the old "valid standalone document with ignored
frontmatter" rule is gone. Splicing is verbatim with no heading re-basing (combined document must
satisfy §4.1); `{{def:}}` in fragments registers document-wide; nesting allowed with cycle
detection across the chain. Minor breaking change: frontmatter in an include target is now an
Error (it was ignored before).

### G9 ✅ Item and paragraph anchors — new spec §5.7

`{#id}` now attaches to list items (end of first paragraph, any depth outside quotes/tables) and
top-level paragraphs — explicit only, never auto-generated, same anchor namespace, targeted with
plain `{{ref:}}`. Refs render the containing section number + rendered designation ("3.1(a)",
"3.1(b)(ii)", "5.2"), reorder-safe; if the template doesn't enumerate the target's list/paragraphs,
refs fall back to the section number with a Warning. §13.2/§13.7 gained continental options:
section-qualified decimal items and per-section paragraph numbering (off by default) — untitled
numbered provisions (čl. 5 odst. 2) without fake headings.

### G10 ✅ Signature blocks — explicitly implementation-defined

Decision: not specified in v0.1. §2.2 now says generation and layout are implementation-defined
(frontmatter-driven generation stays a SHOULD with per-document-type sources); §3.6's `legal_name`
MUST is conditional on an implementation actually generating blocks; §13.7 lists "Signature block
layout" as a template setting. A structured signature model remains a candidate for a future
revision.

### G11 ✅ Spec-version field — `legaldown` in §3.2

Optional `legaldown: "0.1"` (quoted — YAML would read `0.1` as a number). Newer-than-supported
declared version → Warning; unknown version MUST NOT be a hard failure; absence = process under the
implementation's version. No placeholders allowed in it (structural field).

### G12 ⏸ Deferred (by decision, until all spec changes are final)

`examples/` with the §17 documents as real files (including attachment files), CONTRIBUTING.md
(linked from README but missing), and a validation fixtures corpus keyed to §15 rules. Also covers
the README "Examples" link currently pointing at `llm/`.

---

## Part 1 — Open: Inconsistencies and Contradictions

### I1. Ghost feature: `{{lang:}}` language blocks 🟠

§1.3 lists "Language block directives for bilingual documents" as an extension; the README's
structure-at-a-glance shows `{{lang: fr}} ... {{/lang}}`. But §14 supports **separate files only**,
§11.1 has no `{{lang:}}`, and no closing-tag grammar exists anywhere.

**Fix:** The separate-file design won — delete the §1.3 bullet and the README line.

### I2. Numbering scheme "SHOULD be specifiable in document metadata" — no such field 🟡

§13.1 says the numbering scheme "SHOULD be specifiable in document metadata or renderer
configuration file", but no such metadata field exists — the same dangling-reference class the
2026-06-17 cleanup removed for locale/currency. Numbering is presentation and §13.7 already lists
it as a template setting.

**Fix:** Strike "document metadata or" from §13.1. One line.

### I3. §15.6 contradicts `sides: RECOMMENDED`; severities unstated 🟠

The §15.6 document-type table requires ≥2 sides/parties for a `contract` (and an `issuer` side for
the other types), but `sides` is only RECOMMENDED and the table's first three rows carry no
severity. Is a contract with no `sides` block an Error, a Warning, or fine?

**Fix:** State severities: when `sides` is present, the minimums are Error; when absent entirely,
one Warning ("document_type constraints cannot be verified without `sides`"). Keeps `sides`
genuinely RECOMMENDED while making the table enforceable.

### I4. §14.3 embeds a CLI and conflicts with §15.7 🟡

(a) A format spec should not mandate a specific executable and flag (*"the `legaldown validate
--sync` command MUST check"*); (b) §14.3 says the checker "warns on structural differences" while
§15.7 classifies hierarchy/id mismatches as Errors; (c) §14.3's "both files declare the same
languages" check is missing from §15.7's table.

**Fix:** Rewrite §14.3 tool-neutrally, align severity (Error), add the language-consistency row to
§15.7.

### I5. Bilingual id-matching incompatible with auto-generated ids 🟠

§14.2 requires identical section identifiers across translation files and §15.7 requires matching
definition ids — but auto-generated ids are slugged from language-specific text, so mismatch is
guaranteed unless every heading and `{{def:}}` carries an explicit id. The spec never tells
bilingual authors this. (G4's non-transliterable-characters Warning helps for non-Latin scripts but
does not cover, e.g., English↔French Latin-script drift.)

**Fix:** In §14.2: documents declaring `translations` SHOULD use explicit identifiers on all
headings and defs; validators SHOULD warn on any auto-generated id in such documents.

### I6. §13.2 enumeration table is content-free; MAY/SHOULD conflict 🟡

The three style columns (Decimal/Outline/Mixed) are **identical in every row** — the table
differentiates nothing. §8.2 says renderers MAY convert unordered lists; §13.2 says SHOULD. Ordered
lists' treatment is still unspecified (renumbered? converted? passed through?).

**Fix:** Collapse the table to one column or differentiate the styles; align on SHOULD; add an
explicit ordered-list rule (recommend: renumber sequentially, MAY apply the enumeration scheme).

### I7. Attachment "numbering position" contradicts verbatim titles 🟡

§3.9 insists the renderer generates no labels (titles are author-written verbatim), yet §3.9/§12.4/
§13.8 speak of attachments "keeping numbering position" and "numbering correctly" — there is no
generated attachment numbering to keep correct; order is the only positional effect. Deeper
tension: author titles hardcode "Schedule **A**/**B**", so reordering attachments means renaming
them — the manual-renumbering problem §1.2 exists to eliminate.

**Fix:** Reword the clauses to speak of *order* only; consider optional template-generated
attachment labels later.

### I8. `{{ref:}}` undefined under "None" numbering and across attachment restarts 🟡

§13.3 substitutes "the section number", which does not exist under §13.1's **None** scheme. And
refs into attachment sections (allowed by §12.4) are ambiguous when per-attachment numbering
restarts (§13.8) — "Section 2" could be main-body 2 or Schedule A's 2.

**Fix:** Under None, render the target's heading text (hyperlinked). For refs crossing the
attachment boundary under restarted numbering, render a qualified form ("Schedule A: …, Section 2")
or require continuous numbering when such refs exist.

### I9. Unknown directives pass through into rendered legal text 🟡

§11.5: unknown directives "SHOULD generate a warning and be passed through to output as-is" — so a
typo like `{{trem: services}}` prints literally into an executed contract. Inconsistent with every
other failure mode (`[BROKEN REF: …]`, `[UNDEFINED: …]`). §15.2 also has no row for it.

**Fix:** Render `[UNKNOWN DIRECTIVE: name]` + Error; add the §15.2 row; reserve pass-through for an
explicit permissive/compatibility mode.

### I10. Body text before the first heading never specified 🟡

Every §17 example opens with paragraph text before the first `#` heading; §4 never mentions
pre-heading content (§5.7 now implicitly acknowledges it by excluding it from paragraph anchors).
Is it valid? Numbered? Can it hold definitions (the examples do)?

**Fix:** Bless it in §4: content before the first heading is an unnumbered preamble; directives are
valid there; renderers place it before the first numbered provision.

### I11. README / LLM-reference drift (remaining) 🟡

| Location | Issue |
|---|---|
| README top navigation | "[Examples](llm)" links to the LLM reference, not examples (resolves with G12) |
| README structure-at-a-glance | `{{lang: fr}} ... {{/lang}}` ghost feature (see I1) |
| README "up to 5 levels" | Spec never states a maximum heading depth (see E6) |
| README Contributing | Links CONTRIBUTING.md, which doesn't exist (resolves with G12) |
| README File Format | Omits `.legal.md`, which the spec allows (§2.1) |
| LLM ref validation summary | Missing: circular definitions (Error, §15.3) and orphaned-sections Info |

**Fix:** One sync pass once I1/E6 land; G12 covers the rest.

### I12. LICENSE points to the wrong repository 🟢

LICENSE gives `https://github.com/legaldown/spec`; the actual remote is
`https://github.com/ForLegalAI/LegalDown`. Attribution instructions pointing at a nonexistent repo
undermine the CC BY attribution requirement.

**Fix:** Update the URL (or claim/redirect the vanity org).

---

## Part 2 — Open: Practical Issues

### P1. No way to reference a side collectively 🟠

`{{party:}}` resolves individual parties; nothing resolves a *side*. The spec's own example (Beta +
Gamma under `clients`) can't say "the Clients" in a validated way.

**Fix:** `{{side: side-name}}` / `{{side: …, label=…}}` mirroring §10.4 (resolve `sides[].name`,
display `label` with §3.6 fallback, `[UNKNOWN SIDE: …]` on failure).

### P2. `{{attach:}}` lacks a `label` override 🟡

`{{attach: schedule-b}}` always renders the full verbatim title mid-sentence ("…as set out in
Schedule B: Pricing."). `{{term:}}` and `{{party:}}` have `label=` for exactly this.

**Fix:** Add optional `label=` with the §11.3 value rules.

### P3. Duration units: no weeks; `M`/`MO` footgun 🟡

No `W` — "two weeks' notice" must be written as 14 days. `M` means *minutes* while ISO 8601 uses
`M` for months — `{{duration: 3, unit=M}}` intending months silently produces "3 minutes".

**Fix:** Add `W`; consider renaming minutes to `MIN` (or dropping `S`/`M` at v0.1); at minimum add
a spec note flagging the trap.

### P4. Amendments cannot reference the original's sections stably 🟠

The §17.4 example hardcodes "Section 5.1 of the Agreement" — a render-time artifact of the
original's configurable numbering scheme. §7.5 imports the original's definitions but not its
section identifiers.

**Fix:** Import section ids too, with a qualified syntax (e.g., `{{ref: payment-terms,
doc=amends}}`) rendered per the original's numbering — or add guidance to cite the executed
rendering and pin the original's scheme.

### P5. Circular-definition Error will false-positive 🟡

§15.3 makes paragraph-scoped circular definitions an Error, but mutual `{{term:}}` mentions between
definition paragraphs are routine legitimate drafting, and a single paragraph declaring two
interlinked terms trips the check by construction. `definitions-review.md` §6 itself floated
Warning.

**Fix:** Downgrade to Warning.

### P6. "Sections with no references" Info check is noise 🟢

§15.3 flags sections nobody cross-references — i.e., most sections of any normal contract. Trains
users to ignore Info output.

**Fix:** Drop the row (unreferenced *attachments* stay covered by §15.10, where it's meaningful).

### P7. Money: sign and precision unspecified 🟢

Is `{{money: -500}}` valid? (§10.5 bans non-positive durations; §10.3 is silent.) Does
`{{money: 10.5}}` render "10.50"?

**Fix:** Require amount ≥ 0 (negatives in prose); renderers preserve source precision, padding to
the currency's minor units only when the template says so.

### P8. Quoted-span matching: determinism invariant unstated 🟢

§7.2's back-scan matching is deterministic only because no character in the default set closes two
different pairs. The set is configurable — an extension can silently break the invariant (e.g., any
added pair closing with U+201C, which already closes `„…“` while opening `“…”`).

**Fix:** State the invariant as a constraint on configured sets; hint at mismatched-marks in the
no-quoted-span diagnostic.

### P9. No path-safety rule for file references 🟡

`{{include:}}`, `amends.file`, `attachments[].file`, and `translations` accept arbitrary relative
paths (`../../…`) with no boundary rule — a hosted validator/renderer needs a normative hook to
refuse escapes.

**Fix:** Paths MUST be relative and MUST resolve within a configurable document root; violations
are an Error.

### P10. Raw HTML, links, and images policy absent 🟡

As a CommonMark superset, LegalDown inherits raw HTML (only comments are addressed), autolinks,
links, and images — none addressed for print rendering or HTML-injection safety.

**Fix:** Add a *CommonMark Feature Handling* section: raw HTML other than comments ignored with a
Warning by default (§9.2 table exception may stand); links preserved as hyperlinks with a template
option for visible URLs in print; images explicitly supported or reserved.

### P11. "Section"/"Article" label words couple content to the numbering scheme 🟢

Authors write "Section {{ref: x}}"; switching the render scheme to outline makes "Section I.A" read
wrong where "Article I.A" is conventional. Not cheaply fixable — document the tension in §6;
possible future `{{ref: x, style=full}}` with a template-supplied label word.

### P12. Frontmatter/body value duplication 🟢

`effective_date` lives in frontmatter and again as `{{date: …}}` in the body — dual maintenance.
v0.2 candidate: a `{{meta: field-name}}` insertion directive.

### P13. `{{party: board-of-directors}}` example doesn't fit the type model 🟢

§10.4's example implies declaring a board as a party, but `type` must be
`legal_entity`/`natural_person` — an internal organ fits neither, and `adopted_by` (a plain string)
is unreferenceable.

**Fix:** Change the example; consider (v0.2) a structured `adopted_by` or an `organ`/`body` type.

---

## Part 3 — Open: Minor / Editorial

| ID | Location | Issue | Fix |
|---|---|---|---|
| E2 | §5.5, §7.2 | Auto-generated id colliding with an *explicit* id (section or def) is undefined (only auto-vs-auto is handled) | Explicit wins; auto id gets suffix + Warning |
| E3 | §3.6 | Side-name fallback "title-case **and pluralize**" is English-only — inconsistent with the language-agnostic rationale for attachment titles | Drop "pluralize"; recommend `label` |
| E4 | §3.2 | `supersedes` is a free string while `amends` is structured | Allow `{title, file}` object form |
| E5 | §14.2 | Heading reads "### 14.2 Separate File " — trailing space, truncated title; §14.1 sentence lacks a period | "Separate File Approach"; add period |
| E6 | §4.1 / README | Max heading depth unstated (README says 5; CommonMark permits 6) | State max (recommend 5, `######` = Error) |
| E7 | §3.2 | `field_types` reserved names cover only `date`/`money`/`duration`/`party`; `text` (a placeholder type) is not reserved and the list's rationale is unstated | State rationale; consider reserving `text` |
| E8 | §5.2 | `{#id}` "separated by a single space" — exactly one? | Allow one or more spaces/tabs, or state strictness deliberately |
| E9 | §1.3 | Setext headings (valid CommonMark) unmentioned — hierarchy/auto-id participation undefined | State: equivalent to ATX levels 1–2 (or forbidden) |
| E10 | §17.4 | Amendment example writes `(the "Agreement")` without `{{def:}}` now that inline defs are first-class | Use `{{def: agreement}}` or annotate the omission |
| E12 | repo root | `.idea/` untracked; no `.gitignore` | Add `.gitignore` |
| E13 | spec header | "Version 0.1 DRAFT" carries no revision date though CHANGELOG tracks dated revisions | Add a revision date line |

---

## Remaining Sequencing

1. **Cleanup pass (fast, few design decisions):** I1, I2, I4, I6–I12, E2–E13, P6, P13's example.
   Clears every remaining internal contradiction.
2. **Decision items:** I3 (sides severity model), I5 (bilingual explicit-ids rule), P1–P5, P7–P11
   — each is either a small normative addition or an explicit deferral; give deferred ones a line
   in a *Roadmap / Known Limitations* section so silence reads as a decision.
3. **G12 (after all changes final):** `examples/`, CONTRIBUTING.md, validation fixtures corpus —
   writing fixtures will also regression-test everything resolved in round 1.
4. Then tag v0.1.
