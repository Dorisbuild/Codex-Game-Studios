# Skill Flow Diagrams

Visual maps of how skills chain together across the 7 development phases.
These show what runs before and after each skill, and what artifacts flow between them.

---

## Default Path: Rigor Minimal (Four Steps to Code)

`modes.rigor: minimal` is the default. The one-page brief is the design record and
its build order is the plan, so there is no epic planning, sprint or phase gate to run.
Every skill below still runs at any tier; rigor changes what is required, not what
is allowed. `$codex-help` follows this route at `minimal`.

```
MINIMAL PATH (modes.rigor: minimal — the default; no $codex-gate-check, stage stays Concept)
  $codex-setup-engine ───────────────────────────────────────────────► project.yaml + AGENTS.md
  $codex-brainstorm ─────────────────────────────────────────────────► design/game-brief.md (one page)
        │                                                          (replaces concept doc, systems index, GDDs)
        ▼
  $codex-create-stories ─────────────────────────────────────────────► production/epics/[slug]/story-*.md
        │                                                          (brief's build order is the plan —
        │                                                           no $codex-create-epics, no $codex-sprint-plan)
        ▼ (one story at a time, in build order)
  $codex-dev-story [story] ──────────────────────────────────────────► routes to correct programmer agent
  $codex-story-done [story] ─────────────────────────────────────────► story closed + next story named
        │
        └── back to $codex-dev-story until every story is Complete, then:
              play the build · $codex-create-stories for more · $codex-settings to raise rigor
```

The overview below is the `standard`/`full` pipeline.

---

## Full Pipeline Overview (Zero to Ship)

