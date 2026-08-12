# Changelog

All notable changes to the LegalDown specification are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). LegalDown is in
early draft (v0.1) and is **not yet stable** — breaking changes may occur between draft revisions
without a major version bump until v1.0.

---

## [Unreleased]

### Translations are secondary documents — 2026-08-12

The bilingual rules required identical section and definition identifiers across linked files but
never said how to achieve that — and auto-generated identifiers, slugged from language-specific
text, guarantee a mismatch. Resolution: make the authoring model explicit rather than nudging with
warnings.

#### Changed

- **Primary/secondary model (spec §14.1, §14.2).** A translation is a **secondary document**
  derived from a **primary**: structure and identifiers originate in the primary — including ids
  auto-generated there (§5.3 is deterministic, so tooling can compute them) — and are mirrored into
  each translation **explicitly**; only the text is translated. Updating a translation means
  mirroring the primary's change under the same identifier and translating the text. There is no
  reason for auto-generation in a translation file, and relying on it is now prohibited.
- **`authoritative` identifies the primary (§3.2, §14.2).** The primary is the linked file whose
  `language` equals the declared `authoritative` language; declaring `authoritative` is RECOMMENDED
  whenever `translations` is present. Without it, validators check the group symmetrically and
  SHOULD warn about auto-generated ids in any linked file.

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Heading or `{{def:}}` without an explicit identifier in a translation file | — | **Added (Error, §15.7)** |
| Auto-generated identifiers in linked files when `authoritative` is absent | — | **Added (Warning, §15.7)** |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §3.2 (`authoritative` row), §14.1, §14.2
  (primary/translations rules), §15.7.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — bilingual section, frontmatter
  comment, validation summary.

---

### Document-type constraint severities — 2026-08-12

§15.6's document-type table (minimum sides/parties, required `issuer` side) carried no severities,
and taken as Errors it would contradict `sides` being RECOMMENDED — a contract without a `sides`
block would implicitly fail. Severities are now explicit.

#### Changed

- **§15.6 severity model.** An invalid `document_type` value is always an Error. When `sides` is
  **present**, violations of the minimum-sides, `issuer`-side, and minimum-parties rows are
  **Errors**. When frontmatter is present but `sides` is **absent entirely**, those rows cannot be
  verified: validators MUST NOT report them as violated and MUST emit a single **Warning** that the
  `document_type` constraints cannot be verified without `sides` — keeping `sides` genuinely
  RECOMMENDED. A document with no frontmatter draws only the no-frontmatter Warning.

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Document-type minimums (sides/parties/`issuer`) | Severity unstated | **Error when `sides` present** |
| `sides` absent while frontmatter is present | (implicitly failing the minimums) | **Single Warning** — constraints not verifiable |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §15.6.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — validation summary.

---

### Consistency cleanup pass — 2026-08-12

