# Game Studio Agent Architecture -- Quick Start Guide

## What Is This?

This is a complete Codex agent architecture for game development. It
organizes 49 specialized AI agents into a studio hierarchy that mirrors
real game development teams, with defined responsibilities, delegation
rules, and coordination protocols. It includes engine-specialist agents
for Godot, Unity, and Unreal — each with dedicated sub-specialists for
major engine subsystems. All design agents and templates are grounded in
established game design theory (MDA Framework, Self-Determination Theory,
Flow State, Bartle Player Types). Use whichever engine set matches your project.

## The Default Path: Rigor Minimal

`modes.rigor` defaults to `minimal` (`$codex-start` asks; `$codex-settings` changes it any
time). At `minimal` the path to code is four steps:

1. `$codex-setup-engine` -- configure the engine
2. `$codex-brainstorm` -- writes the one-page `design/game-brief.md`, in place of the
   concept doc, systems decomposition and per-system GDDs
3. `$codex-create-stories` -- turns the brief's MVP list into stories under
   `production/epics/<slug>/`; the brief's build order is the plan, so there is
   no `$codex-create-epics` or `$codex-sprint-plan`
4. `$codex-dev-story` then `$codex-story-done`, story by story -- `$codex-story-done` names the
   next story, and `$codex-help` knows this route

