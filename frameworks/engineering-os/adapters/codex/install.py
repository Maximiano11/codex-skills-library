"""Owned-file installation with optimistic preconditions, backup and rollback."""
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import uuid

from engineering_os.util import ContractError, digest, read_json, relative_file

START = b"<!-- engineering-os:start -->"
END = b"<!-- engineering-os:end -->"
PARTS = ("core", "adapters", "scripts", "skills", "workflows", "policies", "templates", "docs", "examples")


def file_bytes(p):
    if p.is_symlink():
        raise ContractError("Refusing symlink: " + str(p))
    if p.exists() and not p.is_file():
        raise ContractError("Expected regular file: " + str(p))
    return p.read_bytes() if p.exists() else None


class Target:
    def __init__(self, home=None, project=None):
        self.project = project is not None
        self.root = Path(project if self.project else home or os.environ.get("CODEX_HOME") or Path.home()/".codex").expanduser().resolve()
        self.state_dir = ".engineering-os" if self.project else "engineering-os"
        self.skills_dir = ".agents/skills" if self.project else "skills"
        self.state_path = self.path(self.state_dir+"/install.json")

    def path(self, rel):
        return relative_file(self.root, rel)

    def load(self):
        if not self.state_path.exists():
            return None
        data = read_json(self.state_path)
        if data.get("schema_version") != 1 or not isinstance(data.get("files"), dict):
            raise ContractError("Unrecognized installation state")
        for rel, info in data["files"].items():
            self.path(rel)
            allowed = rel.startswith(self.state_dir+"/runtime/") or rel.startswith(self.skills_dir+"/")
            if not allowed or not isinstance(info, dict) or type(info.get("owned")) is not bool:
                raise ContractError("Invalid ownership record")
        if data.get("agents_path") not in {"AGENTS.md", "AGENTS.override.md"}:
            raise ContractError("Invalid instruction path in state")
        return data


def package_files(package):
    root = Path(package).resolve()
    result = {}
    for name in ("VERSION", "LICENSE", "README.md"):
        result[name] = file_bytes(root/name)
        if result[name] is None:
            raise ContractError("Incomplete package: " + name)
    for part in PARTS:
        directory = root/part
        if directory.is_symlink():
            raise ContractError("Package contains a symlink")
        for base, dirs, files in os.walk(directory, followlinks=False):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            if any((Path(base)/d).is_symlink() for d in dirs):
                raise ContractError("Package contains symlinked directory")
            for name in files:
                p = Path(base)/name
                if p.suffix in {".pyc", ".pyo"}:
                    continue
                result[p.relative_to(root).as_posix()] = file_bytes(p)
    return result


def instructions(runtime):
    path = str(runtime).replace("`", "")
    return ("\n\n" + START.decode() + "\n## Engineering OS\n\n"
            "- Em tarefas de software, aplique primeiro `prompt-engineer` e use `engineering-os`\n"
            "  para selecionar apenas os workflows e skills pertinentes ao risco e ao modo autorizado.\n"
            "- Reutilize governança/QA existentes. Análise, explicação, auditoria e planejamento\n"
            "  não autorizam implementação. Preserve regras e instruções específicas do projeto.\n"
            "- Use critérios verificáveis e evidências reais; informe VALIDATED, PARTIALLY_VALIDATED\n"
            "  ou BLOCKED no escopo verificado. Isso não autoriza publicação nem operações destrutivas.\n"
            "- Runtime local: `" + path + "`. Leia somente referências necessárias. Skills e\n"
            "  AGENTS.md orientam o agente; não garantem interceptação de todas as mensagens.\n"
            + END.decode() + "\n").encode()


def remove_block(content, expected):
    if content.count(START) != 1 or content.count(END) != 1 or content.count(expected) != 1:
        raise ContractError("Managed AGENTS block is missing, duplicated or locally modified")
    return content.replace(expected, b"", 1)


