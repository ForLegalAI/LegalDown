# LegalDown Examples

Working LegalDown documents, kept as real files so they can be validated and rendered by tooling —
not just read. Every document here is intended to be **valid** under
[the specification](../spec/legaldown-spec.md); deliberately invalid documents live in the
validation fixtures corpus instead.

Two tiers:

- **[`simple/`](simple)** — the specification's §17 examples, verbatim. Start here.
- **[`advanced/`](advanced)** — larger documents exercising the full feature surface: includes,
  attachments, anchors below heading level, bilingual pairs, and templates.

---

## simple/

| Example | Document type | Shows |
|---|---|---|
| [`nda/mutual-nda.lgd`](simple/nda/mutual-nda.lgd) | `contract` | Two sides, definitions (sectioned and inline), `{{term:}}`, `{{party:}}` with `label`, `{{date:}}`, attachments (LegalDown + PDF), `{{attach:}}` |
| [`notice/termination-notice.lgd`](simple/notice/termination-notice.lgd) | `unilateral_act` | `issuer` side, a definition whose body is a `{{date:}}` |
| [`policy/remote-work-policy.lgd`](simple/policy/remote-work-policy.lgd) | `collective_act` | `adopted_by`, `adoption_date`, `supersedes` (string form) |
| [`amendment/first-amendment.lgd`](simple/amendment/first-amendment.lgd) | amendment | `amends` metadata; definitions imported from the amended NDA (§7.5) — `{{term: agreement}}` and `{{term: confidential-info}}` resolve without redeclaration |

## advanced/

| Example | Shows |
|---|---|
| [`msa/`](advanced/msa) | The flagship contract: multi-party sides, a `natural_person` party, `field_types` + `{{field:}}`, `{{side:}}`, item and paragraph anchors, `{{include:}}`, two LegalDown attachments + one PDF, recitals, tables, `supersedes` object form |
| [`amendment/`](advanced/amendment) | Amends the MSA above; declares its own definitions while using imported ones |
| [`bilingual/`](advanced/bilingual) | An en/fr pair: `translations`, `authoritative`, explicit identifiers throughout, French guillemet term delimiters (§7.2) |
| [`template/`](advanced/template) | A fillable template: `{{placeholder:}}` in frontmatter value fields (§3.10) and in body text, with identifier and structural fields kept concrete |

---

## Feature coverage

Where to find a live example of each feature. Section numbers refer to the specification.

| Feature | § | Example |
|---|---|---|
| Frontmatter, sides and parties | 3.2–3.5 | every example |
| `natural_person` party, `date_of_birth` | 3.4 | `advanced/msa` |
| Multiple parties on one side | 3.3 | `advanced/msa` (three Clients) |
| Multiple representatives | 3.5 | `advanced/msa` |
| `field_types` declarations | 3.2 | `advanced/msa` |
| `amends` metadata | 3.8 | `simple/amendment`, `advanced/amendment` |
| `supersedes` — string form / object form | 3.2 | `simple/policy` / `advanced/msa` |
| Attachments (LegalDown and non-LegalDown) | 3.9, 12.4 | `simple/nda`, `advanced/msa` |
| Placeholders in frontmatter | 3.10 | `advanced/template` |
| `legaldown` version declaration | 3.2 | `advanced/*` |
| Metadata extensions (unknown fields ignored) | 3.7 | `advanced/bilingual` (`language_note`) |
| Preamble before the first heading | 4.4 | every example |
| Heading depth to level 4 | 4.1 | `advanced/msa` (attachment `service-description`) |
| Explicit section identifiers | 5.2 | every example |
| Auto-generated identifiers | 5.3 | `advanced/msa` attachment `pricing` (`## Currency and Taxes` → `currency-and-taxes`) |
| Item and paragraph anchors | 5.7 | `advanced/msa`, its include fragment |
| `{{ref:}}` to a section | 6.2 | `advanced/msa` attachment `pricing` → `scope-changes` |
| `{{ref:}}` to an item anchor | 5.7, 6.3 | `advanced/msa` (`change-approval`, `cause-breach`) |
| `{{attach:}}`, with and without `label` | 6.4 | `simple/nda`, `advanced/msa` |
| Definitions — sectioned, inline, auto-derived id | 7.2 | `advanced/msa` (`acceptance-criteria` omits its id) |
| Definitions introduced in an amendment | 7.5 | `advanced/amendment` (`personal-data`) |
| Definition import from an amended original | 7.5 | `simple/amendment` |
| `{{term:}}` with `label` (inflected form) | 7.3 | `advanced/msa` (`Deliverables`) |
| Guillemet term delimiters | 7.2 | `advanced/bilingual` (fr) |
| Emphasis, code spans | 8.1 | `advanced/msa` (§ Interpretation) |
| Lists — unordered, nested, ordered | 8.2–8.3 | `advanced/msa`, attachment `service-description` |
| Block quotes (recitals) | 8.4 | `advanced/msa` |
| Horizontal rule | 8.5 | `advanced/msa` (end of body, before the appended schedules) |
| HTML comments | 8.6 | `advanced/msa` |
| Links and images | 8.7 | attachment `service-description` |
| Tables | 9.1 | `advanced/msa`, attachment `pricing` |
| `{{date:}}` | 10.2 | every example |
| `{{money:}}` with `currency` and `note` | 10.3 | `advanced/msa`, its include and attachments |
| `{{party:}}` with `label` | 10.4 | `simple/nda`, `advanced/msa` |
| `{{duration:}}` — all seven units | 10.5 | `advanced/msa` and its fragments cover `S`, `MIN`, `H`, `D`, `W`, `MO`; `simple/amendment` covers `Y` |
| `{{field:}}` custom typed values | 10.6 | `advanced/msa` (`ticket-id`), include (`invoice-id`) |
| `{{placeholder:}}` — text, date, money | 10.7 | `advanced/template`, `advanced/msa` |
| `{{side:}}` collective reference | 10.8 | `advanced/msa` |
| `{{include:}}` body-only fragment | 12.1–12.2 | `advanced/msa` (`includes/payment-terms.lgd`) |
| Attachment files (body-only, no `#`) | 12.4 | `simple/nda`, `advanced/msa` |
| Bilingual primary/translation pair | 14 | `advanced/bilingual` |

---

## Notes for implementers

- **Attachment and include fragments** carry no frontmatter and no level 1 heading — the parent
  document supplies both (§12.2, §12.4).
- **Binary placeholders.** The `.pdf` and `.png` files are minimal but structurally valid — the
  PDFs carry a correct cross-reference table, `/Size`, and `/Length`, so a renderer that opens them
  gets a parseable one-page document rather than a parse error. They exist so file-existence checks
  (§15.10, §16.4) have something to resolve; their visible content is irrelevant.
- **Expected diagnostics.** These documents should validate with no Errors. A conforming validator
  may still emit Info-level notes (for example, a definition used before its declaration point).
- **Rendering** these documents requires choosing a numbering scheme and style template (§13); none
  is included here, since presentation is deliberately outside the document.
