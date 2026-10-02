#!/usr/bin/env python3
"""Create and audit Codex Game Studios provenance receipts.

This helper records machine-readable receipt metadata and checks that a human or
host supplied the required evidence for a Skill pass. It intentionally never
creates a transcript, patch, checkpoint, or verification result on its own.
An ``init`` pass therefore remains NOT ASSESSED until the Codex host copies its
real transcript and the other observed artifacts into the run directory.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Iterable


SCHEMA_VERSION = 1
RECEIPT_JSON = "receipt.json"
RECEIPT_MD = "receipt.md"
EVIDENCE_FILES = (
    "TRANSCRIPT.md",
    "INPUTS.md",
    "CHANGES.patch",
    "VERIFICATION.md",
    "checkpoint-before.md",
    "checkpoint-after.md",
)
STATUSES = ("VERIFIED", "PARTIAL", "NOT ASSESSED", "FAIL")
SELECTOR_RE = re.compile(r"^\$codex-[a-z0-9]+(?:-[a-z0-9]+)*(?:\s|$)")
SHA_LINE_RE = re.compile(
    r"^SHA256\s+([0-9a-fA-F]{64})\s{2}(.+?)\s*$", re.MULTILINE
)
EXIT_LINE_RE = re.compile(
    r"^\s*(?:EXIT_CODE|exit(?:\s+|_)code|return(?:\s+|_)code|status)\s*[:=]\s*(-?\d+)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
COMMAND_LINE_RE = re.compile(
    r"^\s*(?:COMMAND|COMMAND_LINE)\s*[:=]\s*\S+", re.IGNORECASE | re.MULTILINE
)
SUMMARY_LINE_RE = re.compile(
    r"^\s*(?:SUMMARY|OUTPUT)\s*[:=]\s*\S+", re.IGNORECASE | re.MULTILINE
)
STATUS_LINE_RE = re.compile(
    r"^\*\*Status:\*\*\s*`([^`]+)`", re.IGNORECASE | re.MULTILINE
)
SELECTOR_LINE_RE = re.compile(
    r"^\*\*Skill selector:\*\*\s*`([^`]+)`", re.IGNORECASE | re.MULTILINE
)
PLACEHOLDER_MARKERS = (
    "<run-id>",
    "<absolute path>",
    "<timestamps>",
    "PASTE HOST TRANSCRIPT",
    "PASTE HOST EXPORT",
)


class ReceiptError(ValueError):
    """A user-actionable receipt error."""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve(path: Path | str) -> Path:
    return Path(os.path.abspath(os.fspath(path))).resolve(strict=False)


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _safe_run_id(run_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", run_id):
        raise ReceiptError("run-id must be 1-64 letters, digits, dot, underscore or hyphen")
    return run_id


def _run_dir(workspace: Path, run_id: str) -> Path:
    workspace = _resolve(workspace)
    if not workspace.is_dir():
        raise ReceiptError(f"workspace directory does not exist: {workspace}")
    return workspace / "production" / "provenance" / _safe_run_id(run_id)


def _load_receipt(run_dir: Path) -> dict[str, object]:
    if run_dir.is_symlink():
        raise ReceiptError(f"run directory is a symlink/junction: {run_dir}")
    path = run_dir / RECEIPT_JSON
    if not path.is_file() or path.is_symlink():
        raise ReceiptError(f"receipt metadata missing or unsafe: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReceiptError(f"receipt metadata unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise ReceiptError("receipt metadata must be a JSON object")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ReceiptError(f"unsupported receipt schema_version: {value.get('schema_version')!r}")
    return value


def _write_receipt_markdown(run_dir: Path, run_id: str, selector: str, workspace: Path) -> None:
    # This is a status=NOT ASSESSED shell only. In particular, it does not
    # pretend to be the host transcript or any observed verification output.
    text = f"""# Skill pass receipt — `{run_id}`

**Status:** `NOT ASSESSED`
**Skill selector:** `{selector}`
**Workspace:** `{workspace}`
**Started / finished:** `<timestamps>`

## Evidence links

