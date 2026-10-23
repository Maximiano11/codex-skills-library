"""Execute helpers against isolated fixtures; never use the user's real projects."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('governance', ROOT / 'scripts/governance.py')
gov = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gov)


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.project = self.base / 'project'
        self.project.mkdir()
        (self.project / 'app.py').write_text('def answer():\n    return 42\n')
        self.change = {'objective': 'Repair isolated fixture', 'rationale': 'Small isolated function',
                       'impact': 1, 'likelihood': 1, 'action': 'develop',
                       'surfaces': [], 'files': ['app.py']}

    def evaluation(self, change=None):
        out = self.base / 'evaluation'
        gov.init(self.project, change or self.change, out)
        return gov.load(out / 'plan.json'), gov.load(out / 'results.json'), out

    def complete(self, results, base):
        # A real assertion is executed in a subprocess; the captured log is the
        # evidence for this synthetic evaluation, not for any production product.
        command = [sys.executable, '-c',
                   "from pathlib import Path; exec(Path('app.py').read_text()); assert answer() == 42; print('1 assertion passed')"]
        proc = subprocess.run(command, cwd=self.project, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        artifact = base / 'observation.log'
        artifact.write_text(proc.stdout + proc.stderr)
        for r in results['criteria']:
            r.update(status='passed', reason='Synthetic gate fixture evaluation', evidence=[{
                'kind': 'test' if r['id'] == 'GOV-TEST' else 'review',
                'path': 'observation.log', 'sha256': gov.sha(artifact),
                'summary': 'Isolated helper contract assertion executed',
                'command': ' '.join(command), 'exit_code': proc.returncode,
                'tests_run': 1, 'failures': 0, 'errors': 0, 'skipped': 0}])
        return results

    def assess(self, p, r, base):
        return gov.assess(p, r, base)

    def test_ten_requested_scenarios(self):
        cases = gov.load(ROOT / 'tests/fixtures/scenarios.json')
        self.assertEqual(len(cases), 10)
        for case in cases:
            with self.subTest(case=case['id']):
                project = self.base / case['id']; project.mkdir()
                path = project / case['file']; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(case['content'])
                change = {**self.change, **{k: case[k] for k in
                          ['impact', 'likelihood', 'action', 'surfaces']}, 'files': [case['file']]}
                before = path.read_bytes()
                risk = gov.classify(change)
                self.assertEqual(risk['risk'], case['expected_risk'])
                self.assertIn(case['required_control'], {c['id'] for c in gov.criteria_for(change)})
                if case['sensitive_action']:
                    self.assertIn(case['sensitive_action'], risk['sensitive_actions'])
                out = self.base / (case['id'] + '-assessment')
                gov.init(project, change, out)
                report = gov.assess(gov.load(out / 'plan.json'), gov.load(out / 'results.json'), out)
                self.assertEqual(report['status'], 'INCOMPLETA')
                self.assertEqual(path.read_bytes(), before)
                if case['id'] == 'no-tests':
                    self.assertEqual(gov.discover(project)['tests'], [])

    def test_executed_evidence_allows_incremental_approval(self):
        p, r, b = self.evaluation()
        self.assertEqual(self.assess(p, self.complete(r, b), b)['status'], 'APROVADA')

    def test_known_failure_overrides_other_pending(self):
        p, r, b = self.evaluation()
        r['criteria'][0].update(status='failed', reason='Observed acceptance failure')
        self.assertEqual(self.assess(p, r, b)['status'], 'REPROVADA')

    def test_high_rating_does_not_hide_failure(self):
        p, r, b = self.evaluation(); self.complete(r, b)
        r['criteria'][0].update(status='failed', reason='Failure', rating=5, rubric='Defined before review')
        self.assertEqual(self.assess(p, r, b)['status'], 'REPROVADA')

    def test_unexecuted_or_blocked_is_incomplete(self):
        for state in ['not_verified', 'blocked']:
            with self.subTest(state=state):
                p, r, b = self.evaluation() if state == 'not_verified' else (p, r, b)
                r['criteria'][0]['status'] = state
                self.assertEqual(self.assess(p, r, b)['status'], 'INCOMPLETA')

    def test_no_evidence_cannot_pass(self):
        p, r, b = self.evaluation()
        r['criteria'][0]['status'] = 'passed'
        with self.assertRaises(ValueError): self.assess(p, r, b)

    def test_review_is_not_executed_test(self):
        p, r, b = self.evaluation(); self.complete(r, b)
        next(c for c in r['criteria'] if c['id'] == 'GOV-TEST')['evidence'][0]['kind'] = 'review'
        with self.assertRaises(ValueError): self.assess(p, r, b)

    def test_skips_or_zero_cases_cannot_pass(self):
        p, r, b = self.evaluation(); self.complete(r, b)
        evidence = next(c for c in r['criteria'] if c['id'] == 'GOV-TEST')['evidence'][0]
        evidence['skipped'] = 1
        with self.assertRaises(ValueError): self.assess(p, r, b)
        evidence['skipped'] = 0; evidence['tests_run'] = 0
        with self.assertRaises(ValueError): self.assess(p, r, b)

    def test_missing_or_duplicate_criteria_rejected(self):
        p, r, b = self.evaluation()
        bad = copy.deepcopy(r); bad['criteria'].pop()
        with self.assertRaises(ValueError): self.assess(p, bad, b)
        r['criteria'].append(r['criteria'][0])
        with self.assertRaises(ValueError): self.assess(p, r, b)

    def test_plan_or_source_tampering_rejected(self):
        p, r, b = self.evaluation()
        bad = copy.deepcopy(p); bad['criteria'].pop()
        with self.assertRaises(ValueError): self.assess(bad, r, b)
        (self.project / 'app.py').write_text('def answer(): return 0\n')
        with self.assertRaises(ValueError): self.assess(p, r, b)

    def test_changed_evidence_rejected(self):
        p, r, b = self.evaluation(); self.complete(r, b)
        (b / 'observation.log').write_text('modified evidence')
        with self.assertRaises(ValueError): self.assess(p, r, b)

    def test_na_requires_reason_and_review(self):
        p, r, b = self.evaluation(); self.complete(r, b)
        item = next(c for c in r['criteria'] if c['id'] == 'GOV-DOC')
        item.update(status='not_applicable', reason='')
        with self.assertRaises(ValueError): self.assess(p, r, b)
        item['reason'] = 'No documented behavior changed in fixture'
        self.assertEqual(self.assess(p, r, b)['status'], 'APROVADA')

    def test_essential_control_cannot_be_waived(self):
        p, r, b = self.evaluation(); self.complete(r, b)
        r['criteria'][0].update(status='not_applicable', reason='Trying to bypass requirements')
        with self.assertRaises(ValueError): self.assess(p, r, b)

    def test_critical_finding_blocks_otherwise_green(self):
        p, r, b = self.evaluation(); self.complete(r, b)
        for severity in ['P0', 'P1']:
            r['findings'] = [{'id': 'issue', 'severity': severity, 'status': 'open', 'evidence': 'Observed issue'}]
            self.assertEqual(self.assess(p, r, b)['status'], 'REPROVADA')

    def test_p2_needs_recorded_decision(self):
        p, r, b = self.evaluation(); self.complete(r, b)
        r['findings'] = [{'id':'issue','severity':'P2','status':'open','evidence':'Observed secondary issue'}]
        with self.assertRaises(ValueError): self.assess(p, r, b)
        r['findings'][0].update(decision='accept', owner='Fixture reviewer', rationale='Accepted fixture tradeoff')
        self.assertEqual(self.assess(p, r, b)['status'], 'APROVADA')

    def test_deploy_needs_real_authorization_record(self):
        p, r, b = self.evaluation({**self.change, 'action': 'deploy'}); self.complete(r, b)
        report = self.assess(p, r, b)
        self.assertEqual(report['status'], 'INCOMPLETA')
        self.assertIn('authorization:production_deploy', report['pending'])
        r['authorizations'] = [{'action': 'production_deploy', 'status': 'granted'}]
        self.assertEqual(self.assess(p, r, b)['status'], 'INCOMPLETA')

    def test_medium_risk_observation_cannot_replace_executed_tests(self):
        p, r, b = self.evaluation({**self.change, 'surfaces':['form'], 'impact':2})
        self.complete(r, b)
        next(c for c in r['criteria'] if c['id']=='GOV-TEST')['evidence'][0]['kind']='observation'
        with self.assertRaises(ValueError): self.assess(p,r,b)

    def test_release_assessment_needs_strict_runner(self):
        p,r,b=self.evaluation({**self.change,'action':'prepare_release'})
        self.complete(r,b)
        report=self.assess(p,r,b)
        self.assertEqual(report['status'],'INCOMPLETA')
        self.assertIn('strict_release_report',report['pending'])

    def test_release_assessment_accepts_real_runner_and_rejects_changed_artifacts(self):
        git=lambda *args: subprocess.check_output(['git','-C',str(self.project),*args],text=True,stderr=subprocess.PIPE).strip()
        git('init','-q')
        (self.project/'review.md').write_text('Actual review of this disposable helper fixture.\n')
        tspec=importlib.util.spec_from_file_location('contract_fixture',ROOT/'scripts/test_release_gate.py')
        tmod=importlib.util.module_from_spec(tspec);tspec.loader.exec_module(tmod)
        (self.project/'fixture.py').write_text(tmod.FIXTURE)
        git('add','.')
        git('-c','user.name=Fixture','-c','user.email=qa@example.invalid','-c','commit.gpgsign=false','commit','-qm','Fixture')
        p,r,b=self.evaluation({**self.change,'action':'prepare_release'})
        self.complete(r,b)
        policy={'version':1,'review':{'completed':True,'revision':git('rev-parse','HEAD'),
                'evidence':'review.md','limitations':[],'findings':[]},'checks':[
            {'id':'build','kind':'build','argv':[sys.executable,'-c',"import ast;from pathlib import Path;ast.parse(Path('app.py').read_text())"]},
            {'id':'lint','kind':'lint','not_applicable':'No linter in fixture'},
            {'id':'types','kind':'types','not_applicable':'No type checker in fixture'},
            {'id':'tests','kind':'tests','argv':[sys.executable,'fixture.py','pass'],'junit':'junit.xml'},
            {'id':'regression','kind':'regression','argv':[sys.executable,'fixture.py','pass'],'junit':'junit.xml'}]}
        gov.write(b/'policy.json',policy)
        proc=subprocess.run([sys.executable,str(ROOT/'scripts/release_gate.py'),'--repo',str(self.project),'--policy',str(b/'policy.json'),'--out',str(b/'strict-run')],capture_output=True,text=True,timeout=20)
        self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
        r['release_report']={'path':'strict-run/report.json','sha256':gov.sha(b/'strict-run/report.json')}
        self.assertEqual(self.assess(p,r,b)['status'],'APROVADA')
        (b/'strict-run/tests/junit.xml').write_text('<testsuite/>')
        with self.assertRaises(ValueError):self.assess(p,r,b)

    def test_audit_of_auth_requires_no_mutation_approval(self):
        risk = gov.classify({**self.change, 'action': 'audit', 'surfaces': ['auth']})
        self.assertEqual(risk['risk'], 'high'); self.assertEqual(risk['sensitive_actions'], [])

    def test_path_hints_catch_underdeclared_auth_and_migration(self):
        for path, surface in [('src/auth/guard.ts','authorization'), ('prisma/migrations/a.sql','migration')]:
            risk = gov.classify({**self.change, 'files':[path]})
            self.assertEqual(risk['risk'], 'high'); self.assertIn(surface, risk['surfaces'])

    def test_invalid_risk_inputs_do_not_default_low(self):
        for patch in [{'impact':True}, {'likelihood':0}, {'surfaces':['unknown']}, {'rationale':''}, {'files':[]}]:
            with self.assertRaises(ValueError): gov.classify({**self.change, **patch})

    def test_scope_escape_secrets_and_empty_scope_rejected(self):
        for files in [['../outside'], ['.env'], ['x.pem'], ['/tmp/absolute'], ['missing.py']]:
            with self.assertRaises(ValueError):
                gov.init(self.project, {**self.change, 'files':files}, self.base / 'bad')

    def test_symlink_scope_and_evidence_rejected(self):
        target = self.base / 'external.py'; target.write_text('secret')
        (self.project / 'link.py').symlink_to(target)
        with self.assertRaises(ValueError):
            gov.source_state(self.project, ['link.py'])
        p, r, b = self.evaluation(); self.complete(r, b)
        artifact = b / 'observation.log'; artifact.unlink(); artifact.symlink_to(target)
        with self.assertRaises(ValueError): self.assess(p, r, b)

    def test_output_cannot_modify_audited_project(self):
        with self.assertRaises(ValueError): gov.init(self.project, self.change, self.project / 'assessment')
        self.assertFalse((self.project / 'assessment').exists())

    def test_inventory_excludes_secrets_and_does_not_run_scripts(self):
        (self.project / 'package.json').write_text(json.dumps({'scripts':{'test':'touch PWNED'}}))
        (self.project / '.env').write_text('synthetic-secret-not-for-output')
        (self.project / 'node_modules').mkdir(); (self.project / 'node_modules/test.ts').write_text('x')
        data = gov.discover(self.project)
        self.assertIn('package.json', data['manifests'])
        self.assertNotIn('.env', json.dumps(data)); self.assertNotIn('node_modules/test.ts', data['tests'])
        self.assertFalse((self.project / 'PWNED').exists())

    def test_article_coverage_and_provenance(self):
        data = gov.load(ROOT / 'checklists/article-120.json')
        self.assertEqual([c['source']['question'] for c in data['criteria']], list(range(1,121)))
        self.assertEqual(len({c['id'] for c in data['criteria']}), 120)
        for c in data['criteria']:
            self.assertEqual(c['source']['page'], 7+(c['source']['question']-1)//20)
            self.assertEqual(c['source']['figure'], c['source']['page']-6)
            self.assertEqual(c['status'], 'not_verified')
        cats = {cat for c in data['criteria'] for cat in c['iso_2011_mapping']}
        self.assertEqual(len(cats), 8)
        full = gov.criteria_for({**self.change,'full_audit':True})
        self.assertEqual(len(full), 136)

    def test_full_audit_allows_inapplicable_capabilities_but_not_declared_sensitive_scope(self):
        full=gov.criteria_for({**self.change,'full_audit':True})
        for control in ['GOV-AUTH','GOV-DATA','GOV-ADR']:
            self.assertTrue(next(c for c in full if c['id']==control)['allow_not_applicable'])
        changed=gov.criteria_for({**self.change,'full_audit':True,'surfaces':['auth']})
        self.assertFalse(next(c for c in changed if c['id']=='GOV-AUTH')['allow_not_applicable'])

    def test_cli_exit_codes(self):
        p, r, b = self.evaluation()
        argv=[sys.executable, str(ROOT/'scripts/governance.py'), 'assess', '--plan', str(b/'plan.json'), '--results', str(b/'results.json')]
        self.assertEqual(subprocess.run(argv, capture_output=True).returncode, 2)
        self.complete(r,b); gov.write(b/'results.json',r)
        self.assertEqual(subprocess.run(argv, capture_output=True).returncode, 0)
        r['criteria'][0].update(status='failed',reason='Observed failure'); gov.write(b/'results.json',r)
        self.assertEqual(subprocess.run(argv, capture_output=True).returncode, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
