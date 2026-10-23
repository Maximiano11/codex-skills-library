#!/usr/bin/env python3
"""Functional CLI contract tests for the gate, using disposable Git repositories."""
import importlib.util
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


SCRIPT = Path(__file__).with_name("release_gate.py")
spec = importlib.util.spec_from_file_location("release_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

# This fixture executes assertions and exports their actual result. It is test
# infrastructure for the gate, never presented as an audited business application.
FIXTURE = r'''
import os, sys, unittest
from pathlib import Path
import xml.etree.ElementTree as ET
mode = sys.argv[1]
class Contract(unittest.TestCase):
    def test_evidence_directory(self):
        if mode == "skip":
            self.skipTest("deliberate mandatory skip")
        self.assertTrue(Path(os.environ["QA_EVIDENCE_DIR"]).is_dir())
        self.assertNotEqual(mode, "fail", "deliberate failing assertion")
suite = unittest.defaultTestLoader.loadTestsFromTestCase(Contract)
result = unittest.TestResult()
suite.run(result)
root = ET.Element("testsuite", tests=str(result.testsRun),
    failures=str(len(result.failures)), errors=str(len(result.errors)),
    skipped=str(len(result.skipped)))
case = ET.SubElement(root, "testcase", name="test_evidence_directory")
for test, message in result.failures:
    ET.SubElement(case, "failure").text = message
for test, message in result.errors:
    ET.SubElement(case, "error").text = message
for test, message in result.skipped:
    ET.SubElement(case, "skipped").text = message
ET.ElementTree(root).write(Path(os.environ["QA_EVIDENCE_DIR"]) / "junit.xml")
sys.exit(0 if result.wasSuccessful() or mode == "fail" else 1)
'''


class GateTests(unittest.TestCase):
    def test_suite_setup_error_is_not_silently_approved(self):
        path = self.base / "setup-error.xml"
        path.write_text('<testsuite tests="1" errors="0"><testcase name="unit"/>'
                        '<error message="mandatory setup failed"/></testsuite>')
        with self.assertRaises(ValueError):
            gate.junit_counts(path)

    def test_suite_failure_and_skip_are_not_silently_approved(self):
        for tag in ["failure", "skipped"]:
            with self.subTest(tag=tag):
                path = self.base / (tag + ".xml")
                path.write_text('<testsuite tests="1"><testcase name="unit"/>'
                                '<' + tag + '/></testsuite>')
                with self.assertRaises(ValueError):
                    gate.junit_counts(path)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        (self.repo / "review.md").write_text("Review of the disposable gate test fixture.\n")
        (self.repo / "fixture.py").write_text(FIXTURE)
        self.git("add", ".")
        self.git("-c", "user.name=QA Fixture", "-c", "user.email=qa@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Disposable fixture")
        self.policy = {
            "version": 1,
            "review": {"completed": True, "revision": self.git("rev-parse", "HEAD"),
                       "evidence": "review.md", "limitations": [], "findings": []},
            "checks": [
                {"id": "build", "kind": "build", "argv": [sys.executable, "-c",
                  "import ast; from pathlib import Path; ast.parse(Path('fixture.py').read_text())"]},
                {"id": "lint", "kind": "lint", "not_applicable": "No linter in this fixture"},
                {"id": "types", "kind": "types", "not_applicable": "No type checker in fixture"},
                {"id": "tests", "kind": "tests", "argv": [sys.executable, "fixture.py", "pass"],
                 "junit": "junit.xml"},
                {"id": "regression", "kind": "regression",
                 "argv": [sys.executable, "fixture.py", "pass"], "junit": "junit.xml"},
            ],
        }
        self.policy_path = self.base / "policy.json"
        self.out = self.base / "evidence"

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args],
                                       text=True, stderr=subprocess.PIPE).strip()

    def run_gate(self, expected):
        self.policy_path.write_text(json.dumps(self.policy))
        completed = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo),
                                    "--policy", str(self.policy_path), "--out", str(self.out)],
                                   text=True, capture_output=True, timeout=15)
        self.assertEqual(completed.returncode, expected, completed.stdout + completed.stderr)
        report = json.loads((self.out / "report.json").read_text())
        self.assertEqual(report["status"], {0: "APROVADO", 1: "REPROVADO",
                                           2: "NÃO VERIFICADO"}[expected])
        return report

    def finding(self, severity):
        self.policy["review"]["findings"] = [
            {"id": "issue-1", "severity": severity, "status": "open",
             "evidence": "review.md: deliberately injected finding for gate test"}]

    def test_pass_executes_assertions_and_preserves_evidence(self):
        report = self.run_gate(0)
        test = next(c for c in report["checks"] if c["id"] == "tests")
        self.assertEqual(test["counts"]["tests"], 1)
        self.assertEqual(test["counts"]["failures"], 0)
        self.assertEqual(test["junit_sha256"], gate.digest(Path(test["junit"])))
        self.assertEqual(report["source"]["revision"], self.git("rev-parse", "HEAD"))
        self.assertFalse(report["source"]["dirty"])

    def test_nonzero_build_blocks_release(self):
        self.policy["checks"][0]["argv"] = [sys.executable, "-c", "raise SystemExit(7)"]
        report = self.run_gate(1)
        self.assertEqual(report["checks"][0]["exit_code"], 7)

    def test_failed_assertion_blocks_even_with_exit_zero(self):
        self.policy["checks"][3]["argv"][-1] = "fail"
        report = self.run_gate(1)
        self.assertEqual(report["checks"][3]["exit_code"], 0)
        self.assertIn("failed, errored or skipped", report["checks"][3]["reason"])

    def test_mandatory_skip_blocks(self):
        self.policy["checks"][3]["argv"][-1] = "skip"
        report = self.run_gate(1)
        self.assertIn("skipped", report["checks"][3]["reason"])

    def test_regression_failure_blocks(self):
        self.policy["checks"][4]["argv"][-1] = "fail"
        self.run_gate(1)

    def test_missing_junit_blocks(self):
        self.policy["checks"][3]["argv"] = [sys.executable, "-c", "pass"]
        self.run_gate(1)

    def test_p0_blocks(self):
        self.finding("P0")
        self.assertEqual(self.run_gate(1)["blocking_findings"], ["issue-1"])

    def test_p1_blocks(self):
        self.finding("P1")
        self.run_gate(1)

    def test_resolved_p1_allows_release(self):
        self.finding("P1")
        self.policy["review"]["findings"][0]["status"] = "resolved"
        self.run_gate(0)

    def test_p2_without_decision_is_unverified(self):
        self.finding("P2")
        self.run_gate(2)

    def test_p2_explicitly_accepted_with_owner(self):
        self.finding("P2")
        self.policy["review"]["findings"][0].update(
            release_decision="accept", owner="fixture reviewer", rationale="Low impact")
        self.run_gate(0)

    def test_p2_block_decision_blocks(self):
        self.finding("P2")
        self.policy["review"]["findings"][0].update(
            release_decision="block", owner="fixture reviewer", rationale="Material impact")
        self.run_gate(1)

    def test_dirty_source_is_unverified(self):
        (self.repo / "unreviewed.py").write_text("new_change = True")
        self.assertIn("clean Git", self.run_gate(2)["reasons"][0])

    def test_wrong_review_revision_is_unverified(self):
        self.policy["review"]["revision"] = "0" * 40
        self.assertIn("differs", self.run_gate(2)["reasons"][0])

    def test_missing_review_is_unverified(self):
        self.policy["review"]["completed"] = False
        self.run_gate(2)

    def test_missing_review_evidence_is_unverified(self):
        self.policy["review"]["evidence"] = "missing.md"
        self.run_gate(2)

    def test_mutation_during_execution_is_unverified(self):
        self.policy["checks"][0]["argv"] = [sys.executable, "-c",
            "from pathlib import Path; Path('review.md').write_text('changed')"]
        self.assertIn("Source changed", self.run_gate(2)["reasons"][0])

    def test_missing_required_category_is_unverified(self):
        self.policy["checks"].pop()
        self.run_gate(2)

    def test_no_test_waiver(self):
        self.policy["checks"][3] = {"id": "tests", "kind": "tests",
                                    "not_applicable": "Attempted bypass"}
        self.run_gate(2)

    def test_duplicate_check_is_unverified(self):
        self.policy["checks"].append(self.policy["checks"][0])
        self.run_gate(2)

    def test_timeout_blocks(self):
        self.policy["checks"][0].update(
            argv=[sys.executable, "-c", "import time; time.sleep(30)"],
            timeout_seconds=0.05)
        self.assertIn("timed out", self.run_gate(1)["checks"][0]["reason"])

    def test_missing_executable_blocks(self):
        self.policy["checks"][0]["argv"] = [str(self.base / "missing-command")]
        self.run_gate(1)

    def test_evidence_cannot_escape_run_folder(self):
        self.policy["checks"][3]["junit"] = "../old.xml"
        self.run_gate(2)

    def test_old_run_folder_cannot_be_reused(self):
        self.out.mkdir()
        sentinel = self.out / "report.json"
        sentinel.write_text('{"status": "OLD"}')
        self.policy_path.write_text(json.dumps(self.policy))
        completed = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo),
            "--policy", str(self.policy_path), "--out", str(self.out)], capture_output=True)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(json.loads(sentinel.read_text())["status"], "OLD")

    def test_non_repository_is_unverified(self):
        self.repo = self.base
        self.run_gate(2)

    def test_invalid_junit_cases_fail_closed(self):
        cases = [
            "<testsuite tests='0'/>",
            "<testsuite tests='2'><testcase name='only-one'/></testsuite>",
            "<testsuite><testcase name='x'><error/></testcase></testsuite>",
            "<testsuite><testcase name='x'><flakyFailure/></testcase></testsuite>",
            "<testsuite><testcase name='x' status='notrun'/></testsuite>",
            "<testsuite><testcase name='x' status='skipped'/></testsuite>",
            "<testsuite disabled='1'><testcase name='x'/></testsuite>",
            "<testsuite><testcase/></testsuite>",
            "<testsuites tests='2'><testsuite><testcase name='x'/></testsuite></testsuites>",
            "<unexpected/>",
            "<broken",
        ]
        path = self.base / "invalid.xml"
        for xml in cases:
            with self.subTest(xml=xml):
                path.write_text(xml)
                with self.assertRaises((ValueError, ET.ParseError)):
                    gate.junit_counts(path)

    def test_nested_junit_counts_are_not_doubled(self):
        path = self.base / "nested.xml"
        path.write_text("<testsuites tests='1'><testsuite tests='1'>"
                        "<testsuite tests='1'><testcase name='x'/></testsuite>"
                        "</testsuite></testsuites>")
        self.assertEqual(gate.junit_counts(path)["tests"], 1)