- Transcript: `TRANSCRIPT.md` (copy from the Codex host; do not summarize)
- Inputs and SHA-256 values: `INPUTS.md`
- Before/after change: `CHANGES.patch`
- Commands and literal output: `VERIFICATION.md`
- Checkpoints: `checkpoint-before.md`, `checkpoint-after.md`

This shell was created by `provenance_receipt.py init`. It is not evidence and
must remain NOT ASSESSED until the host-supplied files are present. The CLI
never creates or fabricates a transcript.
"""
    (run_dir / RECEIPT_MD).write_text(text, encoding="utf-8", newline="\n")


def init_receipt(workspace: Path | str, run_id: str, selector: str) -> Path:
    """Create a non-asserting receipt shell and no evidence files."""

    workspace_path = _resolve(workspace)
    if Path(workspace).is_symlink():
        raise ReceiptError("workspace must not be a symlink/junction")
    if not SELECTOR_RE.match(selector):
        raise ReceiptError("selector must be an explicit $codex-* Skill selector")
    run_dir = _run_dir(workspace_path, run_id)
    if os.path.lexists(run_dir):
        raise FileExistsError(f"run directory already exists; refusing to overwrite: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)
    metadata: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "workspace": str(workspace_path),
        "skill_selector": selector,
        "status": "NOT ASSESSED",
        "evidence": {name: name for name in EVIDENCE_FILES},
        "created_at": _now(),
        "warning": "Metadata is not proof. The CLI never creates or fabricates a host transcript.",
    }
    (run_dir / RECEIPT_JSON).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _write_receipt_markdown(run_dir, run_id, selector, workspace_path)
    return run_dir


def _git_description(workspace: Path) -> str:
    try:
        commit = subprocess.run(
            ["git", "-C", str(workspace), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        status = subprocess.run(
            ["git", "-C", str(workspace), "status", "--porcelain", "--untracked-files=all"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        if commit.returncode == 0 and status.returncode == 0:
            return f"commit={commit.stdout.strip()} dirty={'true' if status.stdout.strip() else 'false'}"
    except (OSError, subprocess.SubprocessError):
        pass
    return "unavailable (descriptive only)"


def capture_inputs(run_dir: Path | str, files: Iterable[str]) -> Path:
    """Capture SHA-256 values only; this command cannot create a transcript."""

    raw_run_path = Path(run_dir)
    if raw_run_path.is_symlink():
        raise ReceiptError("run directory must not be a symlink/junction")
    run_path = _resolve(raw_run_path)
    metadata = _load_receipt(run_path)
    workspace_value = metadata.get("workspace")
    if not isinstance(workspace_value, str):
        raise ReceiptError("receipt workspace is missing")
    workspace = _resolve(workspace_value)
    if not workspace.is_dir():
        raise ReceiptError(f"workspace directory does not exist: {workspace}")
    expected_run = workspace / "production" / "provenance" / str(metadata.get("run_id", ""))
    if run_path != expected_run:
        raise ReceiptError("run directory is outside receipt workspace provenance root")
    requested = list(files)
    if not requested:
        raise ReceiptError("at least one --file is required")
    records: list[tuple[str, str]] = []
    for value in requested:
        candidate = Path(value)
        raw_path = candidate if candidate.is_absolute() else workspace / candidate
        if raw_path.is_symlink():
            raise ReceiptError(f"input is a symlink/junction: {value}")
        path = _resolve(raw_path)
        if not _is_within(path, workspace):
            raise ReceiptError(f"input is outside workspace: {value}")
        if path.is_symlink() or not path.is_file():
            raise ReceiptError(f"input is not a regular file: {value}")
        relative = path.relative_to(workspace).as_posix()
        records.append((relative, _sha256(path)))
    records = sorted(set(records))
    lines = [
        "# Input hashes captured by provenance_receipt.py",
        "INPUTS_SOURCE: receipt-cli (hashes only; not a transcript)",
        f"WORKSPACE: {workspace}",
        f"CAPTURED_AT: {_now()}",
        f"SOURCE_GIT: {_git_description(workspace)}",
        "",
    ]
    lines.extend(f"SHA256 {digest}  {relative}" for relative, digest in records)
    destination = run_path / "INPUTS.md"
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"input receipt already exists; refusing to overwrite: {destination}")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return destination


def _manifest_input_errors(text: str, required_skill: str | None = None) -> list[str]:
    errors: list[str] = []
    records = SHA_LINE_RE.findall(text)
    if not records:
        errors.append("INPUTS.md has no canonical SHA256 lines")
        return errors
    seen: set[str] = set()
    paths: set[str] = set()
    for _digest, relative in records:
        path = PurePosixPath(relative)
        if path.is_absolute() or not path.parts or ".." in path.parts or "." in path.parts:
            errors.append(f"INPUTS.md has unsafe path: {relative}")
        if relative in seen:
            errors.append(f"INPUTS.md repeats path: {relative}")
        seen.add(relative)
        paths.add(relative)
    if required_skill:
        expected = f".agents/skills/{required_skill}/SKILL.md"
        if expected not in paths:
            errors.append(f"INPUTS.md must hash the selected Skill: {expected}")
    return errors


def _evidence_errors(run_dir: Path, metadata: dict[str, object]) -> list[str]:
    errors: list[str] = []
    status = metadata.get("status")
    if metadata.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"receipt schema_version must be {SCHEMA_VERSION}")
    if status not in STATUSES:
        errors.append(f"receipt status must be one of {', '.join(STATUSES)}")
    selector = metadata.get("skill_selector")
    if not isinstance(selector, str) or not SELECTOR_RE.match(selector):
        errors.append("receipt skill_selector must be an explicit $codex-* selector")
    if metadata.get("run_id") != run_dir.name:
        errors.append("receipt run_id does not match directory name")
    evidence = metadata.get("evidence")
    if not isinstance(evidence, dict) or any(evidence.get(name) != name for name in EVIDENCE_FILES):
        errors.append("receipt evidence map must name all required evidence files")
    workspace_value = metadata.get("workspace")
    if not isinstance(workspace_value, str):
        errors.append("receipt workspace is missing")
    else:
        workspace = _resolve(workspace_value)
        if not workspace.is_dir():
            errors.append(f"receipt workspace does not exist: {workspace_value}")
        elif run_dir != workspace / "production" / "provenance" / str(metadata.get("run_id", "")):
            errors.append("run directory is outside receipt workspace provenance root")

    receipt_md = run_dir / RECEIPT_MD
    if not receipt_md.is_file() or receipt_md.is_symlink():
        errors.append("receipt.md is missing or unsafe")
    else:
        try:
            text = receipt_md.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"receipt.md unreadable: {exc}")
        else:
            status_match = STATUS_LINE_RE.search(text)
            if not status_match:
                errors.append("receipt.md has no **Status:** line")
            elif status_match.group(1).strip() != status:
                errors.append("receipt.md status does not match receipt.json")
            selector_match = SELECTOR_LINE_RE.search(text)
            if not selector_match or selector_match.group(1).strip() != selector:
                errors.append("receipt.md selector does not match receipt.json")
            if any(marker.casefold() in text.casefold() for marker in PLACEHOLDER_MARKERS):
                errors.append("receipt.md still contains generated placeholder markers")

    for name in EVIDENCE_FILES:
        path = run_dir / name
        if path.is_symlink() or not path.is_file():
            errors.append(f"missing evidence: {name}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"evidence unreadable ({name}): {exc}")
            continue
        if not text.strip():
            errors.append(f"evidence is empty: {name}")
            continue
        if name == "TRANSCRIPT.md":
            if "TRANSCRIPT_SOURCE: CODEX_HOST_EXPORT" not in text:
                errors.append("TRANSCRIPT.md must declare TRANSCRIPT_SOURCE: CODEX_HOST_EXPORT")
            if not isinstance(selector, str) or selector not in text:
                errors.append("TRANSCRIPT.md does not contain the receipt selector")
            if any(marker.casefold() in text.casefold() for marker in PLACEHOLDER_MARKERS):
                errors.append("TRANSCRIPT.md still contains generated placeholder markers")
        elif name == "INPUTS.md":
            required_skill = None
            if isinstance(selector, str):
                required_skill = selector.split(maxsplit=1)[0].removeprefix("$")
            errors.extend(_manifest_input_errors(text, required_skill))
        elif name == "CHANGES.patch":
            has_diff = "diff --git " in text or ("--- " in text and "+++ " in text)
            if not has_diff and "NO_CHANGES:" not in text:
                errors.append("CHANGES.patch needs a git diff or explicit NO_CHANGES: reason")
        elif name == "VERIFICATION.md":
            if not COMMAND_LINE_RE.search(text):
                errors.append("VERIFICATION.md has no COMMAND: line")
            exits = [int(value) for value in EXIT_LINE_RE.findall(text)]
            if not exits:
                errors.append("VERIFICATION.md has no exact EXIT_CODE/exit code line")
            if not SUMMARY_LINE_RE.search(text):
                errors.append("VERIFICATION.md has no SUMMARY: or OUTPUT: line")
            if status == "VERIFIED" and 0 not in exits:
                errors.append("VERIFIED receipt needs at least one EXIT_CODE: 0")
    return errors


def verify_receipt(run_dir: Path | str) -> tuple[bool, list[str], str]:
    """Return ``(strict_pass, errors, effective_status)`` without modifying files."""

    run_path = _resolve(run_dir)
    if not run_path.is_dir():
        return False, [f"run directory does not exist: {run_path}"], "NOT ASSESSED"
    try:
        metadata = _load_receipt(run_path)
    except ReceiptError as exc:
        return False, [str(exc)], "NOT ASSESSED"
    errors = _evidence_errors(run_path, metadata)
    declared = metadata.get("status")
    effective = declared if declared in STATUSES else "NOT ASSESSED"
    if errors and effective == "VERIFIED":
        effective = "NOT ASSESSED"
    return effective == "VERIFIED" and not errors, errors, effective


def _cmd_init(args: argparse.Namespace) -> int:
    try:
        path = init_receipt(args.workspace, args.run_id, args.selector)
    except FileExistsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (OSError, ReceiptError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"INIT: NOT ASSESSED — {path}")
    print("No transcript, patch, checkpoint or verification output was created.")
    print(f"Next: copy host evidence, then run python {Path(__file__).resolve()} verify {path}")
    return 0


def _cmd_capture(args: argparse.Namespace) -> int:
    try:
        path = capture_inputs(args.run_dir, args.file)
    except FileExistsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (OSError, ReceiptError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"CAPTURED: INPUTS.md (hashes only) — {path}")
    print("This command did not create or modify a transcript.")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    try:
        ok, errors, status = verify_receipt(args.run_dir)
    except (OSError, ReceiptError) as exc:
        print("VERIFY: NOT ASSESSED", file=sys.stderr)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    stream = sys.stdout if ok else sys.stderr
    print(f"VERIFY: {status}", file=stream)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    else:
        print(f"Evidence: {len(EVIDENCE_FILES)} required files plus receipt metadata", file=stream)
    return 0 if ok else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    init_parser = commands.add_parser("init", help="create a NOT ASSESSED receipt shell")
    init_parser.add_argument("--workspace", type=Path, required=True)
    init_parser.add_argument("--run-id", required=True)
    init_parser.add_argument("--selector", required=True, help="explicit $codex-* selector")
    init_parser.set_defaults(handler=_cmd_init)

    capture_parser = commands.add_parser("capture-inputs", help="write SHA-256 input records only")
    capture_parser.add_argument("run_dir", type=Path)
    capture_parser.add_argument("--file", action="append", required=True, help="workspace-relative file (repeatable)")
    capture_parser.set_defaults(handler=_cmd_capture)

    verify_parser = commands.add_parser("verify", help="strictly verify a receipt and its evidence")
    verify_parser.add_argument("run_dir", type=Path)
    verify_parser.set_defaults(handler=_cmd_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
