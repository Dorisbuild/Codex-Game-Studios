# Skill Test Spec: `$codex-skill-improve`

## Skill Summary

`$codex-skill-improve <name>` records a static/category baseline, diagnoses the
smallest fix, asks before editing one skill, and retests the same dimensions.

## Static Assertions

- [ ] Skill frontmatter contains `name` and `description` only.
- [ ] It records exact before/after counts rather than claiming improvement.
- [ ] It preserves the pre-edit content without using `git checkout`.
- [ ] It asks before editing `.agents/skills/<name>/SKILL.md`.
- [ ] It restores only the saved pre-edit content when the score is unchanged or
      worse and the user approves restoration.

## Test Cases

### Case 1: Failing skill improves

**Fixture:** One static failure caused by a missing handoff.

**Expected:** The skill shows a diagnosis and diff, receives approval, adds the
handoff, reruns the same test, and reports a lower failure count.

### Case 2: User declines

**Fixture:** The baseline has a real failure; the user declines the proposed edit.

**Expected:** No file changes occur and the baseline remains in the report.

### Case 3: Retest is worse

**Fixture:** The proposed edit introduces malformed frontmatter.

**Expected:** The skill reports `NOT ASSESSED`/failure and asks whether to restore
the saved content; it never calls `git checkout`.

### Case 4: Category not assigned

**Fixture:** The catalog entry has no category.

**Expected:** Static testing still runs and the category dimension is explicitly
reported as skipped, not as a zero score.

## Protocol Compliance

- [ ] Shows diagnosis and before/after blocks before writing.
- [ ] Reopens the edited file and reruns the measured checks.
- [ ] Ends with `$codex-skill-test audit` or the next skill name.
