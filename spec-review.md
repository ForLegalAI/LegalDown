# LegalDown v0.1 — Release Readiness & Consistency Review

**Status:** Living review, updated after implementation rounds 1 and 2 (both 2026-08-12; originally
issued against commit `d05a8b8`). **Round 1** resolved all release-blocking and major gaps (G1–G11,
merged in PR #24). **Round 2** (branch `consistency-cleanup`) cleared the consistency cleanup tier:
I1–I2, I4, I6–I12, E1–E13, P6, and P13. What remains open: two decision items (I3, I5), the
practical-improvement tier (P1–P5, P7–P12), and the deferred ecosystem work (G12).

**Scope:** [`spec/legaldown-spec.md`](spec/legaldown-spec.md), [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md),
[`README.md`](README.md), [`CHANGELOG.md`](CHANGELOG.md), [`LICENSE`](LICENSE). Detailed change
records for every resolved item are in [`CHANGELOG.md`](CHANGELOG.md) under *Unreleased*.

---

## Issue Index

| ID | Status | Issue |
|---|---|---|
| G1–G4 | ✅ Round 1 | Conformance levels; directive grammar & quoting; identifier namespaces; deterministic auto-ids |
| G5 | ✅ Round 1 (removed) | Undefined "structured output formats" clauses |
| G6–G9 | ✅ Round 1 | Frontmatter validation; include validation; include semantics; item/paragraph anchors |
| G10 | ✅ Round 1 (descoped) | Signature blocks → implementation-defined |
| G11 | ✅ Round 1 | `legaldown` spec-version field |
| G12 | ⏸ Deferred | Ecosystem: examples dir, CONTRIBUTING.md, test corpus |
| I1 | ✅ Round 2 | Ghost `{{lang:}}` blocks removed from §1.3 and README |
| I2 | ✅ Round 2 | Numbering scheme: dangling "document metadata" clause struck (§13.1) |
| I3 | ⬜ Open | §15.6 minimum-sides rules vs `sides: RECOMMENDED`; severities unstated |
| I4 | ✅ Round 2 | §14 rewritten tool-neutrally; severities aligned; language-set row added to §15.7 |
| I5 | ⬜ Open | Bilingual id-matching incompatible with auto-generated ids |
| I6 | ✅ Round 2 | §13.2 table collapsed; ordered-list rule added; §8.2 aligned to SHOULD |
| I7 | ✅ Round 2 | Attachment wording now order-only (§3.9, §12.4, §13.8) |
| I8 | ✅ Round 2 | `{{ref:}}` defined under "None" scheme and across attachment restarts (§13.3) |
| I9 | ✅ Round 2 | Unknown directives → Error + `[UNKNOWN DIRECTIVE: name]` marker (§11.5) |
| I10 | ✅ Round 2 | Preamble blessed (new §4.4) |
| I11 | ✅ Round 2 | README/LLM drift cleared (G12-gated rows excepted) |
| I12 | ✅ Round 2 | LICENSE URLs corrected to ForLegalAI/LegalDown |
| P1 | ⬜ Open | No way to reference a side collectively |
| P2 | ⬜ Open | `{{attach:}}` lacks a `label` override |
| P3 | ⬜ Open | Duration units: no weeks; `M`/`MO` footgun |
| P4 | ⬜ Open | Amendments cannot reference the original's sections stably |
| P5 | ⬜ Open | Circular-definition Error will false-positive |
| P6 | ✅ Round 2 | Orphaned-sections Info row removed from §15.3 |
| P7 | ⬜ Open | Money: sign and precision unspecified |
| P8 | ⬜ Open | Quoted-span matching: determinism invariant unstated |
| P9 | ⬜ Open | No path-safety rule for file references |
| P10 | ⬜ Open | Raw HTML, links, and images policy absent |
| P11 | ⬜ Open | "Section"/"Article" label words couple content to numbering scheme |
| P12 | ⬜ Open | Frontmatter/body value duplication (no `{{meta:}}`) |
| P13 | ✅ Round 2 (example) | §10.4 board example replaced; organ/`adopted_by` modeling deferred to roadmap |
| E1–E13 | ✅ Rounds 1–2 | All editorial items (E1/E11 in round 1; E2–E10, E12, E13 in round 2) |

---

## Part 0 — Resolved

Short implementation notes; full details per item in [`CHANGELOG.md`](CHANGELOG.md).

### Round 1 (PR #24) — the normative gaps

- **G1 Conformance levels (new §16):** Core / Rendering / Full, cumulative; levels bind
  implementations only and are a floor, not a ceiling; §16.5 forbids silent degradation
  (`[NOT PROCESSED: ...]`). Examples renumbered §16 → §17; §11.1 Status column → Level column.
- **G2 Directive grammar (new §11.2–§11.4):** EBNF; one positional value first; order-insensitive
  named parameters (duplicate = Error, unknown = Warning); quoted values carry commas/`}}`
  (`label="Smith, Jones & Co."`) with `\"`/`\\` escapes; directives inert in code and comments;
  literal `{{` via CommonMark backslash escape; "well-formed" defined by opener commitment.
- **G3 Identifier namespaces (new §5.6):** anchor (sections + item/paragraph anchors + attachment
  ids) / definitions / placeholders / frontmatter names; def id may equal section id (benign);
  `{{ref:}}` to an attachment id is an Error; renderers disambiguate emitted anchors.
- **G4 Deterministic auto-ids (§5.3):** NFKD + exhaustive transliteration table; no romanization
  (removed letters/digits draw a Warning recommending explicit ids); latent slug bugs fixed;
  prefix/suffix cap exemptions stated.
- **G5 resolved by removal:** source file is the canonical machine-readable representation;
  LegalDown defines no export format (§10.1).
- **G6 Frontmatter validation (§3.2, §15.6):** optionality model; YAML-parse/title/ISO-date/
  language-code checks; placeholder format-check exemption.
- **G7/G8 Includes:** §12.2 unified on the body-only fragment model (no frontmatter, no `#`,
  verbatim splice, document-wide defs, nested with cycle detection); new §15.11 validation table.
- **G9 Item and paragraph anchors (new §5.7):** `{#id}` below headings, explicit-only, rendered
  "3.1(a)" / "5.2" via plain `{{ref:}}`; continental numbered-paragraph template options.
- **G10 descoped:** signature block generation is implementation-defined (§2.2); `legal_name` MUST
  is conditional; §13.7 lists the layout setting.
- **G11:** optional `legaldown: "0.1"` field; newer-version Warning; never a hard failure.
- Plus 12 post-review fixes from PR #24's two review passes (grammar determinism, level scoping,
  anchor-namespace consistency).