Clears the remaining internal contradictions and editorial defects from the release-readiness
review (`spec-review.md` items I1–I2, I4, I6–I12, E2–E13, P6, and P13's example). No new features;
two behavior changes are called out below.

#### Behavior changes

- **Unknown directives are now an Error (§11.5, §15.2).** Previously a typo'd directive
  (`{{trem: services}}`) drew only a Warning and printed **verbatim into rendered output** — unlike
  every other failure, which renders a loud bracketed marker. Unknown directives now render as
  `[UNKNOWN DIRECTIVE: name]` with an Error; verbatim pass-through survives only as an explicit,
  non-default permissive mode (forward compatibility).
- **`text` joins the reserved `field_types` names (§3.2, §15.5).** It is a built-in placeholder
  type; a custom field type named `text` was confusable with it. Minor breaking change for any
  document that declared a `text` field type.

#### Changed

- **Ghost feature removed:** §1.3 no longer lists "language block directives", and the README no
  longer shows `{{lang: fr}} ... {{/lang}}` — bilingual support is separate-files only (§14), as
  designed.
- **§13.1** — numbering scheme is specifiable in the style template or renderer configuration; the
  dangling "document metadata" clause is struck (same class as the 2026-06-17 locale cleanup).
- **§14 rewritten tool-neutrally:** §14.3 no longer mandates a `legaldown validate --sync` CLI and
  no longer says "warns" where §15.7 says Error; the missing language-set consistency check is now
  a §15.7 row. §14.1/§14.2 editorial fixes ("Separate File Approach").
- **§13.2 enumeration table collapsed** to a single default sequence (its three style columns were
  identical); templates may define their own per-level sequences. **Ordered lists** are now
  specified: renderers renumber them at render time (source numbers are never authoritative) and
  may apply the enumeration scheme; §8.2 aligned with §13.2 (SHOULD for unordered, MAY for
  ordered).
- **Attachment "numbering position" wording** (§3.9, §12.4, §13.8) now speaks of *order* only —
  there is no generated attachment numbering to keep correct.
- **`{{ref:}}` edge cases defined (§13.3, §6.3):** under the "None" scheme, refs render the
  target's heading text (plus the enumeration path for item/paragraph anchors); refs crossing
  attachment numbering restarts are qualified with the target's scope — the attachment title
  ("Schedule A: Service Description, Section 2"), or the document title for main-body targets.
- **Preamble blessed (new §4.4):** content before the first heading is a valid, unnumbered
  preamble; all directives allowed; no anchors; placed before the first numbered provision.
- **Heading model completed (§4.1):** maximum depth is 5 (`######` = Error); setext headings are
  valid and map to levels 1–2 (ATX recommended).
- **§5.5** — an auto-generated identifier colliding with an *explicit* anchor is now covered: the
  explicit id wins, the auto id gets the numeric suffix plus Warning.
- **§3.6** — side-name display fallback no longer pluralizes (English-only behavior); the fallback
  is deterministic (hyphens → spaces, each word capitalized), `label` recommended.
- **`supersedes`** (§3.2) — may now be a `{title, file}` object like `amends`, or remain a string.
- **§5.2** — the anchor separator is "one or more spaces or tabs" (was "a single space").
- **§10.4 example** no longer declares a `board-of-directors` party (an organ fits neither party
  `type`); §17.4's amendment example now uses `(the "Agreement" {{def: agreement}})` and
  `{{term: agreement}}` throughout, showcasing inline definitions.
- **Spec header** carries a revision date pointing at this changelog (§ front page).
- **LICENSE** attribution URLs corrected to `https://github.com/ForLegalAI/LegalDown`; `.gitignore`
  added; README mentions `.legal.md` and drops the ghost `{{lang:}}` line.

#### Removed

- §15.3's "Sections with no references (possible orphaned content)" Info row — it flagged most
  sections of any normal contract (unreferenced *attachments* remain covered by §15.10).

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Unknown directive name | Warning + verbatim pass-through | **Error**, renders `[UNKNOWN DIRECTIVE: name]` (§15.2) |
| Heading depth exceeds level 5 | (undefined) | **Added (Error, §15.2)** |
| Linked bilingual files declare the same language set | §14.3 only, severity unclear | **Added (Error, §15.7)** |
| `field_types` key named `text` | Allowed | **Error** (reserved, §15.5) |
| Auto-generated id collides with an explicit anchor | (undefined) | Suffix + **Warning** (§5.5) |
| Sections with no references | Info | **Removed** |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — header, §1.3, §3.2, §3.6, §3.9, §4.1, new
  §4.4, §5.2, §5.5, §8.2, §10.4, §11.5, §13.1–§13.3, §13.8, §14, §15.2, §15.3, §15.5, §15.7, §17.4.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — heading rules, preamble, reserved
  types, display fallback, cross-references, directives, bilingual, validation summary.
- [`README.md`](README.md), [`LICENSE`](LICENSE), new [`.gitignore`](.gitignore).

---

### Spec version declaration in frontmatter — 2026-08-12

A document had no way to state which LegalDown version it targets (`version` is the *document's*
version) — a forward-compatibility gap once later spec revisions change semantics, as the
definitions overhaul already did within the draft.

#### Added

- **`legaldown` frontmatter field (spec §3.2), OPTIONAL.** Declares the specification version the
  document was authored against, e.g. `legaldown: "0.1"` (quoted — unquoted YAML would read `0.1`
  as a number). Implementations SHOULD warn when the declared version is newer than the one they
  implement and MUST NOT fail solely because it is unknown; absence means the document is processed
  under the implementation's version. Added to the §3.1 example.
- `legaldown` joins the fields that MUST NOT hold a `{{placeholder:}}` (§3.10, §15.5) — it governs
  processing semantics, like `document_type`.

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Declared `legaldown` version newer than the implementation supports | — | **Added (Warning, §15.6)** |
| `{{placeholder:}}` in a structural frontmatter field | Error | Error — field list now includes `legaldown` |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §3.1 example, §3.2 (field row + rules),
  §3.10, §15.5, §15.6.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — frontmatter block, structural-field
  lists, validation summary.

---

### Signature blocks: explicitly implementation-defined — 2026-08-12

§2.2 asked renderers to generate signature blocks from frontmatter and §3.6 hung a MUST
(`legal_name` always appears on signature blocks) on that feature — but nothing defined a signature
block's content or layout: no fields exist for signing lines, dates, places, or capacities, and
`adopted_by` is a plain string. Decision: signature block generation is **implementation-defined**
in v0.1 rather than specified.

#### Changed

- **§2.2 note rewritten.** Signature blocks remain outside LegalDown markup; generation from
  frontmatter stays a SHOULD with the per-document-type sources (all sides / issuer / issuer +
  `adopted_by`), but content and layout are explicitly left to the implementation and its style
  template.
- **§3.6** — the `legal_name` rule is now conditional: *where an implementation generates signature
  blocks*, party `legal_name` MUST appear on them (previously an unconditional MUST hanging on an
  undefined feature).
- **§13.7** — style template settings gain "Signature block layout", giving the
  implementation-defined behavior a configuration home.

A structured signature model (per-representative signing lines, date/place placeholders, witnesses)
remains a candidate for a future revision; nothing in this change precludes it.

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §2.2, §3.6, §13.7.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — unchanged (the LLM reference does not
  cover signature rendering).

---

### Item and paragraph anchors — 2026-08-12

Legal cross-referencing happens below headings — "Section 4.2(b)", "čl. 5 odst. 2" — but anchors
existed only on headings, and headings require title text, so enumerated items could not be
referenced and continental untitled numbered paragraphs could not be expressed at all. This
revision extends the existing `{#id}` / `{{ref:}}` machinery below heading level. No new directive,
no new namespace.

#### Added

- **Item and paragraph anchors (new spec §5.7).** `{#id}` may be placed at the very end of a list
  item's first paragraph (any list depth; not in lists inside block quotes/tables) or at the very
  end of a top-level paragraph directly inside a section (not before the first heading):

  ```markdown
  Provider may suspend the Services if:

  - payment is overdue by more than thirty (30) days {#suspension-overdue}
  - Client breaches confidentiality {#suspension-breach}
  ```

  Explicit only — **never auto-generated** (prose makes bad slugs; existing documents unaffected).
  These anchors join the anchor namespace (§5.6) and are targeted with plain `{{ref:}}`.
- **Designation rendering (§6.3/§13.3).** A ref to an item/paragraph renders the containing
  section's number plus the item's enumeration path or paragraph number under the active template —
  "3.1(a)", "3.1(b)(ii)", "5.2" — hyperlinked and reorder-safe, extending the no-hardcoded-numbers
  guarantee below heading level. If the template renders that list as plain bullets (or doesn't
  number paragraphs), the ref falls back to the containing section's number and emits a Warning —
  honest degradation instead of spooky forced enumeration.
- **Continental numbered provisions (§13.2, §13.7).** Templates MAY render first-level list items
  as section-qualified decimals (5.1, 5.2, …) and MAY number top-level paragraphs within sections
  (off by default) — covering untitled numbered-paragraph drafting without fake headings.

#### Changed

- **§5 retitled** "Section Identifiers" → "Identifiers and Anchors"; §5.1, §5.6 (anchor-namespace
  row and rules), and §6.2 updated so `{{ref:}}` resolves sections *and* item/paragraph anchors
  (attachment ids still only via `{{attach:}}`).

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Explicit anchors unique | Error (sections only) | Error — now spans section ids + item/paragraph anchors (§15.2) |
| `{#id}`-like marker outside an anchor position | — | **Added (Warning, §15.2)** — likely misplaced anchor |
| `{{ref:}}` to an item/paragraph the template does not enumerate | — | **Added (Warning, §15.3)** — renders as containing section number |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §5 title, §5.1, new §5.7, §5.6, §6.2, §6.3,
  §13.2, §13.3, §13.7, §15.2, §15.3, §16.2.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — anchors block, validation summary.
- [`README.md`](README.md) — "Identifiers make references stable" blurb, structure-at-a-glance
  snippet.

---

### File inclusion: unified fragment model and validation — 2026-08-12

Includes were the least-specified multi-file feature: §12.2 required included files to be "valid
LegalDown documents" whose frontmatter is then ignored (a different fragment model than attachment
files use, for the same job), said nothing about heading levels at the splice point, definitions, or
nesting — and §15 had no include validation table at all, so none of §12.2's requirements had a
severity.

