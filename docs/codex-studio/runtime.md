# Codex execution contract

Read this once when using the studio skills in a session. Each skill adds its
domain-specific workflow. Project artifacts are English-first: design,
architecture, stories, code comments, tests, commit messages, and technical
records use English. Chat questions and reports may follow the user's language
when requested. Localization of player-facing text is a later `$codex-localize`
phase, not a reason to mix languages in source documents.

## Inputs and names

All shipped skills use `codex-` names and folders. Select a skill in the host
or include `$codex-start`, `$codex-dev-story`, etc. in the user message. These
selectors are not shell commands. Read arguments from the current message,
preserving quoted paths and multi-word values. For implicit invocation, infer
arguments from the request or ask for missing required inputs. No argument
macros or command injection are required. Role names refer to
`.codex/agents/<role>.toml`, not skills.

## Decisions and permission

A conversation checkpoint means explaining the relevant trade-off, asking a
concise plain-language question, and waiting when approval is required. It is
not a callable tool or a mandatory UI. If the host offers an optional question
UI, follow its actual schema and mode restrictions; ask approval questions in
ordinary conversation. Skill examples describe possible answers, not a fixed
number of questions/options to force into a tool call.

Respect decisions already present in the request. Automation modes control
design checkpoints, not host permissions, publication consent, or scope.
Subagents return unresolved product decisions to the parent instead of
pretending they can open a decision UI.

## Files and terminals

Run repository-relative commands from the project root. Report absolute local
artifact paths. `Read`, `Write`, `Edit`, `Glob`, and `Grep` in prose describe
operations, not assumed tool names. Use the host's actual tools. Searches use
`rg`; bounded reads can use PowerShell `Get-Content` with `Select-Object`, or
Bash `sed -n 'N,Mp' FILE`. Quote and escape paths for the selected shell.

Bash snippets must run in Bash, not as PowerShell syntax. On Windows use Git
Bash. Each terminal call may start a new process: variables and sourced
functions do not persist across independent calls. Source and use helper
functions in the **same** Bash process every time:

```bash
bash -lc 'source tools/codex-studio/config/yaml-helper.sh; resolve_setting modes.workflow'
```

The simpler configuration command is:

```bash
bash tools/codex-studio/config/yaml-helper.sh resolve_config --keys workflow,automation
```

`CODEX_STUDIO_ROOT` is this library's optional explicit root override, not an
environment variable supplied automatically by Codex. Helpers also locate
the repository from their own path. Missing tools/configuration are explicit
gaps, not passing results. Do not invent a skill-directory environment variable.

## Roles and delegation

The 49 TOML roles use `name`, `description`, and `developer_instructions`.
Model and reasoning defaults are omitted so parent choices apply. Do not
assume account access to a fixed model.

Use the host's real subagent tools. Select a custom role if the host supports
it; otherwise read its TOML and pass the relevant instructions in the delegated
brief. Do not invent role-selection API parameters. Supply task, inputs,
permitted outputs, and evidence requirements. History inheritance depends on
host/fork settings, so every brief should be sufficient on its own.

Collect real results before reporting a review as completed. When delegation
is unavailable, distinguish sequential self-review from independent review;
record the latter NOT ASSESSED when required and not actually performed.

## No implicit services

The project installs no lifecycle hooks, interceptors, statusline, automatic
memory, or notification service. Checkpoints/logs are written only by explicit
skill steps or scripts. Optional Git-hook recipes are not installed when this
project is opened. Inherited settings without active consumers are reserved,
not enabled functionality.

## Single-pass dispatcher

`tools/codex-studio/orchestrate.py` is the first Codex-native library layer.
It reads `project.yaml`, the minimal-path artifacts, story `Status` fields and
the optional `production/sprint-status.yaml`, then emits one JSON or text plan:

```text
python tools/codex-studio/orchestrate.py --once --text
```

The plan may select `$codex-setup-engine`, `$codex-brainstorm`,
`$codex-create-stories`, `$codex-dev-story`, `$codex-story-done`,
`$codex-story-readiness` or `$codex-smoke-check`. It stops on a blocked story or
inconsistent status sources. `--write-checkpoint` uses an exclusive lock and an
atomic replace for `production/session-state/active.md`; it never edits story
status or invokes a selector. The Codex host remains responsible for executing
the selected skill, tests, approvals and any next pass.

Game `project.yaml` settings are separate from Codex configuration. There is
no promised `.codex/config.local.toml` auto-loading layer. `AGENTS.override.md`
replaces `AGENTS.md` at the same scope, rather than appending preferences.

## Official references

- [Skills](https://developers.openai.com/codex/skills/)
- [Custom subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

The current host's tools and constraints govern actual execution.

## Clean-room game workspaces

Do not use the library-maintenance checkout as the context for a new game.
Create an isolated workspace with `tools/create_game_workspace.py`, then open
that destination in a new Codex window. The creator is deliberately a file
copy and manifest operation; it does not run `$codex-*`, initialize Git, set a
remote, or install anything globally. Read
[`clean-room-workflow.md`](clean-room-workflow.md) for the exact copy boundary,
Skill sequence, provenance receipts and negative replay requirements.

`tools/codex-studio/provenance_receipt.py` is an optional evidence checker for
that workflow. It can hash declared inputs and validate host-supplied files,
but it cannot observe Codex conversation state and never fabricates a
transcript or `VERIFIED` result.

The repository contains no game fixture. A new game's root is the directory
created by `tools/create_game_workspace.py`; pass that root explicitly when
running the dispatcher if the command is launched from elsewhere. The root
`project.yaml` remains engine-neutral until `$codex-setup-engine` configures the
game, so the first plan should be `$codex-setup-engine` rather than an implicit
engine default.
