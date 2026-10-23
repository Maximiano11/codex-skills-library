"""Filesystem behavior and preservation tests; never touch the real Codex profile."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install_skills.py')
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.profile = Path(self.temp.name) / 'profile'
        self.entries = installer.catalog(ROOT)

    def apply(self, names, dry=False):
        return installer.install(ROOT, self.entries, names, self.profile, dry)

    def test_catalog_only_includes_36_open_skills(self):
        self.assertEqual(len(self.entries), 36)
        self.assertNotIn('documents', self.entries)
        for entry in self.entries.values():
            installer.validate_source(ROOT, entry)

    def test_dry_run_creates_nothing(self):
        self.assertEqual(self.apply(['brandkit'], True), [('brandkit', 'instalar')])
        self.assertFalse(self.profile.exists())

    def test_selected_full_tree_and_existing_configuration_preserved(self):
        self.profile.mkdir()
        for name in ('AGENTS.md', 'AGENTS.override.md', 'config.toml'):
            (self.profile / name).write_text('unchanged ' + name)
        unrelated = self.profile / 'skills/custom'
        unrelated.mkdir(parents=True)
        (unrelated / 'SKILL.md').write_text('custom')
        self.apply(['brandkit', 'skill-creator'])
        for name in ('brandkit', 'skill-creator'):
            self.assertEqual(installer.inventory(self.profile/'skills'/name),
                             installer.inventory(ROOT/self.entries[name]['path']))
        self.assertFalse((self.profile/'skills/engineering-os').exists())
        self.assertEqual((unrelated/'SKILL.md').read_text(), 'custom')
        for name in ('AGENTS.md', 'AGENTS.override.md', 'config.toml'):
            self.assertEqual((self.profile/name).read_text(), 'unchanged ' + name)

    def test_identical_install_is_idempotent(self):
        self.apply(['brandkit'])
        target = self.profile/'skills/brandkit/SKILL.md'
        before = target.stat().st_mtime_ns
        self.assertEqual(self.apply(['brandkit']), [('brandkit', 'mantida (idêntica)')])
        self.assertEqual(target.stat().st_mtime_ns, before)

    def test_conflict_blocks_entire_batch(self):
        target = self.profile/'skills/brandkit'
        target.mkdir(parents=True)
        (target/'SKILL.md').write_text('adapted')
        with self.assertRaises(installer.InstallError):
            self.apply(['code-reviewer', 'brandkit'])
        self.assertFalse((self.profile/'skills/code-reviewer').exists())
        self.assertEqual((target/'SKILL.md').read_text(), 'adapted')

    def test_unknown_and_external_skill_block_before_writes(self):
        for name in ('documents', '../escape', 'does-not-exist'):
            with self.assertRaises(installer.InstallError):
                self.apply(['brandkit', name])
            self.assertFalse(self.profile.exists())

    def test_symbolic_destination_is_rejected(self):
        outside = Path(self.temp.name)/'outside'; outside.mkdir()
        self.profile.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            self.apply(['brandkit'])
        self.assertEqual(list(outside.iterdir()), [])

    def test_symbolic_skill_is_rejected(self):
        self.profile.mkdir(); (self.profile/'skills').mkdir()
        target = Path(self.temp.name)/'outside'; target.mkdir()
        (self.profile/'skills/brandkit').symlink_to(target, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            self.apply(['brandkit'])
        self.assertEqual(list(target.iterdir()), [])

    def test_bundled_system_skill_is_not_shadowed(self):
        target = self.profile/'skills/.system/skill-creator'; target.mkdir(parents=True)
        (target/'SKILL.md').write_text('client supplied')
        with self.assertRaises(installer.InstallError):
            self.apply(['brandkit', 'skill-creator'])
        self.assertFalse((self.profile/'skills/brandkit').exists())

    def test_changed_source_hash_is_rejected(self):
        self.entries['brandkit'] = dict(self.entries['brandkit'], sha256='0'*64)
        with self.assertRaises(installer.InstallError):
            self.apply(['brandkit'])
        self.assertFalse(self.profile.exists())

    def test_source_links_are_rejected(self):
        source = Path(self.temp.name)/'source'; source.mkdir()
        (source/'link').symlink_to(ROOT/'README.md')
        with self.assertRaises(installer.InstallError):
            installer.inventory(source)

    def test_executable_modes_are_preserved(self):
        self.apply(['openai-docs'])
        self.assertEqual(installer.inventory(self.profile/'skills/openai-docs'),
                         installer.inventory(ROOT/self.entries['openai-docs']['path']))

    def test_interactive_selection_and_cancellation(self):
        with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value='brandkit, 1'), patch('builtins.print'):
            self.assertEqual(installer.choose(self.entries), ['brandkit', sorted(self.entries)[0]])
        with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value=''), patch('builtins.print'):
            self.assertEqual(installer.choose(self.entries), [])
        with patch('sys.stdin.isatty', return_value=False):
            with self.assertRaises(installer.InstallError):
                installer.choose(self.entries)

    def test_cli_all_and_codex_home_environment(self):
        env = dict(os.environ, CODEX_HOME=str(self.profile), PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/install_skills.py'),
                                 'install', '--all'], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((self.profile/'skills').glob('*/SKILL.md'))), 36)
        result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/install_skills.py'),
                                 'install'], env=env, input='', capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('--skills', result.stderr)

    def test_extra_user_file_and_empty_directory_are_preserved_as_conflicts(self):
        self.apply(['brandkit'])
        target = self.profile/'skills/brandkit'
        (target/'user-notes.txt').write_text('keep')
        (target/'user-empty').mkdir()
        with self.assertRaises(installer.InstallError):
            self.apply(['brandkit'])
        self.assertEqual((target/'user-notes.txt').read_text(), 'keep')
        self.assertTrue((target/'user-empty').is_dir())

    def test_destination_created_between_preflight_and_copy_is_not_overwritten(self):
        original_copytree = installer.shutil.copytree
        def concurrent_copy(source, destination, **kwargs):
            destination.mkdir(parents=True)
            (destination/'concurrent.txt').write_text('keep concurrent data')
            return original_copytree(source, destination, **kwargs)
        with patch.object(installer.shutil, 'copytree', side_effect=concurrent_copy):
            with self.assertRaises(FileExistsError):
                self.apply(['brandkit'])
        self.assertEqual((self.profile/'skills/brandkit/concurrent.txt').read_text(), 'keep concurrent data')

    def test_explicit_profile_overrides_environment(self):
        other = Path(self.temp.name)/'other'
        env = dict(os.environ, CODEX_HOME=str(other), PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/install_skills.py'),
                                 'install', '--skills', 'brandkit', '--codex-home', str(self.profile)],
                                env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.profile/'skills/brandkit/SKILL.md').is_file())
        self.assertFalse(other.exists())

    def test_file_destination_is_preserved(self):
        target = self.profile/'skills'; target.parent.mkdir(); target.write_text('keep file')
        with self.assertRaises(installer.InstallError):
            self.apply(['brandkit'])
        self.assertEqual(target.read_text(), 'keep file')

    def test_duplicate_selection_installs_once(self):
        self.assertEqual(self.apply(['brandkit', 'brandkit']), [('brandkit', 'instalar')])
        self.assertTrue((self.profile/'skills/brandkit/LICENSE').is_file())

    def test_manifest_traversal_is_rejected(self):
        fake = Path(self.temp.name)/'fake'; fake.mkdir()
        entry = dict(self.entries['brandkit'], path='skills/../../outside')
        (fake/'manifest.json').write_text(json.dumps({'skills':[entry]}))
        with self.assertRaises(installer.InstallError):
            installer.catalog(fake)


if __name__ == '__main__':
    unittest.main()
