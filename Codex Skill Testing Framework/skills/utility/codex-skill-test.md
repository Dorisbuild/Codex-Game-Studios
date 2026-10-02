# Skill Test Spec: `$codex-skill-test`

## Skill Summary

`$codex-skill-test` validates Codex skills and project-scoped TOML agents in four
modes: static structure, behavioral spec, category rubric, and catalog audit.
It reports evidence and asks before saving a result.

## Static Assertions

- [ ] Skill frontmatter contains only the required `name` and `description`.
- [ ] The skill documents at least two phases and a clear outcome vocabulary.
- [ ] The skill distinguishes `FAIL` from `NOT ASSESSED`.
- [ ] Any write path names its target and asks for approval before editing.
- [ ] The skill resolves catalog entries and uses `.toml` agent paths.

## Test Cases

### Case 1: Static happy path

**Fixture:** A valid skill and a valid `.codex/agents/creative-director.toml`.

**Expected:** The skill runs the five static checks, states the denominator,
and returns `COMPLIANT`, `WARNINGS`, or `NON-COMPLIANT` with evidence.

**Assertions:**

- [ ] It reads the complete target file rather than relying on the catalog alone.
- [ ] It does not write in static mode.
- [ ] It names the exact failed check and a minimal recommendation.

### Case 2: Missing target

**Fixture:** `$codex-skill-test spec does-not-exist`.

**Expected:** It reports `NOT ASSESSED`, names the missing path, and stops.

**Assertions:**

- [ ] No missing file is treated as a pass.
- [ ] No result file is written without approval.

### Case 3: TOML agent

**Fixture:** A valid custom agent with `name`, `description`, and
`developer_instructions`, with no pinned model.

**Expected:** The agent passes metadata checks and is reported as inheriting the
parent Codex session model.

**Assertions:**

- [ ] The path ends in `.toml`.
- [ ] Optional model checks are marked `NOT ASSESSED` when the local catalog is
  unavailable, not guessed.

### Case 4: Behavioral spec

**Fixture:** A catalog entry whose spec contains one happy path and one blocked
case.

**Expected:** Every assertion is evaluated; a missing fixture yields
`NOT ASSESSED`, while a contradictory behavior yields `FAIL`.

### Case 5: Audit

**Fixture:** One catalog entry has a stale spec path.

**Expected:** `$codex-skill-test audit` reports the stale path and denominator instead
of silently omitting the entry.

## Protocol Compliance

- [ ] Presents the report before offering to save it.
- [ ] Asks before writing `Codex Skill Testing Framework/results/`.
- [ ] Reopens a saved report and returns its absolute path.
- [ ] Ends with `$codex-skill-test audit` or `$codex-skill-improve <name>` as a next step.
