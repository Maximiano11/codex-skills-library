from pathlib import Path
import copy
import json
import os
import tempfile
import shutil
import unittest
from unittest.mock import patch

from engineering_os.orchestrator import plan
from engineering_os.util import ContractError, fingerprint, relative_file
from adapters.codex import install

PACKAGE = Path(__file__).resolve().parents[1]


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class PlanningTests(unittest.TestCase):
    def test_small_ui_is_low_and_selective(self):
        p = plan({"request": "Corrija CSS do botão", "scope": "local", "reversible": True, "acceptance": ["Alinhamento verificado no navegador"]}, PACKAGE)
        self.assertEqual(p["risk"], "low")
        self.assertIn("product-ux", p["skills"])
        self.assertNotIn("database-engineer", p["skills"])
        self.assertTrue(p["implementation_ready"])

    def test_unknown_is_not_low_or_implementation(self):
        p = plan({"request": "Melhor desempenho, talvez"}, PACKAGE)
        self.assertEqual(p["risk"], "medium")
        self.assertFalse(p["code_changes_authorized_by_mode"])
        self.assertFalse(p["implementation_ready"])

    def test_sensitive_small_diff_is_high(self):
        p = plan({"request": "Corrija autorizacao", "scope": "local", "reversible": True}, PACKAGE)
        self.assertEqual(p["risk"], "high")
        self.assertIn("security-auditor", p["skills"])

    def test_analysis_does_not_authorize_modification(self):
        p = plan({"request": "Analise o endpoint sem implementar", "acceptance": ["Explicar causa"]}, PACKAGE)
        self.assertFalse(p["code_changes_authorized_by_mode"])
        self.assertNotIn("implementation-standards", p["skills"])
        self.assertNotIn("implement", [s["id"] for s in p["steps"]])

    def test_explanation_only_uses_prompt_engineer(self):
        p = plan({"request": "Apenas explique a arquitetura"}, PACKAGE)
        self.assertEqual(p["skills"], ["prompt-engineer"])

    def test_contradictory_mode_is_rejected(self):
        with self.assertRaises(ContractError):
            plan({"request": "Apenas explique", "mode": "implement"}, PACKAGE)

    def test_ambiguity_stops_dependent_implementation(self):
        p = plan({"request": "Mude o desconto", "acceptance": ["Novo desconto"], "ambiguities": ["Qual percentual?"]}, PACKAGE)
        self.assertEqual(p["risk"], "high")
        self.assertFalse(p["implementation_ready"])
        self.assertEqual(p["original_request"], "Mude o desconto")

    def test_bad_schema_is_rejected(self):
        for change in ({"request": "x", "traits": ["invented"]}, {"request": "x", "approved": True}, {"request": "x", "reversible": "yes"}):
            with self.assertRaises(ContractError):
                plan(change, PACKAGE)

    def test_http_route_is_identified_without_api_keyword(self):
        p = plan({"request": "Crie GET /items retornando JSON"}, PACKAGE)
        self.assertIn("api", p["traits"])
        self.assertIn("software-architect", p["skills"])

    def test_auth_bug_keeps_correction_workflow_and_security_review(self):
        p = plan({"request": "Corrija o bug de autorizacao"}, PACKAGE)
        self.assertEqual(p["workflow"], "bug-investigation")
        self.assertIn("implementation-standards", p["skills"])
        self.assertIn("security-auditor", p["skills"])


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.home = self.base/"user home"
        self.home.mkdir()
        self.target = install.Target(home=self.home)

    def deploy(self, **kwargs):
        changes, state = install.plan_install(PACKAGE, self.target, **kwargs)
        return install.apply(self.target, changes), state

    def test_dry_run_creates_nothing(self):
        before = snapshot(self.home)
        changes, _ = install.plan_install(PACKAGE, self.target)
        install.apply(self.target, changes, dry_run=True)
        self.assertEqual(snapshot(self.home), before)
        self.assertFalse((self.home/"engineering-os").exists())

    def test_install_is_idempotent_and_uninstall_preserves_user_data(self):
        original = b"Existing rules\r\nwith custom bytes\xc3\xa1\n"
        (self.home/"AGENTS.md").write_bytes(original)
        self.deploy()
        self.assertTrue((self.home/"AGENTS.md").read_bytes().startswith(original))
        changes, _ = install.plan_install(PACKAGE, self.target)
        self.assertEqual(changes, {})
        with (self.home/"AGENTS.md").open("ab") as f:
            f.write(b"\nnew user instruction\n")
        changes, _ = install.plan_install(PACKAGE, self.target)
        self.assertEqual(changes, {})
        install.apply(self.target, install.plan_uninstall(self.target))
        self.assertEqual((self.home/"AGENTS.md").read_bytes(), original+b"\nnew user instruction\n")
        self.assertFalse(self.target.state_path.exists())

    def test_borrows_existing_prompt_and_preserves_it(self):
        prompt = self.home/"skills/prompt-engineer"
        prompt.mkdir(parents=True)
        (prompt/"SKILL.md").write_text('---\nname: prompt-engineer\ndescription: Custom existing skill\n---\nUser content\n')
        (prompt/"custom.txt").write_text("keep")
        before = snapshot(prompt)
        _, state = self.deploy()
        self.assertEqual(state["borrowed_skills"], ["prompt-engineer"])
        self.assertEqual(snapshot(prompt), before)
        install.apply(self.target, install.plan_uninstall(self.target))
        self.assertEqual(snapshot(prompt), before)

    def test_collision_is_not_overwritten(self):
        path = self.home/"skills/prompt-engineer/SKILL.md"
        path.parent.mkdir(parents=True); path.write_text("unrecognized user file")
        before = snapshot(self.home)
        with self.assertRaises(ContractError):
            self.deploy()
        self.assertEqual(snapshot(self.home), before)

    def test_unmanaged_runtime_collision_is_not_overwritten(self):
        path = self.home/"engineering-os/runtime/VERSION"
        path.parent.mkdir(parents=True); path.write_text("custom")
        before = snapshot(self.home)
        with self.assertRaises(ContractError):
            self.deploy()
        self.assertEqual(snapshot(self.home), before)

    def test_modified_owned_file_blocks_update_and_uninstall(self):
        self.deploy()
        path = self.home/"engineering-os/runtime/VERSION"
        path.write_text("user modification")
        before = snapshot(self.home)
        self.assertEqual(install.diagnose(self.target)["integrity"], "drift")
        for action in (lambda: install.plan_install(PACKAGE, self.target, update=True), lambda: install.plan_uninstall(self.target)):
            with self.assertRaises(ContractError): action()
        self.assertEqual(snapshot(self.home), before)

    def test_symlink_escape_is_rejected(self):
        outside = self.base/"outside"; outside.mkdir()
        (self.home/"skills").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ContractError): self.deploy()
        self.assertEqual(snapshot(outside), {})

    def test_active_override_receives_guidance(self):
        (self.home/"AGENTS.md").write_text("base")
        (self.home/"AGENTS.override.md").write_text("override")
        self.deploy()
        self.assertEqual((self.home/"AGENTS.md").read_text(), "base")
        self.assertIn(install.START, (self.home/"AGENTS.override.md").read_bytes())

    def test_new_override_is_diagnosed(self):
        self.deploy()
        (self.home/"AGENTS.override.md").write_text("shadow")
        self.assertEqual(install.diagnose(self.target)["integrity"], "drift")

    def test_tampered_instruction_block_blocks_uninstall(self):
        self.deploy()
        p = self.home/"AGENTS.md"
        p.write_bytes(p.read_bytes().replace(b"Engineering OS", b"Modified OS"))
        with self.assertRaises(ContractError): install.plan_uninstall(self.target)

    def test_precondition_race_is_rejected_before_writes(self):
        changes, _ = install.plan_install(PACKAGE, self.target)
        (self.home/"AGENTS.md").write_text("concurrent edit")
        with self.assertRaises(ContractError): install.apply(self.target, changes)
        self.assertEqual((self.home/"AGENTS.md").read_text(), "concurrent edit")
        self.assertFalse(self.target.state_path.exists())

    def test_in_process_failure_rolls_back_applied_files(self):
        before = snapshot(self.home)
        changes, _ = install.plan_install(PACKAGE, self.target)
        real = install.atomic_write
        triggered = []
        def fail(path, content):
            if str(path).endswith("runtime/VERSION") and not triggered:
                triggered.append(True)
                raise OSError("simulated write failure")
            return real(path, content)
        with patch.object(install, "atomic_write", side_effect=fail):
            with self.assertRaises(OSError): install.apply(self.target, changes)
        after = {k:v for k,v in snapshot(self.home).items() if "/backups/" not in k}
        self.assertEqual(after, before)
        self.assertFalse((self.home/"engineering-os/install.lock").exists())

    def test_code_home_environment_is_respected(self):
        with patch.dict(os.environ, {"CODEX_HOME": str(self.home)}):
            self.assertEqual(install.Target().root, self.home.resolve())

    def test_project_install_does_not_touch_global_home(self):
        project = self.base/"project"; project.mkdir()
        target = install.Target(project=project)
        changes, _ = install.plan_install(PACKAGE, target)
        install.apply(target, changes)
        self.assertTrue((project/".agents/skills/prompt-engineer/SKILL.md").is_file())
        self.assertEqual(snapshot(self.home), {})
        install.apply(target, install.plan_uninstall(target))
        self.assertFalse((project/"AGENTS.md").exists())

    def candidate(self, version):
        folder = self.base/("candidate-"+version)
        folder.mkdir()
        for rel, data in install.package_files(PACKAGE).items():
            p=folder/rel;p.parent.mkdir(parents=True, exist_ok=True);p.write_bytes(data)
        (folder/"VERSION").write_text(version+"\n")
        return folder

    def test_update_is_controlled_and_changes_version(self):
        self.deploy()
        candidate=self.candidate("1.0.1")
        with self.assertRaises(ContractError): install.plan_install(candidate,self.target)
        changes,state=install.plan_install(candidate,self.target,update=True)
        before=snapshot(self.home)
        install.apply(self.target,changes,dry_run=True)
        self.assertEqual(snapshot(self.home),before)
        install.apply(self.target,changes)
        self.assertEqual(install.diagnose(self.target)["version"],"1.0.1")
        self.assertEqual(install.diagnose(self.target)["integrity"],"ok")

    def test_major_migration_and_downgrade_are_rejected(self):
        self.deploy()
        major=self.candidate("2.0.0")
        with self.assertRaises(ContractError): install.plan_install(major,self.target,update=True)
        lower=self.candidate("0.9.0")
        with self.assertRaises(ContractError): install.plan_install(lower,self.target,update=True,allow_major=True)

    def test_incomplete_package_cannot_remove_operational_installation(self):
        self.deploy()
        before=snapshot(self.home)
        incomplete=self.base/"incomplete";incomplete.mkdir()
        for name in ("VERSION","LICENSE","README.md"):
            (incomplete/name).write_text("1.0.1\n" if name=="VERSION" else "incomplete")
        with self.assertRaises(ContractError): install.plan_install(incomplete,self.target,update=True)
        self.assertEqual(snapshot(self.home),before)
        self.assertEqual(install.diagnose(self.target)["integrity"],"ok")

    def test_uninstall_dry_run_preserves_every_file(self):
        self.deploy();before=snapshot(self.home)
        install.apply(self.target,install.plan_uninstall(self.target),dry_run=True)
        self.assertEqual(snapshot(self.home),before)

    def test_untracked_files_survive_uninstall(self):
        self.deploy()
        custom=self.home/"skills/code-reviewer/notes.txt";custom.write_text("user notes")
        install.apply(self.target,install.plan_uninstall(self.target))
        self.assertEqual(custom.read_text(),"user notes")


class UtilityTests(unittest.TestCase):
    def test_traversal_is_rejected(self):
        with self.assertRaises(ContractError): relative_file(Path.cwd(), "../outside")

    def test_fingerprint_detects_dirty_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/"code.py").write_text("one")
            before=fingerprint(p)
            (p/"code.py").write_text("two")
            self.assertNotEqual(before["sha256"], fingerprint(p)["sha256"])


if __name__ == "__main__":
    unittest.main()
