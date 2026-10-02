# Explicit checks, not installed hooks

Codex Game Studios installs no lifecycle hooks or command interceptors. Its
active helpers use ordinary command-line arguments, not assistant event JSON:

| Tool | Explicit invocation |
| --- | --- |
| Configuration | `bash tools/codex-studio/config/yaml-helper.sh resolve_config` |
| Story status | `bash tools/codex-studio/scripts/story-status.sh` |
| Artifact observations | `bash tools/codex-studio/scripts/artifact-check.sh --path minimal` |
| Engine/config consistency | `bash tools/codex-studio/scripts/project-coherence.sh` |
| Framework validation | `python tools/verify_codex_studio.py` |

Adjacent Git-hook recipes are optional examples, not active configuration.
Inspect commands and modes before installing them. Future Codex integrations
require the installed version's official schema and disposable-project tests.
Opening this repository grants no permission to install or trust hooks.