> **Breaking change (minor).** An include target that carried its own frontmatter was previously
> tolerated (frontmatter "SHOULD be ignored"); it is now an Error. Fix: delete the fragment's
> frontmatter — it was ignored anyway.

#### Changed

- **One fragment model (spec §12.2, retitled "Include Fragments").** Include targets now use the
  same file model as LegalDown attachment files (§12.4): body-only fragments — no YAML frontmatter,
  no level 1 heading, LegalDown extensions only (`.lgd`, `.legaldown`, `.legal.md`). The old "valid
  standalone document with ignored frontmatter" rule is gone. §12.3's comparison table gains a
  "File model" row showing the two features now match.
- **Splice semantics defined.** Content is spliced verbatim at the directive position — heading
  levels are **not** re-based; the combined document must satisfy the §4.1 hierarchy (a fragment
  whose headings would skip a level at the insertion point is invalid). The author writes the
  surrounding heading in the including document, as §12.1's example always showed.
- **Definitions and nesting settled.** A `{{def:}}` in an included fragment registers a
  document-wide term (same as attachment files; §7.2 updated). Fragments may nest further
  `{{include:}}`s; the circular-include check spans the entire chain.
- **§12.1** no longer says implementations "MAY support" inclusion — support is governed by the
  conformance level (Full, §16.4; the phrase predates conformance levels).

#### Validation changes

New table **§15.11 Include Validation** — §12's requirements finally have severities:

