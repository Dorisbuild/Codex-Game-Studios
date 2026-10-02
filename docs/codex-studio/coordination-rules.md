# Codex subagent coordination rules

1. **Vertical delegation:** directors delegate to department leads, who delegate
   to specialists. Skip a tier only when the brief explains why.
2. **Horizontal consultation:** agents may consult peers but do not make binding
   decisions outside their declared domain.
3. **Conflict resolution:** escalate to the shared parent; use
   `creative-director` for design conflicts and `technical-director` for
   technical conflicts when no shared parent exists.
4. **Change propagation:** `producer` coordinates changes that cross several
   departments.
5. **No unilateral cross-domain edits:** a subagent edits only the named output
   paths in its brief, and never the same file as another active subagent.

## Subagent dispatch

Project agents are TOML files under `.codex/agents/`. A parent Codex session
spawns them with a narrow prompt containing:

- the role and the exact question;
- files and rules to read;
- an allowed output path (or an explicit read-only constraint); and
- the return format, including `PASS`, `CONCERNS`, `BLOCKED`, or
  `NOT ASSESSED` when applicable.

Independent read/review tasks may run in parallel. Wait for all results before
starting a dependent task. If any result is `BLOCKED` or `NOT ASSESSED`, surface
the reason instead of converting it to a pass.

## User authority

The parent session presents material trade-offs to the user and waits for a
decision checkpoint before changing scope, deleting files, or writing a new
design/configuration artifact. A subagent may prepare a draft, but it does not
silently commit a product decision.

See `docs/codex-studio/agent-teams.md` for the parallel-work checklist and
`docs/codex-studio/model-tiers.md` for model inheritance/pinning.
