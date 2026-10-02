#!/usr/bin/env python3
"""Create a clean, independent Codex Game Studios game workspace.

The maintenance checkout is a framework-only library; game workspaces and
runtime evidence are intentionally kept separate. This helper copies only the
framework and its test/spec resources, then creates empty game directories and
a small onboarding file. It never initialises Git, installs anything, starts a
Codex thread, or removes an existing directory.

The default operation is a read-only plan.  Use ``--create`` only when the
target path is a new directory.  ``--verify`` checks the manifest hashes and
the clean-template boundary without deleting user files.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Iterable, Mapping


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "workspace-manifest.json"

# These are the framework roots. ``design``, ``src`` and ``production`` are
# deliberately *not* source roots: a game workspace owns those directories,
# while this maintenance checkout keeps only empty placeholders. The new
# workspace receives empty versions of those directories below instead.
COPY_DIRS = (
    ".agents",
    ".codex",
    "docs",
    "tools",
    "tests",
    "Codex Skill Testing Framework",
)

# Files required by the standalone verifier, plus the legal and project
# identity files that make a copy useful outside Git.  README/AGENTS/project
# config/.gitignore are generated so they cannot carry a demo's context.
COPY_ROOT_FILES = (
    "LICENSE",
    "NOTICE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".gitattributes",
    "codex-studio.toml",
    "requirements-dev.txt",
)
REQUIRED_ROOT_FILES = (
    "LICENSE",
    "NOTICE.md",
    "AGENTS.md",
    "codex-studio.toml",
    "requirements-dev.txt",
)

# Local/runtime material that must never be copied into a new game workspace.
# Names are compared case-insensitively, matching the distribution packager's
# safety rules.  The scan is applied to all source paths, including excluded
# game directories, so an old artifact cannot be reintroduced accidentally.
EXCLUDED_DIR_NAMES = {
    ".git",
    ".godot",
    ".pytest_cache",
    "__pycache__",
    "build",
    "builds",
    "dist",
    "exports",
    "library",
    "logs",
    "node_modules",
    "obj",
    "out",
    "results",
    "session-logs",
    "session-state",
    "temp",
}
EXCLUDED_FILE_NAMES = {
    "agents.override.md",
    "config.local.toml",
    "credentials.json",
    "project.local.yaml",
    "secrets.json",
}
EXCLUDED_SUFFIXES = {
    ".bak",
    ".backup",
    ".key",
    ".log",
    ".pem",
    ".pyc",
    ".swp",
    ".swo",
    ".tmp",
    ".temp",
}

GENERATED_DIRS = ("src", "design", "production")
GENERATED_FILES = (
    "AGENTS.md",
    "README.md",
    ".gitignore",
    "project.yaml",
    "START_HERE.md",
    "src/.gitkeep",
    "design/.gitkeep",
    "production/.gitkeep",
)


class WorkspaceError(ValueError):
    """A user-actionable workspace creation or verification error."""


@dataclass(frozen=True)
class WorkspacePlan:
    """Read-only description of one workspace creation."""

    source: Path
    target: Path
    copied: tuple[Path, ...]
    generated: tuple[Path, ...]
    excluded: tuple[str, ...]
    source_git: Mapping[str, object]

    @property
    def copied_count(self) -> int:
        return len(self.copied)

    @property
    def generated_count(self) -> int:
        return len(self.generated)


def _is_junction(path: Path) -> bool:
    """Return whether *path* is a Windows junction when supported."""

    checker = getattr(path, "is_junction", None)
    try:
        return bool(checker()) if checker is not None else False
    except OSError:
        return False


def _is_link(path: Path) -> bool:
    return path.is_symlink() or _is_junction(path)


def _lexists(path: Path) -> bool:
    # Path.exists() is false for a dangling symlink.  ``lexists`` lets us
    # reject that case before a target is ever created.
    return os.path.lexists(os.fspath(path))


def _norm(path: Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def _is_within(child: Path, parent: Path) -> bool:
    child_text, parent_text = _norm(child), _norm(parent)
    try:
        return os.path.commonpath((child_text, parent_text)) == parent_text
    except ValueError:
        # Different Windows drives cannot contain one another.
        return False


def _existing_components(path: Path) -> Iterable[Path]:
    """Yield existing components of an absolute path from root to leaf."""

    absolute = Path(os.path.abspath(os.fspath(path)))
    components: list[Path] = []
    current = absolute
    while not _lexists(current):
        parent = current.parent
        if parent == current:
            break
        current = parent
    while True:
        components.append(current)
        if current == current.parent:
            break
        current = current.parent
    for component in reversed(components):
        yield component


def _reject_linked_components(path: Path, label: str) -> None:
    for component in _existing_components(path):
        if _is_link(component):
            raise WorkspaceError(f"{label} traverses symlink/junction: {component}")


def _scan_source_links(source: Path) -> None:
    """Reject every source link, including links in excluded game folders."""

    if _is_link(source):
        raise WorkspaceError(f"source is a symlink/junction: {source}")
    for base, directories, files in os.walk(source, topdown=True, followlinks=False):
        base_path = Path(base)
        for name in (*directories, *files):
            candidate = base_path / name
            if _is_link(candidate):
                raise WorkspaceError(f"source contains symlink/junction: {candidate}")


def _source_git(source: Path) -> dict[str, object]:
    """Describe Git provenance without making Git a runtime dependency."""

    note = "descriptive provenance only; it is not proof of how files were produced"
    try:
        commit_result = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if commit_result.returncode != 0:
            raise OSError(commit_result.stderr.strip() or "git rev-parse failed")
        status_result = subprocess.run(
            ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=all"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if status_result.returncode != 0:
            raise OSError(status_result.stderr.strip() or "git status failed")
        return {
            "available": True,
            "commit": commit_result.stdout.strip(),
            "dirty": bool(status_result.stdout.strip()),
            "note": note,
        }
    except (OSError, subprocess.SubprocessError):
        return {
            "available": False,
            "commit": None,
            "dirty": None,
            "note": note + "; Git metadata unavailable in this environment",
        }


def _excluded_path(relative: Path) -> bool:
    parts = [part.casefold() for part in relative.parts]
    if any(part in EXCLUDED_DIR_NAMES for part in parts[:-1]):
        return True
    name = relative.name.casefold()
    return name in EXCLUDED_FILE_NAMES or name.startswith(".env") or relative.suffix.casefold() in EXCLUDED_SUFFIXES


def _collect_copy_files(source: Path) -> tuple[Path, ...]:
    files: list[Path] = []
    for root_name in COPY_DIRS:
        root = source / root_name
        if not root.is_dir():
            raise WorkspaceError(f"required framework directory is missing: {root_name}")
        for candidate in sorted(root.rglob("*")):
            relative = candidate.relative_to(source)
            if _excluded_path(relative):
                continue
            if candidate.is_file():
                files.append(relative)
    for name in COPY_ROOT_FILES:
        path = source / name
        if not path.exists():
            # Optional documentation files are copied when available; the
            # verifier-required files are a hard error in a malformed source.
            if name in REQUIRED_ROOT_FILES:
                raise WorkspaceError(f"required framework file is missing: {name}")
            continue
        if path.is_file() and not _excluded_path(Path(name)):
            files.append(Path(name))
    return tuple(sorted(set(files), key=lambda path: path.as_posix().casefold()))


def _read_framework_version(source: Path) -> tuple[str, str]:
    text = (source / "project.yaml").read_text(encoding="utf-8")
    version_match = re.search(r"^\s+version:\s*([^#\s]+)", text, re.MULTILINE)
    date_match = re.search(r"^\s+last_upgraded:\s*([^#\s]+)", text, re.MULTILINE)
    version = version_match.group(1).strip() if version_match else "1.1.0"
    upgraded = date_match.group(1).strip() if date_match else "unknown"
    return version, upgraded


def _engine_neutral_project_yaml(source: Path) -> str:
    version, upgraded = _read_framework_version(source)
    return (
        "# Codex Game Studios project configuration — clean engine-neutral template.\n"
        "# Run $codex-start before selecting an engine for this game.\n\n"
        "schema_version: 1\n\n"
        "framework:\n"
        f"  version: {version}\n"
        f"  last_upgraded: {upgraded}\n"
    )


def _clean_agents() -> str:
    return """# Codex Game Studios — clean game workspace

