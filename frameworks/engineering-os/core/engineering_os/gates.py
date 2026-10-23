"""Evidence collection and conservative local gates; never a deployment permission."""
from datetime import datetime, timezone
from pathlib import Path
import os
import signal
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from .util import ContractError, canonical, digest, fingerprint, read_json, relative_file, write_new


PURPOSES = {"tests", "lint", "typecheck", "build", "security", "compatibility", "regression", "documentation", "acceptance", "review"}


def execute(argv, project, stdout, stderr, timeout):
    """Bound command lifetime and terminate its process group on POSIX, not just parent."""
    kwargs = {"start_new_session": True} if os.name == "posix" else {
        "creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)}
    proc = subprocess.Popen(argv, cwd=project, stdout=stdout, stderr=stderr, shell=False, **kwargs)
    try:
        return proc.wait(timeout=timeout)
    finally:
        if os.name == "posix":
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif proc.poll() is None:
            # Standard Windows utility, best effort; this is not a sandbox/job object.
            try:
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                pass
        if proc.poll() is None:
            proc.kill()
        proc.wait()


def validate_profile(profile):
    if not isinstance(profile, dict) or set(profile) - {"schema_version", "checks"} or profile.get("schema_version") != 1:
        raise ContractError("Unsupported profile schema")
    checks = profile.get("checks")
    if not isinstance(checks, list) or len(checks) > 100:
        raise ContractError("checks must be a list of at most 100 entries")
    ids = set()
    for check in checks:
        if not isinstance(check, dict) or set(check) - {"id", "purpose", "kind", "required", "argv", "report", "timeout"}:
            raise ContractError("Unknown check fields")
        cid = check.get("id")
        if not isinstance(cid, str) or not cid or not all(c.isalnum() or c in "-_" for c in cid) or cid in ids:
            raise ContractError("Invalid or duplicate check id")
        ids.add(cid)
        if type(check.get("required")) is not bool or check.get("purpose") not in PURPOSES or check.get("kind") not in {"command", "junit", "review"}:
            raise ContractError("Explicit required/purpose/kind needed")
        if check["purpose"] == "tests" and check["kind"] != "junit":
            raise ContractError("Test checks require an actual JUnit report adapter")
        if check["kind"] != "review":
            argv = check.get("argv")
            if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a or "\0" in a for a in argv):
                raise ContractError("Commands require a nonempty argv list; shell strings are not supported")
            timeout = check.get("timeout", 60)
            if type(timeout) not in (int, float) or not 0 < timeout <= 3600:
                raise ContractError("Timeout must be between 0 and 3600 seconds")
        if check["kind"] == "junit" and not isinstance(check.get("report"), str):
            raise ContractError("JUnit checks need a report path relative to the new output directory")
    return profile


def junit_summary(data):
    if len(data) > 10 * 1024 * 1024 or b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ContractError("Unsafe or oversized XML")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        raise ContractError("Invalid JUnit XML") from e
    if root.tag not in {"testsuite", "testsuites"}:
        raise ContractError("Not a JUnit testsuite/testsuites document")
    cases = list(root.iter("testcase"))
    result = {"tests": len(cases), "failures": 0, "errors": 0, "skipped": 0}
    for c in cases:
        for key, tag in (("failures", "failure"), ("errors", "error"), ("skipped", "skipped")):
            result[key] += int(c.find(tag) is not None)
    for suite in root.iter():
        if suite.tag not in {"testsuite", "testsuites"}:
            continue
        children = list(suite.iter("testcase"))
        observed = {"tests": len(children),
                    "failures": sum(c.find("failure") is not None for c in children),
                    "errors": sum(c.find("error") is not None for c in children),
                    "skipped": sum(c.find("skipped") is not None for c in children)}
        for key, value in observed.items():
            if key in suite.attrib:
                try:
                    matches = int(suite.attrib[key]) == value
                except ValueError:
                    matches = False
                if not matches:
                    raise ContractError("JUnit counts disagree with testcase elements")
    return result


def verdict(profile, records, fresh=True, critical=False):
    validate_profile(profile)
    by_id = {r["id"]: r for r in records}
    if len(by_id) != len(records) or any(r.get("status") not in {"passed", "failed", "not_verified"} for r in records):
        raise ContractError("Invalid evidence records")
    mandatory = [c for c in profile["checks"] if c["required"]]
    failed = [c["id"] for c in mandatory if by_id.get(c["id"], {}).get("status") == "failed"]
    pending = [c["id"] for c in mandatory if by_id.get(c["id"], {}).get("status") != "passed"]
    # Empty coverage or missing acceptance/review evidence never approves a delivery.
    if not mandatory:
        pending.append("mandatory-criteria-not-configured")
    if not any(c["required"] and c["purpose"] in {"acceptance", "review"} for c in profile["checks"]):
        pending.append("acceptance-or-review-not-configured")
    if not fresh:
        pending.append("stale-source-or-profile")
    state = "BLOCKED" if failed or critical else "PARTIALLY_VALIDATED" if pending else "VALIDATED"
    return {"state": state, "failed": failed, "pending": pending, "critical_findings": critical,
            "scope": "configured local mandatory criteria only; no deployment authorization"}


