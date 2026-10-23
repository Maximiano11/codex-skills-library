from pathlib import Path
import copy
import json
import os
import sys
import tempfile
import time
import unittest

from engineering_os import gates
from engineering_os.util import ContractError, canonical, digest, fingerprint


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root/"source"; self.project.mkdir()
        (self.project/"code.py").write_text("value = 1\n")
        self.profile = {"schema_version": 1, "checks": [
            {"id": "acceptance", "kind": "review", "purpose": "acceptance", "required": True}]}

    def review(self, result="passed", findings=None):
        return {"acceptance": {"reviewer": "fixture independent reviewer", "source_sha256": fingerprint(self.project)["sha256"],
                "result": result, "criteria": ["value remains 1"], "evidence": ["code.py:1 inspected"], "findings": findings or []}}

    def test_empty_profile_never_approves(self):
        p={"schema_version":1,"checks":[]}
        self.assertEqual(gates.verdict(p,[])["state"], "PARTIALLY_VALIDATED")

    def test_missing_or_stale_review_is_pending(self):
        for review in (None, {"acceptance": {**self.review()["acceptance"], "source_sha256": "old"}}):
            out=self.root/("out"+str(len(list(self.root.iterdir()))))
            result=gates.collect(self.project,self.profile,out,attestations=review)
            self.assertEqual(result["verdict"]["state"], "PARTIALLY_VALIDATED")

    def test_current_attributed_review_passes_configured_scope(self):
        out=self.root/"out"
        result=gates.collect(self.project,self.profile,out,attestations=self.review())
        self.assertEqual(result["verdict"]["state"],"VALIDATED")
        self.assertEqual(gates.verify(self.project,self.profile,out)["state"],"VALIDATED")

    def test_failed_mandatory_criterion_blocks(self):
        result=gates.collect(self.project,self.profile,self.root/"out",attestations=self.review("failed"))
        self.assertEqual(result["verdict"]["state"],"BLOCKED")

    def test_critical_open_finding_blocks_even_passing_review(self):
        result=gates.collect(self.project,self.profile,self.root/"out",attestations=self.review(findings=[{"severity":"P1","open":True}]))
        self.assertEqual(result["verdict"]["state"],"BLOCKED")

    def test_source_drift_invalidates_evidence(self):
        out=self.root/"out"
        gates.collect(self.project,self.profile,out,attestations=self.review())
        (self.project/"code.py").write_text("value = 2\n")
        self.assertEqual(gates.verify(self.project,self.profile,out)["state"],"PARTIALLY_VALIDATED")

    def test_profile_drift_invalidates_evidence(self):
        out=self.root/"out";gates.collect(self.project,self.profile,out,attestations=self.review())
        self.profile["checks"].append({"id":"extra","kind":"review","purpose":"review","required":True})
        self.assertEqual(gates.verify(self.project,self.profile,out)["state"],"PARTIALLY_VALIDATED")

    def add_command(self, code, **kwargs):
        check={"id":"check","kind":"command","purpose":"build","required":True,"argv":[sys.executable,"-B","-c",code]}
        check.update(kwargs);self.profile["checks"].append(check)

    def test_commands_require_explicit_execution(self):
        self.add_command("raise RuntimeError('must not run')")
        with self.assertRaises(ContractError): gates.collect(self.project,self.profile,self.root/"out")
        self.assertFalse((self.root/"out").exists())

    def test_shell_string_is_rejected(self):
        self.add_command("pass",argv="echo unsafe")
        with self.assertRaises(ContractError): gates.validate_profile(self.profile)

    def test_tests_cannot_be_declared_as_plain_exit_code(self):
        self.add_command("pass",purpose="tests")
        with self.assertRaises(ContractError): gates.validate_profile(self.profile)

    def test_missing_binary_is_pending(self):
        self.add_command("pass",argv=[str(self.root/"missing-executable")])
        result=gates.collect(self.project,self.profile,self.root/"out",True,self.review())
        self.assertEqual(result["verdict"]["state"],"PARTIALLY_VALIDATED")

    def test_nonzero_process_blocks(self):
        self.add_command("raise SystemExit(7)")
        result=gates.collect(self.project,self.profile,self.root/"out",True,self.review())
        self.assertEqual(result["verdict"]["state"],"BLOCKED")

    def test_timeout_is_pending(self):
        self.add_command("import time; time.sleep(1)",timeout=0.01)
        result=gates.collect(self.project,self.profile,self.root/"out",True,self.review())
        self.assertEqual(result["verdict"]["state"],"PARTIALLY_VALIDATED")

    def junit(self, xml):
        code="from pathlib import Path; Path(r'{output}/tests.xml').write_text("+repr(xml)+")"
        self.add_command(code,kind="junit",purpose="tests",report="tests.xml")

    def test_real_testcases_are_required(self):
        self.junit('<testsuite tests="0"/>')
        result=gates.collect(self.project,self.profile,self.root/"out",True,self.review())
        self.assertEqual(result["verdict"]["state"],"PARTIALLY_VALIDATED")

    def test_skips_are_pending(self):
        self.junit('<testsuite tests="1" skipped="1"><testcase name="x"><skipped/></testcase></testsuite>')
        result=gates.collect(self.project,self.profile,self.root/"out",True,self.review())
        self.assertEqual(result["verdict"]["state"],"PARTIALLY_VALIDATED")

    def test_junit_failure_blocks_even_when_process_succeeds(self):
        self.junit('<testsuite tests="1" failures="1"><testcase name="x"><failure/></testcase></testsuite>')
        result=gates.collect(self.project,self.profile,self.root/"out",True,self.review())
        self.assertEqual(result["verdict"]["state"],"BLOCKED")

    def test_junit_drift_is_detected(self):
        self.junit('<testsuite tests="1"><testcase name="actual"/></testsuite>')
        out=self.root/"out";result=gates.collect(self.project,self.profile,out,True,self.review())
        self.assertEqual(result["verdict"]["state"],"VALIDATED")
        (out/"tests.xml").write_text('<testsuite tests="0"/>')
        self.assertEqual(gates.verify(self.project,self.profile,out)["state"],"PARTIALLY_VALIDATED")

    def test_malformed_and_forged_counts_rejected(self):
        for xml in (b"invalid",b'<testsuite tests="100"><testcase/></testsuite>', b'<!DOCTYPE x><testsuite/>'):
            with self.assertRaises(ContractError): gates.junit_summary(xml)

    def test_no_output_leak_to_result(self):
        self.add_command("print('FAKE_SECRET_FOR_TEST')")
        result=gates.collect(self.project,self.profile,self.root/"out",True,self.review())
        self.assertNotIn("FAKE_SECRET_FOR_TEST",json.dumps(result))
        self.assertFalse(any(p.name in {"stdout.txt","stderr.txt"} for p in (self.root/"out").iterdir()))

    def test_output_in_source_and_reused_output_are_rejected(self):
        with self.assertRaises(ContractError): gates.collect(self.project,self.profile,self.project/"out")
        out=self.root/"out";out.mkdir()
        with self.assertRaises(ContractError): gates.collect(self.project,self.profile,out)

    def test_duplicate_ids_rejected(self):
        self.profile["checks"].append(dict(self.profile["checks"][0]))
        with self.assertRaises(ContractError): gates.validate_profile(self.profile)

    @unittest.skipUnless(os.name == "posix", "POSIX process group behavior")
    def test_timeout_terminates_inherited_child_process(self):
        marker=self.root/"late-write.txt"
        child="import time; from pathlib import Path; time.sleep(0.9); Path("+repr(str(marker))+").write_text('late')"
        parent="import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',"+repr(child)+"]); time.sleep(5)"
        self.add_command(parent,timeout=0.25)
        result=gates.collect(self.project,self.profile,self.root/"out",True,self.review())
        self.assertEqual(result["verdict"]["state"],"PARTIALLY_VALIDATED")
        time.sleep(1)
        self.assertFalse(marker.exists(),"Timed-out command left a child able to mutate files")

    @unittest.skipUnless(os.name == "posix", "POSIX file permission semantics")
    def test_permission_change_invalidates_evidence(self):
        code=self.project/"code.py";code.chmod(0o700)
        out=self.root/"out"
        gates.collect(self.project,self.profile,out,attestations=self.review())
        code.chmod(0o600)
        self.assertEqual(gates.verify(self.project,self.profile,out)["state"],"PARTIALLY_VALIDATED")
