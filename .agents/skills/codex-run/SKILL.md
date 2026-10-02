---
name: codex-run
description: "Run one state-aware Codex Game Studios step and leave a recoverable checkpoint."
---

> **Codex execution:** This is a host-level orchestration skill. Read
> `docs/codex-studio/runtime.md` and `docs/codex-studio/roadmap.md` before
> acting. `$codex-*` selectors are prompts, not shell commands.

# Codex Run — one safe production pass

Use this skill when the user wants the project to continue from its current
state, for example “run the next step” or “resume the game”. It
advances **one** routable action per invocation. A second invocation is required
after the selected skill has produced and verified its result.

## Phase 1: Read the dispatcher plan

From the project root run:

```text
python tools/codex-studio/orchestrate.py --once --text
```

Treat the output as an observation, not as permission to skip a user decision.
The dispatcher checks, in order:

1. configured engine → `$codex-setup-engine`;
2. minimal brief or full concept → `$codex-brainstorm`;
3. implementation stories → `$codex-create-stories`;
4. `In Review`, `In Progress`, then `Ready` stories in build order;
5. blocked, unclassified, or all-complete states.

If the state is `inconsistent`, `blocked`, or `needs_status`, stop and report
the exact files and reason. Do not mark a story complete to make the route
advance. If the state is `all_stories_complete`, run the named smoke gate and
do not start another story automatically.

If the project contains `START_HERE.md` with `provenance: required`, create or
open a new `production/provenance/<run-id>/` receipt before implementation.
Record the selected Skill, the workspace/base hash, input artifact hashes and
the SHA-256 values of the Skill and rules you read. A receipt is not a claim by
itself: the new-window host transcript must contain the explicit `$codex-*`
selector and any approvals/delegation results. The optional helper can create a
non-forging shell and input hashes:

```text
python tools/codex-studio/provenance_receipt.py init --workspace . --run-id <run-id> --selector '$codex-run'
python tools/codex-studio/provenance_receipt.py capture-inputs production/provenance/<run-id> --file .agents/skills/codex-run/SKILL.md --file docs/codex-studio/runtime.md
```

It never creates a transcript or upgrades a status. Use
`docs/codex-studio/templates/skill-receipt.md` as the receipt skeleton.

## Phase 2: Execute exactly one selected action

If the plan names a skill, read that skill's complete `SKILL.md` and follow its
approval, delegation, engine, test, and evidence rules. The selected skill may
ask a normal conversation checkpoint; preserve it. Do not invoke a second
implementation story in the same pass, and do not claim that this skill runs in
the background.

Before closing the pass, collect observed results:

- the exact command and exit code for tests/builds that were actually run;
- the story path and status after the skill's write;
- retained visual or run evidence when the story type requires it;
- any unresolved question, blocker, or independent review that was not run;
- the provenance receipt status. Use `VERIFIED` only when the selector,
  transcript, input/rule hashes, before/after diff, checkpoint snapshots and
  observed commands agree; otherwise report `PARTIAL` or `NOT ASSESSED`.

## Phase 3: Persist and report the checkpoint

After the selected action returns, re-run the dispatcher. If the resulting plan
is stable, write the bounded checkpoint explicitly:

```text
python tools/codex-studio/orchestrate.py --once --write-checkpoint --text \
  --files "<paths changed in this pass>"
```

The writer uses `production/session-state/active.md.lock` and an atomic replace.
It never edits Story or sprint status. If the lock already exists, stop, report
the lock path, and preserve the previous checkpoint.

For a provenance-required workspace, also retain `checkpoint-before.md`,
`checkpoint-after.md`, `TRANSCRIPT.md`, `INPUTS.md`, `CHANGES.patch` and
`VERIFICATION.md` under the same run directory. Do not fabricate a transcript
from a summary after the fact. Missing host transcript means `NOT ASSESSED`.

## Output

Return:

```text
State: [state]
Action: [what was selected and what actually ran]
Evidence: [commands/results and retained paths]
Checkpoint: [absolute active.md path, or not written with reason]
Provenance: [VERIFIED | PARTIAL | NOT ASSESSED + receipt path]
Next: [the next dispatcher result, or the blocker]
```

This skill is a Codex single-pass coordinator. Long-running continuation still
requires the Codex host, a user-triggered follow-up, a Codex heartbeat, or an
external scheduler; none is installed by this repository.
