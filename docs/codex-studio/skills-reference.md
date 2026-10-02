# Available Codex Skills

75 repository skills organized by phase. Select a skill by name in Codex (for
example, `$codex-start`), or describe the matching task in plain language.

## Onboarding & Navigation

| Command | Purpose |
|---------|---------|
| `$codex-start` | First-time onboarding — asks where you are, then guides you to the right workflow |
| `$codex-help` | Context-aware "what do I do next?" — reads current stage and surfaces the required next step |
| `$codex-project-stage-detect` | Full project audit — detect phase, identify existence gaps, recommend next steps |
| `$codex-setup-engine` | Configure engine + version, detect knowledge gaps, populate version-aware reference docs |
| `$codex-adopt` | Brownfield format audit — checks internal structure of existing GDDs/ADRs/stories, produces migration plan |
| `$codex-settings` | View or change project config — the effective merged values, or a local override in `project.local.yaml` |
| `$codex-run` | Run one state-aware workflow pass, stop safely on blockers, and persist a recoverable checkpoint |

## Game Design

| Command | Purpose |
|---------|---------|
| `$codex-brainstorm` | Guided ideation using professional studio methods (MDA, SDT, Bartle, verb-first) |
| `$codex-map-systems` | Decompose game concept into systems, map dependencies, prioritize design order |
| `$codex-design-system` | Guided, section-by-section GDD authoring for a single game system |
| `$codex-quick-design` | Lightweight design spec for small changes — tuning, tweaks, minor additions |
| `$codex-review-all-gdds` | Cross-GDD consistency and game design holism review across all design docs |
| `$codex-propagate-design-change` | When a GDD is revised, find affected ADRs and produce an impact report |

## Art & Assets

| Command | Purpose |
|---------|---------|
| `$codex-art-bible` | Guided, section-by-section Art Bible authoring — creates visual identity spec before asset production begins |
| `$codex-asset-spec` | Generate per-asset visual specifications and AI generation prompts from GDDs, level docs, or character profiles |
| `$codex-asset-audit` | Audit assets for naming conventions, file size budgets, and pipeline compliance |

## UX & Interface Design

| Command | Purpose |
|---------|---------|
| `$codex-ux-design` | Guided section-by-section UX spec authoring (screen/flow, HUD, or pattern library) |
| `$codex-ux-review` | Validate UX specs for GDD alignment, accessibility, and pattern compliance |

## Architecture

| Command | Purpose |
|---------|---------|
| `$codex-create-architecture` | Guided authoring of the master architecture document |
| `$codex-architecture-decision` | Create an Architecture Decision Record (ADR) |
| `$codex-architecture-review` | Validate all ADRs for completeness, dependency ordering, and GDD coverage |
| `$codex-create-control-manifest` | Generate flat programmer rules sheet from accepted ADRs |

## Stories & Sprints

| Command | Purpose |
|---------|---------|
| `$codex-create-epics` | Translate GDDs + ADRs into epics — one per architectural module |
| `$codex-create-stories` | Break a single epic into implementable story files |
| `$codex-dev-story` | Read a story and implement it — routes to the correct programmer agent |
| `$codex-sprint-plan` | Generate or update a sprint plan; initializes sprint-status.yaml |
| `$codex-sprint-status` | Fast 30-line sprint snapshot (reads sprint-status.yaml) |
| `$codex-story-readiness` | Validate a story is implementation-ready before pickup (READY/NEEDS WORK/BLOCKED) |
| `$codex-story-done` | 8-phase completion review after implementation; updates story file, surfaces next story |
| `$codex-estimate` | Structured effort estimate with complexity, dependencies, and risk breakdown |

## Reviews & Analysis

| Command | Purpose |
|---------|---------|
| `$codex-design-review` | Review a game design document for completeness and consistency |
| `$codex-code-review` | Architectural code review for a file or changeset |
| `$codex-balance-check` | Analyze game balance data, formulas, and config — flag outliers |
| `$codex-content-audit` | Audit GDD-specified content counts against implemented content |
| `$codex-scope-check` | Analyze feature or sprint scope against original plan, flag scope creep |
| `$codex-perf-profile` | Structured performance profiling with bottleneck identification |
| `$codex-tech-debt` | Scan, track, prioritize, and report on technical debt |
| `$codex-gate-check` | Validate readiness to advance between development phases (PASS/CONCERNS/NOT ASSESSED/FAIL) |
| `$codex-consistency-check` | Scan all GDDs against the entity registry to detect cross-document inconsistencies (stats, names, rules that contradict each other) |
| `$codex-security-audit` | Audit the game for security vulnerabilities: save tampering, cheat vectors, network exploits, data exposure, and input validation gaps |

## QA & Testing

