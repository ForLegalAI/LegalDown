# Contributing to LegalDown

LegalDown is an open specification. Contributions are welcome — from typo fixes to new language
features.

The specification is currently **v0.1 DRAFT**: breaking changes are still possible between draft
revisions, and are recorded in [`CHANGELOG.md`](CHANGELOG.md).

---

## Where to start

| You want to… | Go to |
|---|---|
| Ask a question, float an idea, or discuss a design | [Discussions](../../discussions) |
| Report an error, ambiguity, or contradiction in the spec | [Issues](../../issues) |
| Propose a concrete change | Discussion first, then a pull request |

**Design changes start in Discussions.** A pull request that changes the language itself is much
more likely to land if the design was agreed first — the specification's job is to be unambiguous,
and that is easier to settle in prose than in a diff.

Small corrections — typos, broken links, a validation row that contradicts its own section — can go
straight to a pull request.

---

## What makes a good specification change

LegalDown has a few standing commitments. A change that conflicts with one of these needs a strong
argument:

- **No hardcoded numbers in source.** Section numbers, list markers, and cross-reference text are
  generated at render time (§1.2). Anything that puts them back into the document is a regression.
- **Content and presentation stay separate.** How something *looks* belongs to the style template
  (§13.7), not the document.
- **Determinism.** Two conformant implementations must produce the same result for the same input.
  If a rule leaves room for interpretation, it is not finished — the identifier algorithm (§5.3)
  and the directive grammar (§11.2) are the reference standard for the level of precision expected.
- **Minimal extensions.** LegalDown extends CommonMark only where legal drafting genuinely needs
  it. Prefer reusing an existing mechanism over adding a new directive.
- **Every rule needs a severity.** A new requirement belongs in the §15 validation tables as an
  Error, Warning, or Info — otherwise implementations will disagree about what to do with it.
- **Every rule needs a conformance level.** Decide whether the check is Core, Rendering, or Full
  (§16). Roughly: a check needing only the document file is **Core**; one needing the active style
  template or rendered output is **Rendering**; one needing another file is **Full**. Where a rule
  sits in a §15 table whose level differs, §16.2 carves it out by name — as it does for the
  template-dependent §15.3 row and the `supersedes.file` existence row.

---

## Pull request checklist

A specification change usually touches more than the specification. Before opening a PR:

- [ ] **[`spec/legaldown-spec.md`](spec/legaldown-spec.md)** — the normative change, including any
      §15 validation rows and §16 conformance placement
- [ ] **[`llm/legaldown-spec-llm.md`](llm/legaldown-spec-llm.md)** — the condensed reference, if the
      change is authoring-facing (skip for implementation-only changes, and say so in the PR)
- [ ] **[`README.md`](README.md)** — if the change affects the introductory material or examples
- [ ] **[`examples/`](examples)** — if the change adds a feature, add or extend an example, and
      update the feature-coverage table in [`examples/README.md`](examples/README.md)
- [ ] **§17 ↔ `examples/simple/` stay byte-identical** — three documents claim the specification's
      §17 fenced blocks and the files in `examples/simple/` are the same text. If you edit either,
      edit both
- [ ] **[`CHANGELOG.md`](CHANGELOG.md)** — a dated entry under `[Unreleased]` (format below)
- [ ] **The spec's `Revision:` date** — bump it when `spec/legaldown-spec.md` changes
- [ ] Cross-references still resolve — section numbers shift when sections are added

If you deliberately skip one of these, say why in the PR description. Reviewers check for this.

### Changelog entries

Entries follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with a few local
conventions. Look at existing entries for the shape:

- A short paragraph explaining **why** — what was broken, ambiguous, or missing
- `#### Added` / `#### Changed` / `#### Removed` sections as needed
- A `#### Validation changes` table with **Rule | Before | After** whenever severities move
- A `#### Files touched` list
- Breaking changes get a blockquote at the top of the entry and a migration note

---

## Examples

Every document in [`examples/`](examples) must be **valid** under the current specification — no
Errors. Warnings and Info notes may be configuration-dependent (see the notes in
[`examples/README.md`](examples/README.md)), so "no Errors" is the bar a contributor can actually
verify. When you add a feature, add or extend an example that exercises it, and
update the feature-coverage table in [`examples/README.md`](examples/README.md) so the claim and
the file agree.

> **Fixtures corpus — not yet published.** A validation fixtures corpus (deliberately invalid
> documents paired with their expected diagnostics, one per §15 rule) is planned before the v0.1
> tag; see the project status in the [README](README.md#project-status-). Once it exists,
> contributors adding a feature will also add a valid/invalid fixture pair. Until then, examples
> are the only required artifact — please do not invent a fixture layout in the meantime.

---

## Style

- **Conformance keywords** — MUST / MUST NOT / SHOULD / SHOULD NOT / MAY, per §1.5. Use them
  deliberately; prose that sounds normative but uses none of them will be read inconsistently.
- **Say who is bound.** "Renderers MUST…", "Validators SHOULD…", "Authors MAY…" — a requirement
  without a subject is ambiguous.
- Reference sections as `§5.3`, and keep a link to the section where the reader may need it.
- **Match the surrounding file's line-wrapping.** `spec/legaldown-spec.md` and
  `llm/legaldown-spec-llm.md` keep each prose paragraph on a single line, so that an edit produces a
  one-line diff instead of a reflow; `CHANGELOG.md`, `CONTRIBUTING.md`, and the example documents
  wrap at roughly 100 characters. Do not reflow a paragraph you did not otherwise change.
- Examples should look like real legal documents, not `foo`/`bar`.

---

## Licensing

The specification is licensed under [CC BY 4.0](LICENSE). By contributing, you agree that your
contribution is licensed under the same terms.

The license covers the specification document and this repository's contents. It does **not** cover
software that implements LegalDown — parsers, validators, renderers, and editors may be released
under any license their authors choose.
