# Active Session State — [project or branch]

<!--
  EXPLICIT FILE-BACKED STATE

  A skill or returning agent reads and writes this file explicitly. The
  repository does not install automatic startup, compaction, shutdown, or
  agent-event handlers, and it does not inject this file into a conversation.

  STATUS is optional focus information. CHECKPOINT is the bounded recovery
  summary: keep the CHECKPOINT block under about 25 lines and overwrite its
  fields on each approved update rather than appending another checkpoint.

  Everything after the closing CHECKPOINT marker is narrative history. Read
  only what is relevant when recovering state. The manually invoked rotation
  helper keeps everything through that marker and archives the narrative.

  ROTATION, when the narrative grows beyond about 200 lines:
      bash tools/codex-studio/scripts/rotate-session-state.sh --dry-run
  Inspect the proposed archive path; after approval invoke it without --dry-run.
  No background event notices the length or performs this operation for you.
-->

<!-- STATUS -->
Epic:
Feature:
Task:
<!-- /STATUS -->

<!-- CHECKPOINT -->
**Updated:** [YYYY-MM-DD]
**Branch:** `[branch]`
**Current task:** [one line — what is actively being worked on]
**Next step:** [one line — the very next action, concrete enough to resume cold]
**Blocked on:** [one line, or `nothing`]
**Files in progress:** [paths, comma-separated, or `none`]
**Run result:** [`$codex-dev-story` writes its `Run result:` line here, verbatim, for `$codex-story-done` to read; other writers leave this line out]
**Open questions:** [one line each, or `none`]
<!-- /CHECKPOINT -->

---

## Notes

[Decisions and rationale, attempted approaches, evidence paths, and context
that would be expensive to reconstruct. Timestamp material observations and
verify them again before treating them as current facts.]

<!--
  FIELD NOTES

  STATUS: Epic, Feature, and Task are optional. Leave fields empty when no focus
  is active. A report can summarize them; there is no bundled status-bar script.

  CHECKPOINT: A cold reader should be able to name the next action from this
  block alone. "Fixing the thing" is vague; "Run the combat unit tests after
  updating src/combat/hitbox.gd" is actionable. Record only observed results.

  The features.session_state compatibility value does not enable or disable
  these explicit file operations. Follow the invoking skill's write protocol.
-->