| Command | Purpose |
|---------|---------|
| `$codex-qa-plan` | Generate a QA test plan for a sprint or feature |
| `$codex-smoke-check` | Run critical path smoke test gate before QA hand-off |
| `$codex-soak-test` | Generate a soak test protocol for extended play sessions |
| `$codex-regression-suite` | Map test coverage to GDD critical paths, identify fixed bugs without regression tests |
| `$codex-test-setup` | Scaffold the test framework and CI/CD pipeline for the project's engine |
| `$codex-test-helpers` | Generate engine-specific test helper libraries for the test suite |
| `$codex-test-evidence-review` | Quality review of test files and manual evidence documents |
| `$codex-test-flakiness` | Detect non-deterministic (flaky) tests from CI run logs |
| `$codex-skill-test` | Validate skill files for structural compliance and behavioral correctness |
| `$codex-skill-improve` | Improve a skill using a test-fix-retest loop — diagnose, propose fix, rewrite, verify |

## Production

| Command | Purpose |
|---------|---------|
| `$codex-milestone-review` | Review milestone progress and generate status report |
| `$codex-retrospective` | Run a structured sprint or milestone retrospective |
| `$codex-bug-report` | Create a structured bug report |
| `$codex-bug-triage` | Read all open bugs, re-evaluate priority vs. severity, assign owner and label |
| `$codex-reverse-document` | Generate design or architecture docs from existing implementation |
| `$codex-playtest-report` | Generate a structured playtest report or analyze existing playtest notes |

## Release

| Command | Purpose |
|---------|---------|
| `$codex-release-checklist` | Generate and validate a pre-release checklist for the current build |
| `$codex-launch-checklist` | Complete launch readiness validation across all departments |
| `$codex-changelog` | Auto-generate changelog from git commits and sprint data |
| `$codex-patch-notes` | Generate player-facing patch notes from git history and internal data |
| `$codex-hotfix` | Emergency fix workflow with audit trail, bypassing normal sprint process |
| `$codex-day-one-patch` | Prepare a focused day-one patch for known issues discovered after gold master but before or at public launch |

## Creative & Content

| Command | Purpose |
|---------|---------|
| `$codex-prototype` | Concept prototype — throwaway build right after brainstorm to validate core idea (Phase 1) |
| `$codex-vertical-slice` | Pre-Production validation — production-quality end-to-end build before committing to Production (Phase 4) |
| `$codex-onboard` | Generate contextual onboarding document for a new contributor or agent |
| `$codex-localize` | Localization workflow: string extraction, validation, translation readiness |

## Team Orchestration

Coordinate multiple agents on a single feature area:

| Command | Coordinates |
|---------|-------------|
| `$codex-team-combat` | game-designer + gameplay-programmer + ai-programmer + technical-artist + sound-designer + qa-tester |
| `$codex-team-narrative` | narrative-director + writer + world-builder + level-designer |
| `$codex-team-ui` | ux-designer + ui-programmer + art-director + accessibility-specialist |
| `$codex-team-release` | release-manager + qa-lead + devops-engineer + producer |
| `$codex-team-polish` | performance-analyst + technical-artist + sound-designer + qa-tester |
| `$codex-team-audio` | audio-director + sound-designer + technical-artist + gameplay-programmer |
| `$codex-team-level` | level-designer + narrative-director + world-builder + art-director + systems-designer + qa-tester |
| `$codex-team-live-ops` | live-ops-designer + economy-designer + community-manager + analytics-engineer |
| `$codex-team-qa` | qa-lead + qa-tester + gameplay-programmer + producer |

## Overlap with Codex's bundled skills

Codex ships its own skills, and one name collides with Codex Game Studios's.

| You type | You get | Use it for |
|---------|---------|-----------|
| `$codex-code-review` | **Codex Game Studios's** — project skills take the bare name | Architectural review against this project's coding standards, SOLID, testability and the control manifest. Knows about ADRs, stories and `docs/architecture/`. |
| `/review` | **Codex's bundled** review — the alias of its `$codex-code-review`, which Codex Game Studios's skill shadows | Reviewing a pull request or a plain diff for correctness bugs, with no knowledge of Codex Game Studios's design documents or gates. |

Both are useful; they answer different questions. Reach for the Codex Game Studios one during
`$codex-dev-story` and before `$codex-story-done`, because it checks the things the gates
later check. Reach for the bundled one when you want a general review of a diff
that has nothing to do with a story.

Codex Game Studios does **not** turn the bundled skills off. `disableBundledSkills` would
remove all of them, including `/debug`, `/security-review` and `/simplify`,
which are worth keeping. If you want a bundled skill hidden, use
`skillOverrides` in your own `.codex/config.toml` rather than disabling
the whole set.
