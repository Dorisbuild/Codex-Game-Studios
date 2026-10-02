# Security Policy

This is a local development workflow that executes prompts and optional shell or
Python helpers in a user's repository. Treat every hook, script, skill, and
custom agent as code that deserves review before enabling it.

## Scope

Report privately if a contribution:

- reads or exports secrets without a documented reason;
- makes an undisclosed network request;
- writes outside its declared project scope;
- bypasses user confirmation for destructive or irreversible actions;
- executes shell commands that are not necessary for the stated validation.

The deterministic helpers under `tools/codex-studio/` should fail closed on malformed
configuration and should never claim that a check passed when it only observed
an artifact.

## Safe use

- Review changes to `.agents/skills/`, `.codex/agents/`, and `tools/codex-studio/`.
- Keep credentials in ignored files and never paste them into a skill or agent.
- Run destructive migration utilities only from a disposable clone or a branch
  with a recoverable tag.
- Prefer read-only subagents for exploration and review.
- Verify outbound network behavior before enabling a connector or MCP server.

## Reporting

Use GitHub's private vulnerability reporting for confirmed security issues in
the repository's Security question (or the maintainer's configured advisory URL).
Include the affected path, reproduction steps, impact, and a proposed
mitigation. Do not publish secrets or exploit details in a public issue.