| Rule | Level |
|---|---|
| Include target path exists | Error |
| Include target is a LegalDown file | Error (extension check applies at Core, §16.2) |
| Circular include chain | Error |
| Included fragment contains frontmatter | Error |
| Included fragment contains a level 1 heading | Error |
| Fragment section identifiers unique across combined document | Error |
| Combined document satisfies §4.1 heading hierarchy | Error |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §12.1–§12.3, §7.2, new §15.11, §16.2 and
  §16.4 (conformance scope).
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — File Inclusion section, validation
  summary.

---

### Frontmatter validation completeness — 2026-08-12

`title` was the only REQUIRED metadata field, yet no validation rule anywhere checked it — nor
whether frontmatter parses, whether date fields are real dates, or whether language codes are valid.
And §2.2 (frontmatter OPTIONAL) sat unresolved against §3.2 (`title` REQUIRED). This revision
closes the holes.

#### Changed

- **Optionality model clarified (spec §3.2).** Frontmatter is OPTIONAL as a block but RECOMMENDED;
  field Status values apply **when frontmatter is present**. A document without frontmatter is
  valid (untitled, no parties) and draws a Warning.

#### Validation changes

New **General metadata checks** table in §15.6:

| Rule | Level |
|---|---|
| Frontmatter, when present, parses as valid YAML | **Added (Error)** |
| Document includes frontmatter | **Added (Warning)** |
| `title` present and non-empty when frontmatter present | **Added (Error)** |
| `effective_date` / `adoption_date` / `date_of_birth` are valid ISO 8601 | **Added (Error)** |
| `language` / `authoritative` / `translations` keys are valid ISO 639-1 | **Added (Warning)** |
| `authoritative` equals `language` or a `translations` key | **Added (Warning)** |
| Representative `name` is non-empty | **Added (Error)** |
| Attachment `title` is non-empty | **Added (Error, §15.10)** |

Placeholder interplay is explicit: where §3.10 permits a placeholder value, it satisfies the
field's presence requirement and is **exempt from that field's format checks** (e.g.,
`effective_date: "{{placeholder: effective-date, type=date}}"` does not fail the ISO 8601 check);
the placeholder's own §15.5 checks apply instead.

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §3.2 (optionality note), §15.6 (general
  metadata checks + placeholder exemption), §15.10 (attachment title row), §16.2 (Core scope).
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — frontmatter note, validation summary.

---

### Removed the undefined "structured output formats" clauses — 2026-08-12

Six rules in §10.2–§10.7 required raw values to "be preserved in structured output formats for
machine processing" — MUST requirements against a format the spec never defined (§13.6 lists only
PDF, DOCX, HTML, and plain text, none of them structured). Decision: the clauses are **removed**,
not defined. The LegalDown source file is itself the canonical machine-readable representation —
every raw value and `note` is available by parsing the source — and the specification deliberately
covers only the LegalDown format, not export or interchange formats. A JSON export may appear later
as tooling or a companion document, outside this spec.

#### Changed

- **§10.1** — the `note` preservation clause is dropped; `note` remains a non-rendered, plain-text
  annotation for automation. A new scope statement makes the position explicit: the source file is
  the canonical machine-readable representation, and LegalDown defines no export or interchange
  format.
- **§11.3** — the value-quoting paragraph no longer lists "structured output" among downstream
  rules.

#### Removed

- The "raw value … MUST be preserved in structured output formats" bullets in §10.2 (date), §10.3
  (money), §10.4 (party), §10.5 (duration), §10.6 (field), and §10.7 (placeholder).

Unaffected: §15.9 validator output ("structured output indicating file, line number, …") is a
different, self-defined use — diagnostic structure — and stays. The LLM reference never used the
term, so it is unchanged.

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §10.1, §10.2–§10.7, §11.3.

---

### Deterministic identifier generation — 2026-08-12

Auto-generation (§5.3) told implementations to "transliterate non-ASCII characters to their closest
ASCII equivalents" — an undefined mapping (`ß` → `ss` or `s`? Cyrillic? CJK?), so two conformant
tools could generate *different* ids for the same heading and a `{{ref:}}` valid in one tool would
break in the other. Since auto-generation is a MUST, this affected every document without explicit
ids. The algorithm is now pinned end to end.

#### Changed

- **§5.3 rewritten as a fully deterministic pipeline** (identical output across implementations is
  now a MUST): Unicode NFKD + combining-mark stripping → fixed transliteration table → remove
  remaining non-ASCII → lowercase → hyphenation → collapse hyphen runs → trim → truncate (64) →
  trim → `section` fallback → `section-` prefix. Via §7.2 the same pipeline governs auto-derived
  definition ids.
- **Transliteration is table + NFKD only — no romanization.** The exhaustive table covers Latin
  letters NFKD cannot reduce (`ß`/`ẞ`→`ss`, `æ`→`ae`, `œ`→`oe`, `ø`→`o`, `đ`/`ð`→`d`, `þ`→`th`,
  `ł`→`l`, `ħ`→`h`, `ı`→`i`); accented Latin (Czech, French, German, …) reduces deterministically
  via NFKD. Scripts without an ASCII decomposition (Cyrillic, Greek, CJK) are **removed, not
  romanized** — romanization schemes are contested and locale-dependent, which is precisely what
  made "closest equivalent" non-deterministic. Such headings fall back to `section` and trigger the
  new warning below; authors in those scripts should use explicit ids.
