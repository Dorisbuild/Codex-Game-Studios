#!/usr/bin/env python3
"""Deterministic, single-pass workflow dispatcher for Codex Game Studios.

The Codex host selects and executes skills; this module does not pretend that a
Python process can invoke ``$codex-*`` selectors.  It reads the project state,
returns one next action, and can atomically persist the bounded checkpoint when
the caller explicitly asks it to do so.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable


SCHEMA_VERSION = 1
STATUS_RE = re.compile(
    r"^\s*(?:>\s*)?(?:[-*]\s*)?(?:\*\*)?Status(?:\*\*)?\s*:\s*(?P<value>.+?)\s*$",
    re.IGNORECASE,
)
TITLE_RE = re.compile(r"^\s*#\s+Story\s+(?:\[[^]]+\]\s*)?(?P<title>.+?)\s*$", re.IGNORECASE)
CHECKPOINT_RE = re.compile(
    r"(?P<open>^<!-- CHECKPOINT -->\s*$)(?P<body>.*?)(?P<close>^<!-- /CHECKPOINT -->\s*$)",
    re.MULTILINE | re.DOTALL,
)
CHECKPOINT_FIELD_RE = re.compile(r"^\*\*(?P<key>[^*]+)\*\*:\s*(?P<value>.*)$")


def project_root(value: str | None = None) -> Path:
    """Resolve a project root without relying on the caller's current folder."""

    if value:
        root = Path(value).expanduser().resolve()
    else:
        root = Path(__file__).resolve().parents[2]
    if not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    return root


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _canonical_status(value: str | None) -> str:
    if not value:
        return "no_status"
    # Sprint status uses machine-friendly separators (``in-progress`` and
    # ``ready-for-dev``), while story files use the human-facing forms
    # (``In Progress`` and ``Ready``).  Normalize the separators before
    # comparing the two sources, but retain a distinct ``not_started`` state:
    # sprint ``backlog`` must not silently become implementation-ready.
    normalized = re.sub(r"[*`]+", "", value).strip().lower()
    normalized = re.sub(r"[-_]+", " ", normalized)
    if re.match(r"^(complete|done)(?:\b|[.!])", normalized):
        return "complete"
    if re.match(r"^(?:in\s+)?review(?:\b|[.!])", normalized):
        return "in_review"
    if re.match(r"^in\s+progress(?:\b|[.!])", normalized):
        return "in_progress"
    if re.match(r"^ready(?:\s+for\s+dev)?(?:\b|[.!])", normalized):
        return "ready"
    if re.match(r"^(?:not\s+started|backlog)(?:\b|[.!])", normalized):
        return "not_started"
    if re.match(r"^blocked(?:\b|[.!])", normalized):
        return "blocked"
    return "other"


@dataclass(frozen=True)
class Story:
    path: str
    title: str
    status: str
    raw_status: str


@dataclass
class Plan:
    schema_version: int
    generated_at: str
    root: str
    mode: str
    state: str
    action: str
    skill: str | None
    story: str | None
    reason: str
    counts: dict[str, int]
    warnings: list[str] = field(default_factory=list)
    consistency_errors: list[str] = field(default_factory=list)

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