This directory is a new, independent game project workspace. Open this entire
root in a new Codex window; do not open an individual skill folder. No engine,
game concept, assets, session state or QA evidence is selected yet.

Project artifacts are English-first: design, architecture, stories, code
comments, tests, commit messages and technical records use English. Player-
facing text must be localization-ready; add other languages later through
`$codex-localize`. Chat explanations may follow the user's language.

## Runtime

- Skills: `.agents/skills/codex-*/SKILL.md`.
- Roles: `.codex/agents/*.toml`.
- References and templates: `docs/codex-studio/`.
- Skill behavior specifications: `Codex Skill Testing Framework/`.
- Configuration: `project.yaml` (engine-neutral until `$codex-setup-engine`).

## First pass

Start with `$codex-start`. Follow its decision checkpoints, then use
`$codex-setup-engine`, `$codex-brainstorm` (or the minimal brief path),
`$codex-create-stories`, `$codex-dev-story`, `$codex-story-done`, and
`$codex-smoke-check` as the project advances. These `$codex-*` selectors are
Codex prompts, not shell commands or background services.

`$codex-start` is the conversational entry point, not a prebuilt in-game main
program. It asks whether you have no idea, a vague idea, a clear concept or
existing work, then asks for the desired rigor and automation level. Use
`$codex-brainstorm` for the follow-up idea interview. An engine-specific main
scene or runtime controller is created later by the approved game stories.