- **Two latent §5.3 bugs fixed in passing:** (a) the old steps produced a double hyphen for
  "Confidential Information & Trade Secrets", contradicting the spec's own single-hyphen example —
  a collapse-hyphen-runs step now exists; (b) hyphens were trimmed *before* the 64-char truncation,
  so a cut could leave a trailing hyphen — trimming now also runs after truncation.
- **§5.5** — collision suffixes (`-2`, `-3`) are assigned in document order, appended after the
  §5.3 algorithm, and exempt from the 64-character maximum (previously unspecified).

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Auto-generated section identifier lost non-transliterable letters or digits | — | **Added (Warning, §15.2)** — recommend explicit id; removed punctuation does not warn |
| Auto-derived definition identifier lost non-transliterable letters or digits | — | **Added (Warning, §15.4)** — recommend explicit id; removed punctuation does not warn |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §5.3 (rewritten, transliteration table,
  warning rule, expanded examples), §5.5 (suffix rules), §15.2 and §15.4 validation tables.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — auto-generation pipeline description,
  validation summary.

---

### Identifier namespaces — 2026-08-12

The spec settled namespace sharing for attachments ("attachment ids share the same namespace as
section identifiers") but was silent or ambiguous everywhere else — most importantly whether a
`{{def:}}` id may equal a section id. Two validators could disagree on whether a "Services" section
plus a defined term "Services" (both auto-generating `services`) is a collision. This revision
defines the full namespace model.

#### Added

- **Identifier Namespaces (new spec §5.6).** One identifier format, separate namespaces; every
  directive resolves only against its own:

  | Namespace | Uniqueness | Resolved by |
  |---|---|---|
  | Anchor (section ids + item/paragraph anchors + attachment ids) | Shared — unique across all | `{{ref:}}` (sections, items, paragraphs), `{{attach:}}` (attachments only) |
  | Definitions | Unique among definitions | `{{term:}}` |
  | Placeholders | Repeats = same logical blank | — |
  | Sides / Parties / `field_types` keys | Per §3.3 / §3.4 / §3.2 | — / `{{party:}}` / `{{field:}}` `type` |

  A definition id MAY equal a section id — explicitly benign (the "Services" section + "Services"
  term case), not a collision. Renderers MUST disambiguate emitted anchors in single-anchor-space
  outputs (e.g., `def-services` vs `services`); the scheme is implementation-defined.
- **`{{ref:}}` is type-specific (spec §6.2 rule).** Although sections, item/paragraph anchors, and
  attachments share the anchor namespace, `{{ref:}}` resolves only section identifiers and
  item/paragraph anchors; targeting an attachment id is a broken reference and validators SHOULD
  suggest `{{attach:}}` in the diagnostic.

#### Changed

- **§5.4** notes that section identifiers share the anchor namespace with attachment ids; **§3.9**
  now points to §5.6.
- **§7.2** — definition ids are unique "among definitions within the document" (previously the
  ambiguous "unique within the document").
- **§10.7** — placeholder ids explicitly form their own namespace and may coincide with any other
  identifier.

#### Validation changes

| Rule | Before | After |
|---|---|---|
| `{{ref:}}` targets an attachment id | (undefined) | **Added (Error, §15.3)** — diagnostic should suggest `{{attach:}}` |
| `{{def:}}` id equals a section identifier | (undefined — arguably a collision) | **Explicitly not an issue** (§5.6) |
| All `{{def:}}` identifiers are unique | Error (scope ambiguous) | Error — scoped to the definitions namespace (§15.4) |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — new §5.6, §5.4, §3.9, §6.2 (rules block),
  §7.2, §10.7, §15.3 and §15.4 validation tables.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — identifier-namespaces block,
  cross-reference and definition notes, validation summary.

---

### Directive grammar and quoted values — 2026-08-12

Directive syntax was previously defined only by example, so "Directives are well-formed — Error"
(§15.2) had no testable definition, and values could never contain a comma or `}}` — making labels
like `Smith, Jones & Co.` and comma-bearing `{{field:}}` values (case citations) unrepresentable.
This revision gives directives a formal grammar and introduces optional quoted values. Backward
compatible: every previously valid directive parses identically.

#### Added

- **Formal directive grammar (spec §11.2, EBNF).** One shared shape for every directive: at most one
  positional value (always first), then order-insensitive named parameters. No whitespace between
  `{{` and the name or before the `:`; whitespace around separators is syntax, never value content.
  Duplicate named parameter → Error; parameter unknown to the directive → ignored + Warning
  (generalizing the §13.5 placeholder rule).
- **Quoted values (spec §11.3).** Any positional or parameter value MAY be wrapped in straight
  double quotes (U+0022) to carry commas, `}}`, `=`, or significant leading/trailing spaces:

  ```markdown
  {{term: services, label="Services, as amended"}}
  {{field: "Smith, Jones & Co. v. Doe", type=case-name}}
  ```

  `\"` and `\\` are the only escape sequences. Quoting is syntax, not content — quoted and unquoted
  spellings parse to the same value, so `{{field:}}` pass-through rendering is unaffected. Typographic quotes do not delimit values; validators warn when an unquoted value
  starts with one (auto-curled quotes).
- **Recognition contexts and escaping (spec §11.4).** Directives are recognized in body text and in
  frontmatter per §3.10, and are **not** recognized inside code spans, code blocks, or HTML
  comments. Literal `{{` is written with the inherited CommonMark backslash escape (`\{{ref: x}}`).
  "Well-formed" is now defined by opener commitment: `{{name:` that cannot complete on the same
  line is a malformed directive (Error); a stray `{{` without `name:` is literal text (Warning).

#### Changed

- **§11 renamed "Directives Summary" → "Directives"** and restructured: old §11.2 (Directive Rules)
  is now §11.5, unchanged in substance, after the new §11.2–§11.4.
- **Comma/`}}` prohibitions rescoped to the unquoted form** in §7.3 (`{{term:}}` label), §10.1
  (`note`), §10.4 (`{{party:}}` label), and §10.6 (`{{field:}}` value). §10.6's "preserve exactly as
  parsed" now explicitly means after unquoting and escape processing, with no further
  transformation.

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Directives are well-formed | Error (undefined) | Error — **now defined** by the §11.2 grammar incl. quoted-value termination |
| Duplicate named parameter in a directive | — | **Added (Error)** |
| Named parameter not defined for the directive | — | **Added (Warning, ignored for rendering)** |
| Unescaped `{{` not beginning a well-formed directive | — | **Added (Warning)** |
| Unquoted value begins with a typographic quotation mark | — | **Added (Warning)** |
| `note` / `label` / `{{field:}}` value contains a comma or `}}` | Error (always) | Error **only when unquoted**; quoted form permitted |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §11 intro and title, new §11.2–§11.4, old
  §11.2 → §11.5, §7.3, §10.1, §10.4, §10.6, §15.2 and §15.5 validation tables.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — shared syntax rules block in
  Directives, label/value notes, validation summary.

---

### Conformance levels — 2026-08-12

Fills the longest-standing dangling reference in the spec: §1.5 has always required implementations
to support "all MUST requirements at their claimed conformance level (see Section 16)" — but the
referenced section never existed (Section 16 was the Complete Examples). This revision defines the
levels and repoints the examples.

#### Added

- **Conformance Levels (new spec §16).** Three cumulative levels:

  | Level | Name | Scope |
  |---|---|---|
  | 1 | Core | Parse + validate a single document (everything determinable from the file alone, including the single-file rows of §15.8/§15.10) |
  | 2 | Rendering | Core + §13 rendering, at least one of PDF/DOCX/HTML |
  | 3 | Full | Rendering + all multi-file processing: includes (§12), attachment content (§12.4/§13.8), amendment definition import (§7.5), bilingual validation (§14/§15.7), path-existence checks |

  General rules: levels bind **implementations only** (documents may use any construct regardless);
  a claimed level is a floor, not a ceiling; SHOULD/MAY features stay non-mandatory at every level.

- **Behavior beyond the claimed level (spec §16.5).** No silent skips: validators MUST warn about
  check categories they did not perform and MUST NOT report a document as passing checks they did
  not run; renderers MUST refuse or insert a visible `[NOT PROCESSED: ...]` marker for content they
  cannot process.

#### Changed

- **§11.1 directive table: "Status" column replaced by "Level".** The old REQUIRED/OPTIONAL values
  conflated author-facing and implementation-facing optionality (no directive is ever *required to
  appear* in a document, so REQUIRED could only sensibly describe implementation support — which the
  conformance levels now govern). The column now names the level at which support is mandatory: Core
  for every directive except `{{include:}}` (Full); a note clarifies that `{{attach:}}` title
  resolution is Core while rendering attachment *content* is Full, and that directive *use* is
  always an authoring choice.
- **§1.5** now names the three levels inline.
- **Complete Examples renumbered §16 → §17** (subsections 16.1–16.4 → 17.1–17.4) to make room at the
  position §1.5 already pointed to. References to "the §16 examples" in earlier changelog entries
  describe the pre-renumber spec. Also adds the previously missing `---` separator before the
  section.

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Check category skipped because it lies beyond the implementation's conformance level | — | **Added (Warning, §16.5)** |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §1.5 (level names), §11.1 (Level column and
  note), new §16 (Conformance Levels), §16 → §17 renumber of Complete Examples.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — unchanged intentionally: conformance
  levels are implementation-facing, and the LLM reference covers reading and authoring documents.

