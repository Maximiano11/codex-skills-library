"""Explainable triage; it supplements technical investigation, not language understanding."""
from pathlib import Path
import re
import unicodedata

from .util import ContractError, read_json


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


def matches(text, terms):
    return any(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) for term in terms)


HIGH = {
    "auth": ["autenticacao", "autorizacao", "authentication", "authorization", "login", "senha", "password", "oauth"],
    "sensitive-data": ["dados sensiveis", "personal data", "tenant", "organizacoes"],
    "migration": ["migration", "migrations", "migracao", "schema", "esquema"],
    "architecture": ["arquitetural", "architectural", "arquitetura", "architecture"],
    "destructive": ["destrutiva", "destrutivo", "delete", "drop table", "excluir dados"],
    "money": ["pagamento", "payment", "desconto", "dinheiro", "billing"],
    "production": ["producao", "production", "deploy", "release"],
}
TRAITS = set(HIGH) | {"ui", "database", "api", "performance", "integration", "concurrency"}
CHANGE_FIELDS = {"request", "mode", "workflow", "traits", "scope", "reversible", "acceptance", "ambiguities"}


def workflows(package):
    result = {}
    for path in sorted((Path(package)/"workflows").glob("*.json")):
        item = read_json(path)
        if item.get("id") != path.stem or item["id"] in result:
            raise ContractError("Invalid or duplicate workflow id")
        result[item["id"]] = item
    return result


def infer_mode(request):
    text = normalize(request)
    if matches(text, ["apenas explique", "somente explicacao", "only explain", "explique", "explain"]):
        return "explain"
    if matches(text, ["plano", "planeje", "plan", "planejamento"]):
        return "plan"
    if matches(text, ["audite", "audit", "auditoria", "review", "revise"]):
        return "audit"
    if matches(text, ["sem implementar", "nao implemente", "somente analise", "apenas analise", "only analyze", "analise", "investigue"]):
        return "analyze"
    if matches(text, ["corrija", "fix", "implemente", "implement", "crie", "create", "adicione", "refatore", "ajuste", "mude", "altere", "desenvolva"]):
        return "implement"
    return "analyze"


def discover(project):
    root = Path(project).resolve()
    if not root.is_dir():
        raise ContractError("Project does not exist")
    known = ["pyproject.toml", "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json", "CMakeLists.txt"]
    found = [name for name in known if (root/name).is_file() and not (root/name).is_symlink()]
    scripts = {}
    if "package.json" in found:
        data = read_json(root/"package.json")
        scripts = data.get("scripts", {})
    return {"project": str(root), "manifests": found, "declared_scripts_not_executed": scripts,
            "local_instructions": [n for n in ("AGENTS.override.md", "AGENTS.md") if (root/n).is_file()],
            "limitations": ["Inventory only; inspect relevant code, ancestor instructions and contracts before implementation."]}


