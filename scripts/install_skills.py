#!/usr/bin/env python3
"""Install, update and uninstall selected skills with ownership and backups."""
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
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


class InstallError(Exception):
    pass


def inventory(directory: Path) -> tuple[dict[str, str], set[str], dict[str, int]]:
    """Reject links/special files; include empty directories and permission modes."""
    if directory.is_symlink() or not directory.is_dir():
        raise InstallError(f'Pasta inválida ou link simbólico: {directory}')
    files, directories, modes = {}, set(), {'.': stat.S_IMODE(directory.stat().st_mode)}
    for path in sorted(directory.rglob('*')):
        relative = path.relative_to(directory).as_posix()
        kind = path.lstat().st_mode
        if stat.S_ISLNK(kind):
            raise InstallError(f'Link simbólico não permitido: {path}')
        if stat.S_ISDIR(kind):
            directories.add(relative)
            modes[relative] = stat.S_IMODE(kind)
        elif stat.S_ISREG(kind):
            files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
            modes[relative] = stat.S_IMODE(kind)
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


STATE_DIR = 'skills-library'
NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')


def normalized_profile(profile: Path) -> Path:
    profile = Path(os.path.abspath(profile.expanduser()))
    if profile.is_symlink():
        raise InstallError(f'Perfil não pode ser link simbólico: {profile}')
    return profile.parent.resolve() / profile.name


def record(snapshot: tuple) -> dict:
    return {'files': snapshot[0], 'directories': sorted(snapshot[1]), 'modes': snapshot[2]}


def checked_file(path: Path) -> None:
    safe_destination(path.parent)
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise InstallError(f'Arquivo de controle inválido: {path}')


def read_state(profile: Path) -> dict:
    control = profile / STATE_DIR
    safe_destination(control)
    path = control / 'state.json'
    checked_file(path)
    state = json.loads(path.read_text()) if path.exists() else {'version': 1, 'installer': 'codex-skills-library', 'skills': {}}
    if not isinstance(state, dict) or state.get('version') != 1 or state.get('installer') != 'codex-skills-library' or not isinstance(state.get('skills'), dict):
        raise InstallError('Estado do instalador inválido; preserve-o e revise antes de continuar.')
    for name, snapshot in state['skills'].items():
        if not NAME.fullmatch(name) or not isinstance(snapshot, dict) or set(snapshot) != {'files', 'directories', 'modes'}:
            raise InstallError('Registro de propriedade inválido.')
        if not isinstance(snapshot['files'], dict) or not isinstance(snapshot['directories'], list) or not isinstance(snapshot['modes'], dict):
            raise InstallError('Snapshot de propriedade inválido.')
    backups = control / 'backups'
    safe_destination(backups)
    if backups.exists():
        for journal in backups.glob('*/operation.json'):
            checked_file(journal)
            operation = json.loads(journal.read_text())
            if not isinstance(operation, dict) or operation.get('status') != 'completed':
                raise InstallError(f'Operação incompleta: {journal}. Revise backup e estado antes de continuar.')
    return state


def atomic_json(path: Path, value: dict) -> None:
    checked_file(path)
    temporary = path.with_name('.' + path.name + '-' + uuid.uuid4().hex)
    try:
        with temporary.open('x', encoding='utf-8') as handle:
            os.chmod(temporary, 0o600)
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def profile_lock(profile: Path):
    control = profile / STATE_DIR
    safe_destination(control)
    control.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = control / 'lock'
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise InstallError(f'Instalador ocupado ou lock pendente: {lock}') from error
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


def prepare(root: Path, entries: dict, names: list[str], profile: Path, mode: str,
            state: dict, adopt: bool) -> tuple[list[tuple[str, str]], dict]:
    destination = profile / 'skills'
    safe_destination(destination)
    allowed = entries if mode == 'install' else state['skills']
    unknown = sorted(set(names) - allowed.keys())
    if unknown:
        raise InstallError('Skills indisponíveis ou não gerenciadas: ' + ', '.join(unknown))
    plan, snapshots = [], {}
    for name in dict.fromkeys(names):
        if not NAME.fullmatch(name):
            raise InstallError(f'Nome inválido: {name}')
        target = destination / name
        safe_destination(target)
        current = record(inventory(target)) if target.exists() else None
        baseline = state['skills'].get(name)
        if baseline is not None and current != baseline:
            raise InstallError(f'Alterações locais ou pasta ausente: {target}. Preservadas; lote bloqueado.')
        if mode != 'uninstall':
            if name not in entries:
                raise InstallError(f'Skill fora do catálogo atual: {name}. Pode ser desinstalada, mas não atualizada.')
            snapshots[name] = record(validate_source(root, entries[name]))
        if mode == 'uninstall':
            action = 'desinstalar'
        elif mode == 'update':
            action = 'mantida (idêntica)' if current == snapshots[name] else 'atualizar'
        else:
            bundled = destination / '.system' / name
            if current is None and (bundled.exists() or bundled.is_symlink()):
                raise InstallError(f'Skill já disponível em {bundled}; não será duplicada.')
            if current is not None:
                if current != snapshots[name]:
                    raise InstallError(f'Conflito: {target}. Use update para skills gerenciadas; adaptações locais serão preservadas.')
                action = 'adotar' if adopt and baseline is None else 'mantida (idêntica)'
            else:
                action = 'instalar'
        plan.append((name, action))
    return plan, snapshots