### Round 2 (`consistency-cleanup`) — the contradiction sweep

- **I1:** `{{lang:}}` ghost feature deleted from §1.3 and the README — bilingual is separate-files
  only, as §14 designed.
- **I2:** §13.1 numbering scheme lives in the style template / renderer config; "document metadata"
  clause struck.
- **I4:** §14.3 rewritten tool-neutrally (no CLI mandate); "warns" vs Error conflict resolved in
  favor of Error; language-set consistency became a §15.7 row.
- **I6:** §13.2's content-free three-column table collapsed to one default sequence; templates may
  define their own; ordered lists renumbered at render time (source numbers never authoritative);
  §8.2 aligned MAY → SHOULD.
- **I7:** attachment "numbering position" wording now speaks of order only.
- **I8:** `{{ref:}}` under the "None" scheme renders heading text; refs across attachment numbering
  restarts are qualified with the attachment title.
- **I9:** unknown directives are an Error rendering `[UNKNOWN DIRECTIVE: name]` — typos never leak
  verbatim into an executed document; pass-through survives only as explicit permissive mode.
- **I10:** new §4.4 blesses the preamble (valid, unnumbered, all directives, no anchors).
- **I11:** README mentions `.legal.md`; LLM ref gained circular-definitions/depth/unknown-directive
  rows and lost the pluralize claim. Remaining rows (Examples link, CONTRIBUTING) resolve with G12.
- **I12:** LICENSE attribution URLs → `ForLegalAI/LegalDown`.
- **P6:** orphaned-sections Info row removed (it flagged most of any normal contract).
- **P13 (example):** §10.4 no longer declares a board as a party; §17.4 now demonstrates inline
  `{{def: agreement}}` + `{{term:}}` (also E10).
- **E2–E13:** auto-vs-explicit id collisions resolved (explicit wins, suffix + Warning); side
  fallback no longer pluralizes; `supersedes` may be a `{title, file}` object; §14.2 heading fixed;
  max heading depth 5 + setext headings specified; `text` reserved in `field_types`; anchor
  separator is "one or more spaces or tabs"; revision date in the spec header; `.gitignore` added.
- **Behavior changes to note:** unknown directives Warning → Error; `field_types` key `text` now
  reserved (minor breaking).

---

## Part 1 — Open: Decision Items

### I3. §15.6 contradicts `sides: RECOMMENDED`; severities unstated 🟠

The §15.6 document-type table requires ≥2 sides/parties for a `contract` (and an `issuer` side for
the other types), but `sides` is only RECOMMENDED in §3.2 and the table's first three rows carry no
severity. Is a contract with no `sides` block an Error, a Warning, or fine?

**Proposed fix:** when `sides` is present, the minimums are Error; when absent entirely, one
Warning ("document_type constraints cannot be verified without `sides`"). Keeps `sides` genuinely
RECOMMENDED while making the table enforceable.

### I5. Bilingual id-matching incompatible with auto-generated ids 🟠

§14.2 requires identical section identifiers across translation files and §15.7 requires matching
definition ids — but auto-generated ids are slugged from language-specific text, so mismatch is
guaranteed unless every heading and `{{def:}}` carries an explicit id. The spec never tells
bilingual authors this. (G4's warning covers non-Latin scripts but not, e.g., English↔French
Latin-script drift.)

**Proposed fix:** in §14.2, documents declaring `translations` SHOULD use explicit identifiers on
all headings and defs; validators SHOULD warn on any auto-generated id in such documents.

---

## Part 2 — Open: Practical Improvements

### P1. No way to reference a side collectively 🟠