class EvidenceResult(unittest.TextTestResult):
    """Export outcomes from this real unittest execution, not inferred exit codes."""
    def startTest(self, test):
        super().startTest(test)
        self.current = ET.SubElement(self.xml, "testcase", name=test.id())

    def addFailure(self, test, err):
        super().addFailure(test, err)
        ET.SubElement(self.current, "failure").text = self._exc_info_to_string(err, test)

    def addError(self, test, err):
        super().addError(test, err)
        ET.SubElement(self.current, "error").text = self._exc_info_to_string(err, test)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        ET.SubElement(self.current, "skipped").text = reason

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            tag = "failure" if issubclass(err[0], test.failureException) else "error"
            ET.SubElement(self.current, tag).text = self._exc_info_to_string(err, test)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regression", action="store_true",
                        help="Run the regression for alternative JUnit skip markers")
    args = parser.parse_args()
    junit = os.environ.get("QA_EVIDENCE_DIR")
    EvidenceResult.xml = ET.Element("testsuite")
    suite = (unittest.TestSuite([GateTests("test_invalid_junit_cases_fail_closed")])
             if args.regression else unittest.defaultTestLoader.loadTestsFromTestCase(GateTests))
    runner = unittest.TextTestRunner(verbosity=2, resultclass=EvidenceResult)
    result = runner.run(suite)
    if junit:
        root = EvidenceResult.xml
        root.set("tests", str(result.testsRun))
        root.set("failures", str(sum(c.find("failure") is not None for c in root)))
        root.set("errors", str(sum(c.find("error") is not None for c in root)))
        root.set("skipped", str(sum(c.find("skipped") is not None for c in root)))
        ET.ElementTree(root).write(Path(junit) / "junit.xml", encoding="utf-8",
                                   xml_declaration=True)
    sys.exit(not result.wasSuccessful())