---

### Frontmatter: locale/currency cleanup and template placeholders — 2026-06-17

Tightens the document-metadata model so the schema and the rendering rules agree, and adds a
reuse-first way to author templates and drafts. No new structural complexity — these changes
*remove* dangling references and *reuse* the existing `{{placeholder:}}` mechanism.

#### Changed

- **No document-level locale or default currency.** The rendering rules previously told renderers to
  read "the document's locale" and "a default currency from the document metadata" (§10.2–§10.5),
  but the frontmatter schema defined neither field. Formatting (date order, separators, currency
  symbol) is **presentation**, so it is now explicitly a render-time setting — the **active locale**
  from the render template or renderer configuration (§10.1). Currency stays per `{{money:}}`
  directive; an omitted `currency` emits a validation warning and MAY fall back to a render-template
  default, but there is **no document-level default currency**.

- **`identification_number` is a cross-type reserved field.** Clarified (§3.4) that
  `identification_number` is the reserved field name for a registration/national identifier on **any**
  party — RECOMMENDED for `legal_entity`, OPTIONAL for `natural_person` (not every individual has
  one). Prefer it over a custom field so tooling can locate the identifier consistently. Documentation
  clarification, not a schema change.

#### Added

- **Placeholders in frontmatter (spec §3.10).** Template and draft documents MAY use the existing
  `{{placeholder:}}` directive (§10.7) as a **quoted** string value in frontmatter, reusing its ids,
  types, and rendering unchanged:

  ```yaml
  legal_name: "{{placeholder: client-legal-name}}"
  effective_date: "{{placeholder: effective-date, type=date}}"
  ```

  - Allowed in **value** fields (`title`, `legal_name`, `address`, `identification_number`,
    `effective_date`, `governing_law`, …); **not** in identifier or structural fields (any `name`,
    `type`, `document_type`, `sides`/`parties` structure).
  - Must be a quoted YAML string (an unquoted `{{` is invalid YAML).
  - A required field holding a placeholder counts as present — the document is treated as a
    template/draft with unfilled blanks; a placeholder id shared with the body is the same blank.