`{{party:}}` resolves individual parties; nothing resolves a *side*. The spec's own example (Beta +
Gamma under `clients`) can't say "the Clients" in a validated way.

**Proposed fix:** `{{side: side-name}}` / `{{side: …, label=…}}` mirroring §10.4 (resolve
`sides[].name`, display `label` with §3.6 fallback, `[UNKNOWN SIDE: …]` on failure).

### P2. `{{attach:}}` lacks a `label` override 🟡

`{{attach: schedule-b}}` always renders the full verbatim title mid-sentence ("…as set out in
Schedule B: Pricing."). `{{term:}}` and `{{party:}}` have `label=` for exactly this.

**Proposed fix:** optional `label=` with the §11.3 value rules.

### P3. Duration units: no weeks; `M`/`MO` footgun 🟡

No `W` — "two weeks' notice" must be written as 14 days. `M` means *minutes* while ISO 8601 uses
`M` for months — `{{duration: 3, unit=M}}` intending months silently produces "3 minutes".

**Proposed fix:** add `W`; consider renaming minutes to `MIN` (or dropping `S`/`M` at v0.1); at
minimum a spec note flagging the trap.

### P4. Amendments cannot reference the original's sections stably 🟠

The §17.4 example hardcodes "Section 5.1 of the Agreement" — a render-time artifact of the
original's configurable numbering scheme. §7.5 imports the original's definitions but not its
section identifiers.

**Proposed fix:** import section ids too, with a qualified syntax (e.g., `{{ref: payment-terms,
doc=amends}}`) rendered per the original's numbering — or add guidance to cite the executed
rendering and pin the original's scheme.

### P5. Circular-definition Error will false-positive 🟡

§15.3 makes paragraph-scoped circular definitions an Error, but mutual `{{term:}}` mentions between
definition paragraphs are routine legitimate drafting, and a single paragraph declaring two
interlinked terms trips the check by construction. `definitions-review.md` §6 itself floated
Warning.

**Proposed fix:** downgrade to Warning.

### P7. Money: sign and precision unspecified 🟢

Is `{{money: -500}}` valid? (§10.5 bans non-positive durations; §10.3 is silent.) Does
`{{money: 10.5}}` render "10.50"?

**Proposed fix:** require amount ≥ 0 (negatives in prose); renderers preserve source precision,
padding to the currency's minor units only when the template says so.

### P8. Quoted-span matching: determinism invariant unstated 🟢

§7.2's back-scan matching is deterministic only because no character in the default set closes two
different pairs. The set is configurable — an extension can silently break the invariant.

**Proposed fix:** state the invariant as a constraint on configured sets; hint at mismatched marks
in the no-quoted-span diagnostic.

### P9. No path-safety rule for file references 🟡

`{{include:}}`, `amends.file`, `attachments[].file`, and `translations` accept arbitrary relative
paths (`../../…`) with no boundary rule — a hosted validator/renderer needs a normative hook to
refuse escapes.

**Proposed fix:** paths MUST be relative and MUST resolve within a configurable document root;
violations are an Error.

### P10. Raw HTML, links, and images policy absent 🟡

As a CommonMark superset, LegalDown inherits raw HTML (only comments are addressed), autolinks,
links, and images — none addressed for print rendering or HTML-injection safety.

**Proposed fix:** a *CommonMark Feature Handling* section: raw HTML other than comments ignored
with a Warning by default (§9.2 table exception may stand); links preserved as hyperlinks with a
template option for visible URLs in print; images explicitly supported or reserved.

### P11. "Section"/"Article" label words couple content to the numbering scheme 🟢

Authors write "Section {{ref: x}}"; switching the render scheme to outline makes "Section I.A" read
wrong where "Article I.A" is conventional. Document the tension in §6; possible future
`{{ref: x, style=full}}` with a template-supplied label word.

### P12. Frontmatter/body value duplication 🟢

`effective_date` lives in frontmatter and again as `{{date: …}}` in the body — dual maintenance.
v0.2 candidate: a `{{meta: field-name}}` insertion directive.

### Deferred design questions (roadmap candidates)

- Structured `adopted_by` / an organ-type party for collective acts (rest of P13)
- Template-generated attachment labels, so titles need not hardcode "Schedule A/B" (noted under I7)
- A structured signature model (from G10's descope)

---

## Part 3 — Deferred: G12 (after all spec changes are final)

- `examples/` directory containing the §17 documents as real files, including their attachment
  files, so they can be validated once tooling exists
- `CONTRIBUTING.md` (linked from README but missing)
- A validation fixtures corpus (`fixtures/valid` + `fixtures/invalid`, one per §15 rule with
  expected diagnostics) — the highest-leverage artifact for compatible third-party implementations,
  and a regression net over everything resolved in rounds 1–2
- Fix the README "Examples" link (currently points at `llm/`)

---

## Remaining Sequencing

1. **Decision items:** I3, I5 — small normative additions once decided.
2. **Practical tier:** P1–P5, P7–P12 — each is either a small normative addition or an explicit
   deferral; deferred ones get a line in a *Roadmap / Known Limitations* section so silence reads
   as a decision.
3. **G12**, then tag v0.1.
