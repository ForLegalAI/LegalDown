#!/usr/bin/env python3
"""Self-check for the LegalDown fixtures corpus.

This does NOT validate LegalDown documents — that is an implementation's job.
It checks that the corpus itself is well-formed and honest:

  * every fixture directory names a rule id defined in specification §15.1
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


def spec_rule_ids():
    text = open(os.path.join(REPO, 'spec', 'legaldown-spec.md'), encoding='utf-8').read()
    section = text[text.index('### 15.1 Validation'):text.index('## 16. Conformance')]
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
            problems.append('%s: not a rule id defined in §15' % rule)
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

    manifest_path = os.path.join(ROOT, 'coverage.json')
    if os.path.exists(manifest_path):
        manifest = json.load(open(manifest_path, encoding='utf-8'))
        if set(manifest.get('covered', [])) != covered:
            problems.append('coverage.json "covered" does not match the directories on disk')
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
