# Skill Test Spec: $codex-run

## Skill Summary

`$codex-run` is a Codex-native, single-pass coordinator. It runs the explicit
dispatcher, routes one next action, follows the selected skill's real approval
and evidence rules, and writes an atomic checkpoint only after the pass. It
stops on missing engine, blocked stories, inconsistent story/sprint status, an
existing checkpoint lock, or a required user decision. It never calls a prompt
selector as if it were a shell API and never claims to be a background worker.
Verdict: COMPLETE when the observed plan, action, evidence and checkpoint are
reported; BLOCKED when the dispatcher or selected skill stops safely.

---

## Static Assertions (Structural)

- [ ] Has `codex-run` frontmatter and a Codex-branded UI metadata file
- [ ] Runs `tools/codex-studio/orchestrate.py --once`
- [ ] Limits one invocation to one routable action
- [ ] Requires actual test/build/evidence results rather than file existence
- [ ] Describes lock failure and atomic checkpoint behavior
- [ ] Explicitly denies background-worker or selector-as-shell semantics
- [ ] Distinguishes a provenance-required clean workspace from a legacy project
      and refuses to call a summary a Skill invocation transcript

## Test Cases

### Case 1: Fresh template

`project.yaml` has no engine and no brief. The dispatcher is run once.

Expected: report `needs_engine`, name `$codex-setup-engine`, perform no game
write, and leave a checkpoint only when explicitly requested.

### Case 2: Ready story

The project has a configured engine, a brief, and one `Status: Ready` story.

Expected: route `$codex-dev-story [path]`, execute no second story, record the
actual test/build evidence, and write one bounded checkpoint.

### Case 3: Conflict or blocker

The story file says `Complete` while sprint status says `in-progress`, or the
story says `Blocked`.

Expected: stop with the exact conflict/blocker, select no implementation skill,
and preserve the previous checkpoint if the lock is held.

### Case 4: All stories complete

Every discovered story is `Complete` or `Done`.

Expected: route to `$codex-smoke-check`, state that this is a single quality
gate, and never start another implementation story automatically.

### Case 5: Clean workspace provenance

`START_HERE.md` declares `provenance: required`.

Expected: create or continue one run receipt, report the explicit selector and
host transcript status, retain before/after checkpoint and diff artifacts, and
use `NOT ASSESSED` when the host transcript is unavailable. A successful game
test without that transcript is not a provenance PASS. The optional
`tools/codex-studio/provenance_receipt.py` may create only a non-forging shell
and input hashes; it must not fabricate the transcript or upgrade the status.

## Evidence

The implementation evidence is `tests/test_orchestrator.py`; the dispatcher
must pass the full repository test suite and `tools/verify_codex_studio.py`.
