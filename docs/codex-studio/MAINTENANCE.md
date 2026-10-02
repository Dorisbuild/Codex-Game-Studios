# Maintenance, export and recovery

## Validate

Use Python 3.11+ with `requirements-dev.txt` installed:

```text
python tools/verify_codex_studio.py
python -m unittest discover -s tests -p "test_*.py" -v
```

The structural verifier includes all skill/agent catalog entries and requires
every behavioral spec to exist. It is not a substitute for running those
workflows against real game requirements and builds.

The provenance helper is deliberately non-forging. Use it from a clean game
workspace to create a `NOT ASSESSED` shell and hash inputs, then copy the real
Codex-host transcript and observed artifacts before verification:

```text
python tools/codex-studio/provenance_receipt.py init --workspace . --run-id 2026-01-01-story-01 --selector '$codex-dev-story'
python tools/codex-studio/provenance_receipt.py capture-inputs production/provenance/2026-01-01-story-01 --file project.yaml --file .agents/skills/codex-dev-story/SKILL.md
python tools/codex-studio/provenance_receipt.py verify production/provenance/2026-01-01-story-01
```

The helper never creates a transcript, diff, checkpoint or test result and never
changes a receipt to `VERIFIED`.

## Export an independent project

```text
python tools/package_studio.py --output dist/Codex-Game-Studios.zip
```

The ZIP includes the skills, agents, shared references, tests and project tools;
it excludes Git metadata, local settings, secrets, runtime logs, backups and
retired integrations. A SHA-256 sidecar identifies the archive. Use `--force`
only to replace a previously generated archive. Extract into a new directory,
run validation there, then optionally initialize your own Git repository.

No publishing URL is invented. The independent checkout has no configured
remote, and package output contains no Git metadata or remote configuration.

## Start a separate game workspace

Use `python tools/create_game_workspace.py --output DEST --create` for a new
game instead of working in the framework checkout. The tool
is non-destructive: `DEST` must be new and empty, and it never removes an
existing directory. Open `DEST` in a new Codex window and follow
`docs/codex-studio/clean-room-workflow.md`; the source/hash manifest is a
snapshot description, not evidence that a Skill was invoked.

## Recover an earlier local snapshot

The independent repository keeps no migration snapshot or retired runtime in
its tree. If a recovery is needed, use the external bundle or archive path
recorded in `VERIFICATION.txt` and always restore to a **new** directory. For a
file snapshot produced by this tool, the command is:

```text
python tools/restore_snapshot.py SNAPSHOT.zip NEW_DIRECTORY --manifest SNAPSHOT.sha256.json
```

The command validates archive member paths and file hashes before extracting,
then re-reads the restored files. It rejects existing destinations and does not
rewrite the original workspace or Git index. Inspect the separate restored copy
before deciding whether to replace any live files. Snapshots and retired
runtime files are deliberately not shipped in independent packages.

## Review changes

The working tree is left uncommitted unless requested. Ordinary Git diff shows
tracked changes; untracked additions also need review. The local migration
evidence includes a complete patch built with a temporary Git index and a
hash-based before/after inventory, without staging the user's actual index.
