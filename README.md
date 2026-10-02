# Codex Game Studios

**An independent Codex skill and role library for AI-assisted game
development.**

This repository contains 75 `codex-*` skills, 49 specialist roles, shared
design and architecture references, production templates, testing
specifications, and explicit tooling for reproducible workflows. It is a
framework, not a game engine and not a game project: no engine, game concept,
runtime build, or historical demo is included.

## Quick start

1. Open the repository root in Codex.
2. Run `$codex-start`, or say “Help me start a game project with Codex Game
   Studios.”
3. Run `$codex-setup-engine` to choose and pin the engine, language, and
   version; this framework does not preselect an engine.
4. Run `$codex-brainstorm` to shape the game idea, then continue through the
   design, story, implementation, and QA workflow.

`$codex-start` is the conversational Codex entry point, not an automatically
generated in-game main program. It asks whether you have no idea, a vague idea,
a clear concept, or existing work, then asks for the desired rigor and
automation level. `$codex-brainstorm` continues the idea interview. An engine
main scene or runtime controller is created later by approved development
stories.

### Create an isolated workspace for a new game (recommended)

Do not develop a game inside this framework-maintenance checkout. Create a
clean, independent workspace first:

```powershell
python tools/create_game_workspace.py --output "C:\Games\MyGame"
python tools/create_game_workspace.py --output "C:\Games\MyGame" --create
```

Open the entire `C:\Games\MyGame` directory in a **new Codex window**, read
`START_HERE.md`, and explicitly run `$codex-start`. The creator does not copy
old demos, build output, session state, or Git history; it does not install
global skills, create remotes, or start threads. See
[`docs/codex-studio/clean-room-workflow.md`](docs/codex-studio/clean-room-workflow.md)
for the complete Skill sequence, provenance records, and negative replay.

Only a new-window transcript containing selectors, approvals, delegation,
input hashes, diffs, checkpoints, and command results can establish that a
game was driven by the Skill workflow. A finished build or screenshot alone is
not Skill provenance.

| Purpose | Skill |
| --- | --- |
| Onboarding / next action | `$codex-start` / `$codex-help` |
| Engine and project setup | `$codex-setup-engine` / `$codex-settings` |
| Concept and lightweight design | `$codex-brainstorm` / `$codex-quick-design` |
| Systems and architecture | `$codex-design-system` / `$codex-create-architecture` |
| Stories, implementation, completion | `$codex-create-stories` / `$codex-dev-story` / `$codex-story-done` |
| Code review and smoke gate | `$codex-code-review` / `$codex-smoke-check` |
| Localization | `$codex-localize` |
| Framework validation | `$codex-skill-test static all` |

See the [skill catalog](docs/codex-studio/SKILLS.md) for the full list and
legacy-name mapping. Skill folders, frontmatter names, and cross-references use
the `codex-` prefix; `agents/openai.yaml` provides Codex-facing display names.

## Native Codex layout

```text
AGENTS.md                         Project rules and boundaries
.agents/skills/codex-*/SKILL.md   75 skill entry points and references
.codex/agents/*.toml              49 role definitions
.codex/config.toml                Project configuration; does not change personal permissions
codex-studio.toml                 Independent project identity and namespace
docs/codex-studio/                Workflow, runtime, and design references
tools/codex-studio/config/        Explicit configuration readers
tools/codex-studio/scripts/       Explicit validation helpers
Codex Skill Testing Framework/    Skill and role behavior specifications
project.yaml                      Engine-neutral project configuration
production/provenance/            Skill transcript, hashes, diffs, and checkpoints
```

- Skills read arguments from the current message; they do not depend on foreign
  command macros or prompt injection.
- Decisions and write approvals happen through ordinary Codex conversation.
- Delegated roles use Codex's actual delegation capability and inherit the
  current model and reasoning settings by default.
- The project does not install lifecycle hooks or treat reference documents as
  a permission-enforcement layer.
- Skills share the complete workspace; do not copy only one skill directory.

See [runtime conventions](docs/codex-studio/runtime.md). If the host still
shows an old skill name, reopen the project or restart Codex.

## Verification and packaging

Development validation requires Python **3.11+**, Git, Bash (Git for Windows
works on Windows), and PyYAML. An engine is needed only when a game workspace is
actually configured, built, or tested.

```powershell
python -m pip install -r requirements-dev.txt
python tools/verify_codex_studio.py
python -m unittest discover -s tests -p "test_*.py" -v
python -m unittest tests.test_provenance_receipt -v
python tools/codex-studio/orchestrate.py --once --text
python tools/package_studio.py --output dist/Codex-Game-Studios.zip
```

The ZIP contains the complete skills and shared dependencies, but no Git
history, remote configuration, local overrides, runtime caches, backups, or
session logs. Extract it into a new directory before initializing a separate
Git repository. The packager never creates a remote or pushes to GitHub.

See [VERIFICATION.txt](VERIFICATION.txt) for the current framework evidence.
Structural validation and Python tests do not claim that every game workflow
has been exercised in a real engine; an unconfigured game engine is explicitly
reported as not assessed. `tools/codex-studio/provenance_receipt.py` validates
host-supplied evidence but never fabricates a Skill selector, transcript, or
test result.

## License and provenance

MIT; see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). This is an
independently maintained community project, not an official OpenAI project.
The retained attribution and source notice do not create a runtime dependency.
