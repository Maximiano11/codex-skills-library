#!/usr/bin/env python3
"""Run unittest and export actual per-test outcomes as JUnit; never infer tests from exit 0."""
from pathlib import Path
import argparse
import io
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"core"), str(ROOT)]


class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = {}

    def startTest(self, test):
        super().startTest(test)
        self.cases[test.id()] = ET.Element("testcase", {"name": test.id()})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        ET.SubElement(self.cases[test.id()], "failure").text = self._exc_info_to_string(err, test)

    def addError(self, test, err):
        super().addError(test, err)
        if test.id() not in self.cases:
            self.cases[test.id()] = ET.Element("testcase", {"name": test.id()})
        ET.SubElement(self.cases[test.id()], "error").text = self._exc_info_to_string(err, test)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if test.id() not in self.cases:
            self.cases[test.id()] = ET.Element("testcase", {"name": test.id()})
        ET.SubElement(self.cases[test.id()], "skipped").text = reason

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            tag = "failure" if issubclass(err[0], test.failureException) else "error"
            ET.SubElement(self.cases[test.id()], tag).text = self._exc_info_to_string(err, test)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        ET.SubElement(self.cases[test.id()], "skipped").text = "expected failure"

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        ET.SubElement(self.cases[test.id()], "failure").text = "unexpected success"


def main():
    p = argparse.ArgumentParser(); p.add_argument("--out", required=True)
    out = Path(p.parse_args().out)
    out.mkdir(parents=True, exist_ok=False)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT/"tests"), top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(suite)
    root = ET.Element("testsuite", {"name": "engineering-os", "tests": str(len(result.cases)),
        "failures": str(sum(c.find("failure") is not None for c in result.cases.values())),
        "errors": str(sum(c.find("error") is not None for c in result.cases.values())),
        "skipped": str(sum(c.find("skipped") is not None for c in result.cases.values()))})
    root.extend(result.cases.values())
    ET.ElementTree(root).write(out/"junit.xml", encoding="utf-8", xml_declaration=True)
    (out/"unittest.txt").write_text(stream.getvalue())
    print(stream.getvalue())
    return 0 if result.wasSuccessful() and result.testsRun > 0 and not result.skipped and not result.expectedFailures else 1


if __name__ == "__main__":
    raise SystemExit(main())
