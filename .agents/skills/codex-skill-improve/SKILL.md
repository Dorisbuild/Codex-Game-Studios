---
name: codex-skill-improve
description: "Improve one Codex skill through a measured test, review, edit, and retest loop."
---

> **Codex execution:** Read `docs/codex-studio/runtime.md` for argument,
> conversation-checkpoint, terminal, and delegation conventions. Use the
> current user request as input; skills do not expand shell macros.

# Skill Improve

## Phase 1: Baseline

Read `.agents/skills/<name>/SKILL.md` and run `$codex-skill-test static <name>`.
Record the exact failures, warnings, and the command output. If the file cannot
be read or its frontmatter is malformed, report `NOT ASSESSED` and stop.

If the catalog assigns a category, run `$codex-skill-test category <name>` and record
that baseline separately. Never combine an unassessed dimension with a clean
score.

## Phase 2: Diagnose

Map each failure to a minimal change:

- missing Codex metadata → add only `name`/`description`;
- missing phase/outcome/handoff → add the smallest truthful section;
- missing approval protocol → name the target path and ask before writing;
- unsupported runtime metadata → remove it from the skill frontmatter;
- a category failure → fix the behavior, not just the wording.

Read any referenced rule or spec before proposing a change. Present a concise
before/after diff and explain why it addresses the measured failure.

## Phase 3: Approval and edit

Ask:

> May I write the proposed improvement to `.agents/skills/<name>/SKILL.md`?

On approval, preserve the original content in the conversation (or a temporary
copy outside the repository), make only the proposed edit, and reopen the file.
Do not use `git checkout` to roll back; that would discard unrelated uncommitted
work.

## Phase 4: Retest and verdict

Run the same static and category commands again. Compare exact counts:

```text
Static:   before F/W -> after F/W
Category: before F/W -> after F/W (when assigned)
Verdict:  improved | unchanged | worse | NOT ASSESSED
```

Keep the change only when the behavior improved or a documented correctness
issue was fixed without creating a new failure. If it is unchanged or worse,
show the diff and ask whether to restore the saved pre-edit content.

## Next steps

Run `$codex-skill-test spec <name>` for behavioral coverage, then `$codex-skill-test audit`
to update the coverage picture. Save a result file only after a separate user
approval.
