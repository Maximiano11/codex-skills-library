"""Lifecycle tests with isolated source snapshots and disposable user profiles."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_install_skills as fixture

ROOT, installer = fixture.ROOT, fixture.installer


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        fixture.InstallerTests.setUp(self)
        self.source = Path(self.temp.name)/'source'
        (self.source/'skills/local').mkdir(parents=True)
        for name in ('brandkit', 'minimalist-ui'):
            shutil.copytree(ROOT/self.entries[name]['path'], self.source/self.entries[name]['path'])
        self.entries = {name: dict(self.entries[name]) for name in ('brandkit', 'minimalist-ui')}

    def operate(self, mode, names=None, dry=False, adopt=False):
        return installer.manage(self.source, self.entries, names or ['brandkit'], self.profile, dry, mode, adopt)

    def install_one(self):
        self.operate('install')

    def change_upstream(self):
        entry = self.entries['brandkit']
        (self.source/entry['path']/'SKILL.md').write_text('New upstream skill\n')
        snapshot = installer.inventory(self.source/entry['path'])
        entry['sha256'] = hashlib.sha256(json.dumps(snapshot[0], sort_keys=True).encode()).hexdigest()

    def state(self):
        return installer.read_state(installer.normalized_profile(self.profile))

    def operations(self):
        return list((self.profile/'skills-library/backups').glob('*/operation.json'))

    def test_update_retains_exact_original_and_previous_state(self):
        self.install_one()
        before = installer.inventory(self.profile/'skills/brandkit')
        state_before = self.state()
        self.change_upstream()
        self.assertEqual(self.operate('update'), [('brandkit', 'atualizar')])
        self.assertEqual((self.profile/'skills/brandkit/SKILL.md').read_text(), 'New upstream skill\n')
        journals = [j for j in self.operations() if json.loads(j.read_text())['mode']=='update']
        self.assertEqual(len(journals), 1)
        self.assertEqual(installer.inventory(journals[0].parent/'skills/brandkit'), before)
        self.assertEqual(json.loads(journals[0].read_text())['before'], state_before)
        self.assertEqual(json.loads(journals[0].read_text())['status'], 'completed')
        self.assertEqual(self.state()['skills']['brandkit'], installer.record(installer.inventory(self.profile/'skills/brandkit')))

    def test_uninstall_moves_original_to_backup_preserves_configuration(self):
        self.install_one()
        for name in ('config.toml','AGENTS.md','AGENTS.override.md'):
            (self.profile/name).write_text('keep '+name)
        custom = self.profile/'skills/custom';custom.mkdir();(custom/'file').write_text('keep')
        before = installer.inventory(self.profile/'skills/brandkit')
        self.operate('uninstall')
        self.assertFalse((self.profile/'skills/brandkit').exists())
        self.assertNotIn('brandkit', self.state()['skills'])
        journal = next(j for j in self.operations() if json.loads(j.read_text())['mode']=='uninstall')
        self.assertEqual(installer.inventory(journal.parent/'skills/brandkit'), before)
        for name in ('config.toml','AGENTS.md','AGENTS.override.md'):
            self.assertEqual((self.profile/name).read_text(), 'keep '+name)
        self.assertEqual((custom/'file').read_text(), 'keep')

    def test_local_edits_block_update_and_uninstall_without_writes(self):
        for mode in ('update', 'uninstall'):
            with self.subTest(mode=mode):
                if not (self.profile/'skills/brandkit').exists():
                    self.install_one()
                target = self.profile/'skills/brandkit/SKILL.md'
                target.write_text('my local edits')
                state = (self.profile/'skills-library/state.json').read_bytes()
                count = len(self.operations())
                with self.assertRaises(installer.InstallError):
                    self.operate(mode)
                self.assertEqual(target.read_text(), 'my local edits')
                self.assertEqual((self.profile/'skills-library/state.json').read_bytes(), state)
                self.assertEqual(len(self.operations()), count)

    def test_local_added_deleted_and_permission_changes_block(self):
        self.install_one()
        target = self.profile/'skills/brandkit'
        for kind in ('added', 'deleted', 'permissions', 'directory-permissions'):
            with self.subTest(kind=kind):
                shutil.rmtree(target)
                shutil.copytree(self.source/self.entries['brandkit']['path'], target)
                if kind=='added': (target/'notes.txt').write_text('mine')
                if kind=='deleted': (target/'SKILL.md').unlink()
                if kind=='permissions': (target/'SKILL.md').chmod(0o600)
                if kind=='directory-permissions':
                    (target/'private').mkdir(mode=0o700)
                with self.assertRaises(installer.InstallError):
                    self.operate('uninstall')
                self.assertTrue(target.exists())

    def test_unmanaged_identical_not_adopted_without_explicit_flag(self):
        target = self.profile/'skills/brandkit'
        shutil.copytree(self.source/self.entries['brandkit']['path'], target)
        self.operate('install')
        self.assertFalse((self.profile/'skills-library').exists())
        for mode in ('update','uninstall'):
            with self.assertRaises(installer.InstallError):
                self.operate(mode)
        before = installer.inventory(target)
        self.operate('install', adopt=True)
        self.assertIn('brandkit', self.state()['skills'])
        self.assertEqual(installer.inventory(target), before)
        self.assertTrue(any((j.parent/'skills/brandkit').exists() for j in self.operations()))
        self.operate('uninstall')
        self.assertFalse(target.exists())

    def test_adoption_refuses_modified_legacy_copy(self):
        target = self.profile/'skills/brandkit'
        shutil.copytree(self.source/self.entries['brandkit']['path'], target)
        (target/'SKILL.md').write_text('legacy adapted')
        with self.assertRaises(installer.InstallError):
            self.operate('install', adopt=True)
        self.assertEqual((target/'SKILL.md').read_text(), 'legacy adapted')
        self.assertFalse((self.profile/'skills-library').exists())

    def test_lifecycle_dry_runs_preserve_all_profile_bytes(self):
        self.install_one();self.change_upstream()
        before = installer.inventory(self.profile)
        self.operate('update', dry=True)
        self.operate('uninstall', dry=True)
        self.assertEqual(installer.inventory(self.profile), before)

    def test_update_batch_conflict_prevents_first_skill_mutation(self):
        self.operate('install', ['brandkit','minimalist-ui'])
        before = (self.profile/'skills/brandkit/SKILL.md').read_bytes()
        (self.profile/'skills/minimalist-ui/SKILL.md').write_text('local')
        self.change_upstream()
        with self.assertRaises(installer.InstallError):
            self.operate('update', ['brandkit','minimalist-ui'])
        self.assertEqual((self.profile/'skills/brandkit/SKILL.md').read_bytes(), before)

    def test_backup_failure_before_move_preserves_original(self):
        self.install_one(); self.change_upstream()
        before = installer.inventory(self.profile/'skills/brandkit')
        with patch.object(Path,'rename', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                self.operate('update')
        self.assertEqual(installer.inventory(self.profile/'skills/brandkit'), before)
        with self.assertRaisesRegex(installer.InstallError, 'incompleta'):
            self.operate('uninstall')

    def test_failure_after_backup_preserves_original_and_blocks_retry(self):
        self.install_one(); self.change_upstream()
        before = installer.inventory(self.profile/'skills/brandkit')
        original_copy = shutil.copytree
        def fail_target(source, target, *args, **kwargs):
            if Path(target)==installer.normalized_profile(self.profile)/'skills/brandkit':
                raise OSError('copy failure')
            return original_copy(source,target,*args,**kwargs)
        with patch.object(shutil,'copytree',side_effect=fail_target):
            with self.assertRaises(OSError):
                self.operate('update')
        journal = next(j for j in self.operations() if json.loads(j.read_text())['mode']=='update')
        self.assertEqual(installer.inventory(journal.parent/'skills/brandkit'),before)
        self.assertEqual(json.loads(journal.read_text())['status'],'pending')
        with self.assertRaisesRegex(installer.InstallError,'incompleta'):
            self.operate('install')

    def test_symlink_state_and_backup_are_rejected(self):
        self.install_one()
        state = self.profile/'skills-library/state.json'
        outside = Path(self.temp.name)/'outside.json'; outside.write_text(state.read_text())
        state.unlink();state.symlink_to(outside)
        with self.assertRaises(installer.InstallError):
            self.operate('uninstall')
        self.assertTrue((self.profile/'skills/brandkit').exists())

    def test_lock_blocks_mutation_and_dry_run(self):
        self.install_one()
        lock = self.profile/'skills-library/lock'; lock.write_text('other process')
        for dry in (True,False):
            with self.assertRaisesRegex(installer.InstallError,'lock'):
                self.operate('uninstall',dry=dry)
        self.assertEqual(lock.read_text(),'other process')

    def test_uninstall_removed_catalog_entry(self):
        self.install_one();self.entries={}
        self.operate('uninstall')
        self.assertFalse((self.profile/'skills/brandkit').exists())

    def test_missing_managed_tree_is_not_silently_removed_from_state(self):
        self.install_one()
        shutil.rmtree(self.profile/'skills/brandkit')
        for mode in ('update', 'uninstall'):
            with self.assertRaises(installer.InstallError):
                self.operate(mode)
        self.assertIn('brandkit', self.state()['skills'])

    def test_state_write_failure_retains_backup_and_blocks_followup(self):
        self.install_one(); self.change_upstream()
        before = installer.inventory(self.profile/'skills/brandkit')
        original = installer.atomic_json
        def failing_write(path, value):
            if path.name=='state.json':
                raise OSError('cannot save state')
            return original(path, value)
        with patch.object(installer, 'atomic_json', side_effect=failing_write):
            with self.assertRaises(OSError):
                self.operate('update')
        journal = next(j for j in self.operations() if json.loads(j.read_text())['mode']=='update')
        self.assertEqual(installer.inventory(journal.parent/'skills/brandkit'), before)
        with self.assertRaisesRegex(installer.InstallError, 'incompleta'):
            self.operate('update')

    def test_root_permission_changes_are_preserved(self):
        self.install_one()
        target = self.profile/'skills/brandkit'; target.chmod(0o700)
        for mode in ('update','uninstall'):
            with self.assertRaises(installer.InstallError):
                self.operate(mode)
        self.assertEqual(target.stat().st_mode & 0o777,0o700)

    def test_symlink_backup_root_blocks_before_skill_mutation(self):
        self.install_one()
        backups = self.profile/'skills-library/backups'
        shutil.rmtree(backups)
        outside = Path(self.temp.name)/'outside';outside.mkdir()
        backups.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            self.operate('uninstall')
        self.assertTrue((self.profile/'skills/brandkit/SKILL.md').exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_foreign_registry_is_preserved(self):
        control = self.profile/'skills-library';control.mkdir(parents=True)
        registry = control/'state.json';registry.write_text('{"version":1,"skills":{}}')
        before = registry.read_bytes()
        with self.assertRaises(installer.InstallError):
            self.operate('install')
        self.assertEqual(registry.read_bytes(),before)
        self.assertFalse((self.profile/'skills').exists())

    def test_identical_update_creates_no_extra_backup(self):
        self.install_one()
        before = installer.inventory(self.profile)
        self.assertEqual(self.operate('update'), [('brandkit','mantida (idêntica)')])
        self.assertEqual(installer.inventory(self.profile),before)

    def test_update_applies_upstream_additions_and_removals_retains_backup(self):
        source = self.source/self.entries['brandkit']['path']
        (source/'old.txt').write_text('old resource')
        def refresh():
            files = installer.inventory(source)[0]
            self.entries['brandkit']['sha256'] = hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()
        refresh();self.install_one()
        (source/'old.txt').unlink();(source/'new.txt').write_text('new resource');refresh()
        self.operate('update')
        self.assertFalse((self.profile/'skills/brandkit/old.txt').exists())
        self.assertEqual((self.profile/'skills/brandkit/new.txt').read_text(),'new resource')
        journal = next(j for j in self.operations() if json.loads(j.read_text())['mode']=='update')
        self.assertEqual((journal.parent/'skills/brandkit/old.txt').read_text(),'old resource')

    def test_uninstall_batch_preserves_all_if_one_is_modified(self):
        self.operate('install', ['brandkit','minimalist-ui'])
        (self.profile/'skills/minimalist-ui/SKILL.md').write_text('local')
        count = len(self.operations())
        with self.assertRaises(installer.InstallError):
            self.operate('uninstall',['brandkit','minimalist-ui'])
        self.assertTrue((self.profile/'skills/brandkit/SKILL.md').exists())
        self.assertEqual(len(self.operations()),count)

    def test_update_rejects_tampered_source_before_backup(self):
        self.install_one()
        before = installer.inventory(self.profile)
        (self.source/self.entries['brandkit']['path']/'SKILL.md').write_text('tampered')
        with self.assertRaises(installer.InstallError):
            self.operate('update')
        self.assertEqual(installer.inventory(self.profile),before)

    def test_cli_update_uninstall_all_use_managed_selection(self):
        self.install_one()
        script=ROOT/'scripts/install_skills.py'
        for mode in ('update','uninstall'):
            result=subprocess.run([sys.executable,'-B',str(script),mode,'--all','--codex-home',str(self.profile)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse((self.profile/'skills/brandkit').exists())


if __name__=='__main__':
    unittest.main()
