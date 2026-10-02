# Local Codex configuration

Codex user settings live in `$CODEX_HOME/config.toml` (normally
`~/.codex/config.toml`). Keep non-secret machine preferences there or use a
supported one-off CLI override rather than committing local account or path
data. Use a credential store or environment variable for credentials.

The tracked `.codex/config.toml` in this repository contains only the small set
of project defaults needed by the custom-agent roster. Do not copy your whole
user config into it. Codex does not automatically load a
`.codex/config.local.toml` layer just because it exists or is gitignored.

## Safe local overrides

Use the Codex CLI's dotted override syntax for a one-off run:

```powershell
codex -C . -c 'agents.max_concurrent_threads_per_session=2'
```

For persistent personal instructions, use `AGENTS.override.md` as described in
`CODEX-local-template.md`: it replaces the same-directory `AGENTS.md` during
discovery rather than extending it. Preserve required shared guidance.

For personal Codex settings, use the settings UI or `$CODEX_HOME/config.toml`.
A trusted project's `.codex/config.toml` takes precedence over user defaults;
the user file is not a way to override a conflicting project setting. Use a
supported CLI `-c` override for that run or explicitly revise the shared
project setting. Managed requirements and live host controls still constrain
what values may take effect.

`project.local.yaml` is different: it is the Codex Game Studios resolver's
explicit per-developer layer for allowlisted **workflow** settings, not a Codex
runtime configuration file.

## Approval guidance

- Keep normal approval/sandbox settings while editing a real game.
- Use read-only mode for review-only sessions.
- Use automatic approval only in a disposable prototype or CI environment.
- This repository does not install lifecycle hooks. Review any separately added
  integration before enabling it; a script's presence alone does not register
  it with Codex or grant it permission to run.

## Verifying the project

Configuration is read from `project.yaml`, not from Codex's TOML settings. Use
the resolver before a workflow that depends on rigor or review mode:

```bash
bash tools/codex-studio/config/yaml-helper.sh resolve_config \
  --keys workflow,review_mode,automation
```

Reference: [Codex configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence).