def _engine_name(root: Path) -> str | None:
    text = _read(root / "project.yaml")
    if not text:
        return None

    def scalar(raw: str) -> str:
        """Read one simple YAML scalar without requiring a YAML dependency."""

        raw = raw.strip()
        quote: str | None = None
        for index, char in enumerate(raw):
            if quote:
                if char == quote and (quote == "'" or index == 0 or raw[index - 1] != "\\"):
                    quote = None
                continue
            if char in {"'", '"'}:
                quote = char
            elif char == "#" and (index == 0 or raw[index - 1].isspace()):
                raw = raw[:index].rstrip()
                break
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"'", '"'}:
            raw = raw[1:-1]
        return raw.strip()

    def indent_width(raw: str) -> int:
        # YAML forbids tabs for indentation, but counting one keeps malformed
        # input from making us inspect an unrelated sibling key.
        return len(raw.expandtabs(2))

    lines = text.splitlines()
    for index, line in enumerate(lines):
        section = re.match(r"^(?P<indent>[ \t]*)engine\s*:\s*(?P<value>.*)$", line, re.IGNORECASE)
        if not section or indent_width(section.group("indent")) != 0:
            continue

        inline = scalar(section.group("value"))
        if inline.startswith("{") and inline.endswith("}"):
            inline = inline[1:-1]
            match = re.search(r"(?:^|,)\s*name\s*:\s*([^,}]+)", inline, re.IGNORECASE)
            if match:
                value = scalar(match.group(1))
                if value and value.lower() not in {"null", "none", "to be configured"}:
                    return value
            continue

        base_indent = indent_width(section.group("indent"))
        child_indent_level: int | None = None
        for child in lines[index + 1:]:
            if not child.strip() or child.lstrip().startswith("#"):
                continue
            leading = child[: len(child) - len(child.lstrip(" \t"))]
            child_indent = indent_width(leading)
            if child_indent <= base_indent:
                break
            if child_indent_level is None:
                child_indent_level = child_indent
            if child_indent != child_indent_level:
                continue
            match = re.match(r"^[ \t]+name\s*:\s*(?P<value>.*)$", child, re.IGNORECASE)
            if not match:
                continue
            value = scalar(match.group("value"))
            if value and value.lower() not in {"null", "none", "to be configured"}:
                return value
            return None
    return None


def _story_from(path: Path, root: Path) -> Story:
    text = _read(path)
    title = path.stem
    raw_status = ""
    for line in text.splitlines():
        title_match = TITLE_RE.match(line)
        if title_match:
            title = title_match.group("title").strip()
        status_match = STATUS_RE.match(line)
        if status_match:
            raw_status = status_match.group("value").strip()
            break
    return Story(
        path=path.relative_to(root).as_posix(),
        title=title,
        status=_canonical_status(raw_status),
        raw_status=raw_status,
    )


def discover_stories(root: Path) -> list[Story]:
    base = root / "production" / "epics"
    if not base.is_dir():
        return []
    return sorted(
        (_story_from(path, root) for path in base.rglob("story-*.md") if path.is_file()),
        key=lambda story: story.path.casefold(),
    )


def _counts(stories: Iterable[Story]) -> dict[str, int]:
    values = list(stories)
    counts = {key: 0 for key in ("total", "complete", "in_review", "in_progress", "ready", "not_started", "blocked", "other", "no_status")}
    counts["total"] = len(values)
    for story in values:
        counts[story.status] = counts.get(story.status, 0) + 1
    return counts


