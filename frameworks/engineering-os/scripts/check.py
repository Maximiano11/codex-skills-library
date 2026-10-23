#!/usr/bin/env python3
"""Compile maintained Python sources in memory, without writing bytecode."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
paths=[]
for folder in ("core", "adapters", "scripts", "tests"):
    paths.extend(sorted((ROOT/folder).rglob("*.py")))
if not paths:
    raise SystemExit("No Python source found")
for path in paths:
    compile(path.read_bytes(),str(path),"exec")
print(str(len(paths))+" maintained Python sources compiled in memory")
