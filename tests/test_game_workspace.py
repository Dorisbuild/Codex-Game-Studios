"""Regression tests for the clean Codex game-workspace creator."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import os
import tempfile
import unittest

from tools.create_game_workspace import (
    MANIFEST_NAME,
    WorkspaceError,
    _source_git,
    build_plan,
    create_workspace,
    main,
    verify_workspace,
)


ROOT = Path(__file__).resolve().parents[1]


class GameWorkspaceCreatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="codex-game-workspace-test-")
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)

    def make_target(self, name: str = "new-game") -> Path:
        return self.parent / name

    def create(self, name: str = "new-game") -> Path:
        target = self.make_target(name)
        manifest_path, _ = create_workspace(ROOT, target)
        self.assertEqual(manifest_path, target / MANIFEST_NAME)
        return target

    def test_default_mode_is_read_only_plan(self) -> None:
        target = self.make_target()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main([str(target)]), 0)
        self.assertFalse(target.exists())
        self.assertIn("PLAN: clean Codex game workspace", output.getvalue())
        self.assertIn("--create", output.getvalue())

    def test_named_output_alias_creates_same_clean_workspace(self) -> None:
        target = self.make_target("named-output")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--output", str(target), "--create"]), 0)
        self.assertTrue((target / MANIFEST_NAME).is_file())
        self.assertIn("No Git repository", output.getvalue())

    def test_verify_accepts_named_output_alias(self) -> None:
        target = self.create("named-verify")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--output", str(target), "--verify"]), 0)
        self.assertIn(str(target.resolve()), output.getvalue())

    def test_create_copies_framework_and_generates_clean_template(self) -> None:
        target = self.create()

        self.assertTrue((target / ".agents/skills/codex-start/SKILL.md").is_file())
        self.assertTrue((target / ".codex/agents/gameplay-programmer.toml").is_file())
        self.assertTrue((target / "docs/codex-studio/runtime.md").is_file())
        self.assertTrue((target / "tests/test_codex_studio.py").is_file())
        self.assertTrue((target / "Codex Skill Testing Framework/catalog.yaml").is_file())
        self.assertTrue((target / "LICENSE").is_file())
        self.assertTrue((target / "NOTICE.md").is_file())
        for directory in ("src", "design", "production"):
            self.assertTrue((target / directory).is_dir())
            self.assertEqual(list((target / directory).iterdir()), [target / directory / ".gitkeep"])

        self.assertFalse((target / "demo").exists())
        self.assertFalse((target / ".git").exists())
        self.assertFalse((target / "VERIFICATION.txt").exists())
        self.assertFalse((target / "production/session-state").exists())
        self.assertFalse((target / "production/qa/evidence").exists())
        self.assertFalse((target / "design/game-brief.md").exists())

        project = (target / "project.yaml").read_text(encoding="utf-8")
        self.assertIn("schema_version: 1", project)
        self.assertNotRegex(project, r"^engine:", msg=project)
        self.assertIn("entire workspace root", (target / "START_HERE.md").read_text(encoding="utf-8"))
        self.assertIn("$codex-start", (target / "START_HERE.md").read_text(encoding="utf-8"))
        self.assertIn("provenance: required", (target / "START_HERE.md").read_text(encoding="utf-8"))

        manifest = json.loads((target / MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertTrue(manifest["copied_files"])
        self.assertIn(".agents/skills/codex-start/SKILL.md", manifest["copied_files"])
        self.assertNotIn(MANIFEST_NAME, manifest["copied_files"])
        self.assertNotIn(MANIFEST_NAME, manifest["generated_files"])
        self.assertIn("commit", manifest["source_git"])
        self.assertIn("dirty", manifest["source_git"])
        self.assertIn("descriptive", manifest["source_git_note"])

    def test_manifest_verifies_and_detects_tampering_without_deleting(self) -> None:
        target = self.create()
        ok, errors = verify_workspace(target)
        self.assertTrue(ok, errors)

        file_path = target / "docs/codex-studio/runtime.md"
        original = file_path.read_text(encoding="utf-8")
        file_path.write_text(original + "\nchanged after creation\n", encoding="utf-8")
        ok, errors = verify_workspace(target)
        self.assertFalse(ok)
        self.assertTrue(any("hash mismatch" in error for error in errors), errors)
        self.assertTrue(file_path.exists())

    def test_existing_target_is_rejected_and_untouched(self) -> None:
        target = self.make_target()
        target.mkdir()
        marker = target / "future-work.txt"
        marker.write_text("keep this", encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            self.assertEqual(main([str(target), "--create"]), 2)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep this")
        self.assertIn("already exists", output.getvalue())

    def test_target_inside_or_above_source_is_rejected(self) -> None:
        with self.assertRaises(WorkspaceError):
            build_plan(ROOT, ROOT / "new-game-inside-source")
        with self.assertRaises(WorkspaceError):
            build_plan(ROOT, ROOT.parent)

    def test_source_links_are_rejected_before_copy(self) -> None:
        source = self.parent / "source-with-link"
        source.mkdir()
        outside = self.parent / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        link = source / "escape.txt"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable on this host")
        with self.assertRaises(WorkspaceError):
            build_plan(source, self.make_target())

    def test_no_git_environment_is_descriptive_not_blocking(self) -> None:
        source = self.parent / "not-a-git-repository"
        source.mkdir()
        metadata = _source_git(source)
        self.assertFalse(metadata["available"])
        self.assertIsNone(metadata["commit"])
        self.assertIsNone(metadata["dirty"])
        self.assertIn("not proof", metadata["note"])

    def test_verify_keeps_future_user_files(self) -> None:
        target = self.create()
        future_file = target / "future-work.txt"
        future_file.write_text("user-owned", encoding="utf-8")
        ok, errors = verify_workspace(target)
        self.assertTrue(ok, errors)
        self.assertEqual(future_file.read_text(encoding="utf-8"), "user-owned")

    def test_verify_rejects_a_symlink_replacing_a_manifest_file(self) -> None:
        target = self.create()
        original = target / "docs/codex-studio/runtime.md"
        outside = self.parent / "outside.md"
        outside.write_bytes(original.read_bytes())
        try:
            original.unlink()
            original.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable on this host")
        ok, errors = verify_workspace(target)
        self.assertFalse(ok)
        self.assertTrue(any("symlink/junction" in error for error in errors), errors)

    def test_verify_rejects_a_symlink_target(self) -> None:
        target = self.create("real-target")
        alias = self.make_target("alias-target")
        try:
            alias.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable on this host")
        ok, errors = verify_workspace(alias)
        self.assertFalse(ok)
        self.assertTrue(any("symlink/junction" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
