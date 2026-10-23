"""Executable selection with real temporary files; no model calls or global edits."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('codex_runtime',
    Path(__file__).resolve().parents[1] / 'scripts/codex_runtime.py')
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.desktop = self.executable('desktop')
        self.path_cli = self.executable('path-cli')

    def executable(self, name):
        p = self.base / name
        p.write_text('#!/bin/sh\nexit 0\n')
        p.chmod(0o700)
        return p

    def test_explicit_selection_precedes_desktop_environment(self):
        self.assertEqual(runtime.resolve_runtime(self.path_cli,
            {'CODEX_CLI_PATH': str(self.desktop)}), (self.path_cli, 'explicit'))

    def test_desktop_environment_precedes_older_path(self):
        with patch.object(runtime.shutil, 'which', return_value=str(self.path_cli)):
            self.assertEqual(runtime.resolve_runtime(environ={'CODEX_CLI_PATH':str(self.desktop)}),
                             (self.desktop, 'desktop_environment'))

    def test_invalid_explicit_environment_does_not_silently_fall_back(self):
        with patch.object(runtime.shutil, 'which', return_value=str(self.path_cli)):
            with self.assertRaises(FileNotFoundError):
                runtime.resolve_runtime(environ={'CODEX_CLI_PATH':str(self.base/'missing')})

    def test_invalid_explicit_argument_does_not_fall_back_to_desktop(self):
        with self.assertRaises(FileNotFoundError):
            runtime.resolve_runtime(self.base/'missing', {'CODEX_CLI_PATH':str(self.desktop)})

    def test_candidate_without_execution_permission_is_rejected(self):
        self.desktop.chmod(0o600)
        with self.assertRaises(FileNotFoundError):
            runtime.resolve_runtime(environ={'CODEX_CLI_PATH':str(self.desktop)})

    def test_desktop_installation_is_available_outside_app_environment(self):
        with patch.object(runtime.sys, 'platform', 'darwin'), patch.object(runtime, 'DESKTOP_CLI', self.desktop):
            self.assertEqual(runtime.resolve_runtime(environ={}), (self.desktop, 'desktop_installation'))

    def test_non_desktop_system_uses_path_and_rejects_missing_executable(self):
        with patch.object(runtime.sys, 'platform', 'linux'):
            with patch.object(runtime.shutil, 'which', return_value=str(self.path_cli)):
                self.assertEqual(runtime.resolve_runtime(environ={}), (self.path_cli, 'PATH'))
            with patch.object(runtime.shutil, 'which', return_value=None):
                with self.assertRaises(FileNotFoundError):runtime.resolve_runtime(environ={})


if __name__ == '__main__':
    unittest.main(verbosity=2)