def _read_checkpoint(root: Path) -> dict[str, str]:
    text = _read(root / "production" / "session-state" / "active.md")
    match = CHECKPOINT_RE.search(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        field_match = CHECKPOINT_FIELD_RE.match(line.strip())
        if field_match:
            fields[field_match.group("key").strip().lower()] = field_match.group("value").strip()
    return fields


def _sprint_records(root: Path) -> dict[str, str]:
    """Read the small status subset used by the studio without requiring PyYAML.

    Supported records are ``path: ...`` followed by ``status: ...`` in a list,
    which is the format emitted by the sprint skills.  If the file is richer or
    malformed, no record is guessed; validation reports that it was skipped.
    """

    path = root / "production" / "sprint-status.yaml"
    lines = _read(path).splitlines()
    records: dict[str, str] = {}
    current_path: str | None = None
    for line in lines:
        path_match = re.match(r"^\s*(?:-\s*)?(?:path|story_path|file):\s*[\"']?([^\"'#]+?)[\"']?\s*$", line, re.IGNORECASE)
        if path_match:
            current_path = _normalize_story_path(path_match.group(1))
            continue
        status_match = re.match(r"^\s*status:\s*[\"']?([^\"'#]+?)[\"']?\s*$", line, re.IGNORECASE)
        if status_match and current_path:
            records[current_path] = status_match.group(1).strip()
            current_path = None
    return records


def _normalize_story_path(value: str) -> str:
    """Normalize the relative path spellings used by YAML and story files."""

    path = value.strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def _matching_sprint_status(story: Story, records: dict[str, str]) -> str | None:
    return records.get(_normalize_story_path(story.path))


def consistency_errors(root: Path, stories: list[Story]) -> list[str]:
    records = _sprint_records(root)
    if not records:
        return []
    errors: list[str] = []
    for story in stories:
        sprint_status = _matching_sprint_status(story, records)
        if sprint_status is None:
            continue
        story_status = story.status
        sprint = _canonical_status(sprint_status)
        # The story file and sprint-status.yaml are two views of the same
        # state.  Require semantic equality in both directions; one-way checks
        # let a stale sprint entry silently route a story into implementation.
        if story_status != sprint:
            errors.append(
                f"{story.path}: story is {story.raw_status or story_status} "
                f"but sprint status is {sprint_status}"
            )
    return errors


def build_plan(root: Path, *, mode: str = "once") -> Plan:
    stories = discover_stories(root)
    counts = _counts(stories)
    warnings: list[str] = []
    errors = consistency_errors(root, stories)
    checkpoint = _read_checkpoint(root)

    if errors:
        return Plan(
            SCHEMA_VERSION, _now(), str(root), mode, "inconsistent", "pause",
            None, None,
            "Project status sources disagree; reconcile the story file and sprint-status.yaml before continuing.",
            counts, warnings, errors,
        )

    if _engine_name(root) is None:
        return Plan(
            SCHEMA_VERSION, _now(), str(root), mode, "needs_engine",
            "configure the engine and pin its version", "$codex-setup-engine", None,
            "project.yaml does not contain a configured engine.name", counts, warnings,
        )

    if not (root / "design" / "game-brief.md").is_file() and not (root / "design" / "gdd" / "game-concept.md").is_file():
        return Plan(
            SCHEMA_VERSION, _now(), str(root), mode, "needs_brief",
            "write or update the game brief", "$codex-brainstorm", None,
            "no minimal-path game brief or full concept document was found", counts, warnings,
        )

    if not stories:
        return Plan(
            SCHEMA_VERSION, _now(), str(root), mode, "needs_stories",
            "create the first implementation stories", "$codex-create-stories", None,
            "no production/epics/**/story-*.md files were found", counts, warnings,
        )

    for wanted, state, skill, action, reason in (
        ("in_review", "story_review", "$codex-story-done", "close the reviewed story", "an existing story is waiting for completion review"),
        ("in_progress", "story_in_progress", "$codex-dev-story", "resume the active story", "an existing story is already in progress"),
        ("ready", "story_ready", "$codex-dev-story", "implement the next ready story", "the next story is ready in build order"),
    ):
        candidate = next((story for story in stories if story.status == wanted), None)
        if candidate:
            return Plan(
                SCHEMA_VERSION, _now(), str(root), mode, state,
                f"{action}: {candidate.path}", f"{skill} {candidate.path}", candidate.path,
                f"{reason}: {candidate.title}", counts, warnings, errors,
            )

    blocked = next((story for story in stories if story.status == "blocked"), None)
    if blocked:
        return Plan(
            SCHEMA_VERSION, _now(), str(root), mode, "blocked", "pause", None, blocked.path,
            f"{blocked.path} is blocked; clear its recorded blocker before another implementation step",
            counts, warnings, errors,
        )

    # ``Not Started``/sprint ``backlog`` is intentionally not an
    # implementation route.  It is a deferred item, so readiness must classify
    # or promote it explicitly before $codex-dev-story can run.
    other = next((story for story in stories if story.status in {"other", "no_status", "not_started"}), None)
    if other:
        return Plan(
            SCHEMA_VERSION, _now(), str(root), mode, "needs_status", "classify the story status",
            "$codex-story-readiness", other.path,
            f"{other.path} has no routable status ({other.raw_status or 'missing'})",
            counts, warnings, errors,
        )

    next_step = "$codex-smoke-check" if counts["complete"] == counts["total"] else "$codex-help"
    warning = "All discovered stories are complete; this is a single-pass gate, not an unattended loop."
    warnings.append(warning)
    return Plan(
        SCHEMA_VERSION, _now(), str(root), mode, "all_stories_complete", "run the next quality gate",
        next_step, None,
        "every discovered story is Complete or Done",
        counts, warnings, errors,
    )


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _branch(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"],
            capture_output=True, text=True, encoding="utf-8", timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return result.stdout.strip() or "detached"


def _lock(path: Path, timeout: float = 0.0):
    """Create an explicit lock file; fail rather than overwrite another writer."""

    deadline = time.monotonic() + max(timeout, 0.0)
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"pid={os.getpid()}\n".encode("ascii", "replace"))
            os.close(fd)
            return
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise RuntimeError(f"checkpoint is locked: {path}")
            time.sleep(0.05)


def _unlock(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def write_checkpoint(root: Path, plan: Plan, *, files: str = "none", timeout: float = 0.0) -> Path:
    """Persist one bounded checkpoint with an atomic replace and explicit lock."""

    directory = root / "production" / "session-state"
    path = directory / "active.md"
    lock_path = directory / "active.md.lock"
    template_path = root / "docs" / "codex-studio" / "templates" / "session-state.md"
    # Create the directory before locking so a fresh project can be resumed,
    # then hold the lock across the read/modify/write sequence.  Reading before
    # acquiring it allows two callers to both load the same old checkpoint and
    # lets the later writer silently discard the first one's update.
    directory.mkdir(parents=True, exist_ok=True)
    _lock(lock_path, timeout)
    try:
        text = _read(path) or _read(template_path)
        if not text:
            text = "# Active Session State\n\n<!-- CHECKPOINT -->\n<!-- /CHECKPOINT -->\n"
        body = "\n".join((
            f"**Updated:** {date.today().isoformat()}",
            f"**Branch:** `{_branch(root)}`",
            f"**Current task:** {plan.action}",
            f"**Next step:** {plan.skill or plan.action}",
            f"**Blocked on:** {plan.reason if plan.state in {'blocked', 'inconsistent'} else 'nothing'}",
            f"**Files in progress:** {files}",
            f"**Open questions:** {'; '.join(plan.consistency_errors) if plan.consistency_errors else 'none'}",
        ))
        replacement = f"<!-- CHECKPOINT -->\n{body}\n<!-- /CHECKPOINT -->"
        if CHECKPOINT_RE.search(text):
            # A callable replacement keeps backslashes in user/file paths
            # literal; string replacement would treat ``\\1`` as a group ref.
            text = CHECKPOINT_RE.sub(lambda _match: replacement, text, count=1)
        else:
            text = text.rstrip() + "\n\n" + replacement + "\n"
        _atomic_write(path, text)
    finally:
        _unlock(lock_path)
    return path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Codex game project root (default: repository root)")
    parser.add_argument("--once", action="store_true", help="emit one deterministic next-action plan")
    parser.add_argument("--validate-state", action="store_true", help="return non-zero when status sources disagree")
    parser.add_argument("--write-checkpoint", action="store_true", help="atomically write the plan to active.md")
    parser.add_argument("--files", default="none", help="files to record in an explicitly requested checkpoint")
    parser.add_argument("--wait-lock", type=float, default=0.0, help="seconds to wait for active.md.lock")
    parser.add_argument("--text", action="store_true", help="print a concise human-readable plan instead of JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not (args.once or args.validate_state or args.write_checkpoint):
        args.once = True
    if args.write_checkpoint and not args.once:
        args.once = True
    try:
        root = project_root(args.root)
        plan = build_plan(root)
        if args.write_checkpoint:
            written = write_checkpoint(root, plan, files=args.files, timeout=args.wait_lock)
        else:
            written = None
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"codex-run: {exc}", file=sys.stderr)
        return 2

    if args.text:
        print(f"state: {plan.state}")
        print(f"skill: {plan.skill or '(pause)'}")
        print(f"story: {plan.story or '(none)'}")
        print(f"action: {plan.action}")
        print(f"reason: {plan.reason}")
        if plan.consistency_errors:
            print("consistency:")
            for error in plan.consistency_errors:
                print(f"  - {error}")
        if written:
            print(f"checkpoint: {written}")
    else:
        payload = plan.as_json()
        if written:
            payload["checkpoint"] = str(written)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.validate_state and plan.consistency_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