Nothing at `minimal` runs `$codex-gate-check`, so `project.stage` stays at Concept.
Every skill still runs at any tier. The trade: no GDDs catch design problems
before code. Raise rigor with `$codex-settings` when the game outgrows the brief;
`standard` and `full` are the longer pipelines under
[First Steps for a New Project](#first-steps-for-a-new-project).

## How to Use

### 1. Understand the Hierarchy

There are three tiers of agents:

- **Tier 1 — Directors** who make high-level decisions (the port gives these
  agents a higher Codex reasoning effort)
  - `creative-director` -- vision and creative conflict resolution
  - `technical-director` -- architecture and technology decisions
  - `producer` -- scheduling, coordination, and risk management

- **Tier 2 — Department leads** who own their domain
  - `game-designer`, `lead-programmer`, `art-director`, `audio-director`,
    `narrative-director`, `qa-lead`, `release-manager`, `localization-lead`

- **Tier 3 — Specialists** who execute within their domain
  - Designers, programmers, artists, writers, testers, engineers

The tiers are seniority of role. Most agents run on your session's model; the
agent file's `model` and `model_reasoning_effort` fields document which defaults
are pinned (`docs/codex-studio/model-tiers.md`). Agents without a `model` inherit the
parent session model.

### 2. Pick the Right Agent for the Job

Ask yourself: "What department would handle this in a real studio?"

| I need to... | Use this agent |
|-------------|---------------|
| Design a new mechanic | `game-designer` |
| Write combat code | `gameplay-programmer` |
| Create a shader | `technical-artist` |
| Write dialogue | `writer` |
| Plan the next sprint | `producer` |
| Review code quality | `lead-programmer` |
| Write test cases | `qa-tester` |
| Design a level | `level-designer` |
| Fix a performance problem | `performance-analyst` |
| Set up CI/CD | `devops-engineer` |
| Design a loot table | `economy-designer` |
| Resolve a creative conflict | `creative-director` |
| Make an architecture decision | `technical-director` |
| Manage a release | `release-manager` |
| Prepare strings for translation | `localization-lead` |
| Test a mechanic idea quickly | `prototyper` |
| Review code for security issues | `security-engineer` |
| Check accessibility compliance | `accessibility-specialist` |
| Get Unreal Engine advice | `unreal-specialist` |
| Get Unity advice | `unity-specialist` |
| Get Godot advice | `godot-specialist` |
| Design GAS abilities/effects | `ue-gas-specialist` |
| Define BP/C++ boundaries | `ue-blueprint-specialist` |
| Implement UE replication | `ue-replication-specialist` |
| Build UMG/CommonUI questions | `ue-umg-specialist` |
| Design DOTS/ECS architecture | `unity-dots-specialist` |
| Write Unity shaders/VFX | `unity-shader-specialist` |
| Manage Addressable assets | `unity-addressables-specialist` |
| Build UI Toolkit/UGUI screens | `unity-ui-specialist` |
| Write idiomatic GDScript | `godot-gdscript-specialist` |
| Write Godot C# code | `godot-csharp-specialist` |
| Create Godot shaders | `godot-shader-specialist` |
| Build GDExtension modules | `godot-gdextension-specialist` |
| Plan live events and seasons | `live-ops-designer` |
| Write patch notes for players | `community-manager` |
| Brainstorm a new game idea | Use `$codex-brainstorm` skill |

### 3. Use Codex skills for Common Tasks

| Command | What it does |
|---------|-------------|
| `$codex-start` | First-time onboarding — asks where you are, guides you to the right workflow |
| `$codex-help` | Context-aware "what do I do next?" — reads your current phase and artifacts |
| `$codex-project-stage-detect` | Analyze project state, detect stage, identify gaps |
| `$codex-setup-engine` | Configure engine + version, populate reference docs |
| `$codex-adopt` | Brownfield audit and migration plan for existing projects |
| `$codex-brainstorm` | Guided game concept ideation from scratch |
| `$codex-map-systems` | Decompose concept into systems, map dependencies, guide per-system GDDs |
| `$codex-design-system` | Guided, section-by-section GDD authoring for a single game system |
| `$codex-quick-design` | Lightweight spec for small changes — tuning, tweaks, minor additions |
| `$codex-review-all-gdds` | Cross-GDD consistency and game design theory review |
| `$codex-propagate-design-change` | Find ADRs and stories affected by a GDD change |
| `$codex-art-bible` | Guided, section-by-section Art Bible authoring — creates visual identity spec before asset production |
| `$codex-asset-spec` | Generate per-asset visual specifications and AI generation prompts from GDDs or character profiles |
| `$codex-ux-design` | Author UX specs (screen/flow, HUD, interaction patterns) |
| `$codex-ux-review` | Validate UX specs for accessibility and GDD alignment |
| `$codex-create-architecture` | Master architecture document for the game |
| `$codex-architecture-decision` | Creates an ADR |
| `$codex-architecture-review` | Validate all ADRs, dependency ordering, GDD traceability |
| `$codex-create-control-manifest` | Flat programmer rules sheet from Accepted ADRs |
| `$codex-create-epics` | Translate GDDs + ADRs into epics (one per architectural module) |
| `$codex-create-stories` | Break a single epic into implementable story files |
| `$codex-dev-story` | Read a story and implement it — routes to the correct programmer agent |
| `$codex-sprint-plan` | Creates or updates sprint plans |
| `$codex-sprint-status` | Quick 30-line sprint snapshot |
| `$codex-story-readiness` | Validate a story is implementation-ready before pickup |
| `$codex-story-done` | End-of-story completion review — verifies acceptance criteria |
| `$codex-estimate` | Produces structured effort estimates |
| `$codex-design-review` | Reviews a design document |
| `$codex-code-review` | Reviews code for quality and architecture |
| `$codex-balance-check` | Analyzes game balance data |
| `$codex-asset-audit` | Audits assets for compliance |
| `$codex-content-audit` | GDD-specified content vs. implemented — find gaps |
| `$codex-scope-check` | Detect scope creep against plan |
| `$codex-perf-profile` | Performance profiling and bottleneck ID |
| `$codex-tech-debt` | Scan, track, and prioritize tech debt |
| `$codex-gate-check` | Validate phase readiness (PASS/CONCERNS/NOT ASSESSED/FAIL) |
| `$codex-consistency-check` | Scan all GDDs for cross-document inconsistencies (conflicting stats, names, rules) |
| `$codex-security-audit` | Audit for security vulnerabilities: save tampering, cheat vectors, network exploits, data exposure |
| `$codex-reverse-document` | Generate design/architecture docs from existing code |
| `$codex-milestone-review` | Reviews milestone progress |
| `$codex-retrospective` | Runs sprint/milestone retrospective |
| `$codex-bug-report` | Structured bug report creation |
| `$codex-playtest-report` | Creates or analyzes playtest feedback |
| `$codex-onboard` | Generates onboarding docs for a role |
| `$codex-release-checklist` | Validates pre-release checklist |
| `$codex-launch-checklist` | Complete launch readiness validation |
| `$codex-changelog` | Generates changelog from git history |
| `$codex-patch-notes` | Generate player-facing patch notes |
| `$codex-hotfix` | Emergency fix with audit trail |
| `$codex-day-one-patch` | Prepare a focused day-one patch for known issues discovered after gold master |
| `$codex-prototype` | Concept prototype — validate core idea before writing GDDs (Phase 1) |
| `$codex-vertical-slice` | Production-quality end-to-end build — validate full game loop (Phase 4) |
| `$codex-localize` | Localization scan, extract, validate |
| `$codex-team-combat` | Orchestrate full combat team pipeline |
| `$codex-team-narrative` | Orchestrate full narrative team pipeline |
| `$codex-team-ui` | Orchestrate full UI team pipeline |
| `$codex-team-release` | Orchestrate full release team pipeline |
| `$codex-team-polish` | Orchestrate full polish team pipeline |
| `$codex-team-audio` | Orchestrate full audio team pipeline |
| `$codex-team-level` | Orchestrate full level creation pipeline |
| `$codex-team-live-ops` | Orchestrate live-ops team for seasons, events, and post-launch content |
| `$codex-team-qa` | Orchestrate full QA team cycle — test plan, test cases, smoke check, sign-off |
| `$codex-qa-plan` | Generate a QA test plan for a sprint or feature |
| `$codex-bug-triage` | Re-prioritize open bugs, assign to sprints, surface systemic trends |
| `$codex-smoke-check` | Run critical path smoke test gate before QA hand-off (PASS/FAIL) |
| `$codex-soak-test` | Generate a soak test protocol for extended play sessions |
| `$codex-regression-suite` | Map coverage to GDD critical paths, flag gaps, maintain regression suite |
| `$codex-test-setup` | Scaffold test framework + CI pipeline for the project's engine (run once) |
| `$codex-test-helpers` | Generate engine-specific test helper libraries and factory functions |
| `$codex-test-flakiness` | Detect flaky tests from CI history, flag for quarantine or fix |
| `$codex-test-evidence-review` | Quality review of test files and manual evidence — ADEQUATE/INCOMPLETE/MISSING |
| `$codex-skill-test` | Validate skill files for compliance and correctness (static / spec / audit) |
| `$codex-skill-improve` | Improve a skill using a test-fix-retest loop — diagnose, propose fix, rewrite, verify |

### 4. Use Templates for New Documents

Templates are in `docs/codex-studio/templates/`:

- `game-design-document.md` -- for new mechanics and systems
- `architecture-decision-record.md` -- for technical decisions
- `architecture-traceability.md` -- maps GDD requirements to ADRs to story IDs
  (`$codex-architecture-review` writes it to `docs/architecture/requirements-traceability.md`)
- `risk-register-entry.md` -- for new risks
- `narrative-character-sheet.md` -- for new characters
- `test-plan.md` -- for feature test plans
- `sprint-plan.md` -- for sprint planning
- `milestone-definition.md` -- for new milestones
- `level-design-document.md` -- for new levels
- `game-pillars.md` -- for core design pillars
- `art-bible.md` -- for visual style reference
- `technical-design-document.md` -- for per-system technical designs
- `post-mortem.md` -- for project/milestone retrospectives
- `sound-bible.md` -- for audio style reference
- `release-checklist-template.md` -- for platform release checklists
- `changelog-template.md` -- for player-facing patch notes
- `release-notes.md` -- for player-facing release notes
- `incident-response.md` -- for live incident response playbooks
- `game-concept.md` -- for initial game concepts (MDA, SDT, Flow, Bartle)
- `game-brief.md` -- for the one-page brief that replaces the concept doc at `rigor: minimal`
- `pitch-document.md` -- for pitching the game to stakeholders
- `economy-model.md` -- for virtual economy design (sink/faucet model)
- `faction-design.md` -- for faction identity, lore, and gameplay role
- `systems-index.md` -- for systems decomposition and dependency mapping
- `project-stage-report.md` -- for project stage detection output
- `design-doc-from-implementation.md` -- for reverse-documenting existing code into GDDs
- `architecture-doc-from-code.md` -- for reverse-documenting code into architecture docs
- `concept-doc-from-prototype.md` -- for reverse-documenting prototypes into concept docs
- `ux-spec.md` -- for per-screen UX specifications (layout zones, states, events)
- `hud-design.md` -- for whole-game HUD philosophy, zones, and element specs
- `accessibility-requirements.md` -- for project-wide accessibility tier and feature matrix
- `interaction-pattern-library.md` -- for standard UI controls and game-specific patterns
- `player-journey.md` -- for 6-phase emotional arc and retention hooks by time scale
- `difficulty-curve.md` -- for difficulty axes, onboarding ramp, and cross-system interactions
- `test-evidence.md` -- template for recording manual test evidence (screenshots, walkthrough notes)

### 5. Follow the Coordination Rules

1. Work flows down the hierarchy: Directors -> Leads -> Specialists
2. Conflicts escalate up the hierarchy
3. Cross-department work is coordinated by the `producer`
4. Agents do not modify files outside their domain without delegation
5. All decisions are documented

## First Steps for a New Project

**Don't know where to begin?** Run `$codex-start`. It asks where you are and routes
you to the right workflow. No assumptions about your game, engine, or experience level.

The paths below walk the `standard`/`full` pipeline. At `rigor: minimal` (the
default), follow [The Default Path](#the-default-path-rigor-minimal) instead.

If you already know what you need, jump directly to the relevant path:

### Path A: "I have no idea what to build"

1. **Run `$codex-start`** (or `$codex-brainstorm open`) — guided creative exploration:
   what excites you, what you've played, your constraints
   - Generates 3 concepts, helps you pick one, defines core loop and pillars
   - Produces a game concept document and recommends an engine
2. **Set up the engine** — Run `$codex-setup-engine` (uses the brainstorm recommendation)
   - Configures AGENTS.md, detects knowledge gaps, populates reference docs
   - Writes engine, naming conventions, and performance budgets to `project.yaml`
     (the source of truth), mirrored to `docs/codex-studio/technical-preferences.md`
   - If the engine version is newer than the LLM's training data, it fetches
     current docs from the web so agents suggest correct APIs
3. **Validate the concept** — Run `$codex-design-review design/gdd/game-concept.md`
   (or `design/game-brief.md`, if `$codex-brainstorm` wrote the one-page brief)
4. **Decompose into systems** — Run `$codex-map-systems` to map all systems and dependencies
5. **Design each system** — Run `$codex-design-system [system-name]` (or `$codex-map-systems next`)
   to write GDDs in dependency order
6. **Prototype the mechanic** — Run `$codex-prototype [core-mechanic]` (1–3 days — before writing GDDs)
7. **Design each system** — Run `$codex-design-system [system-name]` to write GDDs, informed by prototype findings
8. **Plan the first sprint** — After architecture and `$codex-vertical-slice`, run `$codex-sprint-plan new`
9. Start building

### Path B: "I know what I want to build"

If you already have a game concept and engine choice:

1. **Set up the engine** — Run `$codex-setup-engine [engine] [version]`
   (e.g., `$codex-setup-engine godot 4.6`) — also creates technical preferences
2. **Write the Game Pillars** — delegate to `creative-director`
3. **Decompose into systems** — Run `$codex-map-systems` to enumerate systems and dependencies
4. **Design each system** — Run `$codex-design-system [system-name]` for GDDs in dependency order
5. **Create the initial ADR** — Run `$codex-architecture-decision`
6. **Create the first milestone** in `production/milestones/`
7. **Plan the first sprint** — Run `$codex-sprint-plan new`
8. Start building

### Path C: "I know the game but not the engine"

If you have a concept but don't know which engine fits:

1. **Run `$codex-setup-engine`** with no arguments — it will ask about your game's
   needs (2D/3D, platforms, team size, language preferences) and recommend
   an engine based on your answers
2. Follow Path B from step 2 onward

### Path D: "I have an existing project"

If you have design docs, prototypes, or code already:

1. **Run `$codex-start`** (or `$codex-project-stage-detect`) — analyzes what exists,
   identifies gaps, and recommends next steps
2. **Run `$codex-adopt`** if you have existing GDDs, ADRs, or stories — audits
   internal format compliance and builds a numbered migration plan to fill gaps
   without overwriting your existing work
3. **Configure engine if needed** — Run `$codex-setup-engine` if not yet configured
4. **Validate phase readiness** — Run `$codex-gate-check` to see where you stand
5. **Plan the next sprint** — Run `$codex-sprint-plan new`

## File Structure Reference

```
AGENTS.md                          -- Master config (read this first, ~80 lines)
project.yaml                       -- Machine-readable project config (engine, modes, stage) — source of truth
.codex/
  config.toml                     -- tracked project defaults for Codex agents
  agents/                         -- 49 project-scoped agent definitions (TOML)
.agents/
  skills/                         -- 75 Codex skills (SKILL.md frontmatter)
tools/codex-studio/                       -- explicit validators and configuration helpers
docs/codex-studio/                        -- workflow docs, rules, gates, and templates
```

Codex also discovers the root and nested `AGENTS.md` files. Personal overrides
belong in the ignored `AGENTS.override.md`; this repository does not register a
legacy runtime settings file or assume an automatic hook runtime.
