# Codex Skill Catalog

All skills use the `codex-` namespace while preserving the original workflow
responsibilities. Role names remain professional discipline names; see
`.codex/agents/`.

| Skill | Original name | Purpose |
| --- | --- | --- |
| `$codex-adopt` | `adopt` | Brownfield audit — do existing artifacts actually work? Numbered migration plan. Unlike $codex-project-stage-detect, checks compliance not existence. |
| `$codex-architecture-decision` | `architecture-decision` | Create an ADR documenting a technical decision: context, alternatives considered, consequences. |
| `$codex-architecture-review` | `architecture-review` | Traceability matrix mapping GDD requirements to ADRs. Finds gaps, cross-ADR conflicts, engine compatibility. PASS/CONCERNS/NOT ASSESSED/FAIL. |
| `$codex-art-bible` | `art-bible` | Author the Art Bible — visual identity gating asset production. Run before $codex-map-systems. |
| `$codex-asset-audit` | `asset-audit` | Audit assets against naming conventions, file size budgets, format standards. Finds orphaned assets, missing references. |
| `$codex-asset-spec` | `asset-spec` | Per-asset visual specs plus AI generation prompts from GDDs and character profiles. After the art bible. |
| `$codex-balance-check` | `balance-check` | Find balance outliers, broken progressions, degenerate strategies, economy imbalances in formulas and data. 'Check game balance'. |
| `$codex-brainstorm` | `brainstorm` | Guided concept ideation using professional studio techniques, player psychology, creative exploration. |
| `$codex-bug-report` | `bug-report` | Structured bug report from a description, or analyze code for potential bugs. Reproduction steps, severity. |
| `$codex-bug-triage` | `bug-triage` | Re-evaluate open bugs — priority vs severity, assign to sprints, surface systemic trends. Run when the count grows. |
| `$codex-changelog` | `changelog` | Auto-generate a changelog from git commits and sprint data. Internal and player-facing versions. |
| `$codex-code-review` | `code-review` | Architectural code review — coding standards, SOLID, testability, performance concerns. |
| `$codex-consistency-check` | `consistency-check` | Scan GDDs against the entity registry for cross-document conflicts. Grep-first approach targets conflicting sections, different stats. |
| `$codex-content-audit` | `content-audit` | Audit GDD content counts against what's implemented — planned vs built. |
| `$codex-create-architecture` | `create-architecture` | Author the architecture blueprint before code is written. Validates decisions against the pinned engine, flags knowledge gaps. |
| `$codex-create-control-manifest` | `create-control-manifest` | Flat must-do/never-do rules sheet per system and layer, extracted from Accepted ADRs. ADRs explain why; this is actionable. |
| `$codex-create-epics` | `create-epics` | Turn GDDs plus architecture into epics — one per architectural module, with untraced requirements. Then $codex-create-stories [epic-slug]. |
| `$codex-create-stories` | `create-stories` | Break one epic into implementable stories embedding TR-ID, ADR guidance, acceptance criteria. Reads the control manifest. After $codex-create-epics. |
| `$codex-day-one-patch` | `day-one-patch` | Day-one launch patch — focused fix for known issues found after gold master. Mini-sprint with QA gate and rollback. |
| `$codex-design-review` | `design-review` | Reviews one design document for completeness, internal consistency, implementability, and design standards. Before handing to programmers. |
| `$codex-design-system` | `design-system` | Section-by-section GDD authoring for one system — walks through each required section, cross-references dependencies. |
| `$codex-dev-story` | `dev-story` | Implement a story: ADR guidelines, right programmer agent, code plus test. Then $codex-story-done ($codex-story-readiness before, $codex-code-review after, at standard/full). |
| `$codex-estimate` | `estimate` | Estimate task effort from complexity, dependencies, velocity, risk. Structured estimate with confidence levels. |
| `$codex-gate-check` | `gate-check` | Ready to advance between development phases? PASS/CONCERNS/NOT ASSESSED/FAIL with blockers and required artifacts. 'Can we move to production?' |
| `$codex-help` | `help` | What should I do next? Use when stuck or you don't know what to do. |
| `$codex-hotfix` | `hotfix` | Emergency fix bypassing normal sprint process — hotfix branch, approvals tracked, backport verified, full audit trail. |
| `$codex-launch-checklist` | `launch-checklist` | Launch readiness across every department: code, content, store, marketing, community, infrastructure, legal, go/no-go sign-offs. |
| `$codex-localize` | `localize` | Localization pipeline — find hardcoded strings, extract string tables, cultural review, VO, RTL, enforce string freeze. |
| `$codex-map-systems` | `map-systems` | Decompose a concept into individual systems, map dependencies, prioritize design order, create the systems index. |
| `$codex-milestone-review` | `milestone-review` | Milestone progress review — completeness, quality metrics, risk, go/no-go recommendation. At checkpoints or before a deadline. |
| `$codex-onboard` | `onboard` | Onboarding doc for a new contributor or agent — project state, conventions, priorities relevant to the specified role. |
| `$codex-patch-notes` | `patch-notes` | Player-facing patch notes from git history and changelogs. Translates developer language into player communication. |
| `$codex-perf-profile` | `perf-profile` | Performance profiling — find bottlenecks, measure against budgets, produce ranked optimization recommendations. |
| `$codex-playtest-report` | `playtest-report` | Structured playtest report template, or turn existing playtest notes into structured feedback. |
| `$codex-project-stage-detect` | `project-stage-detect` | Analyze project state, detect stage, identify gaps, recommend next steps. 'Where are we in development?' |
| `$codex-propagate-design-change` | `propagate-design-change` | A GDD changed — scan ADRs and the traceability index for now-stale architectural decisions. Impact report, guides resolution. |
| `$codex-prototype` | `prototype` | Concept prototype before GDDs — throwaway HTML, Engine or Paper build, PROCEED/PIVOT/KILL/NOT ASSESSED. After $codex-brainstorm and $codex-setup-engine. |
| `$codex-qa-plan` | `qa-plan` | QA test plan for a sprint — classifies stories by Logic/Integration/Visual/UI, covers automated tests, manual cases, smoke scope. |
| `$codex-quick-design` | `quick-design` | Lightweight spec for small changes — tuning adjustments, minor mechanics. Embeds directly into stories; skips full GDD. |
| `$codex-regression-suite` | `regression-suite` | Map test coverage to GDD critical paths, find fixed bugs lacking regression tests, flag drift from new features. |
| `$codex-release-checklist` | `release-checklist` | Pre-release checklist — build verification, certification requirements, store metadata, launch readiness. |
| `$codex-retrospective` | `retrospective` | Sprint or milestone retrospective from completed work, velocity, blockers. Actionable insights for the next iteration. |
| `$codex-reverse-document` | `reverse-document` | Generate missing design or architecture docs from existing implementation — works backwards from code and prototypes. |
| `$codex-review-all-gdds` | `review-all-gdds` | Holistic cross-GDD review — contradictions between systems, dominant strategies, economic imbalance, cognitive overload, pillar drift. |
| `$codex-scope-check` | `scope-check` | Scope creep check — current scope versus the original plan. Flags additions, quantifies bloat, recommends cuts. 'Any scope creep?' |
| `$codex-security-audit` | `security-audit` | Security audit — save tampering, cheat vectors, network exploits, data exposure, input validation. Before public or multiplayer release. |
| `$codex-settings` | `settings` | View or change project config — effective merged values, or set locally in project.local.yaml. |
| `$codex-run` | `run` | Run one state-aware workflow step, stop safely on blockers, and save a recoverable checkpoint. |
| `$codex-setup-engine` | `setup-engine` | Configure engine and version. Pins it in AGENTS.md; web search fills reference docs when the version is beyond LLM training data. |
| `$codex-skill-improve` | `skill-improve` | Improve one Codex skill through a measured test, review, edit, and retest loop. |
| `$codex-skill-test` | `skill-test` | Validate Codex skill files and project-scoped agent definitions for structure and documented behavior. |
| `$codex-smoke-check` | `smoke-check` | Critical-path smoke gate before QA hand-off — runs the automated suite. A failed check means the build is not QA-ready. |
| `$codex-soak-test` | `soak-test` | Soak test protocol for extended play — what to observe and log for slow leaks, fatigue, late-appearing edge cases. |
| `$codex-sprint-plan` | `sprint-plan` | New or updated sprint plan from the current milestone, completed work, and available capacity. |
| `$codex-sprint-status` | `sprint-status` | Fast, concise sprint snapshot — burndown and emerging risks for situational awareness. 'How is the sprint going?' |
| `$codex-start` | `start` | First-time onboarding — asks where you are, then guides you to the right workflow. |
| `$codex-story-done` | `story-done` | End-of-story completion review — verifies each acceptance criterion, checks GDD/ADR deviations, prompts code review, updates status. |
| `$codex-story-readiness` | `story-readiness` | Is a story implementation-ready? Checks clear acceptance criteria, open questions, ADR refs. READY/NEEDS WORK/BLOCKED/NOT ASSESSED. |
| `$codex-team-audio` | `team-audio` | Orchestrate the audio team — audio-director, sound-designer, technical-artist, gameplay-programmer — direction through implementation. |
| `$codex-team-combat` | `team-combat` | Orchestrate the combat team — game-designer, gameplay-programmer, ai-programmer, technical-artist, sound-designer, qa-tester — design through implement and validate. |
| `$codex-team-level` | `team-level` | Orchestrate the level team — level-designer, narrative-director, world-builder, art-director, systems-designer, qa-tester — for complete area creation. |
| `$codex-team-live-ops` | `team-live-ops` | Orchestrate the live-ops team — live-ops-designer, economy-designer, analytics-engineer, community-manager, writer — for a season or live event. |
| `$codex-team-narrative` | `team-narrative` | Orchestrate the narrative team — narrative-director, writer, world-builder, level-designer — for story, world lore, narrative-driven levels. |
| `$codex-team-polish` | `team-polish` | Orchestrate the polish team — performance-analyst, technical-artist, sound-designer, qa-tester — to optimize and harden a feature or area. |
| `$codex-team-qa` | `team-qa` | Orchestrate the QA team through a full testing cycle — qa-lead strategy and test plan, qa-tester case writing, execution, sign-off. |
| `$codex-team-release` | `team-release` | Orchestrate the release team — release-manager, qa-lead, devops-engineer, producer — to execute a release from candidate to deployment. |
| `$codex-team-ui` | `team-ui` | Orchestrate the UI team through the UX pipeline — authoring, visual design, implementation, review, polish. Uses $codex-ux-design, $codex-ux-review, studio templates. |
| `$codex-tech-debt` | `tech-debt` | Track, categorize and prioritize technical debt across the codebase — scans for debt indicators, maintains a register. |
| `$codex-test-evidence-review` | `test-evidence-review` | Quality review of test files and evidence — goes beyond existence, evaluates assertion coverage. ADEQUATE/INCOMPLETE/MISSING/NOT ASSESSED per story. |
| `$codex-test-flakiness` | `test-flakiness` | Find flaky tests from CI logs — aggregates pass rates, spots intermittent failures, recommends quarantine. After multiple runs. |
| `$codex-test-helpers` | `test-helpers` | Generate engine-specific test helper libraries — assertion utilities, factory functions, mocks in the engine's test folder. Reduces boilerplate. |
| `$codex-test-setup` | `test-setup` | Scaffold the test framework and CI — tests/ directory, engine test runner, GitHub Actions workflow. Once, before the first sprint. |
| `$codex-ux-design` | `ux-design` | Section-by-section UX spec authoring for a screen, flow or HUD. Reads the player journey to provide context; also project-wide accessibility. |
| `$codex-ux-review` | `ux-review` | Validate a UX spec, HUD design or pattern library — accessibility, GDD alignment, readiness. APPROVED / NOT ASSESSED / NEEDS REVISION / MAJOR REVISION NEEDED. |
| `$codex-vertical-slice` | `vertical-slice` | Pre-production validation — end-to-end build to confirm the full loop is achievable before committing to Production. After GDDs, architecture, UX specs. |