def plan(change, package, project=None):
    if not isinstance(change, dict) or set(change) - CHANGE_FIELDS:
        raise ContractError("Unknown change fields or invalid change object")
    request = change.get("request")
    if not isinstance(request, str) or not request.strip():
        raise ContractError("request must be nonempty text")
    mode = change.get("mode", infer_mode(request))
    if mode not in {"implement", "analyze", "plan", "explain", "audit"}:
        raise ContractError("Invalid mode")
    text = normalize(request)
    if mode == "implement" and matches(text, ["sem implementar", "nao implemente", "somente analise", "apenas explique", "only analyze", "only explain"]):
        raise ContractError("Implementation mode conflicts with an explicit read-only request")
    traits = change.get("traits", [])
    if not isinstance(traits, list) or any(t not in TRAITS for t in traits):
        raise ContractError("Unknown traits")
    traits = set(traits)
    reasons = []
    for trait, terms in HIGH.items():
        if matches(text, terms):
            traits.add(trait)
            reasons.append("Sensitive signal in request: " + trait)
    for trait, terms in {
        "ui": ["css", "interface", "formulario", "form", "scroll", "drag", "ux"],
        "database": ["banco", "database", "sql", "schema", "esquema"],
        "api": ["endpoint", "api"], "performance": ["performance", "latencia", "lento", "slow"],
        "integration": ["integracao", "integration"], "concurrency": ["concorrencia", "concurrency"],
    }.items():
        if matches(text, terms):
            traits.add(trait)
    if re.search(r"\b(get|post|put|patch|delete|head|options)\s+/", text):
        traits.add("api")
    for key in ("acceptance", "ambiguities"):
        values = change.get(key, [])
        if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ContractError(key + " must contain nonempty text entries")
    if change.get("scope", "unknown") not in {"local", "module", "system", "unknown"}:
        raise ContractError("Invalid scope")
    if "reversible" in change and type(change["reversible"]) is not bool:
        raise ContractError("reversible must be boolean")
    catalog = workflows(package)
    workflow = change.get("workflow")
    if workflow is None:
        workflow = "feature-development"
        routes = [
            ("incident-response", ["incidente", "incident", "indisponivel", "outage"]),
            ("release-readiness", ["producao", "production", "release", "deploy"]),
            ("security-review", ["seguranca", "security", "autenticacao", "authentication"]),
            ("quality-audit", ["auditoria de qualidade", "quality audit"]),
            ("project-bootstrap", ["novo projeto", "bootstrap", "new project"]),
            ("architecture-change", ["arquitetural", "architecture", "arquitetura"]),
            ("refactoring", ["refatore", "refactor", "refatoracao"]),
            ("bug-investigation", ["corrija", "bug", "fix", "conflito"]),
        ]
        for candidate, terms in routes:
            if candidate == "security-review" and mode == "implement":
                continue
            if matches(text, terms):
                workflow = candidate
                break
    if workflow not in catalog:
        raise ContractError("Unknown workflow")
    risk = "medium"
    if traits.intersection(HIGH) or workflow in {"architecture-change", "release-readiness", "incident-response", "security-review"}:
        risk = "high"
        reasons.append("Critical surface or workflow; inspect impact before changing")
    elif change.get("scope") == "local" and change.get("reversible") is True and workflow == "bug-investigation" and not traits.intersection({"integration", "api", "database", "concurrency"}):
        risk = "low"
        reasons.append("Explicitly local, reversible correction without critical signals")
    else:
        reasons.append("Feature, module impact or insufficient context to classify as low")
    selected = ["prompt-engineer"]
    if mode != "explain":
        selected += catalog[workflow]["skills"]
        for trait, skill in {"ui": "product-ux", "database": "database-engineer", "migration": "database-engineer", "auth": "security-auditor", "sensitive-data": "security-auditor", "api": "software-architect", "performance": "performance-engineer"}.items():
            if trait in traits:
                selected.append(skill)
        if mode != "implement":
            selected = [s for s in selected if s not in {"implementation-standards", "release-manager"} or workflow == "release-readiness"]
        if risk == "low":
            selected = [s for s in selected if s not in {"software-architect", "technical-documentation"}]
    steps = catalog[workflow]["steps"] if mode == "implement" else [
        {"id": "understand", "depends_on": [], "action": "Inspect relevant context without changing code"},
        {"id": "deliver", "depends_on": ["understand"], "action": "Deliver the requested " + mode + "; no implementation is authorized"},
    ]
    acceptance = change.get("acceptance", [])
    ambiguities = change.get("ambiguities", [])
    return {"schema_version": 1, "original_request": request, "mode": mode,
            "code_changes_authorized_by_mode": mode == "implement", "workflow": workflow,
            "risk": risk, "risk_reasons": reasons, "traits": sorted(traits),
            "skills": list(dict.fromkeys(selected)), "acceptance": acceptance,
            "acceptance_source": "provided by operator; validate against request/context",
            "ambiguities": ambiguities, "implementation_ready": mode == "implement" and bool(acceptance) and not ambiguities,
            "steps": steps, "gates": ["acceptance", "review"] + ([] if mode == "explain" else ["affected-validation"]) + (["recovery-and-sensitive-surface-review"] if risk == "high" else []),
            "context": discover(project) if project else None,
            "limits": ["Triage uses conservative rules; it does not understand arbitrary language or resolve business ambiguity.",
                       "Risk, mode and acceptance must be confirmed from real context; a plan is not proof of authorization or quality.",
                       "Release, destructive actions and external mutations require applicable specific authorization."]}
