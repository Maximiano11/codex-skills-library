#!/usr/bin/env python3
"""Governance helpers. No target project writes or arbitrary command execution.

Assessment exit codes: 0 APROVADA, 1 REPROVADA, 2 INCOMPLETA.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.0.0'
GATES = {'requirements', 'architecture', 'implementation', 'tests',
         'security', 'documentation', 'delivery'}
STATUSES = {'passed', 'failed', 'not_applicable', 'not_verified', 'blocked'}
SURFACES = {'ui', 'form', 'api', 'business_rule', 'shared_component', 'auth',
            'authorization', 'financial', 'sensitive_data', 'migration',
            'architecture', 'breaking_contract', 'destructive', 'security',
            'performance', 'compatibility', 'portability', 'safety', 'docs'}
SENSITIVE = {'auth', 'authorization', 'financial', 'sensitive_data', 'migration',
             'architecture', 'breaking_contract', 'destructive', 'security', 'safety'}
IGNORED = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build',
           'coverage', 'output', '.next', '.vercel', 'uploads', 'vendor'}
DEFAULT_IDS = {1, 3, 9, 15, 85}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def load(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, 'Duplicate JSON key: ' + k)
            result[k] = v
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n',
                          encoding='utf-8')


def now():
    return datetime.now(timezone.utc).isoformat()


def safe_path(project, relative):
    require(nonempty(relative), 'Missing scope path')
    p = Path(relative)
    require(not p.is_absolute() and '..' not in p.parts, 'Scope path must be relative')
    require(not any(x in {'.git', 'node_modules', '.venv', 'vendor'} for x in p.parts),
            'Scope cannot include generated dependencies or Git internals')
    require(not any(x.startswith('.env') or x in {'credentials.json', 'secrets.json'}
                    or x.endswith(('.pem', '.key', '.p12')) for x in p.parts),
            'Do not include credential files in evidence scope')
    full = (project / p).resolve()
    require(full.is_relative_to(project.resolve()), 'Scope escaped project')
    require(not (project / p).is_symlink(), 'Scope symlinks are not supported')
    require(not full.exists() or full.is_file(), 'Scope must name files, not directories')
    return full


def source_state(project, files):
    require(project.is_dir(), 'Project directory does not exist')
    require(isinstance(files, list) and files and all(nonempty(p) for p in files),
            'Declare nonempty files scope')
    require(len(files) == len(set(files)), 'Duplicate scope file')
    states = {}
    for rel in sorted(files):
        p = safe_path(project, rel)
        states[rel] = sha(p) if p.is_file() else None
    try:
        rev = subprocess.check_output(['git', '-C', str(project), 'rev-parse', 'HEAD'],
                                      stderr=subprocess.PIPE, text=True, timeout=10).strip()
        dirty = bool(subprocess.check_output(['git', '-C', str(project), 'status',
                    '--porcelain', '--untracked-files=all'], text=True,
                    stderr=subprocess.PIPE, timeout=10).strip())
    except (OSError, subprocess.SubprocessError):
        rev, dirty = None, None
    return {'revision': rev, 'dirty': dirty, 'files': states}


def classify(change):
    require(isinstance(change, dict), 'Change must be an object')
    for k in ('objective', 'rationale'):
        require(nonempty(change.get(k)), 'Missing ' + k)
    for k in ('impact', 'likelihood'):
        require(type(change.get(k)) is int and 1 <= change[k] <= 3,
                k + ' must be an integer 1..3')
    surfaces = change.get('surfaces')
    require(isinstance(surfaces, list) and all(s in SURFACES for s in surfaces),
            'Invalid surfaces')
    require(len(set(surfaces)) == len(surfaces), 'Duplicate surface')
    action = change.get('action')
    require(action in {'audit', 'develop', 'prepare_release', 'deploy'}, 'Invalid action')
    files = change.get('files')
    require(isinstance(files, list) and files and all(nonempty(x) for x in files),
            'Missing files scope')
    # Conservative path hints reduce accidental underclassification; human review
    # can distinguish audit from mutation but cannot silently erase these signals.
    detected = set(surfaces)
    for rel in files:
        low = rel.lower()
        if re.search(r'(^|[/_.-])(auth|oauth|permissions?|authorization|guards?)([/_.-]|$)', low):
            detected.add('authorization')
        if re.search(r'(^|[/_.-])(migrations?)([/_.-]|$)', low):
            detected.add('migration')
    score = change['impact'] * change['likelihood']
    risk = 'low' if score <= 2 else 'medium' if score <= 4 else 'high'
    if detected & SENSITIVE or action == 'deploy':
        risk = 'high'
    if detected & {'form', 'api', 'business_rule', 'shared_component'} and risk == 'low':
        risk = 'medium'
    approvals = []
    if action != 'audit':
        approvals = sorted(detected & {'auth', 'authorization', 'migration',
                                      'architecture', 'breaking_contract',
                                      'destructive', 'security'})
    if action == 'deploy':
        approvals.append('production_deploy')
    return {'risk': risk, 'score': score, 'surfaces': sorted(detected),
            'sensitive_actions': approvals,
            'validation': {'low': 'targeted', 'medium': 'affected_integrations_regression',
                           'high': 'expanded_security_recovery_review'}[risk],
            'rationale': change['rationale']}


def criteria_for(change):
    risk = classify(change)
    surfaces = set(risk['surfaces'])
    article = load(ROOT / 'checklists/article-120.json')['criteria']
    controls = load(ROOT / 'checklists/engineering.json')['criteria']
    selected = set(DEFAULT_IDS)
    if surfaces & {'ui', 'form'}:
        selected |= {41, 42, 45, 51, 52, 55, 56}
    if surfaces & {'auth', 'authorization', 'security', 'sensitive_data', 'financial'}:
        selected |= {7, 8, 34, 35, 36}
    if surfaces & {'api', 'compatibility', 'breaking_contract'}:
        selected |= {5, 6, 109, 111, 117}
    if surfaces & {'migration', 'destructive', 'sensitive_data', 'financial'}:
        selected |= {25, 26, 31, 32, 108, 112}
    if 'performance' in surfaces:
        selected |= set(range(61, 81))
    if 'portability' in surfaces:
        selected |= {101, 102, 103, 104, 113, 114, 115, 116}
    if 'architecture' in surfaces:
        selected |= {81, 83, 84, 85, 87, 96, 100}
    require(type(change.get('full_audit', False)) is bool, 'full_audit must be boolean')
    if change.get('full_audit'):
        selected = set(range(1, 121))
    ids = {'GOV-REQ', 'GOV-ARCH', 'GOV-CODE', 'GOV-TEST', 'GOV-SEC', 'GOV-DOC',
           'GOV-DEL', 'GOV-REG'}
    triggered = set()
    for surface, name in [('ui', 'GOV-UI'), ('form', 'GOV-UI'),
                          ('auth', 'GOV-AUTH'), ('authorization', 'GOV-AUTH'),
                          ('migration', 'GOV-DATA'), ('financial', 'GOV-DATA'),
                          ('sensitive_data', 'GOV-DATA'), ('destructive', 'GOV-DATA'),
                          ('architecture', 'GOV-ADR'), ('safety', 'GOV-SAFE'),
                          ('performance', 'GOV-PERF'), ('compatibility', 'GOV-COMP'),
                          ('breaking_contract', 'GOV-COMP'), ('portability', 'GOV-PORT')]:
        if surface in surfaces:
            ids.add(name)
            triggered.add(name)
    if change.get('full_audit'):
        ids |= {x['id'] for x in controls}
    result = [{**x, 'allow_not_applicable': True}
              if change.get('full_audit') and x['id'] in {'GOV-AUTH','GOV-DATA','GOV-ADR'}
                 and x['id'] not in triggered else dict(x)
              for x in controls if x['id'] in ids]
    for item in article:
        if item['source']['question'] in selected:
            result.append({**item, 'gate': 'tests', 'allow_not_applicable': True})
    return result


def init(project, change, out):
    risk = classify(change)
    source = source_state(project, change['files'])
    require(any(v is not None for v in source['files'].values()),
            'At least one scope file must exist')
    criteria = criteria_for(change)
    out = out.resolve()
    require(not out.is_relative_to(project.resolve()), 'Evidence must be outside project')
    out.mkdir(parents=True, exist_ok=False)
    plan = {'version': 1, 'skill_version': VERSION, 'created_at': now(),
            'project': str(project.resolve()), 'source': source, 'change': change,
            'risk': risk, 'criteria': criteria,
            'catalog_hashes': {p: sha(ROOT / p) for p in
                              ['checklists/article-120.json', 'checklists/engineering.json']}}
    plan['plan_id'] = stable(plan)
    results = {'version': 1, 'plan_id': plan['plan_id'], 'authorizations': [],
               'findings': [], 'limitations': [], 'criteria': [
                   {'id': c['id'], 'status': 'not_verified', 'reason': '',
                    'evidence': []} for c in criteria]}
    write(out / 'plan.json', plan)
    write(out / 'results.json', results)
    return {'status': 'INCOMPLETA', 'plan': str(out / 'plan.json'),
            'criteria_count': len(criteria), 'risk': risk}


def evidence_ok(items, base):
    require(isinstance(items, list) and items, 'Missing evidence')
    kinds = set()
    for ev in items:
        require(isinstance(ev, dict) and ev.get('kind') in {'test', 'observation', 'review'},
                'Evidence kind must be test, observation or review')
        require(nonempty(ev.get('summary')), 'Missing observable evidence summary')
        p = Path(ev.get('path', ''))
        require(nonempty(ev.get('path')) and not p.is_absolute() and '..' not in p.parts,
                'Evidence path must be relative to results directory')
        full = (base / p).resolve()
        require(full.is_relative_to(base.resolve()) and not (base / p).is_symlink(),
                'Evidence escaped results directory')
        require(full.is_file() and full.stat().st_size > 0, 'Missing/empty evidence file')
        require(ev.get('sha256') == sha(full), 'Evidence hash mismatch')
        kinds.add(ev['kind'])
        if ev['kind'] == 'test':
            require(nonempty(ev.get('command')) and ev.get('exit_code') == 0
                    and type(ev.get('exit_code')) is int, 'Test command did not succeed')
            require(type(ev.get('tests_run')) is int and ev['tests_run'] > 0,
                    'Test evidence must record executed cases')
            require(all(type(ev.get(k)) is int and ev[k] == 0
                        for k in ('failures', 'errors', 'skipped')), 'Test did not fully pass')
    return kinds


def release_evidence(plan, record, base):
    """Validate the strict runner artifact, its logs and its native test reports."""
    require(isinstance(record, dict) and nonempty(record.get('path')),
            'Release needs the strict runner report')
    relative = Path(record['path'])
    require(not relative.is_absolute() and '..' not in relative.parts,
            'Release report must be relative to results directory')
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()) and path.is_file() and
            record.get('sha256') == sha(path), 'Invalid release report or digest')
    report = load(path)
    require(report.get('status') == 'APROVADO', 'Strict release runner did not pass')
    require(Path(report.get('repository', '')).resolve() == Path(plan['project']).resolve(),
            'Release report belongs to another repository')
    require(plan['source']['revision'] is not None and plan['source']['dirty'] is False,
            'Release requires a reviewed clean Git revision')
    require(report.get('source') == {k: plan['source'][k] for k in ('revision', 'dirty')},
            'Release report belongs to another revision')
    require(report.get('review', {}).get('completed') is True and
            report['review'].get('revision') == plan['source']['revision'],
            'Release review is incomplete or stale')
    review_file = safe_path(Path(plan['project']), report['review'].get('evidence'))
    require(review_file.is_file() and report.get('review_evidence_sha256') == sha(review_file),
            'Release review evidence changed')
    require(report.get('blocking_findings') == [], 'Release has blocking findings')
    checks = report.get('checks')
    require(isinstance(checks, list) and checks, 'Missing strict release checks')
    require({c.get('kind') for c in checks} == {'build','lint','types','tests','regression'},
            'Missing release check category')
    names = [c.get('id') for c in checks]
    require(all(nonempty(x) for x in names) and len(set(names)) == len(names),
            'Missing/duplicate release check id')
    spec = importlib.util.spec_from_file_location('governance_release_gate', ROOT / 'scripts/release_gate.py')
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    for check in checks:
        if check.get('status') == 'NOT_APPLICABLE':
            require(check['kind'] not in {'tests', 'regression'} and nonempty(check.get('reason')),
                    'Release test cannot be waived')
            continue
        require(check.get('status') == 'PASSED' and check.get('exit_code') == 0,
                'Strict release check did not pass')
        log = Path(check.get('log', '')).resolve()
        require(log.is_relative_to(path.parent) and log.is_file() and
                sha(log) == check.get('log_sha256'), 'Release log missing/changed')
        if check['kind'] in {'tests', 'regression'}:
            junit = Path(check.get('junit', '')).resolve()
            require(junit.is_relative_to(path.parent) and junit.is_file() and
                    sha(junit) == check.get('junit_sha256'), 'Release JUnit missing/changed')
            require(runner.junit_counts(junit) == check.get('counts'), 'Release test counts differ')


def assess(plan, results, base):
    require(plan.get('version') == results.get('version') == 1, 'Unsupported schema')
    require(plan.get('plan_id') == stable({k: v for k, v in plan.items() if k != 'plan_id'}),
            'Plan was modified; create a new evaluation')
    require(results.get('plan_id') == plan['plan_id'], 'Results belong to another plan')
    for p, expected in plan['catalog_hashes'].items():
        require(sha(ROOT / p) == expected, 'Catalog changed; create a new plan')
    require(plan['criteria'] == criteria_for(plan['change']), 'Plan criteria inconsistent')
    require(plan['risk'] == classify(plan['change']), 'Plan risk inconsistent')
    require(source_state(Path(plan['project']), plan['change']['files']) == plan['source'],
            'Source changed; create a new plan for final source state')
    records = results.get('criteria')
    require(isinstance(records, list), 'Missing criteria results')
    require(all(isinstance(r, dict) and nonempty(r.get('id')) for r in records),
            'Invalid criterion result')
    indexed = {r['id']: r for r in records}
    require(len(indexed) == len(records), 'Duplicate criterion result')
    require(set(indexed) == {c['id'] for c in plan['criteria']},
            'Missing or unexpected criterion result')
    require({c['gate'] for c in plan['criteria']} == GATES, 'All seven gates are required')
    blockers, pending = [], []
    for c in plan['criteria']:
        r = indexed[c['id']]
        status = r.get('status')
        require(status in STATUSES, 'Unknown status: ' + c['id'])
        if status == 'failed':
            require(nonempty(r.get('reason')), 'Failure needs reason')
            blockers.append(c['id'])
        elif status in {'not_verified', 'blocked'}:
            pending.append(c['id'])
        elif status == 'not_applicable':
            require(c['allow_not_applicable'], 'Essential control cannot be waived: ' + c['id'])
            require(nonempty(r.get('reason')), 'N/A requires justification')
            evidence_ok(r.get('evidence'), base)
        elif status == 'passed':
            kinds = evidence_ok(r.get('evidence'), base)
            if c['id'] == 'GOV-TEST':
                require(kinds & {'test', 'observation'}, 'A review is not an executed verification')
                if plan['risk']['risk'] != 'low' or plan['change']['action'] in {'prepare_release', 'deploy'}:
                    require('test' in kinds, 'Functional/high-risk/release work requires executed test evidence')
        if 'rating' in r:
            require(type(r['rating']) is int and 1 <= r['rating'] <= 5
                    and nonempty(r.get('rubric')), 'Rating needs integer 1..5 and prior rubric')
    findings = results.get('findings')
    require(isinstance(findings, list), 'Findings inventory required')
    seen = set()
    for f in findings:
        require(isinstance(f, dict) and nonempty(f.get('id')) and f['id'] not in seen,
                'Missing/duplicate finding id')
        seen.add(f['id'])
        require(f.get('severity') in {'P0', 'P1', 'P2', 'P3'} and
                f.get('status') in {'open', 'resolved'} and nonempty(f.get('evidence')),
                'Invalid finding')
        if f['status'] == 'open':
            if f['severity'] in {'P0', 'P1'}:
                blockers.append(f['id'])
            if f['severity'] == 'P2':
                require(f.get('decision') in {'block', 'accept'} and
                        nonempty(f.get('owner')) and nonempty(f.get('rationale')),
                        'Open P2 requires decision, owner and rationale')
                if f['decision'] == 'block':
                    blockers.append(f['id'])
    auths = results.get('authorizations')
    require(isinstance(auths, list), 'Authorizations must be a list')
    for action in plan['risk']['sensitive_actions']:
        matching = [a for a in auths if isinstance(a, dict) and a.get('action') == action
                    and a.get('status') == 'granted' and nonempty(a.get('user_source'))
                    and nonempty(a.get('scope'))]
        if not matching:
            pending.append('authorization:' + action)
    if plan['change']['action'] in {'prepare_release', 'deploy'}:
        if results.get('release_report') is None:
            pending.append('strict_release_report')
        else:
            release_evidence(plan, results['release_report'], base)
    require(isinstance(results.get('limitations'), list) and
            all(nonempty(x) for x in results['limitations']), 'Invalid limitations')
    status = 'REPROVADA' if blockers else 'INCOMPLETA' if pending else 'APROVADA'
    return {'status': status, 'scope': 'incremental_assessment_not_deployment_permission',
            'risk': plan['risk']['risk'], 'plan_id': plan['plan_id'],
            'assessed_at': now(), 'blocking': blockers, 'pending': pending,
            'counts': dict(Counter(r['status'] for r in records)),
            'limitations': results['limitations'],
            'trust_limit': 'Local records and hashes do not authenticate a reviewer or prove factual claims.'}


def discover(project):
    require(project.is_dir(), 'Project does not exist')
    files, manifests, scripts = [], [], {}
    capped = False
    for directory, dirs, names in os.walk(project, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED and
                         not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            p = Path(directory) / name
            if p.is_symlink() or name.startswith('.env') or name.endswith(('.pem', '.key', '.p12')):
                continue
            rel = str(p.relative_to(project))
            files.append(rel)
            if name in {'package.json', 'pyproject.toml', 'pom.xml', 'build.gradle',
                        'build.gradle.kts', 'go.mod', 'Cargo.toml', 'composer.json'}:
                manifests.append(rel)
                if name == 'package.json' and p.stat().st_size < 1_000_000:
                    try:
                        data = load(p)
                        scripts[rel] = {'scripts': data.get('scripts', {}),
                                        'engines': data.get('engines', {})}
                    except (OSError, ValueError, AttributeError):
                        scripts[rel] = {'parse_error': True}
            if len(files) >= 10000:
                capped = True
                break
        if capped:
            break
    return {'project': str(project.resolve()), 'read_only': True, 'truncated': capped,
            'manifests': manifests, 'package_scripts_not_executed': scripts,
            'instruction_files': [p for p in files if Path(p).name in {'AGENTS.md', 'AGENTS.override.md'}],
            'tests': [p for p in files if re.search(r'(^|/)(tests?|__tests__)/|[._-](test|spec)[._-]|(^|/)test_[^/]+\.py$', p)],
            'ci': [p for p in files if p.startswith('.github/workflows/') or
                   Path(p).name in {'.gitlab-ci.yml', 'Jenkinsfile', 'azure-pipelines.yml'}],
            'documentation': [p for p in files if p.endswith('.md')],
            'note': 'Inventory is not architecture, test execution, coverage or security proof.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    d = commands.add_parser('discover'); d.add_argument('--project', type=Path, required=True)
    r = commands.add_parser('risk'); r.add_argument('--change', type=Path, required=True)
    i = commands.add_parser('init')
    i.add_argument('--project', type=Path, required=True)
    i.add_argument('--change', type=Path, required=True)
    i.add_argument('--out', type=Path, required=True)
    a = commands.add_parser('assess')
    a.add_argument('--plan', type=Path, required=True)
    a.add_argument('--results', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'discover': result = discover(args.project.resolve())
        elif args.command == 'risk': result = classify(load(args.change))
        elif args.command == 'init': result = init(args.project.resolve(), load(args.change), args.out)
        else: result = assess(load(args.plan), load(args.results), args.results.resolve().parent)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == 'assess':
            return {'APROVADA': 0, 'REPROVADA': 1, 'INCOMPLETA': 2}[result['status']]
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(json.dumps({'status': 'INCOMPLETA', 'reason': str(error)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
