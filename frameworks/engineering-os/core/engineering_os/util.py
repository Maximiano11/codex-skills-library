import hashlib
import json
import os
from pathlib import Path
import stat


class ContractError(ValueError):
    pass


def read_json(path):
    p = Path(path)
    if p.stat().st_size > 10 * 1024 * 1024:
        raise ContractError("JSON exceeds 10 MiB")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ContractError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(p.read_text(encoding="utf-8"), object_pairs_hook=unique)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def write_new(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")


def relative_file(root, value):
    p = Path(value)
    if p.is_absolute() or not p.parts or any(x in ("..", ".") for x in p.parts):
        raise ContractError("Expected a relative path without traversal")
    root = Path(root).resolve()
    target = root / p
    for ancestor in (target, *target.parents):
        if ancestor == root:
            break
        if ancestor.is_symlink():
            raise ContractError("Symlink is not permitted: " + str(ancestor))
    if not target.resolve().is_relative_to(root):
        raise ContractError("Path escapes root")
    return target


EXCLUDED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".eos-runs"}


def fingerprint(project):
    """Hash regular source bytes and symlink identities without following links/secrets."""
    root = Path(project).resolve()
    if not root.is_dir():
        raise ContractError("Project directory is absent")
    entries = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        for name in list(dirs) + sorted(files):
            p = Path(base) / name
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                entries[rel] = "symlink:" + digest(os.readlink(p).encode())
            elif p.is_file() and not (name.startswith(".env") or name.endswith((".pem", ".key", ".pyc"))):
                h = hashlib.sha256()
                with p.open("rb") as f:
                    for chunk in iter(lambda: f.read(1024 * 1024), b""):
                        h.update(chunk)
                entries[rel] = {"sha256": h.hexdigest(), "mode": stat.S_IMODE(p.stat().st_mode)}
            if len(entries) > 100000:
                raise ContractError("Fingerprint exceeds 100000 source files")
    return {"sha256": digest(canonical(entries)), "files": len(entries),
            "exclusions": sorted(EXCLUDED_DIRS) + [".env*", "*.pem", "*.key", "*.pyc"]}