```
PHASE 1: CONCEPT
  $codex-start ──────────────────────────────────────────────────────► routes to A/B/C/D
  $codex-brainstorm ──────────────────────────────────────────────────► design/gdd/game-concept.md
  $codex-setup-engine ────────────────────────────────────────────────► project.yaml + AGENTS.md
  $codex-prototype [core-mechanic] ───────────────────────────────────► prototypes/[name]-concept/REPORT.md
        │ PROCEED                                                  (validate idea BEFORE writing GDDs)
        ▼
  $codex-design-review [game-concept.md] ────────────────────────────► concept validated
  $codex-art-bible ──────────────────────────────────────────────────► design/art/art-bible.md
  $codex-map-systems ────────────────────────────────────────────────► design/gdd/systems-index.md
  $codex-gate-check ─────────────────────────────────────────────────► PASS → advance to systems-design
        │
        ▼
PHASE 2: SYSTEMS DESIGN
  $codex-map-systems next ───────────────────────────────────────────► picks the next system to design
        │
        ▼ (for each system, in dependency order)
  $codex-design-system [name] ──────────────────────────────────────► design/gdd/[system].md
  $codex-design-review [system].md ─────────────────────────────────► per-GDD review comments
        │
        ▼ (after all MVP GDDs done)
  $codex-review-all-gdds ────────────────────────────────────────────► design/gdd/gdd-cross-review-[date].md
  $codex-gate-check ─────────────────────────────────────────────────► PASS → advance to technical-setup
        │
        ▼
PHASE 3: TECHNICAL SETUP
  $codex-create-architecture ────────────────────────────────────────► docs/architecture/architecture.md
  $codex-architecture-decision (×N) ─────────────────────────────────► docs/architecture/[adr-nnn].md
  $codex-architecture-review ────────────────────────────────────────► review report + docs/architecture/tr-registry.yaml
  $codex-create-control-manifest ────────────────────────────────────► docs/architecture/control-manifest.md
  $codex-test-setup ─────────────────────────────────────────────────► test framework + CI/CD pipeline
  $codex-test-helpers ───────────────────────────────────────────────► tests/helpers/ (engine-specific library)
  $codex-ux-design accessibility ─────────────────────────────────────► design/accessibility-requirements.md
  $codex-ux-design patterns ──────────────────────────────────────────► design/ux/interaction-patterns.md
  $codex-gate-check ─────────────────────────────────────────────────► PASS → advance to pre-production
        │
        ▼
PHASE 4: PRE-PRODUCTION
  [UX — before epics, so specs exist when stories are written]
  $codex-ux-design [screen/hud] ──────────────────────────────────────► design/ux/*.md
  $codex-ux-review ──────────────────────────────────────────────────► UX specs approved (HARD gate for $codex-team-ui)

  [Vertical slice — before epics, validate full game loop]
  $codex-vertical-slice ─────────────────────────────────────────────► prototypes/[name]-vertical-slice/REPORT.md
  $codex-playtest-report ────────────────────────────────────────────► production/qa/playtests/

  [Stories + sprint plan — only after vertical slice PROCEEDS]
  $codex-create-epics [layer] ───────────────────────────────────────► production/epics/*/EPIC.md
  $codex-create-stories [epic-slug] ─────────────────────────────────► production/epics/*/story-*.md
  $codex-sprint-plan new ────────────────────────────────────────────► production/sprints/sprint-001.md
  $codex-gate-check ─────────────────────────────────────────────────► PASS → advance to production
        │
        ▼
PHASE 5: PRODUCTION (repeating sprint loop)
  $codex-sprint-status ──────────────────────────────────────────────► sprint snapshot
  $codex-story-readiness [story] ────────────────────────────────────► story validated READY
        │
        ▼ (pick up and implement)
  $codex-dev-story [story] ──────────────────────────────────────────► routes to correct programmer agent
        │
        ▼ (during implementation, as needed)
  $codex-code-review ────────────────────────────────────────────────► code review report
  $codex-scope-check ────────────────────────────────────────────────► scope creep detected / clear
  $codex-content-audit ──────────────────────────────────────────────► GDD content gaps identified
  $codex-bug-report ─────────────────────────────────────────────────► production/qa/bugs/BUG-NNNN.md
  $codex-bug-triage ─────────────────────────────────────────────────► bugs re-prioritized + assigned

  [Team skills for feature areas — spawn when working a full feature]
  $codex-team-combat / $codex-team-narrative / $codex-team-ui / $codex-team-level / $codex-team-audio

  [QA cycle per sprint]
  $codex-qa-plan ────────────────────────────────────────────────────► production/qa/qa-plan-[sprint-slug]-[date].md
  $codex-smoke-check ────────────────────────────────────────────────► smoke test gate (PASS/FAIL)
  $codex-regression-suite ───────────────────────────────────────────► coverage gaps + missing regression tests
  $codex-test-evidence-review ───────────────────────────────────────► evidence quality report
  $codex-test-flakiness ─────────────────────────────────────────────► flaky test report
        │
        ▼
  $codex-story-done [story] ─────────────────────────────────────────► story closed + next surfaced
  $codex-sprint-plan [next] ─────────────────────────────────────────► next sprint
        │
        ▼ (after Production milestone)
  $codex-milestone-review ───────────────────────────────────────────► milestone report
  $codex-gate-check ─────────────────────────────────────────────────► PASS → advance to polish
        │
        ▼
PHASE 6: POLISH
  $codex-perf-profile ───────────────────────────────────────────────► perf report + fixes
  $codex-balance-check ──────────────────────────────────────────────► balance report + fixes
  $codex-asset-audit ────────────────────────────────────────────────► asset compliance report
  $codex-tech-debt ──────────────────────────────────────────────────► docs/tech-debt-register.md
  $codex-soak-test ──────────────────────────────────────────────────► soak test protocol + results
  $codex-team-polish ────────────────────────────────────────────────► polish sprint orchestrated
  $codex-team-qa ────────────────────────────────────────────────────► full QA cycle sign-off
  $codex-security-audit ─────────────────────────────────────────────► production/security/security-audit-[date]-[scope].md
  $codex-localize qa ────────────────────────────────────────────────► production/localization/loc-qa-[locale]-[date].md
  $codex-release-checklist ──────────────────────────────────────────► production/releases/release-checklist-[version].md
  $codex-changelog ──────────────────────────────────────────────────► docs/CHANGELOG.md
  $codex-patch-notes ────────────────────────────────────────────────► docs/patch-notes/[version].md (draft)
  $codex-gate-check ─────────────────────────────────────────────────► PASS → advance to release
        │
        ▼
PHASE 7: RELEASE
  $codex-launch-checklist ───────────────────────────────────────────► launch readiness report
  $codex-team-release ───────────────────────────────────────────────► release pipeline orchestrated
        │
        ▼ (post-launch, ongoing)
  $codex-hotfix ─────────────────────────────────────────────────────► emergency fix with audit trail
  $codex-team-live-ops ──────────────────────────────────────────────► live-ops content plan
```

---

## Skill Chain: $codex-design-system in Detail

How a single GDD gets authored, reviewed, and handed to architecture:

