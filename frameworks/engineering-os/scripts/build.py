#!/usr/bin/env python3
"""Build a local source archive with a SHA-256 inventory, without publishing."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def build(output):
    root=ROOT.resolve()
    output=Path(output).resolve()
    if output.is_relative_to(root) or output.exists():
        raise ValueError("Output must be new and outside the source tree")
    files={}
    for path in sorted(root.rglob("*")):
        rel=path.relative_to(root)
        if any(p in {".git","__pycache__",".venv"} for p in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError("Source archive refuses symlinks")
        if path.is_file() and rel.as_posix() != "SOURCE-MANIFEST.json" and not path.name.startswith(".env") and path.suffix not in {".key",".pem",".pyc"}:
            files[rel.as_posix()]=path.read_bytes()
    manifest={"version":(root/"VERSION").read_text().strip(),
              "files":{k:hashlib.sha256(v).hexdigest() for k,v in files.items()}}
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,"x",compression=zipfile.ZIP_DEFLATED) as archive:
        for rel,data in {**files,"SOURCE-MANIFEST.json":(json.dumps(manifest,indent=2)+"\n").encode()}.items():
            info=zipfile.ZipInfo("engineering-os/"+rel,date_time=(2026,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None: raise ValueError("Archive CRC verification failed")
        for rel,sha in manifest["files"].items():
            if hashlib.sha256(archive.read("engineering-os/"+rel)).hexdigest()!=sha:
                raise ValueError("Archive checksum mismatch")
    return {"output":str(output),"files":len(files),"bytes":output.stat().st_size,
            "sha256":hashlib.sha256(output.read_bytes()).hexdigest()}


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--out",required=True)
    print(json.dumps(build(parser.parse_args().out),indent=2))
