"""Tests for the non-forging provenance receipt helper."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/codex-studio/provenance_receipt.py"
SPEC = importlib.util.spec_from_file_location("provenance_receipt", MODULE_PATH)
assert SPEC and SPEC.loader
provenance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(provenance)


class ProvenanceReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="codex-provenance-test-")
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)

    def init(self) -> Path:
        return provenance.init_receipt(
            self.workspace, "run-01", "$codex-dev-story"
        )

    def test_init_is_not_assessed_and_never_fabricates_evidence(self) -> None:
        run = self.init()
        metadata = json.loads((run / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "NOT ASSESSED")
        self.assertEqual(
            sorted(path.name for path in run.iterdir()), ["receipt.json", "receipt.md"]
        )
        ok, errors, status = provenance.verify_receipt(run)
        self.assertFalse(ok)
        self.assertEqual(status, "NOT ASSESSED")
        self.assertTrue(any("TRANSCRIPT.md" in error for error in errors))

    def test_capture_inputs_hashes_only_and_rejects_escape(self) -> None:
        run = self.init()
        source = self.workspace / "design.md"
        source.write_text("brief", encoding="utf-8")
        inputs = provenance.capture_inputs(run, ["design.md"])
        self.assertIn("SHA256 ", inputs.read_text(encoding="utf-8"))
        self.assertFalse((run / "TRANSCRIPT.md").exists())
        with self.assertRaises(provenance.ReceiptError):
            provenance.capture_inputs(run, ["../outside.md"])

    def test_fake_summary_transcript_is_not_host_evidence(self) -> None:
        run = self.init()
        self._write_minimum_evidence(run, transcript="TRANSCRIPT_SOURCE: SUMMARY\n$codex-dev-story\n")
        ok, errors, status = provenance.verify_receipt(run)
        self.assertFalse(ok)
        self.assertEqual(status, "NOT ASSESSED")
        self.assertTrue(any("CODEX_HOST_EXPORT" in error for error in errors))

    def test_verified_receipt_requires_selected_skill_hash(self) -> None:
        run = self.init()
        (self.workspace / "design.md").write_text("brief", encoding="utf-8")
        provenance.capture_inputs(run, ["design.md"])
        self._write_minimum_evidence(
            run,
            transcript="TRANSCRIPT_SOURCE: CODEX_HOST_EXPORT\nUSER: $codex-dev-story\n",
        )
        metadata = json.loads((run / "receipt.json").read_text(encoding="utf-8"))
        metadata["status"] = "VERIFIED"
        (run / "receipt.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        markdown = (run / "receipt.md").read_text(encoding="utf-8")
        (run / "receipt.md").write_text(
            markdown.replace("`NOT ASSESSED`", "`VERIFIED`").replace("<timestamps>", "2026-01-01T00:00:00Z"),
            encoding="utf-8",
        )
        ok, errors, status = provenance.verify_receipt(run)
        self.assertFalse(ok)
        self.assertEqual(status, "NOT ASSESSED")
        self.assertTrue(any("selected Skill" in error for error in errors), errors)

    def test_complete_host_evidence_can_be_verified(self) -> None:
        run = self.init()
        (self.workspace / "design.md").write_text("brief", encoding="utf-8")
        skill = self.workspace / ".agents/skills/codex-dev-story/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("skill", encoding="utf-8")
        provenance.capture_inputs(run, ["design.md", ".agents/skills/codex-dev-story/SKILL.md"])
        self._write_minimum_evidence(
            run,
            transcript="TRANSCRIPT_SOURCE: CODEX_HOST_EXPORT\nUSER: $codex-dev-story\n",
        )
        metadata = json.loads((run / "receipt.json").read_text(encoding="utf-8"))
        metadata["status"] = "VERIFIED"
        (run / "receipt.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        markdown = (run / "receipt.md").read_text(encoding="utf-8")
        markdown = markdown.replace("`NOT ASSESSED`", "`VERIFIED`").replace(
            "<timestamps>", "2026-01-01T00:00:00Z"
        )
        (run / "receipt.md").write_text(markdown, encoding="utf-8")
        ok, errors, status = provenance.verify_receipt(run)
        self.assertTrue(ok, errors)
        self.assertEqual(status, "VERIFIED")

    @staticmethod
    def _write_minimum_evidence(run: Path, transcript: str) -> None:
        (run / "TRANSCRIPT.md").write_text(transcript, encoding="utf-8")
        (run / "CHANGES.patch").write_text(
            "NO_CHANGES: documentation-only test fixture\n", encoding="utf-8"
        )
        (run / "VERIFICATION.md").write_text(
            "COMMAND: python -m unittest\nEXIT_CODE: 0\nSUMMARY: tests passed\n",
            encoding="utf-8",
        )
        (run / "checkpoint-before.md").write_text("before\n", encoding="utf-8")
        (run / "checkpoint-after.md").write_text("after\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