def manage(root: Path, entries: dict, names: list[str], profile: Path, dry_run: bool,
           mode: str = 'install', adopt: bool = False) -> list[tuple[str, str]]:
    profile = normalized_profile(profile)
    lock = profile / STATE_DIR / 'lock'
    if lock.exists() or lock.is_symlink():
        raise InstallError(f'Instalador ocupado ou lock pendente: {lock}')
    state = read_state(profile)
    plan, snapshots = prepare(root, entries, names, profile, mode, state, adopt)
    if dry_run or not any(action != 'mantida (idêntica)' for _, action in plan):
        return plan
    with profile_lock(profile):
        # Re-plan under the cooperative profile lock before any skill mutation.
        state = read_state(profile)
        plan, snapshots = prepare(root, entries, names, profile, mode, state, adopt)
        changed = [(name, action) for name, action in plan if action != 'mantida (idêntica)']
        if not changed:
            return plan
        operation = profile / STATE_DIR / 'backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex)
        operation.mkdir(parents=True, mode=0o700)
        journal = {'status': 'pending', 'mode': mode, 'skills': changed, 'before': state, 'expected_sources': snapshots}
        atomic_json(operation / 'operation.json', journal)
        print(f'Backup/journal: {operation}')
        next_state = json.loads(json.dumps(state))
        for name, action in changed:
            target = profile / 'skills' / name
            safe_destination(target)
            before = state['skills'].get(name)
            if action in ('atualizar', 'desinstalar'):
                if record(inventory(target)) != before:
                    raise InstallError(f'Alteração concorrente preservada: {target}')
                if action == 'atualizar':
                    if record(validate_source(root, entries[name])) != snapshots[name]:
                        raise InstallError(f'Fonte mudou: {name}')
                    staged = operation / 'staged' / name
                    shutil.copytree(root / entries[name]['path'], staged)
                    if record(inventory(staged)) != snapshots[name]:
                        raise InstallError(f'Cópia de preparação divergente: {name}')
                backup = operation / 'skills' / name
                backup.parent.mkdir(exist_ok=True, mode=0o700)
                # Move the original intact into the retained backup; never delete its bytes.
                if record(inventory(target)) != before:
                    raise InstallError(f'Alteração concorrente preservada: {target}')
                target.rename(backup)
                if record(inventory(backup)) != before:
                    raise InstallError(f'Backup divergente; original preservado em {backup}')
                if action == 'atualizar':
                    shutil.copytree(staged, target)
                    if record(inventory(target)) != snapshots[name]:
                        raise InstallError(f'Cópia divergente: {target}')
                    next_state['skills'][name] = snapshots[name]
                else:
                    del next_state['skills'][name]
            elif action == 'instalar':
                if record(validate_source(root, entries[name])) != snapshots[name]:
                    raise InstallError(f'Fonte mudou: {name}')
                shutil.copytree(root / entries[name]['path'], target)
                if record(inventory(target)) != snapshots[name]:
                    raise InstallError(f'Cópia divergente: {target}')
                next_state['skills'][name] = snapshots[name]
            elif action == 'adotar':
                if record(inventory(target)) != snapshots[name]:
                    raise InstallError(f'Alteração concorrente preservada: {target}')
                # Explicit adoption leaves the existing tree untouched and backs it up.
                backup = operation / 'skills' / name
                shutil.copytree(target, backup)
                if record(inventory(backup)) != snapshots[name]:
                    raise InstallError(f'Backup divergente: {name}')
                next_state['skills'][name] = snapshots[name]
        atomic_json(profile / STATE_DIR / 'state.json', next_state)
        journal['status'] = 'completed'
        atomic_json(operation / 'operation.json', journal)
        print(f'Backup/journal preservado: {operation}')
    return plan


def install(root: Path, entries: dict, names: list[str], profile: Path, dry_run: bool) -> list[tuple[str, str]]:
    return manage(root, entries, names, profile, dry_run)


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
    for mode in ('install', 'update', 'uninstall'):
        command = sub.add_parser(mode, help={'install': 'Instalar skills novas.', 'update': 'Atualizar skills gerenciadas intactas.', 'uninstall': 'Remover skills gerenciadas intactas, com backup.'}[mode])
        selection = command.add_mutually_exclusive_group()
        selection.add_argument('--skills', '--skill', nargs='+', action='extend', metavar='NOME')
        selection.add_argument('--all', action='store_true', help='Todas as incluídas (install) ou gerenciadas (update/uninstall).')
        command.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex'))
        command.add_argument('--dry-run', action='store_true', help='Validar e mostrar o plano sem escrever.')
        if mode == 'install':
            command.add_argument('--adopt-existing', action='store_true', help='Assumir explicitamente gestão de cópias existentes idênticas ao catálogo, com backup.')
    args = parser.parse_args(argv)
    try:
        entries = {} if args.command == 'uninstall' else catalog(ROOT)
        if args.command == 'list':
            for name, entry in sorted(entries.items()):
                print(f'{name:40} {entry["license"]:12} {entry["category"]}')
            print(f'\n{len(entries)} skills incluídas; referências externas não são instaláveis.')
            return 0
        selectable = entries if args.command == 'install' else read_state(normalized_profile(args.codex_home))['skills']
        names = sorted(selectable) if args.all else args.skills if args.skills else choose(selectable)
        if not names:
            print('Cancelado; nenhuma alteração.')
            return 0
        plan = manage(ROOT, entries, names, args.codex_home, args.dry_run, args.command, getattr(args, 'adopt_existing', False))
        print(f'Perfil: {args.codex_home.expanduser().absolute()}')
        for name, action in plan:
            print(f'{name}: {action}')
        print('Prévia; nenhuma escrita.' if args.dry_run else 'Concluído. Confira a descoberta em uma nova sessão do Codex.')
        print('AGENTS.md, config.toml e runtime Engineering OS não são modificados.')
        return 0
    except (InstallError, OSError, ValueError, KeyError, TypeError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        print('Adaptações e configurações são preservadas. Se houver operação incompleta, revise o journal/backup antes de continuar.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
