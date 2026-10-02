"""Tests for the Codex single-pass dispatcher and checkpoint writer."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "codex_orchestrate", ROOT / "tools/codex-studio/orchestrate.py"
)
assert SPEC and SPEC.loader
orchestrate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = orchestrate
SPEC.loader.exec_module(orchestrate)


class OrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="codex orchestrator ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "docs/codex-studio/templates").mkdir(parents=True)
        (self.root / "production/session-state").mkdir(parents=True)
        (self.root / "production/epics/core").mkdir(parents=True)
        (self.root / "docs/codex-studio/templates/session-state.md").write_text(
            "# State\n\n<!-- CHECKPOINT -->\n**Next step:** old\n<!-- /CHECKPOINT -->\n",
            encoding="utf-8",
        )
        (self.root / "project.yaml").write_text(
            "schema_version: 1\nengine:\n  name: Godot\n", encoding="utf-8"
        )
        (self.root / "design").mkdir()
        (self.root / "design/game-brief.md").write_text("# Brief\n", encoding="utf-8")

    def story(self, name: str, status: str) -> Path:
        path = self.root / "production/epics/core" / name
        path.write_text(f"# Story {name}\n\n> **Status**: {status}\n", encoding="utf-8")
        return path

    def test_missing_engine_is_first_gate(self) -> None:
        (self.root / "project.yaml").write_text("schema_version: 1\n", encoding="utf-8")
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "needs_engine")
        self.assertEqual(plan.skill, "$codex-setup-engine")

    def test_top_level_name_is_not_treated_as_engine_name(self) -> None:
        (self.root / "project.yaml").write_text(
            "schema_version: 1\nname: Example Game\n", encoding="utf-8"
        )
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "needs_engine")

    def test_engine_name_must_come_from_engine_mapping(self) -> None:
        (self.root / "project.yaml").write_text(
            "schema_version: 1\nmetadata:\n  name: Example Game\nengine:\n  name: Godot # pinned\n",
            encoding="utf-8",
        )
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "needs_stories")

    def test_nested_engine_name_is_not_engine_name(self) -> None:
        (self.root / "project.yaml").write_text(
            "schema_version: 1\nengine:\n  config:\n    name: Example Game\n",
            encoding="utf-8",
        )
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "needs_engine")

    def test_missing_brief_is_second_gate(self) -> None:
        (self.root / "design/game-brief.md").unlink()
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "needs_brief")
        self.assertEqual(plan.skill, "$codex-brainstorm")

    def test_missing_stories_is_third_gate(self) -> None:
        (self.root / "design/game-brief.md").write_text("# Brief\n", encoding="utf-8")
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "needs_stories")
        self.assertEqual(plan.skill, "$codex-create-stories")

    def test_review_precedes_in_progress_and_ready(self) -> None:
        self.story("story-001.md", "Ready")
        self.story("story-002.md", "In Progress")
        self.story("story-003.md", "In Review")
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "story_review")
        self.assertEqual(plan.story, "production/epics/core/story-003.md")
        self.assertEqual(plan.skill, "$codex-story-done production/epics/core/story-003.md")

    def test_ready_is_selected_in_build_order(self) -> None:
        self.story("story-001.md", "Complete")
        self.story("story-002.md", "Ready")
        self.story("story-003.md", "Ready")
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "story_ready")
        self.assertEqual(plan.story, "production/epics/core/story-002.md")

    def test_blocked_story_stops_without_selecting_a_skill(self) -> None:
        self.story("story-001.md", "Blocked — waiting for an ADR")
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "blocked")
        self.assertIsNone(plan.skill)
        self.assertEqual(plan.action, "pause")

    def test_all_complete_routes_to_smoke_gate(self) -> None:
        self.story("story-001.md", "Complete")
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "all_stories_complete")
        self.assertEqual(plan.skill, "$codex-smoke-check")
        self.assertTrue(plan.warnings)

    def test_status_sources_must_agree(self) -> None:
        story = self.story("story-001.md", "Complete")
        (self.root / "production/sprint-status.yaml").write_text(
            "stories:\n  - path: production/epics/core/story-001.md\n    status: in-progress\n",
            encoding="utf-8",
        )
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "inconsistent")
        self.assertIn(str(story.relative_to(self.root)).replace("\\", "/"), plan.consistency_errors[0])
        self.assertEqual(plan.skill, None)

    def test_status_aliases_match_the_same_semantic_state(self) -> None:
        story = self.story("story-001.md", "In Progress")
        (self.root / "production/sprint-status.yaml").write_text(
            "stories:\n  - file: ./production\\epics\\core\\story-001.md # path alias\n    status: in-progress\n",
            encoding="utf-8",
        )
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "story_in_progress")
        self.assertEqual(plan.consistency_errors, [])

    def test_backlog_does_not_match_ready(self) -> None:
        story = self.story("story-001.md", "Ready")
        (self.root / "production/sprint-status.yaml").write_text(
            "stories:\n  - path: production/epics/core/story-001.md\n    status: backlog\n",
            encoding="utf-8",
        )
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "inconsistent")
        self.assertIn("story is Ready but sprint status is backlog", plan.consistency_errors[0])

    def test_not_started_matches_backlog_without_routing_to_implementation(self) -> None:
        self.story("story-001.md", "Not Started")
        (self.root / "production/sprint-status.yaml").write_text(
            "stories:\n  - path: production/epics/core/story-001.md\n    status: backlog\n",
            encoding="utf-8",
        )
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "needs_status")
        self.assertEqual(plan.skill, "$codex-story-readiness")
        self.assertEqual(plan.consistency_errors, [])

    def test_ready_and_done_are_a_symmetric_conflict(self) -> None:
        self.story("story-001.md", "Ready")
        (self.root / "production/sprint-status.yaml").write_text(
            "stories:\n  - path: production/epics/core/story-001.md\n    status: done\n",
            encoding="utf-8",
        )
        plan = orchestrate.build_plan(self.root)
        self.assertEqual(plan.state, "inconsistent")
        self.assertIn("sprint status is done", plan.consistency_errors[0])

    def test_checkpoint_is_atomic_and_bounded(self) -> None:
        self.story("story-001.md", "Ready")
        plan = orchestrate.build_plan(self.root)
        path = orchestrate.write_checkpoint(self.root, plan, files="src/player.gd")
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text.count("<!-- CHECKPOINT -->"), 1)
        self.assertIn("**Next step:** $codex-dev-story production/epics/core/story-001.md", text)
        self.assertIn("**Files in progress:** src/player.gd", text)
        self.assertFalse((path.parent / "active.md.lock").exists())

    def test_checkpoint_preserves_backslashes_in_file_list(self) -> None:
        self.story("story-001.md", "Ready")
        plan = orchestrate.build_plan(self.root)
        path = orchestrate.write_checkpoint(self.root, plan, files=r"C:\src\player.gd\1")
        self.assertIn(r"**Files in progress:** C:\src\player.gd\1", path.read_text(encoding="utf-8"))

    def test_checkpoint_creates_missing_state_directory(self) -> None:
        self.story("story-001.md", "Ready")
        shutil.rmtree(self.root / "production/session-state")
        plan = orchestrate.build_plan(self.root)
        path = orchestrate.write_checkpoint(self.root, plan)
        self.assertTrue(path.is_file())

    def test_checkpoint_reads_only_after_lock_is_acquired(self) -> None:
        self.story("story-001.md", "Ready")
        plan = orchestrate.build_plan(self.root)
        active = self.root / "production/session-state/active.md"
        lock = active.with_name("active.md.lock")
        original_read = orchestrate._read
        observed: list[bool] = []

        def read_after_lock(path: Path) -> str:
            if path == active:
                observed.append(lock.exists())
            return original_read(path)

        with mock.patch.object(orchestrate, "_read", side_effect=read_after_lock):
            orchestrate.write_checkpoint(self.root, plan)
        self.assertEqual(observed, [True])

    def test_existing_lock_fails_without_overwriting(self) -> None:
        self.story("story-001.md", "Ready")
        plan = orchestrate.build_plan(self.root)
        lock = self.root / "production/session-state/active.md.lock"
        lock.write_text("pid=other\n", encoding="ascii")
        self.addCleanup(lambda: lock.unlink(missing_ok=True))
        with self.assertRaisesRegex(RuntimeError, "checkpoint is locked"):
            orchestrate.write_checkpoint(self.root, plan)


if __name__ == "__main__":
    unittest.main()
