# Skill pass receipt — `<run-id>`

**Status:** `VERIFIED | PARTIAL | NOT ASSESSED | FAIL`
**Skill selector:** `$codex-...`
**Workspace:** `<absolute path>`
**Started / finished:** `<timestamps>`

## Evidence links

- Transcript: `TRANSCRIPT.md`
- Inputs and SHA-256 values: `INPUTS.md`
- Before/after change: `CHANGES.patch`
- Commands and literal output: `VERIFICATION.md`
- Checkpoints: `checkpoint-before.md`, `checkpoint-after.md`

## Required assertions

- [ ] The new-window transcript contains the explicit selector.
- [ ] User approvals and delegated roles are copied from the host record.
- [ ] Skill and referenced-rule hashes match the workspace at invocation time.
- [ ] The diff is bounded to this pass and matches the changed-file list.
- [ ] Commands include exact exit codes and machine-readable summaries.
- [ ] Missing transcript, hash, checkpoint or command evidence is reported as
      `NOT ASSESSED`, not silently treated as a pass.

This receipt records evidence. It does not itself prove that a model followed
the Skill; the host transcript and observed artifacts provide that evidence.
