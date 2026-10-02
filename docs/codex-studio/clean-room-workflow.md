# Clean-room game workspace and Skill replay

The framework repository and a game under development are different workspaces.
Keep them in different Codex windows. The framework window changes skills,
roles, references and validation; the game window consumes a released copy of
those files and changes only the new game.

## Language baseline

Use English for game design, architecture, stories, source comments, tests,
commit messages and technical records. Keep player-facing strings
localization-ready from the first implementation, then add translations in a
later `$codex-localize` pass. Chat explanations can follow the user's language;
the artifact baseline remains English.

## Create a clean workspace

From this repository root, preview the files that will be copied:

```powershell
python tools/create_game_workspace.py --output "C:\Games\MyGame"
```

The command is a dry run unless `--create` is supplied. Create only a new,
empty destination:

```powershell
python tools/create_game_workspace.py `
  --output "C:\Games\MyGame" `
  --create
```

The creator copies the Codex skills, roles, references, testing framework,
helpers, project rules and legal files. It deliberately does **not** copy
`demo/`, `production/qa/`, `production/session-state/`, `dist/`, engine builds,
the framework's `VERIFICATION.txt`, or Git metadata. It writes
`START_HERE.md` and a source/hash manifest so the new window can identify the
framework snapshot without mistaking that manifest for proof that a Skill ran.
The creator never initializes Git, configures a remote, installs a global skill,
starts a Codex thread, or deletes a destination.

After creation, open the destination itself in a **new Codex window**. Do not
open only `.agents/skills/` and do not continue the framework-maintenance chat.
Read that workspace's `AGENTS.md` and `START_HERE.md` first.

## Required new-window sequence

Use explicit Skill selectors so the invocation is visible in the new window:

```text
$codex-start
$codex-setup-engine
$codex-brainstorm
$codex-create-architecture
$codex-map-systems
$codex-create-epics
$codex-create-stories
$codex-dev-story
$codex-story-done
$codex-smoke-check
```

The exact branches may skip a design step only when the Skill explains why and
records `NOT ASSESSED`; skipping is not a pass. `$codex-run` may coordinate one
next action, but it is single-pass and never invokes selectors as shell
commands. Run it again only after the selected Skill has returned and its
evidence has been reviewed.

## Provenance required for a claim that Skills drove the work

The game output and a Skill claim are separate facts. For every implementation
pass, retain a directory under `production/provenance/<run-id>/` containing:

```text
TRANSCRIPT.md       the new-window user prompt, explicit $codex-* selector,
                    approvals, delegation results and the Skill's final report
INPUTS.md           workspace base commit/hash, input artifact hashes,
                    skill/rule paths and their SHA-256 values
CHANGES.patch       git diff (or an equivalent before/after inventory)
VERIFICATION.md     exact commands, exit codes, literal summaries and paths
                    to retained artifacts
checkpoint-before.md / checkpoint-after.md
```

`TRANSCRIPT.md` must be copied from the host conversation or its exported
record; a hand-written summary is not a substitute. A receipt may describe a
Skill, but it cannot prove invocation without the selector and transcript.
Mark the run `VERIFIED` only when the transcript, hashes, diff, checkpoint and
observed commands agree. Otherwise use `PARTIAL` or `NOT ASSESSED`. Never turn
the existence of a brief, story or source file into evidence that its authoring
Skill ran. Start from [`templates/skill-receipt.md`](templates/skill-receipt.md)
when creating the receipt.

### Optional receipt helper (non-forging)

The repository includes a local checker for the evidence boundary:

```powershell
python tools/codex-studio/provenance_receipt.py init `
  --workspace . --run-id 2026-01-01-story-01 --selector '$codex-dev-story'
python tools/codex-studio/provenance_receipt.py capture-inputs `
  production/provenance/2026-01-01-story-01 `
  --file project.yaml --file .agents/skills/codex-dev-story/SKILL.md `
  --file docs/codex-studio/runtime.md
python tools/codex-studio/provenance_receipt.py verify `
  production/provenance/2026-01-01-story-01
```

`init` creates only `receipt.json` and a `NOT ASSESSED` Markdown shell. It does
not create `TRANSCRIPT.md`, a patch, checkpoints or command output. The host
must copy the actual Codex conversation export into `TRANSCRIPT.md` and declare
`TRANSCRIPT_SOURCE: CODEX_HOST_EXPORT`; a hand-written summary is rejected.
`capture-inputs` writes SHA-256 lines to `INPUTS.md` only and cannot upgrade a
receipt. `verify` exits non-zero unless all six evidence files are present and
the receipt is explicitly marked `VERIFIED`; missing or synthetic evidence is
reported as `NOT ASSESSED`, never silently passed.

## Negative replay before trusting the workflow

At least once in a fresh workspace, test the stops as well as the happy path:

1. Mark an ADR dependency `Proposed` or remove the required engine input. The
   selected Skill must report `BLOCKED`/`NOT ASSESSED` and write no source.
2. Make the declared test runner exit non-zero or omit its machine-readable
   summary. `$codex-smoke-check` must report `FAIL`/`NOT ASSESSED`, never PASS.
3. Introduce a story/sprint status conflict. The dispatcher must report
   `inconsistent` and select no implementation Skill.

Restore each mutation from a recorded copy, then rerun the positive path. Keep
the negative receipts beside the positive receipt.

## What this proves

- The creator proves isolation and a reproducible framework snapshot.
- The Skill transcript and receipts prove which Codex workflow was actually
  invoked and what it changed.
- Engine commands, tests and screenshots prove the game artifact's behavior.

None of these substitutes for the others. A passing Godot build alone is not a
Skill provenance result; a green structural verifier alone is not a game test.
