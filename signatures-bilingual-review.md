# Signatures, Bilingual Files, Party Fields & Amendments — Review & Proposal

**Status:** Design rationale (adopted). The designs below are implemented in the spec in the same
change; this document records the reasoning. See [`CHANGELOG.md`](CHANGELOG.md) for the summary.

**Scope:** §1.3, §2.2, §3.4, §3.6, §3.8, §7.5, §10.4, §14 of
[spec/legaldown-spec.md](spec/legaldown-spec.md).

**Note:** Part C interacts with list-item anchors from the body-constructs change; this proposal
assumes that change lands first.

### Decisions captured

- **A** (bilingual) — drop the inline `{{lang:}}` language-block references; keep separate files as the
  only mechanism, and specify how translation files work in detail.
- **B** (signatures) — add a small, optional signature-block data model; design + example below.
- **C** (party fields) — **agreed**: add inline rendering of a declared party field.
- **D** (amendments) — **agreed**: acknowledge the cross-document-numbering limitation; no new
  mechanism.

---

## Part A — Bilingual documents via translation files

### A.1 Remove the unspecified inline language block

§1.3 lists *"Language block directives for bilingual documents"* and the README shows
`{{lang: fr}} … {{/lang}}`, but no such directive is specified anywhere (no section, absent from the
§11 directive table; §14 describes separate files only). **Remove both references.** Separate files
are the single, fully-specified bilingual mechanism. Nothing else in the spec depends on `{{lang:}}`.

### A.2 The translation-file model (expanded §14)

A **translation set** is two or more standalone LegalDown files, one per language, that represent the
same document. Each file links to the others and the set is kept **structurally identical** so that
generated numbering and every cross-reference resolve to the same target in every language.

**Linking metadata (frontmatter):**

- `language` — this file's language (ISO 639-1).
- `translations` — map of *other* languages → file path, e.g. `{ fr: contract-fr.lgd }`. Each file
  lists its siblings.
- `authoritative` — the language that governs in a dispute (ISO 639-1), identical across the set;
  OPTIONAL. If absent, no language is authoritative.

**Recommended file naming:** `<basename>-<lang>.lgd` (e.g. `msa-en.lgd`, `msa-cs.lgd`).

**What MUST be identical across every file in the set (structural invariants):**

| Invariant | Why |
|---|---|
| Heading hierarchy (count, nesting, order) | Generated section numbers must match |
| Section identifiers (`{#id}`) | `{{ref:}}` must resolve to the same provision |
| **List-item anchor ids** | Anchored sub-clauses must resolve identically (`7.3(b)`) |
| Definition ids (`{{def:}}`) | `{{term:}}` must resolve in every language |
| Attachment ids and order | `{{attach:}}` and attachment numbering must match |
| Placeholder ids | A fill applies to the same blank in every language |
| Party `name` identifiers and `sides` structure | `{{party:}}` must resolve; signatories align |
| `document_type` and each party `type` | Same document shape and validation |
| `field_types` keys | `{{field:}}` types resolve consistently |

**What MAY differ (localized):**

- `title`, `subtitle`, heading **text**, body prose.
- Defined **term text** (the quoted term — "Confidential Information" vs « Information confidentielle »).
- `{{cite:}}` text (the same authority cited in each language's conventional form).
- Party `label`, `address`, and `governing_law` display text.
- `{{placeholder:}}` surrounding prose (the id stays the same).

**What SHOULD be identical:**

- Party `legal_name` — an entity's official registered name generally does not translate. (Recorded as
  SHOULD, not MUST, to allow transliteration where a jurisdiction requires it.)

**Three or more languages:** the `translations` map simply lists more siblings; all files in the set
obey the same invariants.

### A.3 Rendering

- Each file renders as a standalone document in its own language.
- Because structures match, a renderer **MAY** additionally produce an aligned **side-by-side /
  dual-column** bilingual output by pairing content on shared section and list-item identifiers. This
  is enabled by the structural-sync requirement and is OPTIONAL.
- An authoritative-language annotation (e.g. a footer "The English version governs") MAY be emitted
  when `authoritative` is set.

### A.4 Validation (expand §14.3 / §15.7)

