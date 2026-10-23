#!/usr/bin/env python3
"""Run the desktop Codex runtime without changing global PATH/configuration.

Usage: python3 codex_runtime.py -- exec ...
Use --codex PATH for an explicitly selected executable, or --print-runtime to inspect.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

DESKTOP_CLI = Path('/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex')


def resolve_runtime(explicit=None, environ=None):
    env = os.environ if environ is None else environ
    if explicit:
        candidate, source = Path(explicit).expanduser(), 'explicit'
    elif env.get('CODEX_CLI_PATH'):
        candidate, source = Path(env['CODEX_CLI_PATH']).expanduser(), 'desktop_environment'
    elif sys.platform == 'darwin' and DESKTOP_CLI.is_file():
        candidate, source = DESKTOP_CLI, 'desktop_installation'
    else:
        found = shutil.which('codex', path=env.get('PATH', os.defpath))
        if not found:
            raise FileNotFoundError('Codex executable not found; pass --codex PATH')
        candidate, source = Path(found), 'PATH'
    candidate = candidate.resolve()
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        raise FileNotFoundError(f'Codex executable is missing or not executable: {candidate}')
    return candidate, source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', type=Path)
    parser.add_argument('--print-runtime', action='store_true')
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        executable, source = resolve_runtime(args.codex)
        if args.print_runtime:
            print(json.dumps({'executable': str(executable), 'source': source}))
            return 0
        forwarded = args.arguments
        if forwarded[:1] == ['--']:
            forwarded = forwarded[1:]
        if not forwarded:
            parser.error('Provide Codex arguments after --, or use --print-runtime')
        os.execv(str(executable), [str(executable), *forwarded])
    except OSError as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
