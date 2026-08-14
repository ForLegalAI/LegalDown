# LegalDown Validation Fixtures

A conformance test corpus for LegalDown validators. Each fixture is a document engineered to
exercise one validation rule from [specification §15](../spec/legaldown-spec.md), paired with the
diagnostic a conforming validator must produce.

This corpus is part of the **specification**, not of any implementation: it is the operational
definition of what the §15 rules mean, so every implementation can verify against neutral ground.
It is licensed under [CC BY 4.0](../LICENSE) like the rest of this repository, and may be used by
implementations under any license.

---

## Layout

```
fixtures/
  valid/                       documents that MUST produce no Errors
    <case>.lgd
    <case>.expected.json
  invalid/
    <rule-id>/                 one directory per §15 rule id
      <case>.lgd               single-file case
      <case>.expected.json
    <rule-id>/                 multi-file case
      main.lgd                 entry point named by "entry"
      <supporting files>
      expected.json
```

Directory names are **rule ids** as defined in §15.1 — stable identifiers that survive section
renumbering.

## Expectation format

```json
{
  "entry": "main.lgd",
  "diagnostics": [
    { "rule": "heading-skip", "level": "error", "line": 7 }
  ],
  "exhaustive": false,
  "requires_level": "core",
  "spec": "§15.2",
  "note": "Level 1 followed by level 3 with no intervening level 2."
}
```

| Field | Meaning |
|---|---|
| `entry` | File the validator is pointed at. Optional for single-file cases (defaults to the sibling `.lgd`) |
| `diagnostics` | Diagnostics that MUST appear. Matching is on `rule` + `level` (+ `line` when given) |
| `exhaustive` | When `true`, the listed diagnostics are the **only** ones permitted. Default `false` |
| `requires_level` | Lowest conformance level (§16) that can evaluate the case: `core`, `rendering`, or `full` |
| `requires_config` | Optional. Configuration the case depends on, e.g. `{"document_root": "."}` (paths relative to the case directory). Runners that cannot supply it skip the case and report it as skipped |
| `spec` | Section the rule is defined in — informational |
| `note` | Why the case trips the rule — informational |

**Message text is never asserted.** §15.9 leaves diagnostic wording to implementations; a fixture
that pinned message strings would fail conformant validators. Only rule id, severity, and location
are normative.

**`exhaustive` defaults to `false`** because a document that violates one rule frequently trips
adjacent advisory checks — an unreferenced definition, an absent `sides` block. Cases that are
genuinely isolated set it to `true`.

## Running the corpus

Implementations supply their own runner; this repository defines the data, not the harness. A
runner must:

1. For each `valid/` case — validate and assert **no Error-level diagnostics**.
2. For each `invalid/` case — validate `entry` and assert every listed diagnostic is present,
   matching on rule id and level (and line, where given). With `exhaustive: true`, assert nothing
   else is reported.
3. Skip any case whose `requires_level` exceeds the implementation's claimed conformance level, and
   report it as skipped rather than passed — §16.5 forbids reporting checks that were not run.

## Coverage

**95 of the 98 rules in §15 have fixtures.** The remaining three are recorded in
[`coverage.json`](coverage.json) with a reason, so the corpus never implies coverage it does not
have:

| Rule | Why there is no fixture |
|---|---|
| `ref-not-enumerated` | Depends on the active style template rather than the document; evaluated from the Rendering level (§16.3) |
| `anchor-autogen-collision` | Implementations resolve it silently by appending numeric suffixes, so it is observable through generated identifiers rather than a diagnostic on a document |
| `legaldown-version-newer` | Depends on which specification version the implementation supports, not on the document |

`coverage.json` is the machine-readable form, and every rule id in §15 appears in exactly one of its
three lists.

## Checking the corpus itself

[`verify.py`](verify.py) checks that the corpus is well-formed and honest — that every directory
names a real §15 rule id, every expectation has the required fields and legal values, every
referenced file exists, every asserted line is in range and not blank, and `coverage.json` matches
what is on disk. It does **not** validate LegalDown documents; that is an implementation's job.

```
$ python fixtures/verify.py
OK — corpus is self-consistent
```

Run it after editing fixtures, and after any change to the §15 tables — it will catch a rule id
that was renamed out from under a fixture directory.