The `validate --sync` check compares all files in a translation set:

| Check | Level |
|---|---|
| All `translations` files exist at declared paths | Error |
| Heading hierarchy matches across the set | Error |
| Section identifiers match across the set | Error |
| List-item anchor ids match across the set | Error |
| Definition ids match across the set | Error |
| Attachment ids and order match across the set | Error |
| Placeholder ids match across the set | Error |
| Party `name` identifiers and `sides` structure match across the set | Error |
| `document_type` and party `type` values match across the set | Error |
| `authoritative` value identical across the set | Warning |
| Party `legal_name` differs across the set | Warning |

---

## Part B — Signature / execution blocks

### B.1 Problem

The whole spec on signing is one note — *"Signature blocks are NOT defined in LegalDown markup.
Renderers SHOULD generate [them] from frontmatter"* (§2.2) — plus "`legal_name` MUST appear" (§3.6).
There is no model for **who signs, in what capacity, joint vs. several signing, place/date of signing,
or witness/notarization**, so every renderer invents its own execution page.

### B.2 Design — a small, optional signature data model

Keep layout in the style template; standardize the **data**. Signature blocks remain generated (never
authored in the body). Add an OPTIONAL `signature` object to a **party**, plus two OPTIONAL
document-level fields. Everything has sensible defaults, so existing documents are unaffected.

**Party `signature` object (all fields OPTIONAL):**

| Field | Values | Default | Meaning |
|---|---|---|---|
| `mode` | `each` \| `joint` \| `any` | `each` | How the party's representatives sign |
| `witness` | boolean | `false` | Add a witness line for this party's signature |
| `notarized` | boolean | `false` | Add a notarization block for this party's signature |

- `mode: each` — each listed representative gets their own signature line (the common case).
- `mode: joint` — all listed representatives must sign **together** (e.g. German *Gesamtvertretung*,
  common in CZ/DE two-director signing). The block groups them as a joint requirement.
- `mode: any` — any **one** of the listed representatives may sign; the block shows alternative lines.
- A `natural_person` signs **personally** (no representatives); `witness`/`notarized` still apply.

**Document-level (OPTIONAL):**

- `place_of_signing` — free text; rendered in the execution block if present.
- (Signing **date** is intentionally not a frontmatter field — the generated block includes a blank
  date line per signatory, filled at execution. A template MAY pre-fill it from `effective_date`.)

**Who signs, by `document_type`** (unchanged, §2.2): contract → all sides; unilateral act → issuer;
collective act → issuer (and `adopted_by`).

### B.3 Minimal rendering requirements

A generated signature block MUST include, per signing party:

1. The party `legal_name`.
2. For each **required** signatory (per `mode`): the representative `name` and `title`, a signature
   line, and a date line. For a natural person: the person and a signature + date line.
3. A witness line when `witness: true`; a notarization block when `notarized: true`.
4. `place_of_signing` when set.

Ordering follows the `sides` / `parties` declaration order. Fonts, spacing, and exact layout are
template-driven. (Electronic-signature workflows MAY suppress or replace the generated block with
platform fields.)

### B.4 Example

```yaml
sides:
  - name: providers
    label: Providers
    parties:
      - name: acme
        type: legal_entity
        legal_name: Acme Corporation
        identification_number: DE-12345678
        representatives:
          - name: John Smith
            title: Chief Executive Officer
          - name: Jane Roe
            title: Chief Financial Officer
        signature:
          mode: joint          # both must sign together
  - name: clients
    label: Clients
    parties:
      - name: john-novak
        type: natural_person
        legal_name: John Novak
        signature:
          witness: true        # personal signature, witnessed
place_of_signing: Prague
```

Renders (illustratively; layout is template-driven):

```
Place of signing: Prague

PROVIDERS — Acme Corporation

____________________________        ____________________________
John Smith                          Jane Roe
Chief Executive Officer             Chief Financial Officer
Date: ____________                  Date: ____________

CLIENTS

____________________________
John Novak
Date: ____________

Witness: ____________________
```

### B.5 Validation

| Check | Level |
|---|---|
| `signature.mode` is one of `each`, `joint`, `any` | Error |
| `signature.mode: joint` or `any` on a party with fewer than two representatives | Warning |
| `signature.witness` / `notarized` are booleans | Error |
| `place_of_signing` is a string | Error |

