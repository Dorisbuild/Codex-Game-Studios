# Behavioral spec: codex-settings

Target: `.agents/skills/codex-settings/SKILL.md`
Category: utility. These are evaluation cases, not a claim they have all run.

## Static assertions

- Name and folder are codex-settings; UI display name begins with Codex.
- The skill reads project.yaml and supported local overrides.
- Every helper function is sourced and called in the same Bash process.
- View requests perform no writes; writes stay within the authorized setting.
- Reserved fields without active consumers are explicitly identified.

## Case 1: View effective configuration

Request: `$codex-settings` on the untouched template.
Expect: workflow minimal, review_mode solo, automation collaborative and their
provenance. No files changed, no invented runtime hook status.

## Case 2: View one key

Request: `$codex-settings modes.workflow`.
Expect: resolve the current value and source; no repeated request for write
approval, no write or global Codex configuration change.

## Case 3: Authorized local update

Request: `$codex-settings --local modes.automation=guided`.
Expect: verify the local-override allowlist and enum, explain the change, follow
the workflow's approval checkpoint, edit only project.local.yaml, then re-read
the resolved value. Preserve unrelated fields and report the absolute path.

## Case 4: Locked project key

Request: `$codex-settings --local engine.name=Godot`.
Expect: surface that the key is not locally overridable, leave files unchanged,
and route engine selection to `$codex-setup-engine`; never silently drop it.

## Case 5: Malformed argument or invalid enum

Requests: `$codex-settings --local =foo`, `$codex-settings modes.workflow=`
and `$codex-settings modes.workflow=unknown`.
Expect: explicit usage/validation result and no writes. Do not turn blank input
into a default value or success.

## Case 6: Reserved runtime field

Request: `$codex-settings features.session_state`.
Expect: label the inherited field RESERVED; distinguish explicit checkpoint
operations from a nonexistent automatic service. No hook is installed.

## Case 7: Windows and independent processes

Fixture: project path contains spaces; each command starts a new process.
Expect: quote paths and source within every function call, or use the direct
resolve_config entry point. No function-not-found or parameter macro expansion.

## Result

Report PASS / FAIL / NOT ASSESSED per case with observed evidence. A metadata
pass does not count as execution of these behavioral cases.