def plan_install(package, target, update=False, allow_major=False):
    from engineering_os.validation import validate_package
    validate_package(package)
    files = package_files(package)
    version = files["VERSION"].decode().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ContractError("Version must be semantic x.y.z")
    previous = target.load()
    if update and not previous:
        raise ContractError("No installation to update")
    if previous:
        old = tuple(map(int, previous["version"].split(".")))
        new = tuple(map(int, version.split(".")))
        if new < old or (new[0] != old[0] and not allow_major):
            raise ContractError("Downgrade or unapproved major-version migration")
        if new != old and not update:
            raise ContractError("Use update for a version change")
    desired = {target.state_dir+"/runtime/"+rel: data for rel, data in files.items()}
    for rel, data in files.items():
        if rel.startswith("skills/"):
            desired[target.skills_dir+"/"+rel[len("skills/"):]] = data
    old_entries = previous["files"] if previous else {}
    entries = {}
    changes = {}
    borrowed_names = set()
    prompt_root = target.path(target.skills_dir+"/prompt-engineer")
    if not previous and prompt_root.exists():
        text = file_bytes(prompt_root/"SKILL.md")
        if not text or not re.search(rb"(?m)^name:\s*['\"]?prompt-engineer['\"]?\s*$", text):
            raise ContractError("Existing prompt-engineer is not a recognizable skill")
        borrowed_names.add("prompt-engineer")
    elif previous:
        borrowed_names.update(previous.get("borrowed_skills", []))
    for rel, data in desired.items():
        dest = target.path(rel)
        current = file_bytes(dest)
        borrowed = any(rel.startswith(target.skills_dir+"/"+name+"/") for name in borrowed_names)
        old = old_entries.get(rel)
        if borrowed:
            # Borrow the existing folder as a whole, even if it has different references.
            if rel.endswith("/SKILL.md") and current is None:
                raise ContractError("Borrowed prompt-engineer disappeared")
            if current is not None:
                entries[rel] = {"owned": False, "sha256": digest(current)}
            continue
        if old and old["owned"]:
            if current is None or digest(current) != old["sha256"]:
                raise ContractError("Local modification blocks update: " + rel)
        elif current is not None:
            raise ContractError("Unmanaged file collision: " + rel)
        if current != data:
            changes[rel] = (current, data)
        entries[rel] = {"owned": True, "sha256": digest(data)}
    for rel, old in old_entries.items():
        if rel not in desired and old["owned"]:
            current = file_bytes(target.path(rel))
            if current is None or digest(current) != old["sha256"]:
                raise ContractError("Local modification blocks removal: " + rel)
            changes[rel] = (current, None)
    if previous:
        agents_path = previous["agents_path"]
        original_exists = previous["agents_original_exists"]
        current = file_bytes(target.path(agents_path))
        if current is None:
            raise ContractError("Instruction file disappeared")
        old_block = base64.b64decode(previous["agents_block"])
        base = remove_block(current, old_block)
    else:
        override = file_bytes(target.path("AGENTS.override.md"))
        agents_path = "AGENTS.override.md" if override and override.strip() else "AGENTS.md"
        current = file_bytes(target.path(agents_path))
        original_exists = current is not None
        base = current or b""
        if START in base or END in base:
            raise ContractError("Unmanaged or malformed Engineering OS instruction block")
    block = instructions(target.path(target.state_dir+"/runtime/scripts/eos.py"))
    updated = current.replace(old_block, block, 1) if previous else base + block
    if current != updated:
        changes[agents_path] = (current, updated)
    state = {"schema_version": 1, "version": version, "files": entries,
             "borrowed_skills": sorted(borrowed_names), "agents_path": agents_path,
             "agents_original_exists": original_exists, "agents_block": base64.b64encode(block).decode()}
    state_data = (json.dumps(state, indent=2, sort_keys=True)+"\n").encode()
    old_state = file_bytes(target.state_path)
    if old_state != state_data:
        changes[target.state_dir+"/install.json"] = (old_state, state_data)
    if previous and changes and not update:
        raise ContractError("Installed package differs; use update after reviewing --dry-run")
    return changes, state