## Evidence and boundaries

Run commands from this workspace root. Keep design under `design/`, source under
the engine's resolved code root, and evidence under `production/qa/evidence/`.
Record approvals, delegated roles, exact commands/exit codes, diffs and
`production/session-state/active.md` checkpoints when auditing a workflow pass.
Do not commit, push, create remotes or install global skills unless the user
explicitly requests it. Retain `LICENSE` and `NOTICE.md` in distributions.
The creator never initialises Git, installs global skills, creates remotes or
threads, and never deletes this workspace; use the generated manifest's verify
mode to inspect a fresh copy before starting work.
"""


def _clean_readme() -> str:
    return """# Codex Game Studios — New Game Workspace

This is a clean, standalone Codex game-development workspace. It contains the
Codex skills, roles, references, helpers, tests and behavior specifications;
it intentionally contains no demo game, build, screenshot, session state or
previous game design. English is the development and documentation baseline;
player-facing strings should be externalized for later localization.

Open the **entire workspace root** in a new Codex window, not a single skill
directory. Begin with `$codex-start`; then follow the engine/design/story loop
described in `START_HERE.md`. A `$codex-*` selector is a Codex prompt, not a
command that runs in a shell.
"""


def _clean_gitignore() -> str:
    return """# Codex local overrides and session state
AGENTS.override.md
project.local.yaml
.codex/config.local.toml
**/production/session-state/
**/production/session-logs/

# Build/editor/runtime output
.godot/
**/.godot/
build/
builds/
exports/
dist/
__pycache__/
*.pyc
*.log
*.tmp
*.swp
*.swo

# Local credentials
.env
.env.*.local
credentials.json
secrets.json
*.key
*.pem
"""


def _start_here() -> str:
    return """# Start Here — Codex Game Studios

provenance: required

## Language baseline

Use English for design documents, architecture decisions, stories, source
comments, tests, commit messages and technical records. Keep player-facing text
in localization-ready string resources; add translations later with
`$codex-localize`. Conversation explanations may follow the user's language.

## Open the correct scope

Open this **entire workspace root** in a new Codex window. Do not open only
`.agents/skills/` or one `SKILL.md`: skills share `AGENTS.md`, `project.yaml`,
`docs/`, `.codex/`, `tools/`, `tests/` and the behavior specifications.