#### Validation changes

| Rule | Before | After |
|---|---|---|
| `{{placeholder:}}` in a frontmatter identifier/structural field | — | **Added (Error)** |
| `{{money:}}` omitted `currency` looks up a *document* default | (implied) | **Removed** — no document default; warning only |

#### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §3.4 (identifier note), new §3.10
  (frontmatter placeholders), §10.1 (active-locale note), §10.2–§10.5 (locale wording), §10.3
  (currency clause), §10.7 (cross-reference), §13.7 (locale listed among style-template settings),
  §15.5 (validation row).
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — Sides and Parties notes, Placeholder
  section, validation summary.

---

### Definitions overhaul (BREAKING) — 2026-06-16

This revision reworks how defined terms are declared (spec §7). The goal was to support the way
lawyers actually define terms — including **inline, at first use** — while making the schema
*simpler*, not more complex. The full design rationale and the alternatives considered are recorded
in [`definitions-review.md`](definitions-review.md).

> **Breaking change.** Every existing `{{def:}}` declaration must be rewritten (see *Migration*
> below). This is acceptable because LegalDown is a v0.1 draft with no stability guarantee.

#### Changed

- **Declaration syntax — term first, then tag.** A definition is now declared by writing the term
  in quotation marks and placing `{{def: id}}` *immediately after it*. The defined term is the text
  inside the quotes. The directive emits no visible output of its own; it anchors the preceding term
  and registers the id.

  ```diff
  - {{def: confidential-info}}
  - **"Confidential Information"** means any non-public information disclosed by one side to the other.
  + "Confidential Information" {{def: confidential-info}} means any non-public information disclosed by one side to the other.
  ```

- **One syntax for sectioned and inline definitions.** The old model required a `{{def:}}` on its
  own line preceding a paragraph and only *inside* a Definitions section. The same `term + tag` form
  now works anywhere — including inline at first use:

  ```markdown
  The Provider shall perform the marketing services described in this Article
  (the "Services" {{def: services}}).
  ```

  This makes the previously unsupported "labeling / first-use" definition pattern
  (`Acme Corporation ("Provider")`) a first-class construct.

- **Definitions may appear anywhere.** The mandatory, single, first-positioned **Definitions
  section** is gone. A top "Definitions" heading remains a *recommended convention* for stipulative
  definitions but is no longer required or structurally constrained. Subheadings under a Definitions
  heading are now allowed.

- **Format-agnostic source.** Defined terms no longer carry emphasis markers (`**bold**`) in source.
  Quotation marks are the only delimiter, and they are a **source-only delimiter that is never
  rendered** — at neither the defining occurrence nor any `{{term:}}` reference. Whether a term
  renders bold, underlined, or small-caps is entirely a render-time decision driven by the style
  template (§13.7) — applying the separation-of-content-and-presentation principle (§1.2) to
  definitions.

- **Reference by location, not body.** A `{{def:}}` records only `(id, term, location)`. The format
  no longer stores or extracts a "definition text." A `{{term:}}` link targets the definition's
  location (the `{{def:}}` anchor); generated glossaries point to the **section/clause** containing
  it. For tooling purposes (circular-reference detection, optional glossary previews) a definition's
  scope is its **containing paragraph** — a deterministic unit. Sentence-level extraction is
  deliberately not specified (unreliable in legal/multilingual text).

