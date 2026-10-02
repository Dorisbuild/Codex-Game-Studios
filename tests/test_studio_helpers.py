"""Integration tests for explicit studio CLIs; no engine or network required.

Run with Python 3.11+: python -m unittest discover -s tests -p 'test_studio_helpers.py' -v
All stateful commands run in disposable fixtures, never the working game tree.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools/codex-studio"


def find_bash() -> str | None:
    """Prefer Git Bash over Windows' WSL launcher; probe candidates, not names."""
    candidates: list[str | None] = []
    if os.name == "nt":
        for key in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
            if os.environ.get(key):
                base = Path(os.environ[key])
                candidates.extend(str(base / suffix) for suffix in
                                  ("Git/bin/bash.exe", "Programs/Git/bin/bash.exe"))
        git = shutil.which("git")
        if git:
            candidates.append(str(Path(git).resolve().parents[1] / "bin/bash.exe"))
    candidates.append(shutil.which("bash"))
    for candidate in dict.fromkeys(candidates):
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            probe = subprocess.run(
                [candidate, "--noprofile", "--norc", "-c", "printf 'studio-bash\\n'; uname -s"],
                capture_output=True, text=True, timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        lines = probe.stdout.splitlines()
        native = os.name != "nt" or (len(lines) > 1 and lines[1].startswith(("MINGW", "MSYS", "CYGWIN")))
        if probe.returncode == 0 and lines and lines[0] == "studio-bash" and native:
            return candidate
    return None


BASH = find_bash()


@unittest.skipUnless(BASH, "Bash unavailable; install Bash or Git for Windows")
class StudioHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="codex studio helpers ")
        self.addCleanup(self.temp.cleanup)
        self.fixture = Path(self.temp.name)
        shutil.copytree(TOOLS, self.fixture / "tools/codex-studio")
        catalog = self.fixture / "docs/codex-studio/workflow-catalog.yaml"
        catalog.parent.mkdir(parents=True)
        shutil.copy2(ROOT / "docs/codex-studio/workflow-catalog.yaml", catalog)
        self.write("project.yaml", 'modes:\n  rigor: minimal\nengine:\n  name: ""\n')
        self.env = os.environ.copy()
        for key in ("CODEX_STUDIO_ROOT", "CODEX_PROJECT_DIR", "CLAUDE_PROJECT_DIR",
                    "CODEX_STUDIO_VERSION"):
            self.env.pop(key, None)
        self.env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + self.env.get("PATH", "")
        self.env["PYTHONIOENCODING"] = "utf-8"

    def write(self, relative: str, text: str) -> Path:
        target = self.fixture / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        return target

    def run_bash(self, *args: str, cwd: Path | None = None,
                 override: Path | None = None) -> subprocess.CompletedProcess[str]:
        env = self.env.copy()
        if override is not None:
            env["CODEX_STUDIO_ROOT"] = override.as_posix()
        return subprocess.run(
            [BASH, "--noprofile", "--norc", *args], cwd=cwd or self.fixture,
            env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )

    def run_tool(self, relative: str, *args: str, **kwargs) -> subprocess.CompletedProcess[str]:
        path = self.fixture / "tools/codex-studio" / relative
        return self.run_bash(path.as_posix(), *args, **kwargs)

    def success(self, result: subprocess.CompletedProcess[str]) -> str:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_every_shell_file_parses(self) -> None:
        files = list((self.fixture / "tools/codex-studio").rglob("*.sh"))
        self.assertEqual(len(files), 10)
        for path in files:
            with self.subTest(script=path.name):
                self.success(self.run_bash("-n", path.as_posix()))

    def test_config_minimal_has_expected_provenance(self) -> None:
        output = self.success(self.run_tool("config/yaml-helper.sh", "resolve_config", "--keys",
                                            "workflow,review_mode,automation"))
        self.assertIn("workflow: minimal (rigor:minimal)", output)
        self.assertIn("review_mode: solo (rigor:minimal)", output)
        self.assertIn("automation: collaborative (default)", output)

    def test_config_source_and_direct_from_subdirectory_match(self) -> None:
        self.write("project.yaml", "modes:\n  rigor: full\n")
        child = self.fixture / "src/deep"
        child.mkdir(parents=True)
        helper = (self.fixture / "tools/codex-studio/config/yaml-helper.sh").as_posix()
        direct = self.success(self.run_tool("config/yaml-helper.sh", "resolve_config",
                                            "--keys", "workflow,review_mode", cwd=child))
        sourced = self.success(self.run_bash(
            "-c", 'set -u; source "$1"; resolve_config --keys workflow,review_mode',
            "test", helper, cwd=child))
        self.assertEqual(sourced, direct)
        self.assertIn("workflow: full (rigor:full)", sourced)

    def test_config_system_overrides_from_subdirectory(self) -> None:
        self.write("project.yaml", "modes:\n  rigor: minimal\nworkflow_overrides:\n"
                   "  system_overrides:\n    combat: full\n")
        child = self.fixture / "src"
        child.mkdir()
        output = self.success(self.run_tool("config/yaml-helper.sh", "resolve_config", "--keys",
                                            "system_overrides", "combat", cwd=child))
        self.assertIn("system_overrides: combat=full", output)
        self.assertIn("workflow[combat]: full (system_overrides)", output)

    def test_source_session_state_and_code_root_use_same_config(self) -> None:
        self.write("project.yaml", "engine:\n  name: Godot\nfeatures:\n  session_state: on\n")
        self.write("project.local.yaml", "engine:\n  name: Unity\nfeatures:\n  session_state: off\n")
        child = self.fixture / "src"
        child.mkdir()
        helper = (self.fixture / "tools/codex-studio/config/yaml-helper.sh").as_posix()
        result = self.run_bash("-c", 'set -u; source "$1"; session_state_enabled', "test", helper, cwd=child)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        output = self.success(self.run_bash("-c", 'set -u; source "$1"; resolve_code_root',
                                            "test", helper, cwd=child))
        self.assertEqual(output, "src\tengine.name")

    def test_config_explicit_root_wins_over_configured_cwd(self) -> None:
        target = self.fixture / "chosen"
        target.mkdir()
        (target / "project.yaml").write_text("modes:\n  rigor: full\n", encoding="utf-8")
        output = self.success(self.run_tool("config/yaml-helper.sh", "resolve_config",
                                            "--keys", "workflow", override=target))
        self.assertIn("workflow: full (rigor:full)", output)

    def test_config_local_override_and_locked_keys(self) -> None:
        self.write("project.yaml", "modes:\n  rigor: full\nengine:\n  name: Godot\n")
        self.write("project.local.yaml", "modes:\n  review_mode: solo\nengine:\n  name: Unity\n")
        output = self.success(self.run_tool("config/yaml-helper.sh", "resolve_config",
                                            "--keys", "workflow,review_mode,engine"))
        self.assertIn("review_mode: solo (project.local.yaml)", output)
        self.assertIn("workflow: full (rigor:full)", output)
        self.assertIn("Godot", output)
        self.assertNotIn("engine: Unity", output)
        self.assertIn("engine.name", output)

    def test_config_invalid_enum_is_reported_from_subdirectory(self) -> None:
        self.write("project.yaml", "modes:\n  automation: nonsense\n")
        child = self.fixture / "src"
        child.mkdir()
        output = self.success(self.run_tool("config/yaml-helper.sh", "resolve_config",
                                            "--keys", "automation", cwd=child))
        self.assertIn("nonsense", output)
        self.assertIn("automation: collaborative", output)

    def test_config_missing_base_guard_is_nounset_safe(self) -> None:
        (self.fixture / "project.yaml").unlink()
        self.write("project.local.yaml", "modes:\n  review_mode: solo\n")
        helper = (self.fixture / "tools/codex-studio/config/yaml-helper.sh").as_posix()
        result = self.run_bash("-c", 'set -u; source "$1"; validate_local_yaml_base', "test", helper)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("$codex-start", result.stderr)
        self.assertNotIn("unbound variable", result.stderr)

    def test_config_missing_and_empty_files_are_not_silent(self) -> None:
        for content in (None, ""):
            with self.subTest(content=content):
                path = self.fixture / "project.yaml"
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_text(content, encoding="utf-8")
                output = self.success(self.run_tool("config/yaml-helper.sh", "resolve_config",
                                                    "--keys", "workflow"))
                self.assertIn("absent" if content is None else "EMPTY", output)

    def test_config_unknown_command_and_bad_arguments_fail(self) -> None:
        for args in (("unknown",), (), ("resolve_config", "--keys"),
                     ("resolve_config", "--keys", ""),
                     ("resolve_config", "--keys", "workflow,typo"),
                     ("resolve_config", "--keys", ",workflow"),
                     ("resolve_config", "--bogus"),
                     ("resolve_config", "combat", "extra")):
            with self.subTest(args=args):
                result = self.run_tool("config/yaml-helper.sh", *args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertTrue(result.stderr)

    def test_invalid_explicit_root_fails(self) -> None:
        missing = self.fixture / "missing"
        for script, args in (("config/yaml-helper.sh", ("resolve_config",)),
                             ("scripts/project-coherence.sh", ()),
                             ("scripts/story-status.sh", ()),
                             ("scripts/artifact-check.sh", ())):
            with self.subTest(script=script):
                self.assertNotEqual(self.run_tool(script, *args, override=missing).returncode, 0)

    def test_yaml_helpers_have_no_event_payload_contract(self) -> None:
        content = (self.fixture / "tools/codex-studio/config/yaml-helper.sh").read_text(encoding="utf-8")
        for marker in ("hook_warn", "hookSpecificOutput", "CODEX_SKILL_DIR", "CODEX_PROJECT_DIR"):
            self.assertFalse(marker in content, f"obsolete runtime marker: {marker}")

    def test_empty_template_readonly_scripts_from_subdirectory(self) -> None:
        child = self.fixture / "src"
        child.mkdir()
        expectations = {
            "story-status.sh": "STORIES      none",
            "project-coherence.sh": "$codex-setup-engine",
            "adr-dep-graph.sh": "ADRS: 0",
            "gdd-structure-check.sh": "No system GDDs",
            "review-scope.sh": "PRIOR_REVIEW: NONE",
        }
        for script, expected in expectations.items():
            with self.subTest(script=script):
                self.assertIn(expected, self.success(self.run_tool("scripts/" + script, cwd=child)))

    def test_coherence_no_project_displays_literal_start_skill(self) -> None:
        (self.fixture / "project.yaml").unlink()
        output = self.success(self.run_tool("scripts/project-coherence.sh"))
        self.assertIn("$codex-start", output)
        self.assertIn("not checked", output)

    def test_coherence_missing_engine_artifacts_displays_literal_skills(self) -> None:
        self.write("project.yaml", "engine:\n  name: Godot\n  version: 4.0\ncommands:\n"
                   "  build: godot --export-release Desktop\n  test: godot -s addons/gdUnit4/runner.gd\n")
        self.write("docs/engine-reference/godot/VERSION.md", "| **Engine Version** | 4.0 |\n")
        output = self.success(self.run_tool("scripts/project-coherence.sh"))
        self.assertIn("$codex-setup-engine", output)
        self.assertIn("$codex-smoke-check", output)
        self.assertIn("$codex-test-setup", output)

    def test_artifact_minimal_has_denominators(self) -> None:
        child = self.fixture / "src"
        child.mkdir()
        output = self.success(self.run_tool("scripts/artifact-check.sh", "--path", "minimal", cwd=child))
        self.assertIn("PATHS: 1", output)
        self.assertIn("STEPS: 5", output)
        self.assertIn("NO_CHECK: 2", output)
        self.assertIn("status=ABSENT", output)

    def test_artifact_bad_arguments_fail(self) -> None:
        for args in (("--path",), ("--phase",), ("--path=",), ("--bogus",),
                     ("--path", "unknown"), ("--phase", "concept", "--path", "minimal"),
                     (self.fixture.as_posix(), self.fixture.as_posix())):
            with self.subTest(args=args):
                result = self.run_tool("scripts/artifact-check.sh", *args)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_noarg_helpers_reject_unknown_options(self) -> None:
        for name in ("story-status.sh", "project-coherence.sh", "review-scope.sh", "adr-dep-graph.sh"):
            with self.subTest(script=name):
                self.assertEqual(self.run_tool("scripts/" + name, "--bogus").returncode, 2)

    def test_all_helpers_have_nonmutating_help(self) -> None:
        files = list((self.fixture / "tools/codex-studio").rglob("*.sh"))
        for file in files:
            with self.subTest(script=file.name):
                output = self.success(self.run_bash(file.as_posix(), "--help"))
                self.assertTrue(output.strip())

    def test_story_status_orders_review_progress_todo(self) -> None:
        for name, state in (("01", "Ready"), ("02", "In Progress"), ("03", "In Review"), ("04", "Complete")):
            self.write(f"production/epics/one/story-{name}.md", f"**Status:** {state}\n")
        output = self.success(self.run_tool("scripts/story-status.sh"))
        self.assertLess(output.index("IN_REVIEW"), output.index("IN_PROGRESS"))
        self.assertLess(output.index("IN_PROGRESS"), output.index("TODO"))
        self.assertIn("COMPLETE     1 of 4", output)

    def test_adr_cycle_is_observed_and_acyclic_exit_is_zero(self) -> None:
        for a, b in (("0001", "0002"), ("0002", "0001")):
            self.write(f"docs/architecture/adr-{a}.md", f"## ADR Dependencies\n| **Depends On** | ADR-{b} |\n")
        output = self.success(self.run_tool("scripts/adr-dep-graph.sh"))
        self.assertIn("CYCLE: adr-0001", output)
        self.assertIn("adr-0001 -> adr-0002", output)
        self.write("docs/architecture/adr-0002.md", "## ADR Dependencies\n| **Depends On** | None |\n")
        output = self.success(self.run_tool("scripts/adr-dep-graph.sh"))
        self.assertNotIn("CYCLE:", output)

    def test_gdd_explicit_file_reports_sections(self) -> None:
        file = self.write("design/gdd/a system.md", "## Overview\n## Detailed Design\n")
        output = self.success(self.run_tool("scripts/gdd-structure-check.sh", file.as_posix()))
        self.assertIn("PRESENT: Overview,Detailed Rules", output)
        self.assertIn("ABSENT:", output)

    def test_review_receipts_detect_content_and_sections(self) -> None:
        file = self.write("design/gdd/a system.md", "# Title\n## Rules\noriginal\n")
        script = "scripts/review-receipts.sh"
        stamp = self.success(self.run_tool(script, "hash", file.as_posix()))
        receipt = self.write("receipt.md", stamp)
        self.assertIn("UNCHANGED:", self.success(self.run_tool(script, "check", receipt.as_posix(), file.as_posix())))
        self.write("design/gdd/a system.md", "# Title\n## Rules\nchanged\n")
        self.assertIn("CHANGED:", self.success(self.run_tool(script, "check", receipt.as_posix(), file.as_posix())))
        stamp = self.success(self.run_tool(script, "sections-hash", file.as_posix()))
        self.write("receipt.md", stamp)
        self.assertIn("SECTION-UNCHANGED: Rules", self.success(self.run_tool(script, "sections-check", receipt.as_posix(), file.as_posix())))

    def test_review_receipts_unknown_or_missing_arguments_fail(self) -> None:
        for args in ((), ("unknown",), ("hash",), ("check",), ("sections-hash",), ("sections-check",)):
            with self.subTest(args=args):
                self.assertEqual(self.run_tool("scripts/review-receipts.sh", *args).returncode, 2)

    def test_mutating_helpers_dry_run_and_error_are_nonmutating(self) -> None:
        state = self.write("production/session-state/active.md",
                           "<!-- CHECKPOINT -->\nState\n<!-- /CHECKPOINT -->\n" + "note\n" * 12)
        original = state.read_bytes()
        output = self.success(self.run_tool("scripts/rotate-session-state.sh", "--dry-run"))
        self.assertIn("DRY RUN", output)
        self.assertEqual(state.read_bytes(), original)
        self.assertFalse((self.fixture / "production/session-logs").exists())
        config = (self.fixture / "project.yaml").read_bytes()
        self.success(self.run_tool("scripts/migrate-v1-config.sh", "--dry-run"))
        self.assertEqual((self.fixture / "project.yaml").read_bytes(), config)
        for script in ("rotate-session-state.sh", "migrate-v1-config.sh"):
            self.assertEqual(self.run_tool("scripts/" + script, "--dry-run", "--extra").returncode, 2)
        self.assertFalse((self.fixture / "production/migration-report.md").exists())

    def test_rotation_in_fixture_preserves_narrative_in_archive(self) -> None:
        state = self.write("production/session-state/active.md",
                           "<!-- CHECKPOINT -->\nState\n<!-- /CHECKPOINT -->\n" + "original story note\n" * 12)
        output = self.success(self.run_tool("scripts/rotate-session-state.sh"))
        self.assertIn("rotated", output)
        self.assertIn("<!-- /CHECKPOINT -->", state.read_text(encoding="utf-8"))
        self.assertNotIn("original story note", state.read_text(encoding="utf-8"))
        archives = list((self.fixture / "production/session-logs").glob("session-state-*.md"))
        self.assertEqual(len(archives), 1)
        self.assertEqual(archives[0].read_text(encoding="utf-8").count("original story note"), 12)

    def test_legacy_config_migration_uses_standalone_release_and_preserves_sources(self) -> None:
        (self.fixture / "project.yaml").unlink()
        stage = self.write("production/stage.txt", "Concept\n")
        review = self.write("production/review-mode.txt", "none\n")
        version = tomllib.loads((ROOT / "codex-studio.toml").read_text(encoding="utf-8"))["version"]
        self.env["CODEX_STUDIO_VERSION"] = version
        self.success(self.run_tool("scripts/migrate-v1-config.sh"))
        config = (self.fixture / "project.yaml").read_text(encoding="utf-8")
        self.assertIn(f"  version: {version}\n", config)
        self.assertIn('  stage: "Concept"', config)
        self.assertIn('  review_mode: solo', config)
        self.assertEqual(stage.read_text(encoding="utf-8"), "Concept\n")
        self.assertEqual(review.read_text(encoding="utf-8"), "none\n")
        self.assertTrue((self.fixture / "production/migration-report.md").is_file())

    def test_legacy_config_migration_reads_helper_manifest_not_target_manifest(self) -> None:
        # CODEX_STUDIO_ROOT points at the target game, while the helper's
        # adjacent manifest identifies the Codex distribution that ran it.
        target = Path(tempfile.mkdtemp(prefix="codex migration target "))
        self.addCleanup(shutil.rmtree, target)
        self.write("codex-studio.toml", 'version = "9.9.9"\n')
        (target / "codex-studio.toml").write_text('version = "8.8.8"\n', encoding="utf-8")
        (target / "production").mkdir(parents=True)
        (target / "production/stage.txt").write_text("Concept\n", encoding="utf-8")
        (target / "production/review-mode.txt").write_text("none\n", encoding="utf-8")

        self.success(self.run_tool("scripts/migrate-v1-config.sh", override=target))
        config = (target / "project.yaml").read_text(encoding="utf-8")
        self.assertIn("  version: 9.9.9\n", config)
        self.assertNotIn("  version: 8.8.8\n", config)

    def test_legacy_config_migration_rejects_invalid_release_before_writing(self) -> None:
        (self.fixture / "project.yaml").unlink()
        self.write("production/stage.txt", "Concept\n")
        self.write("production/review-mode.txt", "none\n")
        self.env["CODEX_STUDIO_VERSION"] = "not-semver"

        result = self.run_tool("scripts/migrate-v1-config.sh")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("invalid framework release", result.stderr)
        self.assertFalse((self.fixture / "project.yaml").exists())
        self.assertFalse((self.fixture / "production/migration-report.md").exists())

    def test_legacy_config_migration_rejects_unreadable_helper_manifest(self) -> None:
        (self.fixture / "project.yaml").unlink()
        self.write("production/stage.txt", "Concept\n")
        self.write("production/review-mode.txt", "none\n")
        self.write("codex-studio.toml", "name = \"Codex Game Studios\"\n")

        result = self.run_tool("scripts/migrate-v1-config.sh")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("could not read a version", result.stderr)
        self.assertFalse((self.fixture / "project.yaml").exists())
        self.assertFalse((self.fixture / "production/migration-report.md").exists())


if __name__ == "__main__":
    unittest.main()
