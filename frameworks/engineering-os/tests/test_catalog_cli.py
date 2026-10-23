from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
import importlib.util
import zipfile
from unittest.mock import patch

from engineering_os.validation import evaluate, validate_package
from engineering_os.util import ContractError, read_json

ROOT=Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def test_all_workflows_and_skill_references_are_valid(self):
        result=validate_package(ROOT)
        self.assertTrue(result["passed"])
        self.assertGreaterEqual(len(result["skills"]),13)
        self.assertEqual(result["workflow_count"],9)

    def test_ten_deterministic_routing_scenarios(self):
        result=evaluate(ROOT)
        self.assertTrue(result["passed"],result)
        self.assertGreaterEqual(len(result["cases"]),10)
        self.assertEqual(result["model_runs_executed"],0)

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.json";path.write_text('{"mode":"analyze","mode":"implement"}')
            with self.assertRaises(ContractError): read_json(path)

    def test_cli_prepares_plan_without_modifying_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/"project";project.mkdir()
            (project/"module.py").write_text("pass\n")
            change=Path(tmp)/"change.json";change.write_text(json.dumps({"request":"Analise o módulo sem implementar"}))
            r=subprocess.run([sys.executable,"-B",str(ROOT/"scripts/eos.py"),"plan","--project",str(project),"--change",str(change)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertFalse(json.loads(r.stdout)["code_changes_authorized_by_mode"])
            self.assertEqual([p.name for p in project.iterdir()],["module.py"])

    def test_cli_errors_are_nonzero_and_structured(self):
        r=subprocess.run([sys.executable,"-B",str(ROOT/"scripts/eos.py"),"plan","--change",str(ROOT/"absent.json")],capture_output=True,text=True)
        self.assertEqual(r.returncode,3)
        self.assertIn("error",json.loads(r.stderr))

    def test_custom_workflow_routes_to_new_specialty_without_core_changes(self):
        from adapters.codex.install import package_files
        from engineering_os.orchestrator import plan
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for rel,data in package_files(ROOT).items():
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            skill=root/"skills/protocol-auditor";skill.mkdir();(skill/"agents").mkdir()
            (skill/"SKILL.md").write_text('---\nname: protocol-auditor\ndescription: "Audit the fixture protocol"\n---\nInspect the documented protocol without modifications.\n')
            (skill/"agents/openai.yaml").write_text('interface:\n  display_name: "Protocol Auditor"\n')
            workflow=read_json(root/"workflows/security-review.json")
            workflow["id"]="protocol-review";workflow["skills"]=["prompt-engineer","protocol-auditor"]
            (root/"workflows/protocol-review.json").write_text(json.dumps(workflow))
            self.assertTrue(validate_package(root)["passed"])
            result=plan({"request":"Audite o protocolo","workflow":"protocol-review"},root)
            self.assertIn("protocol-auditor",result["skills"])
            self.assertFalse(result["code_changes_authorized_by_mode"])


class BuildTests(unittest.TestCase):
    def module(self):
        spec=importlib.util.spec_from_file_location("eos_build",ROOT/"scripts/build.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module

    def test_archive_is_local_verified_and_rebuildable(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);source=tmp/"source";source.mkdir()
            (source/"VERSION").write_text("1.0.0\n")
            (source/"module.py").write_text("value=1\n")
            (source/"SOURCE-MANIFEST.json").write_text("previous manifest")
            module=self.module()
            with patch.object(module,"ROOT",source):
                result=module.build(tmp/"archive.zip")
                with zipfile.ZipFile(result["output"]) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertIn("engineering-os/module.py",archive.namelist())
                with self.assertRaises(ValueError):module.build(tmp/"archive.zip")

    def test_archive_rejects_symlink_and_output_in_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);source=tmp/"source";source.mkdir();(source/"VERSION").write_text("1.0.0\n")
            module=self.module()
            with patch.object(module,"ROOT",source):
                with self.assertRaises(ValueError):module.build(source/"output.zip")
                (source/"external").symlink_to(tmp/"outside")
                with self.assertRaises(ValueError):module.build(tmp/"output.zip")