```
systems-index.md (input)
game-concept.md (input)
upstream GDDs (input, if any)
        │
        ▼
$codex-design-system [name]
        │
        ├── Pre-check: feasibility table + engine risk flags
        │
        ├── Section cycle × 8:
        │     question → options → decision → draft → approval → WRITE
        │     [each section written to file immediately after approval]
        │
        └── Output: design/gdd/[system].md (complete, all 8 sections)
                │
                ▼
        $codex-design-review design/gdd/[system].md
                │
                ├── APPROVED → mark DONE in systems-index, proceed to next system
                ├── NEEDS REVISION → agent shows specific issues, re-enter section cycle
                └── MAJOR REVISION → significant redesign needed before next system
                        │
                        ▼ (after all MVP GDDs + cross-review)
                $codex-review-all-gdds
                        │
                        └── Output: gdd-cross-review-[date].md
```

---

## Skill Chain: UX / UI Pipeline in Detail

Screen and HUD specs are authored in Phase 4 (Pre-Production), before epics are
written, so that story acceptance criteria can reference specific UX artifacts.
Accessibility and interaction-pattern specs are authored earlier, in Phase 3
(Technical Setup), since at `full` the Technical Setup → Pre-Production gate
requires them (at `standard` they are recommended; at `minimal` they drop).

```
design/gdd/*.md (UI/UX requirements extracted)
design/player-journey.md (emotional arc, if authored)
        │
        ▼
$codex-ux-design hud              → design/ux/hud.md
$codex-ux-design screen [name]    → design/ux/screens/[name].md
$codex-ux-design patterns         → design/ux/interaction-patterns.md
        │
        ▼
$codex-ux-review design/ux/
        │
        ├── APPROVED → UX specs ready, proceed to $codex-create-epics
        ├── NEEDS REVISION → blocking issues listed → fix → re-run review
        └── MAJOR REVISION → fundamental UX problems → redesign before epics
                │
                ▼ (after APPROVED — in Phase 5 when implementing UI features)
        $codex-team-ui
                │
                ├── Phase 1: $codex-ux-design (if any specs still missing) + $codex-ux-review
                ├── Phase 2: visual design (art-director)
                ├── Phase 3: layout implementation (ui-programmer)
                ├── Phase 4: accessibility audit (accessibility-specialist)
                └── Phase 5: final review

Note: $codex-ux-design accessibility and $codex-ux-design patterns belong in Phase 3
      (Technical Setup); $codex-ux-design screen/hud and $codex-ux-review belong in Phase 4
      (Pre-Production). $codex-team-ui belongs in Phase 5 (Production) when a UI
      feature is being built.
```

---

## Skill Chain: Dev Story Flow in Detail

How a story moves from backlog to closed:

```
$codex-story-readiness [story]
        │
        ├── READY → Status: ready-for-dev → pick up for implementation
        ├── NEEDS WORK → agent shows specific gaps → resolve → re-run readiness
        └── BLOCKED → ADR still Proposed, or upstream story incomplete
                │
                ▼ (after READY)
        $codex-dev-story [story]
                │
                ├── Reads: story file, linked GDD requirement, ADR decisions, control manifest
                ├── Routes to: gameplay-programmer / engine-programmer / ui-programmer / etc.
                │
                └── Implementation begins
                        │
                        ▼ (optional, during/after implementation)
                $codex-code-review          → architectural review of changeset
                $codex-scope-check          → verify no scope creep vs. original story criteria
                $codex-test-evidence-review → validate test files and manual evidence quality
                        │
                        ▼
                $codex-story-done [story]
                        │
                        ├── COMPLETE → Status: Complete, sprint-status.yaml updated, next story surfaced
                        ├── COMPLETE WITH NOTES → complete but some criteria deferred (logged)
                        └── BLOCKED → acceptance criteria cannot be verified → investigate blocker
```

---

## Skill Chain: Story Lifecycle (Backlog to Closed)

How a story gets from backlog to closed (summary view):

```
$codex-create-epics [layer]
        │
        └── Output: production/epics/[slug]/EPIC.md
                │
                ▼
        $codex-create-stories [epic-slug]
                │
                └── Output: production/epics/[slug]/story-NNN-[slug].md
                            (Status: Ready or Blocked if ADR is Proposed)
                │
                ▼
        $codex-story-readiness [story]
                │
                ├── READY → $codex-dev-story → implement → $codex-story-done
                ├── NEEDS WORK → resolve gaps → re-run
                └── BLOCKED → fix upstream dependency first
```

---

## Skill Chain: QA Pipeline in Detail

