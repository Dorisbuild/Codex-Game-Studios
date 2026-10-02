# Context Management

Context is the most critical resource in a Codex session. Manage it actively.

## File-Backed State (Primary Strategy)

**The file is the memory, not the conversation.** Conversations are ephemeral and
will be compacted or lost. Files on disk persist across compactions and session crashes.

### Session State File

Maintain `production/session-state/active.md` as a living checkpoint. Update it
after each significant milestone:

- Design section approved and written to file
- Architecture decision made
- Implementation milestone reached
- Test results obtained

**Create it from `docs/codex-studio/templates/session-state.md`** after the
workflow's write approval. Skills explicitly read and update this file; opening
Codex, spawning an agent, and compacting or ending a session do not update it.
The `features.session_state` compatibility setting does not enable a runtime.

Two regions, and the distinction is load-bearing:

| Region | Who reads it | Rule |
|--------|--------------|------|
| `<!-- STATUS -->` … `<!-- /STATUS -->` | a skill or returning agent explicitly reading the file | Optional Epic/Feature/Task focus; not a Codex status-bar integration |
| `<!-- CHECKPOINT -->` … `<!-- /CHECKPOINT -->` | a skill or returning agent explicitly reading the file | **Overwrite, never append.** Keep the block under ~25 lines |
| Everything after `<!-- /CHECKPOINT -->` | humans, and an agent that needs the history | Free-form notes; not automatically injected |

The checkpoint holds: current task, next step, what it is blocked on, files in
progress, open questions. Write it so a cold reader can resume without opening
anything else.

> **Why the split.** An append-only history grows without bound. Keeping the
> current checkpoint separate lets a returning agent read the current task
> first, then request only the historical notes it needs. This is an explicit
> file-reading convention, not an event-driven context injection mechanism.

**Rotation.** When the narrative passes ~200 lines, move it into
`production/session-logs/`:

```bash
bash tools/codex-studio/scripts/rotate-session-state.sh --dry-run
# After approval to archive these notes:
bash tools/codex-studio/scripts/rotate-session-state.sh
```

The checkpoint stays and the narrative is appended to a dated log. The skill or
user decides when to invoke rotation; there is no automatic observer or archive.

### Optional Focus Block

Include a structured focus block in `active.md` when Epic/Feature/Task context
helps the next reader. It can be useful at any stage. The project stage still
comes from `project.stage` in `project.yaml`, with the documented legacy fallback.

```markdown
<!-- STATUS -->
Epic: Combat System
Feature: Melee Combat
Task: Implement hitbox detection
<!-- /STATUS -->
```

- All three fields (Epic, Feature, Task) are optional — include only what applies
- Update this block when switching focus areas
- A report may summarize it as `Combat System > Melee Combat > Hitboxes`; the
  repository does not install a Codex status line
- Leave the fields empty when no active work focus exists

After any disruption (compaction, crash, or a new session), read the state file
first.

### Incremental File Writing

When creating multi-section documents (design docs, architecture docs, lore entries):

1. Ask to create the file ("May I create [path] with the section skeleton?"), then
   create it with every section header and empty bodies
2. Discuss and draft one section at a time in conversation
3. Write each section to the file as soon as it's approved (a skill that writes
   once at the end, such as `$codex-create-architecture`, records approved sections in
   the session state instead)
4. Update the session state file after each section
5. After writing a section, previous discussion about that section can be safely
   compacted — the decisions are in the file

This keeps the context window holding only the *current* section's discussion
(~3-5k tokens) instead of the entire document's conversation history (~30-50k tokens).

## Context Resilience

- Write approved decisions and evidence paths to files before the conversation
  grows too large; do not rely on a fixed context-percentage threshold.
- Good checkpoint boundaries include a completed section, test run, or task.
- Use only the context-management controls the current Codex client actually
  exposes. This project does not install compaction commands or event hooks.
- If the user starts a new session for unrelated work or recovery, provide the
  checkpoint path and the concrete next step; do not assume history will transfer.

## Context Budgets by Task Type

- Light (read/review): ~3k tokens startup
- Medium (implement feature): ~8k tokens
- Heavy (multi-system refactor): ~15k tokens

## Deterministic Helpers — `tools/codex-studio/scripts/`

The cheapest context saving is not summarising a document, it is **not reading it
at all**. When a question has a deterministic answer, a script should answer it
and the model should spend its budget on judgment instead.

Two directories, two purposes — reach for the right one:

| Directory | Purpose | Invoked by |
|---|---|---|
| `tools/codex-studio/config/` | Configuration resolution helpers | `bash tools/codex-studio/config/yaml-helper.sh resolve_config --keys ...` |
| `tools/codex-studio/scripts/` | Manually invoked from a skill body | `bash tools/codex-studio/scripts/<name>.sh` |

Current helpers:

- **`gdd-structure-check.sh`** — which of the 8 standard sections a GDD contains.
  Replaces a full-document read per GDD, and cannot hallucinate a missing
  section. Reports **presence only**; the caller applies the workflow tier.
- **`review-scope.sh`** — which GDDs changed since the last cross-review, plus
  their declared dependencies. Replaces reasoning through git history.

Two rules when adding one:

1. **Show the exact command.** A skill should state the command, working
   directory, expected exit status, and what it will do with the output. Codex
   approval remains controlled by the active session; there is no skill
   tool-permission frontmatter in this project.
2. **Emit observations, not verdicts.** A script that scores or judges will
   eventually contradict a tier, mode, or per-system override it does not know
   about. Report what is on disk and let the caller decide what it means.

## Subagent Delegation

Use subagents for research and exploration to keep the main session clean.
Subagents run in their own context window. Ask for a concise return summary:

- **Use subagents** when investigating across multiple files, exploring unfamiliar code,
  or doing research that would consume >5k tokens of file reads
- **Use direct reads** when you know exactly which 1-2 files to check
- History inheritance depends on the current host and the chosen fork settings.
  In hosts exposing `fork_turns`, follow its actual schema; a full-history fork
  inherits history and model settings, while a fresh fork needs a self-contained
  brief. Never assume the child has no history or that it has read a named file.
- Always include the role, question, approved file scope, essential facts, and
  return contract explicitly. Read `docs/codex-studio/agent-teams.md` before
  choosing a role or dispatching work.

## Compaction Instructions

When context is compacted, preserve the following in the summary:

- Reference to `production/session-state/active.md` (read it to recover state)
- List of files modified in this session and their purpose
- Any architectural decisions made and their rationale
- Active sprint tasks and their current status
- Agent invocations and their outcomes (success/failure/blocked)
- Test results (pass/fail counts, specific failures)
- Unresolved blockers or questions awaiting user input
- The current task and what step we are on
- Which sections of the current document are written to file vs. still in progress

**After compaction:** Read `production/session-state/active.md` and any files being
actively worked on to recover full context. The files contain the decisions; the
conversation history is secondary.

## Recovery After Session Crash

If a session dies ("prompt too long") or you start a new session to continue work:

1. Explicitly read `production/session-state/active.md`, if it exists. If it is
   missing, inspect the user's named artifacts and current Git changes instead
   of inventing a prior checkpoint.
2. Read the partially completed files listed in the checkpoint and verify that
   recorded paths, test results, and blockers still apply.
3. Continue from the next incomplete section or task, preserving user decisions
   and reporting any stale checkpoint facts. No lifecycle event runs these steps
   on the project's behalf.
