# Contributing to Codex Game Studios

This repository is a Codex-native game workflow template. Contributions should
improve a real workflow gap, a skill, an agent prompt, a deterministic helper,
or the documentation that explains them.

## Layout rules

- Skills live in `.agents/skills/codex-<name>/SKILL.md`; each skill directory must
  contain YAML frontmatter with `name` and `description`.
- Custom agents live in `.codex/agents/<name>.toml`; each file must define
  `name`, `description`, and `developer_instructions`.
- Repository and path-specific instructions belong in `AGENTS.md` files.
- Reusable templates and workflow references belong under `docs/codex-studio/`.
- Shell/Python helpers belong under `tools/codex-studio/` and must emit observations,
  not silently make product decisions.

## Prompt and workflow rules

- Keep role boundaries explicit and route cross-domain conflicts upward.
- Ask the user before writing design, configuration, or source files unless the
  calling workflow has already named and approved the destination.
- State assumptions, options, trade-offs, and verification evidence.
- Do not make a subagent edit the same file as another subagent concurrently.
- Keep the `minimal` path short; higher rigor must add measurable confidence,
  not paperwork for its own sake.

## Testing changes

For skills, validate frontmatter and run the relevant static/spec checks. For
agents, parse the TOML and exercise domain-boundary and return-contract cases.
For helpers, run them from the repository root and a nested directory on Windows
Git Bash, macOS, or Linux where applicable. Record exact commands and outcomes
in the change description.

Useful checks:

```bash
python -m py_compile tools/verify_codex_studio.py tools/package_studio.py tools/restore_snapshot.py
bash tools/codex-studio/config/yaml-helper.sh resolve_config --keys workflow,review_mode
bash tools/codex-studio/scripts/story-status.sh
```

## Commit style

Use Conventional Commits, for example:

```text
feat: add a Godot combat review skill
fix: resolve project root from nested Codex sessions
docs: clarify the minimal workflow
```

Do not commit generated session logs, secrets, engine build output, or game
artifacts that belong in a separate project repository.

## License

The project is MIT licensed. Keep the upstream copyright and license notice in
substantial derivative work.
