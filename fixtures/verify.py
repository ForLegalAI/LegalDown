#!/usr/bin/env python3
"""Self-check for the LegalDown fixtures corpus.

This does NOT validate LegalDown documents — that is an implementation's job.
It checks that the corpus itself is well-formed and honest:

  * every fixture directory names a rule id defined in specification §16.1
  * every expectation file has the required fields and legal values
  * every referenced file exists and every asserted line is in range and non-blank
  * coverage.json matches what is actually on disk

Run from the repository root:  python fixtures/verify.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
LEVELS = {'error', 'warning', 'info'}
TIERS = {'core', 'rendering', 'full'}
CAPABILITIES = {'assembly'}
ASSEMBLY_INPUTS = ('template.lgd', 'answers.yaml')
# Template constructs that must not survive assembly. Body patterns ignore escaped text
# (assembly escapes every inserted "{", so a literal "\{when=" in expected output is correct);
# the attachment "when:" entry is looked for in frontmatter only.
BODY_MARKERS = (
    ('a when= condition', re.compile(r'(?<!\\)\{[^{}\n]*\bwhen=')),
    ('a {{choose:}} directive', re.compile(r'(?<!\\)\{\{choose:')),
    ('a drafting note', re.compile(r'^[ \t]*>[ \t]*\[!drafting\]', re.I | re.M)),
)
FRONTMATTER_MARKERS = (
    ('a questions entry', re.compile(r'^questions:', re.M)),
    ('an attachment when entry', re.compile(r'^[ \t]+when:', re.M)),
)


def spec_rule_ids():
    text = open(os.path.join(REPO, 'spec', 'legaldown-spec.md'), encoding='utf-8').read()
    section = text[text.index('### 16.1 Validation'):text.index('## 17. Conformance')]
    ids = set(re.findall(r'^\| `([a-z0-9-]+)` \|', section, re.M))
    ids |= set(re.findall(r'rule id `([a-z0-9-]+)`', section))
    return ids


def check():
    problems = []
    known = spec_rule_ids()
    if not known:
        return ['could not extract rule ids from the specification']

    covered = set()
    for rule in sorted(os.listdir(os.path.join(ROOT, 'invalid'))):
        d = os.path.join(ROOT, 'invalid', rule)
        if not os.path.isdir(d):
            continue
        covered.add(rule)
        if rule not in known:
            problems.append('%s: not a rule id defined in §16' % rule)
        expectations = [f for f in os.listdir(d) if f.endswith('.json')]
        if not expectations:
            problems.append('%s: no expectation file' % rule)
        for name in expectations:
            exp = json.load(open(os.path.join(d, name), encoding='utf-8'))
            for key in ('diagnostics', 'exhaustive', 'requires_level'):
                if key not in exp:
                    problems.append('%s/%s: missing "%s"' % (rule, name, key))
            if exp.get('requires_level') not in TIERS:
                problems.append('%s/%s: requires_level %r not in %s'
                                % (rule, name, exp.get('requires_level'), sorted(TIERS)))
            cap = exp.get('requires_capability')
            if cap is not None and cap not in CAPABILITIES:
                problems.append('%s/%s: requires_capability %r not in %s'
                                % (rule, name, cap, sorted(CAPABILITIES)))
            config = exp.get('requires_config', {})
            if not isinstance(config, dict):
                problems.append('%s/%s: requires_config must be an object' % (rule, name))
                config = {}
            answers = config.get('answers')
            if cap == 'assembly' and not answers:
                problems.append('%s/%s: an assembly case must name its answers set in '
                                'requires_config.answers' % (rule, name))
            if answers and cap != 'assembly':
                problems.append('%s/%s: a case with an answers set must declare '
                                'requires_capability: "assembly"' % (rule, name))
            if answers and not os.path.exists(os.path.join(d, answers)):
                problems.append('%s/%s: answers set %s does not exist' % (rule, name, answers))
            if 'final' in config and config['final'] is not True:
                problems.append('%s/%s: requires_config.final must be true' % (rule, name))
            if not exp.get('diagnostics'):
                problems.append('%s/%s: no diagnostics asserted' % (rule, name))
            for diag in exp.get('diagnostics', []):
                if diag.get('level') not in LEVELS:
                    problems.append('%s/%s: level %r not in %s'
                                    % (rule, name, diag.get('level'), sorted(LEVELS)))
                if diag.get('rule') not in known:
                    problems.append('%s/%s: asserts unknown rule %r'
                                    % (rule, name, diag.get('rule')))
                target = diag.get('file') or exp.get('entry') or name.replace('.expected.json', '.lgd')
                path = os.path.join(d, target)
                if not os.path.exists(path):
                    problems.append('%s/%s: target %s does not exist' % (rule, name, target))
                    continue
                if 'line' in diag:
                    lines = open(path, encoding='utf-8').read().split('\n')
                    n = diag['line']
                    if not 1 <= n <= len(lines):
                        problems.append('%s/%s: line %d out of range in %s' % (rule, name, n, target))
                    elif not lines[n - 1].strip():
                        problems.append('%s/%s: line %d is blank in %s' % (rule, name, n, target))

    for name in sorted(os.listdir(os.path.join(ROOT, 'valid'))):
        if not name.endswith('.lgd'):
            continue
        exp_path = os.path.join(ROOT, 'valid', name.replace('.lgd', '.expected.json'))
        if not os.path.exists(exp_path):
            problems.append('valid/%s: no expectation file' % name)
            continue
        exp = json.load(open(exp_path, encoding='utf-8'))
        errors = [d for d in exp.get('diagnostics', []) if d.get('level') == 'error']
        if errors:
            problems.append('valid/%s: asserts Error-level diagnostics' % name)

    assembly = os.path.join(ROOT, 'assembly')
    for case in sorted(os.listdir(assembly)) if os.path.isdir(assembly) else []:
        d = os.path.join(assembly, case)
        if not os.path.isdir(d):
            continue
        for f in ASSEMBLY_INPUTS:
            if not os.path.exists(os.path.join(d, f)):
                problems.append('assembly/%s: missing %s' % (case, f))
        case_file = os.path.join(d, 'case.json')
        if os.path.exists(case_file):
            meta = json.load(open(case_file, encoding='utf-8'))
            if meta.get('requires_level', 'core') not in TIERS:
                problems.append('assembly/%s: case.json requires_level %r not in %s'
                                % (case, meta.get('requires_level'), sorted(TIERS)))
        # Output is either a single expected.lgd, or an expected/ tree holding every output file
        # (template.lgd plus fragments and LegalDown attachment files at their relative paths).
        single = os.path.join(d, 'expected.lgd')
        tree = os.path.join(d, 'expected')
        if os.path.isdir(tree):
            if os.path.exists(single):
                problems.append('assembly/%s: has both expected.lgd and expected/' % case)
            if not os.path.exists(os.path.join(tree, 'template.lgd')):
                problems.append('assembly/%s: expected/ has no template.lgd' % case)
            outputs = []
            for root, _, files in os.walk(tree):
                for f in files:
                    path = os.path.join(root, f)
                    rel = os.path.relpath(path, tree)
                    outputs.append((rel, path))
                    if rel != 'template.lgd' and not os.path.exists(os.path.join(d, rel)):
                        problems.append('assembly/%s: expected/%s has no input file %s'
                                        % (case, rel, rel))
        elif os.path.exists(single):
            outputs = [('template.lgd', single)]
        else:
            problems.append('assembly/%s: missing expected.lgd or expected/' % case)
            outputs = []
        for rel, path in sorted(outputs):
            text = open(path, encoding='utf-8').read()
            if text == '':
                continue  # an emptied file is written as zero bytes (§15.7.2 step 8)
            front, body = '', text
            if text.startswith('---\n') and '\n---\n' in text[4:]:
                end = text.index('\n---\n', 4)
                front, body = text[4:end + 1], text[end + 5:]
            for label, pattern in BODY_MARKERS:
                if pattern.search(body):
                    problems.append('assembly/%s: %s still contains %s' % (case, rel, label))
            for label, pattern in FRONTMATTER_MARKERS:
                if pattern.search(front):
                    problems.append('assembly/%s: %s still contains %s' % (case, rel, label))
            if not text.endswith('\n') or text.endswith('\n\n'):
                problems.append('assembly/%s: %s must end with exactly one line break'
                                % (case, rel))

    manifest_path = os.path.join(ROOT, 'coverage.json')
    if os.path.exists(manifest_path):
        manifest = json.load(open(manifest_path, encoding='utf-8'))
        if set(manifest.get('covered', [])) != covered:
            problems.append('coverage.json "covered" does not match the directories on disk')
        if manifest.get('total_rules') != len(known):
            problems.append('coverage.json total_rules is %r, but §16 defines %d rule ids'
                            % (manifest.get('total_rules'), len(known)))
        claimed = covered | set(manifest.get('not_yet_covered', [])) \
            | set(manifest.get('not_mechanically_testable', {}))
        if claimed != known:
            missing = sorted(known - claimed)
            extra = sorted(claimed - known)
            if missing:
                problems.append('coverage.json omits rule ids: %s' % ', '.join(missing))
            if extra:
                problems.append('coverage.json lists unknown rule ids: %s' % ', '.join(extra))
    else:
        problems.append('coverage.json is missing')

    return problems


if __name__ == '__main__':
    found = check()
    if found:
        print('FAIL — %d problem(s):' % len(found))
        for p in found:
            print('  -', p)
        sys.exit(1)
    print('OK — corpus is self-consistent')