## Auditable first game pass

1. `$codex-start` — answer the starting-point, rigor and automation checkpoints.
2. `$codex-setup-engine` — pin the engine and version only after its checkpoint.
3. `$codex-brainstorm` (or the minimal brief route).
4. `$codex-create-stories` — turn the approved design into buildable stories.
5. `$codex-dev-story <story>` — one story per pass; record delegated roles,
   files, tests, parse/build output and the checkpoint.
6. `$codex-story-done <story>` — verify every acceptance criterion and approve
   completion; it does not silently mark failed or untested work complete.
7. `$codex-smoke-check` — run the project's real test/build runner and retain
   the manual smoke evidence.

The selectors above are prompts consumed by Codex. They are not shell commands,
automatic hooks, background workers, global installations, Git operations or
thread creation. The single-pass dispatcher, when used, selects one next
action; the Codex host still executes that skill and invokes the dispatcher
again.

There is no prebuilt in-game "main program" at this point. `$codex-start` is
the Codex conversation entry point: it asks where you are starting and what
idea you have, then records rigor and automation choices. `$codex-brainstorm`
continues that interview. A runtime main scene/controller is produced later by
engine-specific stories after the design is approved.

## Evidence to retain

For a skill replay, save the original prompts and answers, approval checkpoints,
delegated role names and returns, exact commands with exit codes, `git diff`,
story status changes, and `production/session-state/active.md` snapshots. The
initial creator manifest records copied-file hashes and descriptive source Git
metadata (`commit`/`dirty`); that metadata is provenance context, not proof that
an AI or a skill produced any file.

`INPUTS.md` must hash the selected `.agents/skills/<name>/SKILL.md` and the
rules/references read for that pass. A transcript selector without that hash
is incomplete provenance.

Use `docs/codex-studio/clean-room-workflow.md` for the non-forging receipt
helper. `python tools/codex-studio/provenance_receipt.py init` creates only a
`NOT ASSESSED` shell; the Codex host must copy the real transcript, diff,
checkpoints and command log before a receipt can be reviewed.

## Clean-template boundary

`src/`, `design/` and `production/` start empty (with only `.gitkeep` files).
There is no `demo/`, `.git/`, `VERIFICATION.txt`, prior game brief, build,
session state or QA evidence. Run `python tools/create_game_workspace.py
--verify .` to verify the initial inventory. Verification never deletes user
files; keep the workspace or make a normal backup when you need rollback.
"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _record(path: Path, root: Path) -> dict[str, object]:
    return {"sha256": _sha256(path), "bytes": path.stat().st_size}


def _validate_paths(source: Path, target: Path) -> tuple[Path, Path]:
    source = Path(os.path.abspath(os.fspath(source)))
    target = Path(os.path.abspath(os.fspath(target)))
    if not source.is_dir():
        raise WorkspaceError(f"source directory does not exist: {source}")
    _reject_linked_components(source, "source")
    _reject_linked_components(target, "target")
    source_real, target_real = source.resolve(), target.resolve(strict=False)
    if _is_within(target_real, source_real):
        raise WorkspaceError("target must not be inside the source directory")
    if _is_within(source_real, target_real):
        raise WorkspaceError("target must not be the source directory or an ancestor of it")
    if _lexists(target):
        raise FileExistsError(f"target already exists; refusing to overwrite: {target}")
    _scan_source_links(source)
    return source, target


def build_plan(source: Path | str = SCRIPT_ROOT, target: Path | str = "game-workspace") -> WorkspacePlan:
    """Validate inputs and return a read-only plan; never creates *target*."""

    source_path, target_path = _validate_paths(Path(source), Path(target))
    copied = _collect_copy_files(source_path)
    source_git = _source_git(source_path)
    excluded = (".git", "demo", "design", "production", "src", "VERIFICATION.txt")
    return WorkspacePlan(
        source=source_path,
        target=target_path,
        copied=copied,
        generated=tuple(Path(item) for item in GENERATED_FILES),
        excluded=excluded,
        source_git=source_git,
    )