def plan_uninstall(target):
    previous = target.load()
    if not previous:
        raise ContractError("No managed installation")
    changes = {}
    for rel, info in previous["files"].items():
        if not info["owned"]:
            continue
        current = file_bytes(target.path(rel))
        if current is None or digest(current) != info["sha256"]:
            raise ContractError("Local modification blocks uninstall: " + rel)
        changes[rel] = (current, None)
    rel = previous["agents_path"]
    current = file_bytes(target.path(rel))
    if current is None:
        raise ContractError("Instruction file disappeared")
    remaining = remove_block(current, base64.b64decode(previous["agents_block"]))
    changes[rel] = (current, remaining if remaining or previous["agents_original_exists"] else None)
    changes[target.state_dir+"/install.json"] = (file_bytes(target.state_path), None)
    return changes


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        path.unlink()
        return
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, name = tempfile.mkstemp(prefix=".eos-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def apply(target, changes, dry_run=False):
    summary = {"target": str(target.root), "dry_run": dry_run,
               "changes": [{"path": rel, "action": "remove" if after is None else "create" if before is None else "update"} for rel, (before, after) in sorted(changes.items())]}
    if dry_run or not changes:
        return summary
    state_dir = target.path(target.state_dir)
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = target.path(target.state_dir+"/install.lock")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
    except FileExistsError as e:
        raise ContractError("Another installation is active; inspect any stale lock manually") from e
    applied = []
    backup = None
    try:
        for rel, (before, _) in changes.items():
            if file_bytes(target.path(rel)) != before:
                raise ContractError("Concurrent modification; refusing transaction: " + rel)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        backup = target.path(target.state_dir+"/backups/"+stamp)
        backup.mkdir(parents=True, mode=0o700)
        journal = {}
        for rel, (before, _) in changes.items():
            journal[rel] = {"existed": before is not None, "sha256": digest(before) if before is not None else None}
            if before is not None:
                p = backup/digest(rel.encode())
                p.write_bytes(before); p.chmod(0o600)
        atomic_write(backup/"journal.json", (json.dumps(journal, indent=2)+"\n").encode())
        # State is written last, so incomplete transactions cannot appear installed.
        for rel in sorted(changes, key=lambda p: p == target.state_dir+"/install.json"):
            before, after = changes[rel]
            dest = target.path(rel)
            if file_bytes(dest) != before:
                raise ContractError("Concurrent modification during transaction: " + rel)
            atomic_write(dest, after)
            applied.append(rel)
        summary["backup"] = str(backup)
    except Exception:
        for rel in reversed(applied):
            before, after = changes[rel]
            dest = target.path(rel)
            if file_bytes(dest) == after:
                atomic_write(dest, before)
        raise
    finally:
        lock.unlink()
    return summary


def diagnose(target):
    state = target.load()
    if not state:
        return {"installed": False, "integrity": "not_installed", "target": str(target.root)}
    drift, borrowed = [], []
    for rel, info in state["files"].items():
        current = file_bytes(target.path(rel))
        if current is None or digest(current) != info["sha256"]:
            (drift if info["owned"] else borrowed).append(rel)
    try:
        remove_block(file_bytes(target.path(state["agents_path"])) or b"", base64.b64decode(state["agents_block"]))
    except ContractError:
        drift.append(state["agents_path"])
    active = "AGENTS.override.md" if (file_bytes(target.path("AGENTS.override.md")) or b"").strip() else "AGENTS.md"
    if active != state["agents_path"]:
        drift.append("instructions-shadowed-by-"+active)
    try:
        from engineering_os.validation import validate_package
        validate_package(target.path(target.state_dir+"/runtime"))
    except (ContractError, OSError, ValueError, KeyError, TypeError):
        drift.append("incomplete-or-invalid-runtime-package")
    return {"installed": True, "version": state["version"], "target": str(target.root),
            "integrity": "drift" if drift else "ok", "drift": drift,
            "borrowed_skills": state["borrowed_skills"], "borrowed_changes": borrowed,
            "limits": ["Checks owned file bytes and active instruction placement, not model compliance or hostile same-user tampering."]}
