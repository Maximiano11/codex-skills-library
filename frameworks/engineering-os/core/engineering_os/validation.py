"""Package invariants and deterministic routing evaluations, separate from model runs."""
from pathlib import Path
import json
import re
import tempfile

from .orchestrator import plan, workflows
from .util import ContractError, fingerprint, read_json, relative_file

REQUIRED_SKILLS = {"engineering-os", "prompt-engineer", "software-architect", "implementation-standards", "product-ux", "database-engineer", "security-auditor", "quality-engineer", "code-reviewer", "performance-engineer", "technical-documentation", "release-manager", "production-reliability"}
REQUIRED_WORKFLOWS = {"feature-development", "bug-investigation", "architecture-change", "refactoring", "security-review", "quality-audit", "release-readiness", "incident-response", "project-bootstrap"}


def validate_package(package):
    root = Path(package)
    essential = ["VERSION", "LICENSE", "README.md", "scripts/eos.py", "policies/governance.md",
                 "core/engineering_os/__init__.py", "core/engineering_os/cli.py",
                 "core/engineering_os/util.py", "core/engineering_os/gates.py",
                 "core/engineering_os/orchestrator.py", "core/engineering_os/validation.py",
                 "adapters/codex/install.py"]
    for name in essential:
        path = relative_file(root, name)
        if not path.is_file() or not path.stat().st_size:
            raise ContractError("Incomplete operational package: " + name)
    skills = {}
    for path in sorted((root/"skills").glob("*/SKILL.md")):
        text = path.read_text()
        front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not front:
            raise ContractError("Missing skill frontmatter: " + str(path))
        name = re.search(r"(?m)^name:\s*(.+?)\s*$", front[1])
        description = re.search(r"(?m)^description:\s*(.+?)\s*$", front[1])
        if not name or name[1].strip("\"'") != path.parent.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.parent.name):
            raise ContractError("Invalid skill name: " + str(path))
        if not description or description[1].strip("\"'") in {"", "|", ">"} or "[TODO:" in text:
            raise ContractError("Invalid generated skill description/scaffold")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not target.startswith(("http:", "https:", "/", "#")):
                if not relative_file(path.parent, target).is_file():
                    raise ContractError("Missing skill reference: " + target)
        if not (path.parent/"agents/openai.yaml").is_file():
            raise ContractError("Missing UI metadata")
        skills[path.parent.name] = {"bytes": len(text.encode()), "words": len(text.split())}
    if not REQUIRED_SKILLS <= skills.keys():
        raise ContractError("Required skills missing")
    catalog = workflows(root)
    if not REQUIRED_WORKFLOWS <= catalog.keys():
        raise ContractError("Required workflows missing")
    for item in catalog.values():
        if set(item) != {"schema_version", "id", "activation", "skills", "steps", "approval", "stop", "outputs", "mode_rule"} or item["schema_version"] != 1:
            raise ContractError("Invalid workflow fields")
        if not item["skills"] or any(s not in skills for s in item["skills"]):
            raise ContractError("Workflow references unavailable skill")
        seen = set()
        for step in item["steps"]:
            if not step.get("action") or not step.get("id") or step["id"] in seen or not set(step["depends_on"]) <= seen:
                raise ContractError("Workflow dependencies must form an ordered acyclic graph")
            seen.add(step["id"])
        if not seen or any(not item[k] for k in ("activation", "approval", "stop", "outputs", "mode_rule")):
            raise ContractError("Incomplete workflow")
    return {"passed": True, "skills": skills, "workflow_count": len(catalog),
            "kind": "package-structure-and-reference-validation", "limits": ["Not a model behavior evaluation or security certification."]}


def evaluate(package):
    root = Path(package)
    scenarios_path = root/"evaluations/scenarios.json"
    oracle_path = root/"evaluations/oracle.json"
    if not scenarios_path.is_file() or not oracle_path.is_file():
        raise ContractError("Run evaluations from the source distribution, not the installed runtime")
    cases = read_json(scenarios_path)["cases"]
    oracle = {c["id"]: c for c in read_json(oracle_path)["cases"]}
    outcomes = []
    for case in cases:
        with tempfile.TemporaryDirectory(prefix="eos-routing-") as tmp:
            folder = Path(tmp)
            for name, text in case["files"].items():
                path = relative_file(folder, name); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
            before = fingerprint(folder)
            result = plan(case["change"], root, folder)
            expected = oracle[case["id"]]
            assertions = {"risk": result["risk"] == expected["risk"],
                          "skills": set(expected["skills_include"]) <= set(result["skills"]),
                          "intent": result["original_request"] == case["request"],
                          "no_mutation_by_planner": before == fingerprint(folder),
                          "selective": len(result["skills"]) < len(REQUIRED_SKILLS)}
            if expected.get("mode"):
                assertions["mode"] = result["mode"] == expected["mode"]
            if expected.get("readonly"):
                assertions["readonly"] = result["code_changes_authorized_by_mode"] is False
            if expected.get("no_change_until_clarification"):
                assertions["ambiguity"] = result["implementation_ready"] is False
            outcomes.append({"id": case["id"], "passed": all(assertions.values()), "assertions": assertions,
                             "risk": result["risk"], "mode": result["mode"], "skills": result["skills"]})
    return {"kind": "deterministic-routing-evaluation", "passed": bool(outcomes) and all(x["passed"] for x in outcomes),
            "cases": outcomes, "model_runs_executed": 0,
            "limits": ["Tests routing and scope contracts, not implementation quality, intent understanding or model compliance."]}