---

## Part C — Inline rendering of a declared party field

### C.1 Problem

`{{party:}}` resolves only to a name/label (§10.4). Notices clauses and identification blocks
("Notices to Acme shall be sent to: …", "Acme Corporation, ID DE-12345678, of 123 Main St") need the
structured `address` / `identification_number` from frontmatter. Today they must be retyped (losing
the single source of truth).

### C.2 Design — a `field` selector on `{{party:}}`

```markdown
{{party: acme, field=address}}
{{party: acme, field=identification_number}}
{{party: acme, field=legal_name}}
```

- `field=` selects a declared field of the party and renders its value verbatim.
- Permitted values: any universal/type field (`legal_name`, `address`, `identification_number`,
  `date_of_birth`) or a custom field declared on the party.
- `field=` and `label=` are **mutually exclusive** (`label` overrides display text; `field` selects a
  stored value). Without either, `{{party:}}` behaves exactly as today.
- If the named field is absent on the party, insert `[UNKNOWN PARTY FIELD: name.field]` and emit a
  validation warning.

**Example:**

```markdown
Notices to {{party: acme}} shall be delivered to {{party: acme, field=address}}.

This Agreement is entered into by {{party: acme, field=legal_name}}
(ID {{party: acme, field=identification_number}}).
```

### C.3 Validation

| Check | Level |
|---|---|
| `field` and `label` not both present on one `{{party:}}` | Error |
| `{{party:}}` `field` names a field present on the party | Warning if absent |

---

## Part D — Amendment cross-reference acknowledgment

### D.1 Problem

The amendment example writes "Section 5.1 of the Agreement is amended to read as follows" (§16.4) —
a hardcoded number, because `{{ref:}}` is internal-only and cross-document references are free text
(`amends.title` / `supersedes`). There is no way to stably target a provision of the original.

### D.2 Proposal — acknowledge, don't add machinery

Add a short note to §3.8 (and cross-reference from §7.5) stating:

> References from an amendment to provisions of the original document are necessarily expressed in the
> original's own terms (its numbering or quoted text), because `{{ref:}}` resolves only within the
> current document and cross-document references (`amends`, `supersedes`) are free text. To stay
> robust against renumbering of the original, authors SHOULD identify the amended provision by quoting
> its text or by a stable description, not by number alone. Stable cross-document targeting is a
> tooling/versioning (LeGit) concern, outside this specification.

No new directive or field. This simply sets expectations and steers authors away from number-only
references.

---

## Consolidated validation additions

| Part | Check | Level |
|---|---|---|
| A | Translation-set structural invariants (headings, ids, list-item ids, def ids, attachments, placeholders, party names/sides, types) match | Error |
| A | `authoritative` identical; party `legal_name` differs | Warning |
| B | `signature.mode` ∈ {`each`,`joint`,`any`}; booleans well-typed | Error |
| B | `joint`/`any` with < 2 representatives | Warning |
| C | `{{party:}}` `field` and `label` mutually exclusive | Error |
| C | `{{party:}}` `field` names a present field | Warning if absent |

## Summary

| Part | Change | Surface |
|---|---|---|
| A | Drop `{{lang:}}`; specify translation-file model + validation | Removes a dangling ref; expands §14 |
| B | Optional `signature` party object + 1 doc field; minimal render rules | Small, fully optional |
| C | `field=` selector on `{{party:}}` | One optional parameter |
| D | Acknowledgment note in §3.8/§7.5 | Documentation only |

## Open questions

1. **Signatures (B):** is `mode` (`each`/`joint`/`any`) the right granularity, or do you want to name
   *which specific* representatives sign jointly (a subset)? `mode` covers the common cases simply.
2. **Signatures (B):** model `witness`/`notarized` per-party (proposed) or also document-level
   defaults?
3. **Party fields (C):** restrict `field=` to a known set (`address`, `identification_number`,
   `legal_name`, `date_of_birth`) or allow any custom field too? (Proposed: allow custom too.)
4. **Bilingual (A):** require the recommended `-<lang>` filename convention, or keep it advisory?
