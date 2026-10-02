# Configuration resolution

Codex Game Studios project settings live in `project.yaml`. Skills that depend on a setting
should run the resolver near the beginning of the workflow and use the emitted
value rather than re-implementing precedence in prose:

```bash
bash tools/codex-studio/config/yaml-helper.sh resolve_config \
  --keys workflow,review_mode,automation
```

Run the command from the repository root. The helper also resolves the root
from its own location, so a skill may call it after changing directories as long
as the path to the script is correct.

## Output contract

The command exits `0` and emits a complete, human-readable block. Each line
contains a value and its source, for example:

```text
review_mode: solo (rigor:minimal)
automation: collaborative (default)
workflow: minimal (rigor:minimal)
```

The script reports observations only. The invoking skill still decides whether
to proceed, ask the user, or return `NOT ASSESSED`.

## Precedence

For a normal setting, the first valid value in this order wins:

1. `project.local.yaml` for keys explicitly allowed as local overrides;
2. `project.yaml`;
3. the documented legacy mirror (`production/review-mode.txt` or
   `production/stage.txt`, where applicable);
4. the expansion derived from `modes.rigor`;
5. the documented default.

Invalid enum values are rejected and named in the resolver's `notes` line;
they do not become effective configuration. A local file cannot override a
locked project key, and the helper reports that fact instead of editing either
file.

## Rigor expansion

`modes.rigor` fronts the following six values when they are not explicitly set:

| Rigor | workflow | docs.density | qa.level | story_granularity | review_mode | team.size |
| --- | --- | --- | --- | --- | --- | --- |
| `minimal` | minimal | terse | minimal | coarse | solo | individual |
| `standard` | standard | balanced | standard | balanced | lean | individual |
| `full` | full | thorough | full | fine | full | studio |

Explicit values continue to win over the derived row. The default rigor is
`minimal`, which keeps a fresh project on the short path until the user elects
more process.

## Skill obligations

A skill that uses configuration must:

- state the exact resolver command it ran;
- preserve the provenance shown by the helper;
- distinguish missing/unreadable input from a clean result;
- avoid writing configuration without the normal user approval; and
- record the resolved mode in any artifact whose behavior depends on it.

If the helper cannot run (for example, Bash or Python is missing), report the
affected keys as `NOT ASSESSED` and use only the documented fallback that the
skill explicitly names. Never silently treat a missing block as a successful
default.
