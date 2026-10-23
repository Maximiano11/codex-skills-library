import argparse
import json
from pathlib import Path
import sys

from . import gates, orchestrator
from .util import ContractError, fingerprint, read_json, write_new


def main(argv=None, package=None):
    package = Path(package or Path(__file__).resolve().parents[2])
    parser = argparse.ArgumentParser(description="Engineering OS: local engineering decisions and evidence")
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("discover"); d.add_argument("--project", required=True)
    p = sub.add_parser("plan"); p.add_argument("--change", required=True); p.add_argument("--project"); p.add_argument("--out")
    f = sub.add_parser("fingerprint"); f.add_argument("--project", required=True)
    for name in ("run", "gate"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--project", required=True)
        cmd.add_argument("--profile", required=True)
        if name == "run":
            cmd.add_argument("--out", required=True)
            cmd.add_argument("--allow-exec", action="store_true")
            cmd.add_argument("--attestations")
        else:
            cmd.add_argument("--evidence", required=True)
    for name in ("install", "update", "uninstall", "doctor"):
        cmd = sub.add_parser(name)
        target = cmd.add_mutually_exclusive_group()
        target.add_argument("--codex-home")
        target.add_argument("--project")
        if name != "doctor":
            cmd.add_argument("--dry-run", action="store_true")
        if name == "update":
            cmd.add_argument("--allow-major", action="store_true")
    sub.add_parser("validate-package")
    sub.add_parser("evaluate")
    args = parser.parse_args(argv)
    try:
        if args.command == "discover":
            result = orchestrator.discover(args.project)
        elif args.command == "plan":
            result = orchestrator.plan(read_json(args.change), package, args.project)
            if args.out:
                write_new(args.out, result)
        elif args.command == "fingerprint":
            result = fingerprint(args.project)
        elif args.command == "run":
            result = gates.collect(args.project, read_json(args.profile), args.out, args.allow_exec,
                                   read_json(args.attestations) if args.attestations else None)
        elif args.command == "gate":
            result = gates.verify(args.project, read_json(args.profile), args.evidence)
        elif args.command in {"install", "update", "uninstall", "doctor"}:
            from adapters.codex.install import Target, apply, diagnose, plan_install, plan_uninstall
            target = Target(home=args.codex_home, project=args.project)
            if args.command == "doctor":
                result = diagnose(target)
            else:
                changes = plan_uninstall(target) if args.command == "uninstall" else plan_install(
                    package, target, args.command == "update", getattr(args, "allow_major", False))[0]
                result = apply(target, changes, args.dry_run)
        elif args.command == "validate-package":
            from .validation import validate_package
            result = validate_package(package)
        else:
            from .validation import evaluate
            result = evaluate(package)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        state = result.get("state", result.get("verdict", {}).get("state"))
        if state == "BLOCKED" or result.get("integrity") == "drift" or result.get("passed") is False:
            return 1
        if state == "PARTIALLY_VALIDATED":
            return 2
        return 0
    except (ContractError, OSError, ValueError, KeyError, TypeError) as e:
        print(json.dumps({"error": type(e).__name__, "message": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 3