def collect(project, profile, output, allow_exec=False, attestations=None):
    validate_profile(profile)
    project = Path(project).resolve()
    output = Path(output).resolve()
    if output == project or output.is_relative_to(project):
        raise ContractError("Evidence output must be outside the source tree")
    if output.exists():
        raise ContractError("Evidence output must be a new directory")
    if any(c["kind"] != "review" for c in profile["checks"]) and not allow_exec:
        raise ContractError("Review argv and effects, then explicitly pass --allow-exec")
    before = fingerprint(project)
    output.mkdir(parents=True, mode=0o700)
    reviews = attestations or {}
    if not isinstance(reviews, dict):
        raise ContractError("Attestations must be keyed by check id")
    records = []
    critical = False
    for check in profile["checks"]:
        cid = check["id"]
        record = {"id": cid, "status": "not_verified", "kind": check["kind"], "purpose": check["purpose"]}
        if check["kind"] == "review":
            review = reviews.get(cid, {})
            if review:
                if not isinstance(review, dict) or set(review) - {"reviewer", "source_sha256", "result", "criteria", "evidence", "findings"}:
                    raise ContractError("Unknown review fields")
                findings = review.get("findings", [])
                if not isinstance(findings, list) or any(not isinstance(f, dict) or f.get("severity") not in {"P0", "P1", "P2", "P3"} or type(f.get("open")) is not bool for f in findings):
                    raise ContractError("Invalid findings")
                critical |= any(f["open"] and f["severity"] in {"P0", "P1"} for f in findings)
                sufficient = (isinstance(review.get("reviewer"), str) and bool(review["reviewer"].strip())
                              and review.get("source_sha256") == before["sha256"]
                              and isinstance(review.get("criteria"), list) and bool(review["criteria"])
                              and isinstance(review.get("evidence"), list) and bool(review["evidence"]))
                if sufficient and review.get("result") in {"passed", "failed"}:
                    record.update(status=review["result"], reason="Attributed review; collector cannot prove its truth")
                else:
                    record["reason"] = "Incomplete or stale review"
                record["attestation_sha256"] = digest(canonical(review))
            else:
                record["reason"] = "Review not supplied"
        else:
            argv = [a.replace("{project}", str(project)).replace("{output}", str(output)) for a in check["argv"]]
            record["argv_sha256"] = digest(canonical(argv))
            # Output is deliberately not echoed or retained: tests can print secrets.
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                try:
                    exit_code = execute(argv, project, stdout, stderr, check.get("timeout", 60))
                    record["exit_code"] = exit_code
                    record["status"] = "passed" if exit_code == 0 else "failed"
                except subprocess.TimeoutExpired:
                    record.update(reason="Command timed out", status="not_verified")
                except OSError as e:
                    record.update(reason="Command unavailable: " + type(e).__name__, status="not_verified")
                for label, stream in (("stdout", stdout), ("stderr", stderr)):
                    stream.seek(0)
                    import hashlib
                    h = hashlib.sha256()
                    size = 0
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        h.update(chunk); size += len(chunk)
                    record[label] = {"sha256": h.hexdigest(), "bytes": size}
            if check["kind"] == "junit" and record.get("exit_code") == 0:
                try:
                    report = relative_file(output, check["report"])
                    if report.stat().st_size > 10 * 1024 * 1024:
                        raise ContractError("JUnit report too large")
                    data = report.read_bytes()
                    summary = junit_summary(data)
                    record["tests"] = summary
                    record["report_sha256"] = digest(data)
                    if summary["failures"] or summary["errors"]:
                        record["status"] = "failed"
                    elif not summary["tests"] or summary["skipped"]:
                        record.update(status="not_verified", reason="Zero executed tests or skipped cases")
                except (OSError, ContractError) as e:
                    record.update(status="not_verified", reason=type(e).__name__ + ": invalid or missing JUnit report")
        records.append(record)
    after = fingerprint(project)
    result = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
              "project": str(project), "source": before, "profile_sha256": digest(canonical(profile)),
              "checks": records, "verdict": verdict(profile, records, before == after, critical),
              "limits": ["No sandbox is provided; argv can have side effects and must be reviewed.",
                         "Process success is not proof of test coverage; test gates require actual parsed JUnit cases.",
                         "Evidence hashes detect accidental drift; a writer with access can forge evidence."]}
    write_new(output/"record.json", result)
    return result


def verify(project, profile, evidence):
    result = read_json(Path(evidence)/"record.json")
    fresh = (result.get("project") == str(Path(project).resolve())
             and result.get("source") == fingerprint(project)
             and result.get("profile_sha256") == digest(canonical(validate_profile(profile))))
    for check in profile["checks"]:
        record = next((r for r in result["checks"] if r["id"] == check["id"]), None)
        if record and record.get("status") == "passed" and check["kind"] == "junit":
            try:
                data = relative_file(evidence, check["report"]).read_bytes()
                if digest(data) != record.get("report_sha256") or junit_summary(data) != record.get("tests"):
                    fresh = False
            except (OSError, ContractError):
                fresh = False
    return verdict(profile, result["checks"], fresh, result["verdict"].get("critical_findings", False))
