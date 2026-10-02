# Codex Game Studios

This is a standalone, community-maintained Codex game-development skill and
role library. Project artifacts are English-first: design, architecture,
stories, code comments, tests, commit messages, and technical records use
English. Use the user's language for explanations when requested. No engine is
selected in this template.

## Runtime

- Skills: `.agents/skills/codex-*/SKILL.md` (folder and name must match).
- Roles: `.codex/agents/*.toml`; inherit the current model by default.
- References/templates: `docs/codex-studio/`.
- Game configuration: `project.yaml`, with supported `project.local.yaml` overrides.
- Explicit helpers: `tools/codex-studio/config/` and `tools/codex-studio/scripts/`.
- Read `docs/codex-studio/runtime.md` for skill arguments, checkpoints, tools,
  and delegation. A checkpoint is ordinary conversation, not a tool name.

Open the whole project. Skills rely on its shared resources and are not
isolated, single-folder installs.

For a new game, do not reuse this framework-maintenance checkout. Run
`python tools/create_game_workspace.py --output DEST --create`, then open DEST
in a new Codex window and read `START_HERE.md`. Use
`docs/codex-studio/clean-room-workflow.md` for the isolated Skill sequence and
provenance evidence. The creator does not initialize Git, install global
skills, or start threads. The non-forging receipt helper is
`tools/codex-studio/provenance_receipt.py`; it never fabricates a host
transcript or upgrades an incomplete run to `VERIFIED`.

## Work boundaries

The current user request authorizes work within its scope. Ask a concise
question when a consequential design choice, expanded scope, file deletion,
external publication, or unapproved irreversible action needs a decision.
Honor collaborative/guided/autonomous design checkpoints; they never override
host permissions or expand the request. Do not re-ask for approved scoped work.

Read the relevant brief, GDD, ADR, story, and checkpoint before game work.
Read the matching reference in `docs/codex-studio/rules/` for gameplay, engine,
networking, UI, data, narrative, shaders, tests, prototypes, or skill edits.
These are references, not auto-loaded rules or enforcement hooks.

Use parallel subagents for independent investigations/reviews when useful.
Give each a narrow brief, inputs, permitted outputs, and return contract.
Avoid concurrent edits to the same file. Report required independent reviews
as NOT ASSESSED if no separate reviewer ran; self-review is not a second agent.
Role definitions do not start 49 agents automatically.

## Game workflow

Start with `$codex-start`, then `$codex-setup-engine` when an engine is needed.
Use minimal rigor for prototypes unless the user's scope warrants more.
Resolve effective settings rather than assuming their defaults:

```bash
bash tools/codex-studio/config/yaml-helper.sh resolve_config --keys workflow,review_mode,automation
```

Pin engine/version and consult matching `docs/engine-reference/` files before
engine-dependent code. Keep values data-driven, separate UI from authoritative
state, and use server authority for multiplayer. Store design under `design/`,
ADRs under `docs/architecture/`, and evidence under `production/qa/evidence/`.

Skills explicitly read/write `production/session-state/active.md` as needed.
No installed hook automatically saves, restores, logs, or validates this project.

## Verification and maintenance

Preserve existing work; back up before bulk migrations. Run relevant checks
and report exact commands, results, and gaps. Parsing does not prove visuals.

```text
python tools/verify_codex_studio.py
python -m unittest discover -s tests -p "test_*.py" -v
python -m unittest tests.test_provenance_receipt -v
```

For one deterministic next-action plan, run the project dispatcher:

```text
python tools/codex-studio/orchestrate.py --once --text
python tools/codex-studio/orchestrate.py --once --write-checkpoint --text
```

The dispatcher is deliberately single-pass: it can select a Codex skill and
atomically record a checkpoint, but the host must execute that skill and invoke
the dispatcher again. It is not a background worker or an automatic skill API.

Behavioral specs live in `Codex Skill Testing Framework/`; use
`$codex-skill-test` for evaluation. Never mark unexecuted workflow/game tests
as passed. Do not commit, push, create remotes, or install global skills unless
requested. Retain `LICENSE` and `NOTICE.md` in distributions. Packaging and
recovery are documented in `docs/codex-studio/MAINTENANCE.md`.