```
[Phase 3 — one-time infrastructure setup]
$codex-test-setup ────────────────────────────────────────────────────► test framework scaffolded + CI/CD wired
$codex-test-helpers ──────────────────────────────────────────────────► tests/helpers/ (GDUnit4, NUnit, etc.)

[Phase 5 — per-sprint QA cycle]
$codex-qa-plan [sprint or feature]
        │
        ├── Reads: story files, GDDs, acceptance criteria
        ├── Classifies each story by test type:
        │     Logic → automated unit test (BLOCKING by default)
        │     Integration → integration test or documented playtest (BLOCKING by default)
        │     Visual/Feel → retained screenshot + lead sign-off (BLOCKING by default)
        │     UI → retained screenshot of each screen (BLOCKING by default)
        │     Config/Data → smoke check (ADVISORY by default)
        │     (gate levels are overridable per type via testing.strict in project.yaml)
        └── Output: production/qa/qa-plan-[sprint-slug]-[date].md
                │
                ▼
        $codex-smoke-check
                │
                ├── PASS → QA hand-off cleared
                └── FAIL → block sprint close → fix critical paths first
                        │
                        ▼
                $codex-regression-suite
                        │
                        └── Coverage gaps + list of fixed bugs without regression tests
                                │
                                ▼
                        $codex-test-evidence-review
                                │
                                └── Validates evidence quality, not just existence
                                        │
                                        ▼ (if CI run history available)
                        $codex-test-flakiness
                                │
                                └── Flaky test report + fix recommendations

[Phase 6 — extended stability testing]
$codex-soak-test ─────────────────────────────────────────────────────► soak test protocol + observed results
$codex-team-qa ───────────────────────────────────────────────────────► full QA cycle sign-off for release gate

[Ongoing — bug management]
$codex-bug-report ────────────────────────────────────────────────────► production/qa/bugs/BUG-NNNN.md
$codex-bug-triage ────────────────────────────────────────────────────► open bugs re-prioritized + assigned

[Meta — harness validation]
$codex-skill-test [lint|spec|catalog] ────────────────────────────────► skill file structural + behavioral check
```

---

## Brownfield Onboarding Flow

For projects with existing work (use `$codex-start` option D or run directly):

```
$codex-project-stage-detect    → stage detection report
        │
        ▼
$codex-adopt
        │
        ├── Phase 1: detect what exists
        ├── Phase 2: FORMAT audit (not just existence)
        ├── Phase 3: classify gaps (BLOCKING / HIGH / MEDIUM / LOW)
        ├── Phase 4: ordered migration plan
        ├── Phase 5: write docs/adoption-plan-[date].md
        └── Phase 6: fix most urgent gap inline (optional)
                │
                ▼
        $codex-design-system retrofit [path]    → fills missing GDD sections
        $codex-architecture-decision retrofit [path] → fills missing ADR sections
        $codex-gate-check                       → where are you in the pipeline?
```

---

## How to Read These Diagrams

| Symbol | Meaning |
|--------|---------|
| `──►` | Produces this artifact |
| `│ ▼` | Flows into next step |
| `├──` | Branch (multiple possible outcomes) |
| `×N` | Runs N times (once per system, story, etc.) |
| `(input)` | Read by the skill but not produced here |
| `[optional]` | Not required for the gate to pass |
| `WRITE` (caps) | File written to disk immediately |

---

## Common Entry Points

| Where you are | Run this |
|---------------|---------|
| Brand new, no idea | `$codex-start` → `$codex-brainstorm` |
| Have a concept, no engine | `$codex-setup-engine` |
| Have concept + engine | `$codex-map-systems` |
| Mid-systems design | `$codex-design-system [next system]` or `$codex-map-systems next` |
| All GDDs done | `$codex-review-all-gdds` → `$codex-gate-check` |
| In technical setup | `$codex-create-architecture` → `$codex-architecture-decision` |
| Starting UX design | `$codex-ux-design screen [name]` or `$codex-ux-design hud` |
| Scaffolding tests | `$codex-test-setup` → `$codex-test-helpers` |
| Have stories, ready to code | `$codex-story-readiness [story]` → `$codex-dev-story [story]` |
| Story done | `$codex-story-done [story]` |
| Running QA for a sprint | `$codex-qa-plan` → `$codex-smoke-check` → `$codex-regression-suite` |
| Bug backlog needs sorting | `$codex-bug-triage` |
| Extended stability testing | `$codex-soak-test` |
| Not sure | `$codex-help` |
| Existing project | `$codex-adopt` |
