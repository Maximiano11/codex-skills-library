#!/usr/bin/env python3
"""Execute reviewed release checks; exit 0=approved, 1=failed, 2=unverified."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
from datetime import datetime, timezone
import xml.etree.ElementTree as ET


KINDS = {"build", "lint", "types", "tests", "regression"}
TEST_KINDS = {"tests", "regression"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_state(repo):
    def git(*args):
        return subprocess.check_output(
            ["git", "-C", str(repo), *args], stderr=subprocess.PIPE, text=True
        ).strip()
    return {"revision": git("rev-parse", "HEAD"),
            "dirty": bool(git("status", "--porcelain", "--untracked-files=all"))}


def validate_policy(policy):
    require(isinstance(policy, dict) and policy.get("version") == 1,
            "Policy version must be 1")
    checks = policy.get("checks")
    require(isinstance(checks, list) and checks, "Required checks are missing")
    ids, kinds = set(), set()
    for check in checks:
        require(isinstance(check, dict), "Invalid check")
        name, kind = check.get("id"), check.get("kind")
        require(isinstance(name, str) and re.fullmatch(r"[a-z0-9-]+", name),
                "Check id must be lowercase letters, digits or hyphens")
        require(name not in ids, "Duplicate check id")
        require(kind in KINDS, "Invalid check kind")
        ids.add(name)
        kinds.add(kind)
        if "not_applicable" in check:
            require(kind not in TEST_KINDS, "Tests and regression cannot be waived")
            require(nonempty(check["not_applicable"]), "Missing applicability reason")
            require("argv" not in check and "junit" not in check,
                    "Not-applicable check cannot also execute")
            continue
        argv = check.get("argv")
        require(isinstance(argv, list) and argv and all(nonempty(a) for a in argv),
                "argv must be a nonempty array of strings")
        timeout = check.get("timeout_seconds", 600)
        require(type(timeout) in (int, float) and math.isfinite(timeout) and timeout > 0,
                "Timeout must be finite and positive")
        if kind in TEST_KINDS:
            require(nonempty(check.get("junit")), "Tests require fresh JUnit evidence")
            junit = Path(check["junit"])
            require(not junit.is_absolute() and ".." not in junit.parts,
                    "JUnit must be relative to its check evidence directory")
    require(KINDS <= kinds, "Declare build, lint, types, tests and regression")
    review = policy.get("review")
    require(isinstance(review, dict), "Review is missing")
    require(review.get("completed") is True, "Review is incomplete")
    require(nonempty(review.get("revision")), "Reviewed Git revision is missing")
    require(nonempty(review.get("evidence")), "Review evidence path is missing")
    require(isinstance(review.get("limitations"), list) and
            all(nonempty(x) for x in review["limitations"]), "Invalid limitations")
    findings = review.get("findings")
    require(isinstance(findings, list), "Findings inventory is missing")
    finding_ids = set()
    for finding in findings:
        require(isinstance(finding, dict), "Invalid finding")
        require(nonempty(finding.get("id")) and finding["id"] not in finding_ids,
                "Finding id is missing or duplicated")
        finding_ids.add(finding["id"])
        require(finding.get("severity") in {"P0", "P1", "P2", "P3"}, "Invalid severity")
        require(finding.get("status") in {"open", "resolved"}, "Invalid finding status")
        require(nonempty(finding.get("evidence")), "Finding evidence is missing")
        if finding["severity"] == "P2" and finding["status"] == "open":
            require(finding.get("release_decision") in {"block", "accept"},
                    "Open P2 needs release decision")
            require(nonempty(finding.get("rationale")) and nonempty(finding.get("owner")),
                    "P2 decision requires rationale and owner")
    return checks, review


def junit_counts(path):
    """Conservative JUnit subset; suite totals must match actual testcase elements."""
    root = ET.parse(path).getroot()
    require(root.tag in {"testsuites", "testsuite"}, "Unsupported JUnit root")
    suites = list(root.iter("testsuite"))
    require(suites, "JUnit has no suites")
    # Errors during suite setup can be emitted directly under testsuite rather
    # than inside testcase. They must never disappear from the case totals.
    parents = {child: parent for parent in root.iter() for child in parent}
    require(all(parents.get(e) is not None and parents[e].tag == "testcase"
                for e in root.iter() if e.tag in {"failure", "error", "skipped"}),
            "JUnit reports failure/error/skip outside a test case")
    require(all(parents.get(e) is not None and parents[e].tag == "testsuite"
                for e in root.iter("testcase")), "JUnit test case is outside a suite")
    for element in [root, *suites]:
        require(int(element.get("disabled", "0")) == 0, "JUnit reports disabled tests")
    for suite in suites:
        cases = list(suite.iter("testcase"))
        actual = {
            "tests": len(cases),
            "failures": sum(c.find("failure") is not None for c in cases),
            "errors": sum(c.find("error") is not None for c in cases),
            "skipped": sum(c.find("skipped") is not None for c in cases),
        }
        for key, value in actual.items():
            if key in suite.attrib:
                require(int(suite.attrib[key]) == value,
                        "Inconsistent JUnit suite count: " + key)
    cases = list(root.iter("testcase"))
    require(cases, "Zero tests executed")
    # Reject common retry/failure extensions rather than hide flaky executions.
    require(not any("flaky" in e.tag.lower() or "rerun" in e.tag.lower()
                    for e in root.iter()), "JUnit contains flaky/retried failures")
    for case in cases:
        require(nonempty(case.get("name")), "Unnamed test case")
        require(case.get("status", "run").lower() in {"run", "passed", "success"},
                "Test was not executed or has an unsupported status")
    counts = {
        "tests": len(cases),
        "failures": sum(c.find("failure") is not None for c in cases),
        "errors": sum(c.find("error") is not None for c in cases),
        "skipped": sum(c.find("skipped") is not None for c in cases),
    }
    for key, value in counts.items():
        if key in root.attrib:
            require(int(root.attrib[key]) == value, "Inconsistent JUnit root count")
    require(not any(counts[k] for k in ("failures", "errors", "skipped")),
            "JUnit reports failed, errored or skipped mandatory tests: " + str(counts))
    return counts


def execute_check(check, repo, folder):
    result = {"id": check["id"], "kind": check["kind"]}
    if "not_applicable" in check:
        return {**result, "status": "NOT_APPLICABLE",
                "reason": check["not_applicable"]}
    folder.mkdir()
    env = dict(os.environ, QA_EVIDENCE_DIR=str(folder))
    argv = [a.replace("{evidence_dir}", str(folder)) for a in check["argv"]]
    result.update(argv=argv, started_at=datetime.now(timezone.utc).isoformat())
    log = folder / "command.log"
    try:
        with log.open("wb") as stream:
            process = subprocess.Popen(argv, cwd=repo, env=env, stdout=stream,
                                       stderr=subprocess.STDOUT,
                                       start_new_session=(os.name == "posix"))
            try:
                result["exit_code"] = process.wait(timeout=check.get("timeout_seconds", 600))
            except subprocess.TimeoutExpired:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
                raise ValueError("Command timed out")
        require(result["exit_code"] == 0, "Command returned nonzero exit code")
        if check["kind"] in TEST_KINDS:
            evidence = (folder / check["junit"]).resolve()
            require(evidence.is_relative_to(folder.resolve()),
                    "JUnit escaped evidence directory")
            result["counts"] = junit_counts(evidence)
            result["junit_sha256"] = digest(evidence)
            result["junit"] = str(evidence)
        result["status"] = "PASSED"
    except (OSError, ValueError, ET.ParseError) as error:
        result.update(status="FAILED", reason=str(error))
    result["finished_at"] = datetime.now(timezone.utc).isoformat()
    result["log"] = str(log)
    result["log_sha256"] = digest(log)
    return result


def run(repo, policy_path, out):
    # Exclusive run directory makes old reports impossible to reuse accidentally.
    out.mkdir(parents=True, exist_ok=False)
    report = {"status": "NÃO VERIFICADO", "repository": str(repo),
              "started_at": datetime.now(timezone.utc).isoformat(),
              "checks": [], "reasons": []}
    exit_code = 2
    try:
        policy = json.loads(policy_path.read_text())
        report["policy_sha256"] = digest(policy_path)
        checks, review = validate_policy(policy)
        report["review"] = review
        before = git_state(repo)
        report["source"] = before
        require(not before["dirty"], "Release requires a clean Git working tree")
        require(before["revision"] == review["revision"],
                "Reviewed revision differs from current HEAD")
        review_path = Path(review["evidence"])
        require(not review_path.is_absolute() and ".." not in review_path.parts,
                "Review evidence must be repository-relative")
        review_file = (repo / review_path).resolve()
        require(review_file.is_relative_to(repo), "Review evidence escaped repository")
        require(review_file.is_file() and review_file.stat().st_size > 0,
                "Review evidence is missing or empty")
        report["review_evidence_sha256"] = digest(review_file)
        blockers = [f["id"] for f in review["findings"] if f["status"] == "open"
                    and (f["severity"] in {"P0", "P1"} or
                         (f["severity"] == "P2" and f["release_decision"] == "block"))]
        report["blocking_findings"] = blockers
        for check in checks:
            report["checks"].append(execute_check(check, repo, out / check["id"]))
        after = git_state(repo)
        require(after == before, "Source changed during execution; rerun on final revision")
        require(digest(policy_path) == report["policy_sha256"],
                "Policy changed during execution")
        require(digest(review_file) == report["review_evidence_sha256"],
                "Review evidence changed during execution")
        failed = any(c["status"] == "FAILED" for c in report["checks"])
        report["status"] = "REPROVADO" if blockers or failed else "APROVADO"
        exit_code = 1 if blockers or failed else 0
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as error:
        report["reasons"].append(str(error))
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": report["status"], "report": str(out / "report.json")},
                     ensure_ascii=False))
    return exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run(args.repo.resolve(), args.policy.resolve(), args.out.resolve())
    except OSError as error:
        print("NÃO VERIFICADO: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
