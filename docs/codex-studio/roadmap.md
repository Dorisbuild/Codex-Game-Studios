# Codex Game Studios capability roadmap

This is the library's own delivery contract. The upstream workflow supplied the
domain coverage; this roadmap defines what the Codex implementation must prove
before it claims independent game production.

## Maturity levels

| Level | Capability | Evidence required |
| --- | --- | --- |
| L0 | Skills, roles, references, validation and packaging | Structural verifier, skill discovery, 113 tests |
| L1 | One real story end to end | Configured engine, build/test/run exit codes, retained visual evidence, story and checkpoint agreement |
| L2 | Reliable cross-session continuation | Atomic checkpoint, one state source, idempotent cold resume, explicit failure record |
| L3 | Semi-automatic production | Single-pass dispatcher, delegated implementation, test/evidence gate, stop on BLOCKED or missing engine |
| L4 | Shippable independent game | Vertical slice, release build matrix, save migration, performance, localization, rollback and release evidence |

The library core remains L0 plus the first L3 building block: the dispatcher can
select one next action and write a locked checkpoint. It intentionally contains
no game or engine fixture. Every future project must earn L1 with its own engine
pin, story/checkpoint agreement, build evidence, playtest and provenance
receipt. The dispatcher remains single-pass and does not claim unattended
background work at any level.

## Near-term order

1. Make story status, sprint status and `active.md` agree or stop safely.
2. Ship and test the clean-room workspace creator so a new Codex window starts
   without demo or framework-maintenance context.
3. Generalize an engine golden path into engine setup, nested project-root
   discovery and smoke-check evidence.
4. **Partial:** ship the non-forging receipt shell/input-hash checker. Remaining
   work is host transcript export, failure/retry records and a cold-resume test
   that can be interrupted at every phase without duplicating writes.
5. Add Codex-host heartbeat or an external runner only as an explicit scheduler;
   never describe a prompt selector as a daemon.
6. Add worktree/ownership isolation before parallel agents edit the same game.