- **`{{term:}}` rendering** now takes the display term from the quoted span at the definition site
  (spec §7.3 / §13.4 step 3) instead of from `**"..."**`. The delimiting quotation marks are not
  rendered.

- **Inflected forms via `label`.** Grammatical inflection (declension, plural, etc.) is expressed
  through the `{{term:}}` `label` override. LegalDown does not encode morphological variants in the
  schema; authoring tools are expected to generate the appropriate `label` automatically.

#### Added

- **Accepted quotation-mark delimiters (spec §7.2).** A defined set of opening/closing pairs is now
  specified — all accepted by default, configurable per document `language`:

  | Pair | Open / Close | Code points |
  |---|---|---|
  | Straight double | `"` / `"` | U+0022 / U+0022 |
  | Curly double | `“` / `”` | U+201C / U+201D |
  | Guillemets | `«` / `»` | U+00AB / U+00BB |
  | Reversed guillemets | `»` / `«` | U+00BB / U+00AB |
  | Low-high double | `„` / `“` | U+201E / U+201C |
  | Curly single | `‘` / `’` | U+2018 / U+2019 |
  | Low-high single | `‚` / `‘` | U+201A / U+2018 |
  | Single guillemets | `‹` / `›` | U+2039 / U+203A |

  Double-quote forms are recommended; single-quote forms are accepted but validators warn when a
  single-quoted term is ambiguous with an apostrophe (U+2019). *This also resolves a pre-existing
  inconsistency: §7.3 previously said terms were extracted from straight-quoted `**"..."**`, yet the
  French bilingual example used guillemets.*

- **Auto-derived identifiers (spec §7.2).** The `id` on `{{def:}}` may now be omitted; when omitted
  it is derived from the quoted term using the §5.3 slug algorithm (`"Services" {{def:}}` →
  `services`). Explicit ids remain recommended for stability and are required to disambiguate when
  two different terms would slug to the same id.

- **Definitions in attachment files (spec §7.2, §12.4).** A `{{def:}}` inside an attachment file now
  registers a document-wide term (ids remain unique across the combined document, per §15.10).
  Previously attachments could only *reference* terms via `{{term:}}`.

#### Removed

- The requirement that all `{{def:}}` declarations live in a single Definitions section.
- The requirement that the Definitions section be the first level-1 (`#`) heading.
- The prohibition on subheadings within the Definitions section.
- The recommendation to format defined terms as bold quoted text (`**"Term"**`).

#### Validation changes

| Rule | Before | After |
|---|---|---|
| Definitions section is the first `#` heading | Error | **Removed** |
| Definitions section contains no subheadings | Error | **Removed** |
| All `{{def:}}` appear in the Definitions section | Error | **Removed** |
| Defined terms follow `**"Term"**` formatting | Warning | **Removed** (replaced) |
| `{{def:}}` immediately preceded by a recognized quoted span | — | **Added (Error)** |
| Two definitions auto-generate the same id (omitted ids) | — | **Added (Error)** |
| Defined term wrapped in emphasis markers in source | — | **Added (Warning)** |
| Single-quoted term ambiguous with an apostrophe | — | **Added (Warning)** |
| Circular definitions detected | Error | Error (now scoped to the containing paragraph) |
| Definition used before declaration | Warning | **Info** (first-use is normal) |
| `{{def:}}` identifiers are unique | Error | Error (unchanged) |
| `{{term:}}` resolves to a declared definition | Error | Error (unchanged) |
| Declared definition never referenced | Warning | Warning (may false-positive when §7.4 auto term recognition is on) |

### Migration

To upgrade an existing document, rewrite each definition so the term sits in quotes **before** the
tag, drop the bold markers, and move everything onto one line:

```diff
- # Definitions {#definitions}
-
- {{def: confidential-info}}
- **"Confidential Information"** means any non-public information...
-
- {{def: services}}
- **"Services"** means the software development services described in Section {{ref: scope-of-work}}.
+ # Definitions {#definitions}
+
+ "Confidential Information" {{def: confidential-info}} means any non-public information...
+
+ "Services" {{def: services}} means the software development services described in Section {{ref: scope-of-work}}.
```

- `{{term:}}` references are **unchanged** — they still bind to the same ids, so no reference needs
  editing.
- The Definitions section is no longer required to be first and may now be placed anywhere; existing
  documents that keep it first remain valid.
- Terms previously hoisted into the Definitions section purely to get a defined-term label may now be
  defined inline at their first use instead.

### Files touched

- [`spec/legaldown-spec.md`](spec/legaldown-spec.md) — §7 (rewritten), §8.1, §11.1, §13.4, §14.2,
  §15.2/§15.3/§15.4 validation tables, and the §16 examples.
- [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md) — Definitions section, text-formatting
  note, validation summary, and the minimal example.
- [`README.md`](README.md) — NDA example, "Definitions are tracked" blurb, and the
  "Document Structure at a Glance" snippet.
- [`definitions-review.md`](definitions-review.md) — design review and rationale (new).
