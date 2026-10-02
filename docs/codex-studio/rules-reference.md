# Workflow rules reference

The files in `docs/codex-studio/rules/` are reusable, path-oriented guidance. Codex
does not automatically load arbitrary Markdown in that directory. A skill or
agent must read the relevant rule before editing the matching files; the
repository `AGENTS.md` files describe the routing and the verification helpers
check the resulting artifacts.

This distinction is intentional:

1. **Instructions are guidance, not a security boundary.** Destructive actions
   still require Codex approval and normal repository review.
2. **Read before write.** Open the applicable rule and an existing target file
   before creating or changing a new artifact.
3. **Record skipped checks.** If a rule cannot run because the engine, test
   root, or input is missing, report `NOT ASSESSED` instead of treating it as a
   pass.

## Rule index

| Rule | Apply before working on | Main checks |
| --- | --- | --- |
| `gameplay-code.md` | gameplay systems | data-driven values, delta time, no UI ownership |
| `engine-code.md` | engine/core code | allocations, thread safety, API stability |
| `ai-code.md` | AI code | budgets, debuggability, data-driven parameters |
| `network-code.md` | networking | authority, versioned messages, input validation |
| `ui-code.md` | UI/presentation | state ownership, localization, accessibility |
| `design-docs.md` | `design/gdd/**` | required sections for the resolved rigor |
| `narrative.md` | `design/narrative/**` | canon, voice, continuity |
| `data-files.md` | data assets | JSON/schema validity and naming |
| `test-standards.md` | test roots | naming, fixtures, coverage evidence |
| `prototype-code.md` | `prototypes/**` | hypothesis, scope, README and evidence |
| `shader-code.md` | shader files | naming, performance, platform constraints |
| `agent-memory.md` | `production/session-state/agent-memory/**` | temporary-memory boundaries |
| `skill-authoring.md` | `.agents/skills/**`, `.codex/agents/**` | verdicts, defaults, skips, sourcing, coverage |

## Engine-specific roots

Resolve `engine.name` from `project.yaml` before applying a code rule:

- Godot: `src/` and `tests/`
- Unity: `Assets/` and `Assets/Tests/`
- Unreal: `Source/<Module>/` and module test directories

The same rule may be used for all three engines, but the path and command must
match the selected engine. See `code-root-resolution.md` and the pinned engine
reference before using an API.
