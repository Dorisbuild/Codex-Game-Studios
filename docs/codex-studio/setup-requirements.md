# Setup Requirements

Codex Game Studios is a repository workflow that runs inside Codex. The template does not
install an engine or a game project for you.

## Required

| Tool | Purpose | Check |
| ---- | ------- | ----- |
| Git | version control, branches, and history | `git --version` |
| Codex CLI or Codex desktop | loads `AGENTS.md`, skills, and custom agents | `codex --version` |
| Python 3.11+ | parses `project.yaml` and runs verification tools | `python --version` |
| Bash | runs the portable Codex Game Studios shell helpers | `bash --version` |

On Windows, Git for Windows supplies Bash. PowerShell may be used for normal
file work; run the shell helpers through Git Bash (or WSL) when a Bash command
is shown in this repository.

## Recommended

| Tool | Purpose |
| ---- | ------- |
| PyYAML | install with `python -m pip install -r requirements-dev.txt` for framework validation |
| the selected engine | headless parsing, tests, and visual verification |
| Git LFS | large binary assets |

The Bash configuration reader needs no PyYAML; the framework verifier does. A missing engine
only blocks engine-specific checks; documentation and configuration checks can
still run.

## First-run check

From the repository root:

```bash
git --version
codex --version
python --version
bash --version
python tools/verify_codex_studio.py
```

Then open the repository root in Codex. The root `AGENTS.md` and more-specific
`AGENTS.md` files are discovered automatically. Select a skill by its Codex
skill name (for example `$codex-start`), or describe the same workflow in plain
language.

## Windows notes

- Keep shell scripts checked out with LF endings; `.gitattributes` already
  declares this for `*.sh`.
- Quote paths containing spaces, such as `E:/AI GAME/GAME`.
- If `bash` is not on `PATH`, run the same script from Git Bash or WSL rather
  than changing the scripts to PowerShell-specific syntax.

## Permissions and hooks

The project does not install automatic hooks or change host permissions.
Explicit check scripts live under `tools/codex-studio/scripts/`; see
`docs/codex-studio/hooks-reference.md`. Never treat opening this workspace as
approval to register services or trust hooks.