def _write_generated(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8", newline="\n")


def _manifest_for(plan: WorkspacePlan, target: Path, copied: Mapping[str, dict[str, object]], generated: Mapping[str, dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "kind": "codex-game-workspace",
        "source_root": str(plan.source),
        "source_git": dict(plan.source_git),
        "source_git_note": "Git commit/dirty values are descriptive provenance, not proof of authorship or skill execution.",
        "copied_files": dict(sorted(copied.items())),
        "generated_files": dict(sorted(generated.items())),
        "excluded_source": list(plan.excluded),
        "clean_template": {
            "empty_dirs": list(GENERATED_DIRS),
            "forbidden_initial_paths": [
                ".git",
                "demo",
                "VERIFICATION.txt",
                "production/session-state",
                "production/qa/evidence",
                "design/game-brief.md",
                "design/gdd",
            ],
        },
        "manifest": {
            "path": MANIFEST_NAME,
            "self_hash": "omitted to avoid a self-referential manifest",
        },
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "rollback": "No automatic deletion is performed. Keep this new directory or use --verify as an inventory check; make a normal backup before user work.",
    }


def create_workspace(source: Path | str, target: Path | str) -> tuple[Path, dict[str, object]]:
    """Materialise a validated plan and return ``(manifest_path, manifest)``."""

    plan = build_plan(source, target)
    target_path = plan.target
    target_path.mkdir(parents=True, exist_ok=False)
    copied_records: dict[str, dict[str, object]] = {}
    generated_records: dict[str, dict[str, object]] = {}
    try:
        for relative in plan.copied:
            source_path = plan.source / relative
            destination = target_path / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, destination)
            copied_records[relative.as_posix()] = _record(destination, target_path)

        generated_contents = {
            "AGENTS.md": _clean_agents(),
            "README.md": _clean_readme(),
            ".gitignore": _clean_gitignore(),
            "project.yaml": _engine_neutral_project_yaml(plan.source),
            "START_HERE.md": _start_here(),
            "src/.gitkeep": "",
            "design/.gitkeep": "",
            "production/.gitkeep": "",
        }
        for relative_name, contents in generated_contents.items():
            destination = target_path / relative_name
            _write_generated(destination, contents)
            generated_records[relative_name] = _record(destination, target_path)

        manifest = _manifest_for(plan, target_path, copied_records, generated_records)
        manifest_path = target_path / MANIFEST_NAME
        # The manifest is intentionally written after all records are collected
        # and is never included in either record map.
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return manifest_path, manifest
    except Exception:
        # The target was guaranteed absent.  Leave a partial directory for
        # inspection rather than deleting anything (including future user work).
        raise


def _safe_manifest_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix().startswith("./"):
        raise WorkspaceError(f"manifest contains unsafe relative path: {value}")
    return path


def verify_workspace(target: Path | str) -> tuple[bool, list[str]]:
    """Verify an existing workspace inventory without modifying or deleting it."""

    target_path = Path(os.path.abspath(os.fspath(target)))
    errors: list[str] = []
    try:
        _reject_linked_components(target_path, "target")
    except WorkspaceError as exc:
        return False, [str(exc)]
    manifest_path = target_path / MANIFEST_NAME
    if not target_path.is_dir():
        return False, [f"target directory does not exist: {target_path}"]
    if not manifest_path.is_file():
        return False, [f"manifest missing: {manifest_path}"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return False, [f"manifest unreadable: {exc}"]
    if manifest.get("manifest", {}).get("path") != MANIFEST_NAME:
        errors.append("manifest path metadata is invalid")
    copied = manifest.get("copied_files", {})
    generated = manifest.get("generated_files", {})
    if not isinstance(copied, dict) or not isinstance(generated, dict):
        errors.append("manifest file inventories must be mappings")
        copied, generated = {}, {}
    if MANIFEST_NAME in copied or MANIFEST_NAME in generated:
        errors.append("manifest must not hash itself")
    for category, records in (("copied", copied), ("generated", generated)):
        for relative, record in records.items():
            try:
                safe = _safe_manifest_path(relative)
                path = target_path / safe
                expected = record.get("sha256") if isinstance(record, dict) else None
                if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                    errors.append(f"{category} record has invalid hash: {relative}")
                elif _is_link(path):
                    errors.append(f"{category} file is a symlink/junction: {relative}")
                elif not path.is_file():
                    errors.append(f"{category} file missing: {relative}")
                elif _sha256(path) != expected:
                    errors.append(f"{category} hash mismatch: {relative}")
            except (OSError, WorkspaceError) as exc:
                errors.append(str(exc))

    for relative in GENERATED_DIRS:
        if not (target_path / relative).is_dir():
            errors.append(f"template directory missing: {relative}")
    forbidden = (
        ".git",
        "demo",
        "VERIFICATION.txt",
        "production/session-state",
        "production/qa/evidence",
        "design/game-brief.md",
        "design/gdd",
    )
    for relative in forbidden:
        if _lexists(target_path / relative):
            errors.append(f"forbidden initial artifact present: {relative}")
    project_text = (target_path / "project.yaml").read_text(encoding="utf-8") if (target_path / "project.yaml").is_file() else ""
    if re.search(r"^(?:engine|project|modes|docs|qa|team|testing|performance|features|naming|platform|accessibility|cadence|specialists):\s*$", project_text, re.MULTILINE):
        errors.append("project.yaml is not engine-neutral")
    start_text = (target_path / "START_HERE.md").read_text(encoding="utf-8") if (target_path / "START_HERE.md").is_file() else ""
    if "$codex-start" not in start_text or "entire workspace root" not in start_text:
        errors.append("START_HERE.md does not contain the whole-root onboarding instructions")
    return not errors, errors


def _print_plan(plan: WorkspacePlan) -> None:
    print("PLAN: clean Codex game workspace (dry-run; no files written)")
    print(f"Source: {plan.source}")
    print(f"Target: {plan.target}")
    print(f"Copy files: {plan.copied_count}")
    print(f"Generated files: {plan.generated_count} (including START_HERE.md and engine-neutral project.yaml)")
    print("Excluded source: " + ", ".join(plan.excluded))
    git = plan.source_git
    if git.get("available"):
        print(f"Source Git: commit={git.get('commit')} dirty={str(git.get('dirty')).lower()} (descriptive only)")
    else:
        print("Source Git: unavailable (descriptive provenance will record this; not a failure)")
    print("Next: rerun with --create to materialize the new directory")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", type=Path, help="new workspace directory (or an existing one with --verify)")
    parser.add_argument("--output", dest="output", type=Path, help="named alias for the new workspace directory")
    parser.add_argument("--source", type=Path, default=SCRIPT_ROOT, help="framework source root (default: this repository)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--create", action="store_true", help="create the new workspace; default is a dry-run plan")
    mode.add_argument("--verify", action="store_true", help="verify an existing workspace manifest without writing")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.target is not None and args.output is not None:
        print("ERROR: provide the workspace path either positionally or with --output, not both", file=sys.stderr)
        return 2
    target = args.output or args.target
    if target is None:
        print("ERROR: a workspace path is required", file=sys.stderr)
        return 2
    try:
        if args.verify:
            ok, errors = verify_workspace(target)
            if ok:
                print(f"VERIFY: PASS — manifest hashes and clean-template inventory match {Path(target).resolve()}")
                return 0
            print("VERIFY: FAIL", file=sys.stderr)
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        plan = build_plan(args.source, target)
        if not args.create:
            _print_plan(plan)
            return 0
        manifest_path, manifest = create_workspace(args.source, target)
        print(f"CREATED: {Path(target).resolve()}")
        print(f"Manifest: {manifest_path.resolve()}")
        print(f"Copied files: {len(manifest['copied_files'])}")
        print(f"Generated files: {len(manifest['generated_files'])}")
        print("No Git repository, commit, global installation or Codex thread was created.")
        print(f"Verify: python {Path(__file__).resolve()} --verify {Path(target).resolve()}")
        return 0
    except FileExistsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (OSError, WorkspaceError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
