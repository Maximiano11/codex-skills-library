#!/usr/bin/env python3
"""Install selected, openly licensed snapshot skills without replacing user files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]


class InstallError(Exception):
    pass


def inventory(directory: Path) -> tuple[dict[str, str], set[str], dict[str, int]]:
    """Reject links/special files; include empty directories and executable modes."""
    if directory.is_symlink() or not directory.is_dir():
        raise InstallError(f'Pasta inválida ou link simbólico: {directory}')
    files, directories, modes = {}, set(), {}
    for path in sorted(directory.rglob('*')):
        relative = path.relative_to(directory).as_posix()
        kind = path.lstat().st_mode
        if stat.S_ISLNK(kind):
            raise InstallError(f'Link simbólico não permitido: {path}')
        if stat.S_ISDIR(kind):
            directories.add(relative)
        elif stat.S_ISREG(kind):
            files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
            modes[relative] = kind & 0o111
        else:
            raise InstallError(f'Arquivo especial não permitido: {path}')
    return files, directories, modes


def catalog(root: Path) -> dict[str, dict]:
    data = json.loads((root / 'manifest.json').read_text())
    result = {}
    for entry in data['skills']:
        if entry.get('distribution') != 'included-open-source':
            continue
        name, relative = entry['name'], entry['path']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in result:
            raise InstallError(f'Nome inválido ou duplicado no catálogo: {name}')
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts or path.parts[:1] != ('skills',):
            raise InstallError(f'Caminho inválido no catálogo: {relative}')
        source = root / path
        for parent in [source, *source.parents]:
            if parent == root:
                break
            if parent.is_symlink():
                raise InstallError(f'Link simbólico no pacote: {parent}')
        result[name] = entry
    return result


def validate_source(root: Path, entry: dict) -> tuple:
    source = root / entry['path']
    snapshot = inventory(source)
    digest = hashlib.sha256(json.dumps(snapshot[0], sort_keys=True).encode()).hexdigest()
    if digest != entry['sha256']:
        raise InstallError(f'Integridade divergente: {entry["name"]}; obtenha um clone íntegro.')
    if not (source / 'SKILL.md').is_file():
        raise InstallError(f'SKILL.md ausente: {entry["name"]}')
    return snapshot


def safe_destination(path: Path) -> None:
    for item in [*reversed(path.parents), path]:
        if item.is_symlink():
            raise InstallError(f'Link simbólico no destino: {item}')
        if item.exists() and not item.is_dir():
            raise InstallError(f'Destino não é diretório: {item}')


def install(root: Path, entries: dict, names: list[str], profile: Path, dry_run: bool) -> list[tuple[str, str]]:
    unknown = sorted(set(names) - entries.keys())
    if unknown:
        raise InstallError('Skills indisponíveis para cópia: ' + ', '.join(unknown))
    profile = Path(os.path.abspath(profile.expanduser()))
    if profile.is_symlink():
        raise InstallError(f'Perfil não pode ser link simbólico: {profile}')
    # Canonicalize system ancestors (e.g. macOS /var -> /private/var).
    profile = profile.parent.resolve() / profile.name
    destination = profile / 'skills'
    safe_destination(destination)
    plan = []
    snapshots = {}
    for name in dict.fromkeys(names):
        entry = entries[name]
        snapshot = validate_source(root, entry)
        snapshots[name] = snapshot
        target = destination / name
        safe_destination(target)
        # Avoid shadowing a client-provided system skill with a second user copy.
        bundled = destination / '.system' / name
        if not target.exists() and (bundled.exists() or bundled.is_symlink()):
            raise InstallError(f'Skill já disponível em {bundled}; não será duplicada.')
        if target.exists():
            if inventory(target) != snapshot:
                raise InstallError(f'Conflito: {target}. Nenhuma skill foi copiada; preserve e compare a instalação existente.')
            plan.append((name, 'mantida (idêntica)'))
        else:
            plan.append((name, 'instalar'))
    if dry_run:
        return plan
    # Complete preflight above before creating any destination or copying any skill.
    for name, action in plan:
        if action != 'instalar':
            continue
        safe_destination(destination)
        target = destination / name
        safe_destination(target)
        if validate_source(root, entries[name]) != snapshots[name]:
            raise InstallError(f'Fonte mudou durante a instalação: {name}')
        # copytree exclusively creates the destination: existing directories are never merged.
        shutil.copytree(root / entries[name]['path'], target, symlinks=False)
        if inventory(target) != snapshots[name]:
            raise InstallError(f'Cópia divergente: {target}; revise a pasta antes de tentar novamente.')
    return plan


def choose(entries: dict) -> list[str]:
    if not sys.stdin.isatty():
        raise InstallError('Sem terminal interativo. Use --skills NOME ... ou --all; consulte list.')
    names = sorted(entries)
    for index, name in enumerate(names, 1):
        print(f'{index:2}. {name}')
    answer = input('Escolha nomes/números separados por espaço ou vírgula (all = todas; Enter = cancelar): ').strip()
    if not answer:
        return []
    if answer == 'all':
        return names
    selected = []
    for value in re.split(r'[\s,]+', answer):
        if value.isdecimal():
            index = int(value)
            if not 1 <= index <= len(names):
                raise InstallError(f'Número inválido: {value}')
            selected.append(names[index - 1])
        else:
            selected.append(value)
    return selected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list', help='Listar apenas as skills incluídas e suas licenças.')
    command = sub.add_parser('install', help='Selecionar e copiar skills para o perfil global.')
    selection = command.add_mutually_exclusive_group()
    selection.add_argument('--skills', '--skill', nargs='+', action='extend', metavar='NOME')
    selection.add_argument('--all', action='store_true', help='Selecionar todas as skills incluídas.')
    command.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex'))
    command.add_argument('--dry-run', action='store_true', help='Validar e mostrar o plano sem escrever.')
    args = parser.parse_args(argv)
    try:
        entries = catalog(ROOT)
        if args.command == 'list':
            for name, entry in sorted(entries.items()):
                print(f'{name:40} {entry["license"]:12} {entry["category"]}')
            print(f'\n{len(entries)} skills incluídas; referências externas não são instaláveis.')
            return 0
        names = sorted(entries) if args.all else args.skills if args.skills else choose(entries)
        if not names:
            print('Cancelado; nenhuma alteração.')
            return 0
        plan = install(ROOT, entries, names, args.codex_home, args.dry_run)
        print(f'Perfil: {args.codex_home.expanduser().absolute()}')
        for name, action in plan:
            print(f'{name}: {action}')
        print('Prévia; nenhuma escrita.' if args.dry_run else 'Concluído. Confira a descoberta em uma nova sessão do Codex.')
        print('AGENTS.md, config.toml e runtime Engineering OS não são modificados.')
        return 0
    except (InstallError, OSError, ValueError, KeyError, TypeError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        print('Arquivos existentes não são substituídos. Em falha de IO, cópias novas podem ficar parciais; revise-as.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
