# LegalDown v0.1 — Release Readiness & Consistency Review

**Status:** Living review, originally issued 2026-08-12 against commit `d05a8b8`; updated through
implementation round 3.

- **Round 1** — all release-blocking and major gaps (G1–G11) — merged in
  [PR #24](https://github.com/ForLegalAI/LegalDown/pull/24), including 12 additional fixes from its
  two review passes.
- **Round 2** — the consistency-cleanup tier (I1–I2, I4, I6–I12, E1–E13, P6, P13) plus the two
  decided items **I3** (document-type severities) and **I5** (translations as secondary documents)
  — merged in [PR #25](https://github.com/ForLegalAI/LegalDown/pull/25).
- **Round 3** — the practical tier (P1–P5, P7–P12), branch `practical-tier`.

**Progress: 49 of 50 tracked items resolved.** The only remaining item is the deferred ecosystem
work (**G12**), after which v0.1 can be tagged. Deliberate deferrals now live in the spec itself —
**§18 Roadmap and Known Limitations**.

**Scope:** [`spec/legaldown-spec.md`](spec/legaldown-spec.md), [`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md),
[`README.md`](README.md), [`CHANGELOG.md`](CHANGELOG.md), [`LICENSE`](LICENSE). Detailed change
records for every resolved item are in [`CHANGELOG.md`](CHANGELOG.md) under *Unreleased*.

---

## Issue Index

| ID | Status | Issue → Resolution |
|---|---|---|
| G1–G4 | ✅ Round 1 | Conformance levels (§16); directive grammar & quoting (§11.2–§11.4); identifier namespaces (§5.6); deterministic auto-ids (§5.3) |
| G5 | ✅ Round 1 (removed) | Undefined "structured output formats" clauses deleted; source file declared canonical (§10.1) |
| G6–G8 | ✅ Round 1 | Frontmatter validation (§15.6); include validation (§15.11); include fragment model (§12.2) |
| G9 | ✅ Round 1 | Item and paragraph anchors (§5.7) with continental numbering options (§13.2) |
| G10 | ✅ Round 1 (descoped) | Signature blocks → implementation-defined (§2.2) |
| G11 | ✅ Round 1 | `legaldown` spec-version field (§3.2) |
| G12 | ⏸ Deferred | Ecosystem: examples dir, CONTRIBUTING.md, fixtures corpus (see Part 1) |
| I1–I2, I4, I6–I12 | ✅ Round 2 | Ghost `{{lang:}}` removed; §13.1/§14 dangling clauses fixed; enumeration/attachment/ref-edge-case/unknown-directive/preamble/drift/LICENSE fixes |
| I3 | ✅ Round 2 | Document-type minimums: Error when `sides` present; single Warning when absent (frontmatter present) |
| I5 | ✅ Round 2 | Translations are secondary documents; explicit ids required in translation files (§14.2, §15.7) |
| P1 | ✅ Round 3 | `{{side:}}` directive (new §10.8) |
| P2 | ✅ Round 3 | `{{attach:}}` `label=` override (§6.4) |
| P3 | ✅ Round 3 | `W` added; `M` removed in favor of `MIN` — breaking, `M` rejected with a `MIN`/`MO` hint (§10.5) |
| P4 | ✅ Round 3 (guidance) | §3.8: cite the executed rendering, pin the scheme; qualified refs → §18 Roadmap |
| P5 | ✅ Round 3 | Circular-definition check downgraded to Warning (§15.3) |
| P6 | ✅ Round 2 | Orphaned-sections Info row removed (§15.3) |
| P7 | ✅ Round 3 | Money non-negative; written precision preserved (§10.3) |
| P8 | ✅ Round 3 | Quote-pair determinism invariant stated for configured sets (§7.2) |
| P9 | ✅ Round 3 | File-reference path safety (new §2.3): relative + document-root containment |
| P10 | ✅ Round 3 | CommonMark handling (new §8.7): raw HTML ignored+Warning; links hyperlinked; images allowed |
| P11 | ✅ Round 3 (documented) | §6.2 note on reference label words; template-supplied labels → §18 |
| P12 | ✅ Round 3 (deferred) | `{{meta:}}` recorded in §18 Roadmap |
| P13 | ✅ Round 2 (example) | §10.4 board example replaced; organ/`adopted_by` modeling → §18 |
| E1–E13 | ✅ Rounds 1–2 | All editorial items |

Behavior/breaking changes across the rounds, for release notes: definitions overhaul (pre-review),
include targets may not carry frontmatter (G8), unknown directives are Errors (I9), `field_types`
key `text` reserved (E7), duration unit `M` → `MIN` (P3).

---

## Part 1 — Remaining: G12 (final step before tagging v0.1)

- **`examples/` directory** containing the §17 documents as real files — including their attachment
  files — so they validate once tooling exists. Fix the README "Examples" link (currently points at
  `llm/`).
- **`CONTRIBUTING.md`** (linked from README but missing).
- **Validation fixtures corpus** — `fixtures/valid` + `fixtures/invalid`, one fixture per §15 rule
  with expected diagnostics. The highest-leverage artifact for compatible third-party
  implementations, and a regression net over everything resolved in rounds 1–3.

Then tag **v0.1**.

---

## Resolution Notes

Compact per-round notes; full details in [`CHANGELOG.md`](CHANGELOG.md).

### Round 1 ([PR #24](https://github.com/ForLegalAI/LegalDown/pull/24)) — the normative gaps

- **G1 Conformance levels (new §16):** Core / Rendering / Full, cumulative; levels bind
  implementations only, floor not ceiling; §16.5 forbids silent degradation. Examples renumbered
  §16 → §17; §11.1 Status column → Level column.
- **G2 Directive grammar (new §11.2–§11.4):** EBNF; positional-first; order-insensitive named
  parameters; quoted values carry commas/`}}` with `\"`/`\\` escapes; directives inert in code and
  comments; opener-commitment well-formedness.
- **G3 Identifier namespaces (new §5.6):** anchor / definitions / placeholders / frontmatter names;
  def id may equal section id; renderers disambiguate emitted anchors.
- **G4 Deterministic auto-ids (§5.3):** NFKD + exhaustive transliteration table; no romanization
  (removed letters/digits → Warning); latent slug bugs fixed; cap exemptions stated.
- **G5:** resolved by removal — the source file is the canonical machine-readable representation.
- **G6/G7/G8:** frontmatter validation completeness; §15.11 include table; includes unified on the
  body-only fragment model (minor breaking: no frontmatter in include targets).
- **G9 Item and paragraph anchors (§5.7):** `{#id}` below headings, explicit-only, rendered
  "3.1(a)" / "5.2" via `{{ref:}}`; continental numbered-paragraph template options.
- **G10:** signature generation implementation-defined. **G11:** optional `legaldown: "0.1"` field.

### Round 2 ([PR #25](https://github.com/ForLegalAI/LegalDown/pull/25)) — contradictions and decisions

- Ghost `{{lang:}}` deleted; §13.1 metadata clause struck; §14 tool-neutral with language-set row;
  §13.2 collapsed + ordered lists specified; attachment wording order-only; `{{ref:}}` under "None"
  and across attachment restarts defined (target-scope qualifier); unknown directives → Error with
  `[UNKNOWN DIRECTIVE: name]`; preamble blessed (§4.4); README/LLM drift and LICENSE URLs fixed;
  E2–E13 editorial sweep.
- **I3:** document-type minimums Error-when-`sides`-present, single Warning when absent.
- **I5:** translations are secondary documents — ids originate in the primary (`authoritative`
  marks it), mirrored explicitly; explicit ids required in translation files (Error), Core-checkable.

### Round 3 (`practical-tier`) — practical improvements

- **P1 `{{side:}}` (new §10.8):** collective side references with §3.6 fallback and
  `[UNKNOWN SIDE: …]` marker; Core level.
- **P2 `{{attach:}}` `label=`:** display override for mid-sentence references.
- **P3 durations:** `W` added; `M` removed — `MIN` is minutes, bare `M` rejected with a `MIN`/`MO`
  hint (breaking; eliminates the ISO 8601 months confusion rather than documenting it).
- **P4 amendments:** guidance in §3.8 (cite the executed rendering; pin the numbering scheme);
  qualified `{{ref: id, doc=amends}}` deferred to §18.
- **P5:** circular definitions Error → Warning. **P7:** money non-negative, precision preserved.
- **P8:** quote-pair determinism invariant stated as a constraint on configured sets.
- **P9 path safety (new §2.3):** all file-reference paths relative and inside a configured document
  root; absolute/escaping paths are Errors — the safety boundary hosted tooling needs.
- **P10 CommonMark handling (new §8.7):** raw HTML (non-comment) ignored + Warning; links as
  hyperlinks with a print-URL template option; images allowed under §2.3 with alt-text fallback.
- **P11/P12:** label-word tension documented (§6.2 note); `{{meta:}}` deferred — both recorded in
  the new non-normative **§18 Roadmap and Known Limitations**, alongside the other deliberate
  deferrals (qualified amendment refs, structured `adopted_by`/organ type, template attachment
  labels, signature model, JSON export companion).
