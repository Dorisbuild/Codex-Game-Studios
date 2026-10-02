# Parallel Codex subagents

Codex Game Studios defines project-scoped roles in `.codex/agents/*.toml`.
A parent session delegates through the subagent tools available in its Codex
host. Each subagent has its own agent thread and returns a report to the parent;
that is different from creating a separate user-owned chat in the sidebar.
Do not create a new user-owned chat merely to perform a subtask.

If the tool can select a custom role by name, use that supported field. If it
accepts only a task name and prompt, read the named TOML file and include the
relevant `developer_instructions` in the brief. Merely naming a task after a
role does not prove that its TOML instructions were loaded. If delegation is
unavailable, perform the required checks sequentially and disclose that no
subagent ran.

History inheritance is host-specific. Where `fork_turns` is available, use its
documented values; full-history forks inherit parent context and settings. A
fresh fork requires a self-contained brief. Always specify essential facts,
the approved file scope, and the return contract instead of assuming either
empty context or complete shared knowledge. The shipped roles inherit the
parent model and reasoning settings; do not invent a model override.

## Use parallel subagents when

- the workstreams read different inputs and write different files;
- each workstream has a named owner, output path, and return contract; and
- the parent can merge the reports without making two agents edit the same file.

## Use sequential subagents when

- the second review depends on the first result;
- both agents would edit the same artifact; or
- a user decision is required between phases.

## Safe dispatch pattern

1. Read the relevant `AGENTS.md`, skill, and gate definition.
2. State the subagent name, exact scope, allowed output path, and completion
   format in the brief.
3. Dispatch independent agents together, then wait for all results.
4. Surface `BLOCKED`, `CONCERNS`, and `NOT ASSESSED` verbatim to the user.
5. The parent, not a subagent, owns cross-domain decisions and final writes
   unless the brief explicitly names an approved output path.

The project default in `.codex/config.toml` is conservative. Respect the actual
host's available concurrency. For a one-off CLI run, a supported `-c` override
changes the limit for that process only; it does not edit the tracked file:

```text
codex -c 'agents.max_concurrent_threads_per_session=2'
```

There is no project-installed agent-spawn log, completion log, or lifecycle
hook. The parent records needed outcomes explicitly in the approved artifact
or session checkpoint and reports the actual paths and checks performed.
Deterministic helpers live in `tools/codex-studio/config/` and
`tools/codex-studio/scripts/`; a skill, user command, or separately reviewed CI
job must invoke them. Codex's own subagent activity UI is host functionality,
not a logging service supplied by this repository.
