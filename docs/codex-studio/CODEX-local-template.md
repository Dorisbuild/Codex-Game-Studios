# AGENTS.override.md template

Use `AGENTS.override.md` only when you deliberately want to **replace the
`AGENTS.md` in the same directory** for instruction discovery. Codex loads at
most one instruction file per directory: a non-empty override is selected
instead of the regular file, not appended to it. Guidance from other discovered
directories remains in the instruction chain.

For a personal checkout override, first read the shared root `AGENTS.md`, then
create the following ignored file and preserve all shared guidance that should
remain active. Do not copy only the short preferences example below and expect
the shared root file to load as well:

```text
AGENTS.override.md
```

Example:

```markdown
# Local project preferences

- Read the shared `AGENTS.md` in this directory explicitly and follow its
  project workflow unless one of the following local preferences says otherwise.
- Preferred engine executable: `godot` at `C:/Tools/Godot/godot.exe`
- Run the focused test command before a full test suite.
- Keep generated exports under `build/local/`.
- Do not commit local screenshots or profiling captures.
```

The explicit read above is a project instruction, not automatic same-directory
merging. Alternatively copy the required shared guidance into the override and
keep that copy synchronized. Remove the override to restore normal discovery
of that directory's `AGENTS.md`; restart the session when needed for the host
to rebuild its instruction chain.

Keep credentials out of instruction files, including ignored ones: their
contents are sent to the model. Use the platform's credential store or
appropriately scoped environment variables. Machine paths and non-secret local
preferences may live in this ignored override rather than tracked guidance.

The repository `.gitignore` excludes `AGENTS.override.md`. If you use a
different filename, add it to your local exclude file instead of changing the
shared ignore rules, and explicitly configure or request that file's loading;
an arbitrary ignored filename is not discovered automatically.

Reference: [Codex instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md#how-codex-discovers-guidance).
