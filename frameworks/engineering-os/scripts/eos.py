#!/usr/bin/env python3
"""Run from source or the installer-managed runtime, without pip installation."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"core"), str(ROOT)]
from engineering_os.cli import main

if __name__ == "__main__":
    raise SystemExit(main(package=ROOT))
