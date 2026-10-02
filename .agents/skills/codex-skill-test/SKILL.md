---
name: codex-skill-test
description: "Validate Codex skill files and project-scoped agent definitions for structure and documented behavior."
---

> **Codex execution:** Read `docs/codex-studio/runtime.md` for argument,
> conversation-checkpoint, terminal, and delegation conventions. Use the
> current user request as input; skills do not expand shell macros.

# Skill Test

This skill tests the framework itself, not a game. It supports four modes:

| Mode | Example | Result |
| --- | --- | --- |
| `static` | `$codex-skill-test static all` | deterministic structure checks |
| `spec` | `$codex-skill-test spec codex-gate-check` | evaluate the matching behavioral spec |
| `category` | `$codex-skill-test category codex-review-all-gdds` | apply the category rubric |
| `audit` | `$codex-skill-test audit` | report catalog and coverage gaps |

Run from the repository root:

```bash
python tools/verify_codex_studio.py
```

Use that verifier for syntax and metadata; use this skill for the judgment that
requires reading the skill, agent, and behavioral specification.

## Phase 1: Resolve the target

Read `Codex Skill Testing Framework/catalog.yaml` first. A skill target is
`.agents/skills/<name>/SKILL.md`; an agent target is
`.codex/agents/<name>.toml`. If the name is absent from the catalog, use the
file that exists. Report a missing target as `NOT ASSESSED`.

Read the repository `AGENTS.md` files and any rule files named by the target
before evaluating it. Do not assume a Markdown reference is automatically
loaded by Codex.

## Phase 2: Static mode

For each skill, read the frontmatter delimited by the first pair of `---` lines
and run these checks:

1. **Codex metadata:** `name` and `description` are present, non-empty, and
   match the skill directory/name. unsupported keys (`allowed-tools`,
   `argument-hint`, `user-invocable`, `model`, and
   `disable-model-invocation`) are absent from skill frontmatter.
2. **Phases:** at least two phase-like headings (`## Phase`, numbered `##`, or
   two distinct top-level sections) are present.
3. **Outcome:** a review/check/gate skill names an outcome such as `PASS`,
   `FAIL`, `CONCERNS`, `BLOCKED`, `READY`, `COMPLETE`, `NOT ASSESSED`, or a
   documented severity scale. Artifact-only skills may report `WARN` instead.
4. **Write protocol:** if the body writes or edits a file, it presents the
   target and asks for approval before that write. Read-only skills explicitly
   say that they do not write.
5. **Handoff:** the final section names a next skill, next action, or follow-up.

For each custom agent, parse TOML and require `name`, `description`, and
`developer_instructions`. If `model` is present, check that the model and
`model_reasoning_effort` are valid for the local Codex installation or mark the
model check `NOT ASSESSED` rather than guessing.

Do not write in static mode. Report one row per file and state the denominator.
Use `COMPLIANT`, `WARNINGS`, `NON-COMPLIANT`, or `NOT ASSESSED` as the aggregate
result.

## Phase 3: Spec mode

1. Resolve the `spec:` path from `catalog.yaml`.
2. Read the target, its `AGENTS.md` context, and the complete spec.
3. Evaluate every static assertion, test case, and protocol assertion literally.
4. Distinguish `FAIL` from `NOT ASSESSED`: an unreadable or missing input is
   not a pass, and a failure found alongside it remains a failure.
5. Return the case verdicts, evidence paths/lines, and an aggregate verdict.

The spec is a desired contract, not a description of the current file. Fix the
target or the spec when one is demonstrably wrong; never weaken a failing case
just to make the report green.

## Phase 4: Category mode

Read the matching section of `Codex Skill Testing Framework/quality-rubric.md`.
Apply only metrics that the target can actually satisfy. For a metric whose
input or engine is absent, record `NOT ASSESSED` with the reason. Do not infer a
pass from an empty directory.

## Phase 5: Audit mode

List all skills and agents from the catalog, verify each target/spec path, and
show coverage counts for static, spec, and category results. Include missing
specs and stale paths; do not silently omit them.

## Output and approval

Show the report in the conversation first. If the user asks to save it, ask:

> May I write this report to `Codex Skill Testing Framework/results/<name>-<date>.md`?

Write only after approval, then reopen the file and report its absolute path.
Updating `catalog.yaml` is a separate write and needs a separate confirmation.

## Next steps

- Run `$codex-skill-test static all` after a skill or agent edit.
- Run `$codex-skill-test spec <name>` for behavioral coverage.
- Run `$codex-skill-test audit` to find missing specs.
- Use `$codex-skill-improve <name>` only after recording a baseline.
