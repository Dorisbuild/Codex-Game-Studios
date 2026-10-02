"""Distribution privacy and lossless, non-overwriting snapshot regressions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from package_studio import export_files, package
from restore_snapshot import restore


class ExportSafetyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="codex export privacy ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def write(self, relative, contents=b"private local state"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
        return path

    def test_sensitive_name_filters_are_case_insensitive(self):
        paths = (
            "docs/.ENV", "docs/.ENV.PRODUCTION", "docs/Credentials.JSON",
            "tools/SECRETs.json", ".codex/AUTH.JSON", ".codex/AGENTS.OVERRIDE.MD",
            ".codex/CONFIG.LOCAL.TOML", "design/PROJECT.LOCAL.YAML",
            "tools/private.KEY", "tools/private.PEM", "docs/local.LOG",
            "docs/__PYCACHE__/private.bin", "production/SESSION-STATE/active.md",
            "production/SESSION-LOGS/context.md",
        )
        for name in paths:
            self.write(name)
        self.assertEqual(list(export_files(self.root)), [])

    def test_local_sandbox_backup_and_temporary_files_are_excluded(self):
        paths = (
            "tests/sandboxes/private-copy.txt", "tests/SANDBOXES/private-copy.txt",
            "tools/private-backup.zip", "docs/snapshot-20261002.TAR.GZ",
            "tools/Backup.ZIP", "docs/backups/old-notes.md",
            "docs/.backups/old-notes.md", "tools/cache.tmp", "tools/notes.md~",
            "docs/report.md.bak", "tools/script.py.swp",
        )
        for name in paths:
            self.write(name)
        self.assertEqual(list(export_files(self.root)), [])

    def test_regular_binary_and_archive_dependencies_are_preserved(self):
        paths = (
            ".agents/skills/codex-example/assets/reference.png",
            ".agents/skills/codex-example/references/workflow.md",
            "tests/fixtures/sample.zip", "tools/resources/engine-sdk.tar.gz",
            "docs/architecture/backup-design.md", "src/backpack.gd",
        )
        for name in paths:
            self.write(name, b"legitimate dependency")
        exported = {p.relative_to(self.root).as_posix() for p in export_files(self.root)}
        self.assertEqual(exported, set(paths))

    def test_optional_game_tree_is_packaged_without_local_state(self):
        """An intentionally supplied sample tree remains packageable."""
        self.write("codex-studio.toml", b'slug = "Codex-Game-Studios"\n')
        self.write("README.md", b"standalone fixture\n")
        self.write("samples/index.html", b"<!doctype html><script src=game.js></script>")
        self.write("samples/game.js", b"console.log('sample')")
        self.write("samples/README.md", b"Run the sample")
        # Engine/editor caches and session state must never turn into release
        # members even when a demo is opened locally before packaging.
        self.write("samples/.godot/editor/file_cache.cfg")
        self.write("samples/production/session-state/active.md")
        with patch("package_studio.Verifier") as verifier:
            verifier.return_value.run.return_value = True
            output = self.root / "dist/demo.zip"
            package(self.root, output)
        with zipfile.ZipFile(output) as archive:
            names = set(archive.namelist())
        self.assertEqual(
            names,
            {
                "Codex-Game-Studios/codex-studio.toml",
                "Codex-Game-Studios/README.md",
                "Codex-Game-Studios/samples/index.html",
                "Codex-Game-Studios/samples/game.js",
                "Codex-Game-Studios/samples/README.md",
            },
        )

    def test_private_filters_do_not_break_reproducible_packaging(self):
        self.write("codex-studio.toml", b'slug = "Codex-Game-Studios"\n')
        self.write("README.md", b"standalone fixture\n")
        self.write("tests/fixtures/sample.zip", b"necessary archive dependency")
        self.write("tools/private-backup.zip")
        self.write("docs/.ENV")
        # Verifier integration is tested in test_codex_studio. This fixture
        # isolates packaging, so registry changes do not mask filter regressions.
        with patch("package_studio.Verifier") as verifier:
            verifier.return_value.run.return_value = True
            first = self.root / "dist/first.zip"
            second = self.root / "dist/second.zip"
            count, one = package(self.root, first)
            _, two = package(self.root, second)
        self.assertEqual(count, 3)
        self.assertEqual(one, two)
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(set(archive.namelist()), {
                "Codex-Game-Studios/codex-studio.toml", "Codex-Game-Studios/README.md",
                "Codex-Game-Studios/tests/fixtures/sample.zip",
            })

    def test_engine_build_outputs_are_excluded_from_distribution(self):
        paths = (
            "codex-studio.toml", "README.md",
            "production/builds/game.exe", "samples/godot-game/builds/game.exe",
            "samples/godot-game/exports/game.pck", "samples/godot-game/build/cache.bin",
        )
        for name in paths:
            self.write(name)
        exported = {p.relative_to(self.root).as_posix() for p in export_files(self.root)}
        self.assertEqual(exported, {"codex-studio.toml", "README.md"})


class RecoveryPortabilityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="codex recovery aliases ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.archive = self.root / "snapshot.zip"
        self.destination = self.root / "restored"

    def make_archive(self, entries):
        with zipfile.ZipFile(self.archive, "w") as archive:
            for name, data in entries:
                archive.writestr(name, data)

    def test_double_separator_and_dot_aliases_are_rejected_before_write(self):
        for index, alias in enumerate(("notes//file.md", "notes/./file.md", "./notes/file.md")):
            self.destination = self.root / f"restored-{index}"
            with self.subTest(alias=alias):
                self.make_archive([("notes/file.md", b"original"), (alias, b"overwrites")])
                with self.assertRaises(ValueError):
                    restore(self.archive, self.destination)
                self.assertFalse(self.destination.exists())

    def test_windows_trailing_dot_and_space_are_rejected_before_write(self):
        for index, alias in enumerate(("file.md.", "file.md ", "notes./file.md", "notes /file.md")):
            self.destination = self.root / f"restored-{index}"
            with self.subTest(alias=alias):
                self.make_archive([(alias, b"ambiguous")])
                with self.assertRaises(ValueError):
                    restore(self.archive, self.destination)
                self.assertFalse(self.destination.exists())

    def test_windows_reserved_and_invalid_names_are_rejected_before_write(self):
        for index, name in enumerate(("NUL", "CON.txt", "AUX.md", "COM1", "LPT9.log", "bad?.txt", "a|b.md")):
            self.destination = self.root / f"restored-{index}"
            with self.subTest(name=name):
                self.make_archive([(name, b"not portable")])
                with self.assertRaises(ValueError):
                    restore(self.archive, self.destination)
                self.assertFalse(self.destination.exists())

    def test_file_directory_conflicts_are_rejected_before_write(self):
        for index, entries in enumerate((
            [("notes", b"file"), ("notes/file.md", b"child")],
            [("notes/file.md", b"child"), ("notes", b"file")],
            [("notes/", b""), ("notes", b"file")],
        )):
            self.destination = self.root / f"restored-{index}"
            with self.subTest(entries=entries):
                self.make_archive(entries)
                with self.assertRaises(ValueError):
                    restore(self.archive, self.destination)
                self.assertFalse(self.destination.exists())

    def test_hash_manifest_and_explicit_directories_restore_without_loss(self):
        files = {"notes/a.md": b"first", "notes/b.md": b"second", "assets/reference.png": b"binary"}
        self.make_archive([("notes/", b""), *files.items()])
        manifest = self.root / "hashes.json"
        manifest.write_text(json.dumps({n: hashlib.sha256(b).hexdigest() for n, b in files.items()}), encoding="utf-8")
        self.assertEqual(restore(self.archive, self.destination, manifest), 3)
        restored = {p.relative_to(self.destination).as_posix(): p.read_bytes()
                    for p in self.destination.rglob("*") if p.is_file()}
        self.assertEqual(restored, files)

    def test_existing_current_data_remains_untouched(self):
        self.destination.mkdir()
        current = self.destination / "current.txt"
        current.write_bytes(b"current uncommitted edits")
        self.make_archive([("current.txt", b"old data")])
        with self.assertRaises(FileExistsError):
            restore(self.archive, self.destination)
        self.assertEqual(current.read_bytes(), b"current uncommitted edits")


if __name__ == "__main__":
    unittest.main()
