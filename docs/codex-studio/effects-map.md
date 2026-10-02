# project.yaml — Effects Map

> ## READ ONE SECTION, NEVER THIS WHOLE FILE
>
> This is a long reference organized into setting sections headed `## <key>`.
> Read the relevant section rather than loading the entire file into context.
>
> To look up a setting:
>
> ```
> rg -n -A 40 -- '^## modes.review_mode' 'docs/codex-studio/effects-map.md'
> ```
>
> Read the section for your key and stop. The same rule the skills already apply
> to their own reference files — `$codex-gate-check` loads only the row for the target
> phase and says "never load the others" — applies here, and this is the largest
> file in the framework by a factor of seven.
>
> This banner exists because six skills cite this document and **none of them
> scoped the citation**. A link to the complete schema is not a request to
> read all sections; keep the read bounded to the setting being evaluated.

This document defines what each `project.yaml` setting actually does across
every skill that reads it. It is the tracked, authoritative reference.

**Purpose:** When a skill reads a setting, this document is the authoritative
source for what each value means for that skill's behavior. Implementers update
this file when adding a new setting or changing how a skill responds to one.

**Format per setting:**
- Priority chain — which source wins when multiple are present
- Per-value intent — what the value means in plain terms
- Skill behavior table — exactly what changes per skill per value

**Coverage scope:** This document covers the skills most affected by each setting.
Skills not listed (e.g. `codex-ux-review`, `codex-balance-check`, `codex-test-flakiness`, `codex-test-helpers`,
`codex-test-setup`, `codex-soak-test`, `codex-perf-profile`, `codex-launch-checklist`, `codex-release-checklist`,
`codex-skill-test`, `codex-skill-improve`, `codex-vertical-slice`) are not meaningfully affected by
`project.yaml` settings and do not need entries here. Add a skill only when its
behavior genuinely branches on a setting value.

**Local override pattern:** `project.yaml` is committed to git as the shared team
config. Per-developer overrides live in `project.local.yaml` (gitignored). Priority
chain across all settings: `project.local.yaml` → `project.yaml` → legacy mirror →
`modes.rigor` expansion → hardcoded default. The expansion step applies only to the
six knobs `rigor` fronts (`modes.workflow`, `docs.density`, `qa.level`,
`modes.story_granularity`, `modes.review_mode`, `team.size`), which for that reason have **no** hardcoded default —
see the `modes.rigor` section.
**Secrets do NOT belong in either file — use environment variables.** See the
"Local Override Pattern" section below for full design including the whitelist of
which settings can be locally overridden.

---

## Local Override Pattern — `project.local.yaml`

The `project.local.yaml` file lets each developer override specific settings for
their own use without affecting the team. The file is gitignored and never
committed.

### How it works

Priority chain (every setting): `project.local.yaml` → `project.yaml` → hardcoded default

If a setting is present in `project.local.yaml`, that value wins. If absent, the
value from `project.yaml` is used. If absent there too, the hardcoded default
takes over.

---

### Deep merge semantics

When both files set a nested value, only the explicitly-set key is overridden.
Sibling keys in the same block are preserved.

Example:

`project.yaml`:
```yaml
testing:
  strict:
    logic: true
    integration: true
    visual: false
```

`project.local.yaml` (sparse override):
```yaml
testing:
  strict:
    logic: false
```

Effective config seen by skills: `logic: false, integration: true, visual: false`.
Only the explicitly-set `logic` key is overridden; sibling keys come through from
`project.yaml`.

---

### Whitelist — which settings can be locally overridden

Only personal-experience settings can be locally overridden. Project-wide facts
(engine, stage, naming conventions, what's required on disk) are locked to
`project.yaml` because divergence between developers would break team coordination.

The rule for deciding which side a setting belongs on:

> **If a setting affects what artifacts exist or what they look like on disk,
> it must be locked to `project.yaml`. If a setting only changes your personal
> experience (which agents spawn for you, whether you get prompts, your local
> CI bypass), it can be locally overridden.**

**Locally overridable** (personal experience only — no effect on artifacts on disk):

| Setting | Why local override makes sense |
|---------|-------------------------------|
| `modes.review_mode` | How much AI review you personally want |
| `modes.automation` | How often the AI prompts you |
| `modes.automation_always_ask` | Your personal safety categories |
| `team.size` | Which agents spawn for your reviews (review depth differs, artifacts don't) |
| `testing.strict.*` (each type) | Whether failures block your local work (CI still enforces project.yaml defaults) |
| `performance.enforce` | Whether budget violations block your local work (CI enforces project defaults) |
| `features.session_state` | RESERVED compatibility value; no session-tracking effect |
| `features.token_budget_warn_at` | RESERVED compatibility value; no monitoring effect |

**Locked to `project.yaml`** (project-wide — would create artifact divergence if local):

| Setting | Why it must be project-wide |
|---------|----------------------------|
| `schema_version`, `framework.*` | File metadata, not preferences — **exempt from the report below**, since a `project.local.yaml` carrying `schema_version: 1` is correct as written |
| `project.name`, `version`, `genre`, `kind`, `stage` | Project identity |
| `engine.*`, `specialists.*` | Whole team must use same engine |
| `naming.*` | Code conventions must be consistent across team |
| `platform.*` | Game facts (what platforms it ships on) |
| `performance.target_framerate`, `frame_budget_ms`, `draw_call_limit`, `memory_ceiling_mb` | Game budgets, shared targets |
| `accessibility.target` | Game commitment, project-wide |
| `cadence.*` | Sprint/milestone length affects team coordination |
| `modes.rigor` | Fronts the four below — locked for the same reason they are |
| `modes.workflow` and `workflow_overrides` | Affects which sections are required in authored docs |
| `modes.story_granularity` | Affects how big stories are in repo — team must be consistent |
| `docs.density` | Affects how deep authored docs are — team must produce consistent docs |
| `qa.level` | Affects what test evidence stories must include on disk |
| `qa.coverage_minimum` | Project quality bar |
| `strict_gate_checks` | Affects whether `project.stage` advances — a project-wide write |
| `commands.*` | Build/test commands are project facts |
| `testing.framework` | Whole project uses one framework |

> **A locked key written into `project.local.yaml` by hand is reported, not
> swallowed.** `$codex-settings --local` refuses to write one, but the
> file is meant to be hand-edited and that path had no guard: `modes.rigor: full`
> there is a real key with a legal value, so enum validation passes it, and then
> resolution never consults the local file for that path — the setting vanishes
> and the user sees the default they were trying to override, with no error
> anywhere. Every check validated the **value**; nothing validated the
> **location**. `validate_local_scope` in `yaml-helper.sh` now names such keys on
> `resolve_config`'s `notes:` line. It **warns and never reconciles**: it does not
> edit the file, does not begin honouring the key, and does not change
> resolution — a locked setting decides which artifacts exist on disk, so
> applying one quietly would produce exactly the divergence this table prevents.
> A clean file stays silent — you are only told when a key is actually in the
> wrong place.

---

### `$codex-settings --local` flag behavior

```
$codex-settings workflow=minimal               → writes to project.yaml (team-wide)
$codex-settings --local automation=autonomous  → writes to project.local.yaml (just you)
```

**Behavior rules:**

- Default (no flag): writes to `project.yaml`
- `--local` flag: writes to `project.local.yaml` (creates it if absent)
- `--local` on a locked setting → error:
  > *"`<setting>` cannot be locally overridden — it's a project-wide setting.
  > Use `$codex-settings <setting>=<value>` (no `--local`) to change it for the whole team."*
- Writing to `project.yaml` when the same setting is currently locally overridden → warning:
  > *"This setting is currently locally overridden in `project.local.yaml`.
  > Writing to `project.yaml` will not affect your effective value."*

---

### Schema validation on read

When skills or explicit configuration helpers read either file:

| Issue | Behavior |
|-------|----------|
| Unknown key (typo or stale setting) | An explicitly invoked skill should flag the unknown key when it detects one. The configuration helper is not a complete schema validator, and no session-start check runs. Do not claim a warning or rejection unless it was actually observed. |
| Invalid value not in enum (e.g. `automation: chaotic`) | Hard error: skill exits with explanation of valid values. |
| Type mismatch (e.g. integer field set to a string) | Hard error: skill exits with type expected. |

---

### Creation and error handling

| Scenario | Behavior |
|----------|----------|
| `$codex-start` on fresh project | Creates `project.yaml` only. Does NOT create `project.local.yaml`. |
| `$codex-settings --local <x>=<y>` when local.yaml doesn't exist | Creates `project.local.yaml` containing just that setting. |
| `project.local.yaml` exists but `project.yaml` doesn't | Hard error: *"`project.yaml` missing — run `$codex-start` to create one. Local overrides require a base."* |
| Both files exist | Read `project.yaml` first, deep-merge `project.local.yaml` on top. Normal operation. |
| Both files set the same key | `project.local.yaml` wins. No prompting. |

---

### Two-developer clash scenarios — and why the whitelist prevents them

**File-level conflict (`project.yaml`):**
Standard git merge conflict. Each developer's `project.local.yaml` is gitignored
and never collides with another developer's. Normal git workflow handles team-wide
changes.

**Logical inconsistency (prevented by whitelist):**

Example of what the whitelist prevents:

> Sarah sets `modes.workflow: minimal` locally to skip GDD requirements. She
> doesn't write GDDs because her local mode doesn't require them. Mike runs
> `$codex-gate-check` with the team's `project.yaml` value, `standard`; gate-check sees missing
> GDDs and fails.

This can't happen because `modes.workflow` is locked to `project.yaml`. Same
for `qa.level`, `docs.density`, `strict_gate_checks`, `naming.*`, and every
other setting that affects what artifacts exist on disk.

Personal experience settings (`automation`, `review_mode`, `team.size`,
`testing.strict.*`, `performance.enforce`) can diverge freely without affecting
anyone else.

---

### Stricter reviewer reviewing a looser reviewer's work

A common worry: "what if my teammate has stricter review settings than me?
Will their `$codex-gate-check` or `$codex-design-review` flag things in my work?"

The answer depends on which kind of difference you're talking about:

**Different review depth, same project requirements (HEALTHY):**

- Teammate A: local `review_mode: full`, `automation: collaborative`, `testing.strict.logic: true`
- Teammate B: local `review_mode: solo`, `automation: autonomous`, `testing.strict.logic: false`
- Both bound by the same project.yaml-locked settings (e.g. `workflow: standard`, `qa.level: standard`)

B writes a GDD that meets `workflow: standard` (all 5 required sections present).
B's `$codex-design-review` runs with `review_mode: solo` — fast advisory check, no
specialists spawned. B moves on.

Later A reviews the same GDD with `review_mode: full` — spawns 5–15 specialists,
finds polish opportunities and edge cases B's lighter review missed. A files
findings as PR comments or follow-up issues. B addresses the ones that matter.

**This is normal team collaboration.** Different reviewers catching different
things is the value of having multiple reviewers. The artifacts on disk are the
same; only review depth differs. Nothing about this scenario creates project-state
divergence.

**Different requirements (PREVENTED by the whitelist):**

If `qa.level` were locally overridable:

- B sets `qa.level: minimal` locally. B's stories don't include test evidence.
- B's `$codex-story-done` accepts the story without evidence. Story marked Complete on disk.
- A pulls. A's `qa.level: standard` requires evidence. A's `$codex-story-done` would have rejected it.
- A's next `$codex-gate-check` fails because evidence is missing across multiple of B's "Complete" stories.

This is the artifact divergence problem. To prevent it, `qa.level` is locked to
`project.yaml`. The team agrees together on what's required; individuals override
only their personal experience, never the team's standards.

**The pattern to remember:**

| Difference type | Outcome |
|----------------|---------|
| Different review depth (review_mode, team.size) | Stricter reviewer surfaces more findings — healthy. Artifacts unchanged. |
| Different local strictness on failures (testing.strict.*, performance.enforce) | Stricter dev's local $codex-story-done blocks earlier — they fix it locally. CI uses project.yaml defaults so team-wide quality bar stays. |
| Different artifact requirements (workflow, qa.level, docs.density, etc.) | **Can't happen — these are locked.** Team agrees once in project.yaml. |

---

### CI behavior

CI environments have no `project.local.yaml` — the file is gitignored and never
present in a fresh clone. CI therefore always runs against `project.yaml`
defaults: strict project standards, no developer-specific overrides.

This is intentional and important:

| Setting | Local default for fast iteration | CI default (`project.yaml`) |
|---------|----------------------------------|------------------------------|
| `modes.review_mode` (locally overridable) | `solo` for one developer | `lean` (a team's usual choice — phase gates always run) |
| `testing.strict.logic` (locally overridable) | `false` for fast WIP commits | `true` (failing tests block CI) |
| `modes.automation` (locally overridable) | `autonomous` for solo flow | `collaborative` (the team's collab protocol, but CI doesn't ask questions anyway — this is mostly a no-op on CI) |

A developer can iterate locally with relaxed gates, but CI catches issues using
the strict project defaults. The team's quality bar is enforced at the CI level
regardless of any individual developer's local config.

---

### Secrets — never in either file

`project.yaml` and `project.local.yaml` are for **preferences and configuration**,
never for **secrets**. API keys, tokens, and credentials belong in:

- **Environment variables** (preferred for production/CI)
- **`.env` file** (gitignored, local dev)
- **OS keychain** (when integrating with services that support it)

When a skill needs an API key (e.g. `$codex-asset-spec` calling Midjourney), it reads
from the environment, not from `project.yaml`. `project.yaml` only stores **which**
generator is used (`art.generator: midjourney`), not the API key for it.

CI environments typically have no `project.local.yaml` (gitignored, not in the
clone) — so CI always runs against `project.yaml` defaults. This is correct
behavior: strict project defaults for CI, looser developer overrides for local work.

---

## modes.review_mode

**Controls:** How many specialist and director agents are spawned during skill execution
**Values:** `full` | `lean` | `solo`
**Default:** *none* — supplied by `modes.rigor` (`minimal`, the default, yields `solo`; `standard` yields `lean`; `full` yields `full`)
**Set by:** `$codex-settings`, or `migrate-v1-config.sh` (which `$codex-adopt` runs) when it carries over a v1.0 `production/review-mode.txt`. `$codex-start` and `$codex-adopt` never write it themselves — unset, it follows `modes.rigor`
**Read by:** See skill table below

**Priority chain (all skills):** inline argument flag → `modes.review_mode` in `project.yaml` → `production/review-mode.txt` (legacy fallback) → `modes.rigor` expansion (no terminal default; `minimal`→`solo`, `standard`→`lean`, `full`→`full`)

> **design-review follows the standard chain.** `modes.review_mode` controls
> design-review depth, its inline flag is `--review` for consistency with every
> other review-mode-aware skill, and with nothing set it follows `modes.rigor` like
> them: `solo` at `minimal` (the default), `lean` at `standard`.

> **Hotfix / day-one-patch exception:** These skills are emergency or release-critical
> pipelines. They are never gated by `review_mode` — all agents always run.

> **Known inertness — `full` and `lean` barely differ in the nine `team-*`
> orchestrators.** Each documents a three-way split: `full` spawns every director
> and lead gate, `lean` skips director gates *unless* they are PHASE-GATE type,
> `solo` skips gate spawning entirely. But the director gates the team skills name
> are the four PHASE-GATEs, which `lean` keeps — and no team pipeline spawns one
> (`$codex-gate-check` is their only spawner). Two things differ: `$codex-team-release`'s
> technical-director release sign-off runs only at `full`, and `$codex-team-narrative` at
> `team.size: small` adds `localization-lead` and `world-builder` only at `full`.
>
> `solo` genuinely differs, and outside the orchestrators (`$codex-design-review`,
> `$codex-architecture-review`) all three levels differ as documented.
>
> **This is recorded, not fixed.** Making `lean` mean something in the
> orchestrators requires deciding which non-phase-gate reviewers each of the nine
> should call at `full` — a design decision about review depth, not a wording fix,
> and one that changes how many agents a run spawns.

---

### Value intent

| Value | Intent |
|-------|--------|
| `full` | All director and specialist gates active. Best for teams, learning, or anyone who wants thorough AI feedback on every decision. |
| `lean` | Phase gates only — per-skill director sign-offs skipped. The `rigor: standard` value. Balances quality with token cost. |
| `solo` | No gates, no director spawns (a pipeline's own review, such as `$codex-team-narrative`'s ND-CONSISTENCY, still runs). Fastest. For confident solo iteration. The default, from `rigor: minimal`. |

---

### Core skills (currently review-mode aware)

| Skill | full | lean | solo |
|-------|------|------|------|
| **codex-design-review** | 5–15 specialist agents spawned in Phase 3b | No specialist agents — single-session analysis only | Phases 1–4 only, no delegation, no next-steps prompt |
| **codex-gate-check** | Director panel runs in parallel — **width set by `modes.workflow`**, not by this axis | Director panel runs in parallel — same width rule; phase gates always run | Artifact existence checks only, no directors spawned |
| **codex-design-system** | All section specialists + CD-GDD-ALIGN sign-off gate | Specialists for Sections D and H only (+ G when its knobs interact, + Visual/Audio when visual feedback is central); CD-GDD-ALIGN skipped | No section specialists; CD-GDD-ALIGN skipped |
| **codex-art-bible** | All section specialists + AD-ART-BIBLE sign-off gate | All section specialists, AD-ART-BIBLE skipped | All section specialists, AD-ART-BIBLE skipped |
| **codex-architecture-decision** | Engine specialist + TD-ADR gate | Engine specialist; TD-ADR skipped | Engine specialist; TD-ADR skipped |
| **codex-create-architecture** | TD-ARCHITECTURE + LP-FEASIBILITY agents, in parallel | Both skipped | Both skipped |
| **codex-brainstorm** | CD-PILLARS, AD-CONCEPT-VISUAL, TD-FEASIBILITY, PR-SCOPE | All skipped | All skipped |
| **codex-map-systems** | TD-SYSTEM-BOUNDARY, PR-SCOPE, CD-SYSTEMS | All skipped | All skipped |
| **codex-story-done** | QL-TEST-COVERAGE + LP-CODE-REVIEW | Both skipped | Both skipped |
| **codex-sprint-plan** | PR-SPRINT feasibility check | Skipped | Skipped |
| **codex-create-epics** | PR-EPIC scope check | Skipped | Skipped |
| **codex-create-stories** | QL-STORY-READY + test case specs | Skipped | Skipped |
| **codex-prototype** | CD-PLAYTEST review — APPROVE keeps the recommendation; CONCERNS and REJECT go to the user, who decides | Skipped — the recommendation stands unreviewed | Skipped — the recommendation stands unreviewed |
| **codex-milestone-review** | PR-MILESTONE feasibility check | Skipped — no producer verdict | Skipped — no producer verdict |
| **codex-playtest-report** | CD-PLAYTEST creative assessment | Skipped | Skipped |
| **codex-story-readiness** | QL-STORY-READY acceptance criteria check | Skipped | Skipped |
| **codex-create-control-manifest** | TD-MANIFEST (technical-director) review | Skipped | Skipped |
| **codex-propagate-design-change** | TD-CHANGE-IMPACT (technical-director) review | Skipped | Skipped |

---

### Skills to be made review-mode aware (currently ignore the setting)

| Skill | full | lean | solo |
|-------|------|------|------|
| **codex-review-all-gdds** | Phase 2 consistency pass + Phase 3 design theory pass (parallel) | Phase 2 consistency pass only, Phase 3 skipped | Phase 2 only, Phase 3 skipped |
| **codex-architecture-review** | Engine specialist + security-engineer (if online features) | Both skipped | Both skipped |
| **codex-dev-story** | Core programmer routing always runs + engine-specialist escalation on HIGH risk stories | Core programmer routing always runs, engine-specialist escalation skipped | Core programmer routing always runs, engine-specialist escalation skipped |
| **codex-code-review** | Language, shader, UI specialists + qa-tester | All optional specialists skipped | All optional specialists skipped |
| **codex-security-audit** | security-engineer spawned | Skipped | Skipped |

---

### Team orchestration skills (pipeline behavior — different relationship)

Team skills are execution pipelines, not review gates. In them `review_mode` sets
only director-gate depth; `team.size` picks the agents (see `## team.size`), and a
pipeline's own review steps run in every mode.

| Skill | full | lean | solo |
|-------|------|------|------|
| **All nine `team-*`** | Every director gate the pipeline names | PHASE-GATE-type gates only | No director gates |
| **codex-team-release** | + technical-director release sign-off before the go/no-go call | Sign-off not run — recorded as `not run (review_mode: lean)` | Sign-off not run — recorded as `not run (review_mode: solo)` |
| **codex-team-narrative** | ND-CONSISTENCY; at `team.size: small`, + `localization-lead` and `world-builder` | ND-CONSISTENCY; at `small`, `narrative-director` + `writer` only | ND-CONSISTENCY still runs when `narrative-director` is active |

---

### Special cases and notes

- **codex-gate-check** is the only skill where `full` and `lean` behave identically —
  phase gates always run. Only `solo` skips them. This is intentional: phase
  gates are the minimum quality bar, not optional extras. **How many directors
  run is a separate axis** — `modes.workflow` sets panel width (`minimal` → PR
  only, `standard` → TD + PR, `full` → all four) to match review breadth to
  project complexity rather than always dispatching four roles. Width never
  softens a verdict: the strictest verdict from
  whoever ran still wins, and `$codex-gate-check` names the perspectives it skipped.
- **codex-art-bible** always spawns its section specialists regardless of mode — only
  the final sign-off gate is controlled by `review_mode`. Specialist delegation is
  mandatory for the authoring output to be useful, and that has not changed.
  **codex-design-system** is different: `lean` keeps the specialists for its high-risk
  sections only (D and H, plus G and Visual/Audio when they matter) and `solo`
  drafts every section without one, and each skipped spawn is announced by name.
  What sets `codex-art-bible`'s **spawn count** is therefore not `review_mode`
  but (a) `modes.workflow`, via how many sections get authored at all — `standard`
  requires sections 1–4, not all 9, and Phase 1 recommends the tier's set — and
  (b) batching consecutive sections that call the *same* agent with the *same*
  input into one delegation (2–4, and 5–6). Unbatched, sections 5 and 6 spawn
  `art-director` twice with the identical `sections 1–4` brief. Every section is
  still specialist-authored; per-section approval and write-to-file are unchanged.
- **codex-dev-story** core programmer routing (gameplay-programmer, ui-programmer, etc.)
  always runs regardless of mode — only the optional engine-specialist escalation
  for HIGH risk stories is gated.
- **codex-hotfix** and **codex-day-one-patch** are exempt — all agents always run.
- When a gate is skipped, skills emit: `"[GATE-ID] skipped — [mode] mode."` before
  proceeding. This is consistent across all skills.

---

## modes.rigor

**Controls:** How much process the project carries overall — the single question
`$codex-start` asks that sets the six knobs below
**Values:** `minimal` | `standard` | `full`
**Default:** `minimal` — see the rationale block above `_yaml_helper_defaults`
in `tools/codex-studio/config/yaml-helper.sh`. Short version: the heavier tier cost several
times more to reach working code without producing a better result.
**Set by:** `$codex-start` (Phase 3d), `$codex-settings`
**Read by:** nothing directly — it is read *through* the six knobs it supplies

**Priority chain:** `modes.rigor` in `project.yaml` → hardcoded default `minimal`
(**locked** — not overridable from `project.local.yaml`, like the four *on-disk*
knobs it fronts — `modes.workflow`, `docs.density`, `qa.level`,
`modes.story_granularity` — because those five change what artifacts exist on
disk. The two personal-experience knobs it also fronts, `modes.review_mode` and
`team.size`, stay locally overridable.)

---

### Expansion table

| `modes.rigor` | `modes.workflow` | `docs.density` | `qa.level` | `modes.story_granularity` | `modes.review_mode` | `team.size` |
|---|---|---|---|---|---|---|
| `minimal` *(default)* | `minimal` | `terse` | `minimal` | `coarse` | `solo` | `individual` |
| `standard` | `standard` | `balanced` | `standard` | `balanced` | `lean` | `individual` |
| `full` | `full` | `thorough` | `full` | `fine` | `full` | `studio` |

### It fronts, it does not replace

The expansion sits **below every explicit source and above the terminal
default**:

```
project.local.yaml → project.yaml → legacy file → rigor expansion → default
```

That ordering is the back-compat guarantee, and it is what makes the migration
free. Three consequences worth stating plainly:

- **An existing `project.yaml` behaves identically.** If it already sets
  `docs.density: terse`, step 2 answers before the expansion is consulted — so
  the value and its reported source (`project.yaml`) are unchanged whether or not
  `rigor` is present. No migration, no `schema_version` bump.
- **Overrides go both ways.** Unlike the `workflow_overrides` **boolean flags** —
  which are additive and stricter-only — an explicit knob may be *looser* than
  the rigor level implies.
  (`workflow_overrides.system_overrides` is also two-directional — it replaces a tier; only the flags are stricter-only.)
  Inheriting the stricter-only rule would make "comprehensive but compact"
  inexpressible, which is the one off-diagonal the docs have always cited.
- **`modes.workflow` keeps `workflow_overrides.system_overrides`.** Per-system
  tiers still beat the rigor-derived project tier. `workflow` was fronted rather
  than folded away precisely because it drives ~5 distinct behaviors and owns the
  only per-system override mechanism.

The six fronted knobs therefore have **no entry in `_yaml_helper_defaults`**. A
terminal default there would answer before the expansion and make `rigor` a no-op
for anyone who had not also set the sub-knob.

### Provenance

Derived values report their source as `rigor:<level>`, so the vocabulary is
`{project.local.yaml, project.yaml, <legacy path>, rigor:<level>, default,
unset}`. `$codex-settings` renders this as `(derived from rigor: standard)` and
force-appends the five to its view-all list — none of them is a leaf of either
YAML file, so enumerating file leaves alone would hide exactly the settings the
user just chose.

---

## modes.workflow

**Controls:** How much design documentation is required before code can begin —
the tradeoff between token/time cost of documentation and speed of reaching
working code
**Values:** `full` | `standard` | `minimal`
**Default:** *none* — supplied by `modes.rigor` (`minimal`, the default, yields `minimal`; `standard` yields `standard`; `full` yields `full`)
**Set by:** `$codex-start` (via `modes.rigor`), `$codex-settings`
**Read by:** See skill tables below

**Priority chain:** `modes.workflow` in `project.yaml` → `modes.rigor` expansion → *(no hardcoded default)*

> **Why the middle level is `standard`, not `indie`.** A developer-type label
> would conflate "type of developer" with "level of process". `standard`
> describes the *amount of process*, not the user, and pairs cleanly with
> `minimal` and `full`.

> **Permissive, not restrictive:** `workflow` controls what is REQUIRED —
> not what is ALLOWED. Any skill can be run at any workflow level. The
> setting changes what gate-check enforces and what completeness checks
> validate, not what the user can invoke.

> **`minimal` floor:** Even in minimal mode, engine choice and a filled
> **`design/game-brief.md`** are required before code starts — the brief's
> build-order field is the plan, so there is no separate `codex-sprint-plan` step.
> Both take minutes and prevent real problems downstream. Everything else can
> be skipped.

> **Escape hatches via `workflow_overrides`:** Users who want *almost* the
> standard set with one extra requirement (e.g. always force Edge Cases) use
> `workflow_overrides` rather than escalating to `full`. See next section.

---

### Value intent

| Value | Token/time cost | Required before code | Best for |
|-------|----------------|---------------------|----------|
| `full` | High | All 8 GDD sections per system, full architecture, all ADRs, art bible, UX specs per screen | Projects where design correctness matters more than speed — teams, commercial titles, learning the full pipeline |
| `standard` | Balanced | 5 GDD sections per system, one architecture doc, critical ADRs, game concept, systems index | Projects that have outgrown a brief — several interacting systems, or a design someone else has to implement |
| `minimal` | Low | One-page `design/game-brief.md` + engine choice (build order in the brief = the plan; no separate sprint plan) | **Default.** Get to code fast — small scope, jam projects, or the design already in your head. Raise it when the project grows |

**standard required GDD sections:** Overview, Detailed Rules, Edge Cases, Dependencies,
Acceptance Criteria.
**standard conditional:** Formulas — required when the system **defines numeric
rules**: rates, curves, thresholds, costs, damage, drop weights, or any value a
balance pass would tune. Optional only when the system defines no such value.

> **The test is what the system defines, not what it is called.** The `Category`
> column in `systems-index.md` is a *hint* — `Gameplay`, `Economy` and
> `Progression` systems almost always qualify — but it is not the test, and a
> `Core`, `UI` or `Persistence` system that defines a numeric rule qualifies too.
>
> Do not restate it as "required when system category is combat, economy,
> progression, or AI". Those four tokens are not the vocabulary `$codex-map-systems`
> writes: `templates/systems-index.md` defines the categories as `Core ·
> Gameplay · Progression · Economy · Persistence · UI · Audio · Narrative ·
> Meta`, and lists **combat and AI as example systems under `Gameplay`**. A
> combat system categorised exactly as the template instructs therefore matched
> none of the four, and Formulas was silently dropped for the system most likely
> to need it. `coding-standards.md` and `rules/design-docs.md` already stated the
> "has math" test; the skills are reconciled to them rather than the other way
> round.

> **Edge Cases is required at `standard`.** Skipping it consistently produces
> "wait, what happens if X is null?" debt during implementation. These 5
> required sections are the minimum that produces implementable code.

> **Art bible is conditional in `standard`.** It is required only if visual
> asset stories exist in the project. Code-focused projects can skip it
> entirely at `standard` level.

---

### Authoring skills

| Skill | full | standard | minimal |
|-------|------|----------|---------|
| **codex-design-system** | All 8 sections required | 5 required sections + conditional Formulas; Player Fantasy, Tuning Knobs skipped | Not required — game brief replaces GDDs. Can still be run voluntarily. |
| **codex-art-bible** | All 9 sections required | Required only if visual asset stories exist; sections 1–4 minimum when required | Not required. Can still be run voluntarily. |
| **codex-create-architecture** | Full architecture — all layers, module ownership, data flow, API boundaries, full ADR audit | Simplified — system layer map + critical ADR list only | Not required. Can still be run voluntarily. |
| **codex-ux-design** | UX spec required per screen | Core screens only (main menu, HUD, primary game loop) | Not required. Can still be run voluntarily. |
| **codex-map-systems** | Required before design-system | Required before design-system | Not required |
| **codex-architecture-decision** | All ADRs on required ADR list must be completed | Critical ADRs only — Foundation layer systems | Not required |

---

### Review and validation skills

| Skill | full | standard | minimal |
|-------|------|----------|---------|
| **codex-design-review** | All 8 sections validated — any missing section blocks approval | 5 required sections validated; missing optional sections warned but do not block | Not applicable — no GDDs to review |
| **codex-review-all-gdds** | Validates all 8 sections across all GDDs | Validates 5 required sections across all GDDs; optional sections surfaced as advisory only | Not applicable |
| **codex-architecture-review** | Full traceability matrix — all GDDs, all ADRs | Reduced scope — architecture doc + critical ADRs only | Not applicable |
| **codex-consistency-check** | Full entity registry cross-check against all GDD sections | Entity registry check against required sections only | Not meaningful — no GDDs to check |
| **codex-content-audit** | Full content count audit against all GDD specs | Limited audit — only specs in required sections counted | Cannot run — no systems index exists |

---

### Phase gate enforcement (gate-check)

`codex-gate-check` is where workflow has the most visible impact — the artifact
checklists differ per phase per mode.

| Gate | full | standard | minimal |
|------|------|----------|---------|
| Concept → Systems Design | game-concept.md, pillars, Visual Identity Anchor | game-concept.md only | `design/game-brief.md` only (content check, not section check) |
| Systems Design → Technical Setup | systems-index, all MVP GDDs reviewed (8 sections), cross-GDD review | systems-index, 5-section GDDs reviewed, cross-GDD review optional | Not applicable — no gates between brief and code; the gate PASSes with that note |
| Technical Setup → Pre-Production | engine, art bible sections 1–4+, 3+ ADRs, architecture, UX specs started | engine, art bible only if visual assets, critical ADRs, architecture | engine configured (required floor) |
| Pre-Production → Production | sprint plan, complete art bible, epics, UX specs, control manifest; Vertical Slice + its playtest recommended (absent → CONCERNS) | epics, sprint plan; complete art bible, UX specs, control manifest recommended; Vertical Slice recommended | the brief's Build order + stories under `production/epics/`; the Vertical Slice items drop — the core loop is fun and runs end to end, checked on the current build |
| Production → Polish | core mechanics, tests, smoke check, QA sign-off, 3+ playtests | core mechanics, smoke check, playable end to end, 1+ playtest, no open S1 bugs | smoke check, playable end to end, no open S1 bugs |
| Polish → Release | all features, content complete, localization (`$codex-localize qa` per locale), QA, smoke, no open S1–S3 bugs, newest `$codex-security-audit` with no open CRITICAL/HIGH | all features, smoke, no open S1 bugs, the security audit | smoke, no open S1 bugs |

<!-- gate-check reconciliation: at `full` and `standard` the Vertical Slice
     keeps its long-standing "recommended, not blocking → CONCERNS if absent;
     FAIL if built-and-broken" status — the tier table never upgrades it to a
     hard blocker. At `minimal` its items drop, and two checks on the current
     build replace them. The genuinely-required floor item at this gate is the
     sprint plan at `standard`/`full`; at `minimal` there is no separate
     sprint-plan step — the brief's Build order plus stories is the floor at
     `minimal`. -->

**Director panel width** (`$codex-gate-check` Section 4b) is workflow's second effect
here. A smaller project needs fewer review perspectives than a complex one.
Delegated directors inherit the parent session model; actual resource use depends
on the task and session settings. The panel scales as follows:

| `workflow` | Panel | Directors |
|---|---|---|
| `full` | 4 | `creative-director`, `technical-director`, `producer`, `art-director` |
| `standard` | 2 | `technical-director`, `producer` |
| `minimal` | 1 | `producer` |

`review_mode` remains the axis that decides *whether* the panel runs at all
(`solo` skips it entirely); workflow decides only how wide it is. Narrowing
never softens a verdict — the strictest verdict from whoever ran still wins, and
`$codex-gate-check` names the perspectives that did not run.

---

### Planning and implementation skills

| Skill | full | standard | minimal |
|-------|------|----------|---------|
| **codex-create-epics** | Requires all GDDs approved (8 sections) | Requires 5-section GDDs approved | **Skipped** (Option A) — no separate epic doc. `$codex-create-stories` reads `design/game-brief.md` directly and synthesizes the implicit epic container itself. |
| **codex-create-stories** | Requires all ADRs on required list present | Requires critical ADRs present | No ADR requirement |
| **codex-dev-story** | Requires TR registry + governing ADR — blocks without them, and on a `Proposed`, `Deprecated` or `Superseded` ADR; a missing control manifest warns | TR registry optional; blocks only on a referenced ADR that is missing, `Proposed`, `Deprecated` or `Superseded` | No TR registry or ADR required — implements against `design/game-brief.md`; a referenced ADR that is missing, `Proposed`, `Deprecated` or `Superseded` still blocks |
| **codex-story-readiness** | Full TR registry + ADR + control manifest validation; any referenced ADR that is missing, `Proposed`, `Deprecated` or `Superseded` BLOCKS | TR registry optional; critical ADR check, and any referenced ADR that is missing, `Proposed`, `Deprecated` or `Superseded` BLOCKS | Acceptance-criteria check (the brief stands in for the GDD); any referenced ADR that is missing, `Proposed`, `Deprecated` or `Superseded` still BLOCKS |
| **codex-story-done** | Full GDD traceability + ADR consistency check | 5-section GDD traceability check | Acceptance criteria check only |
| **codex-qa-plan** | Full test plan derived from all 8 GDD sections | Test plan from 5 required sections | Test plan from acceptance criteria only |
| **codex-regression-suite** | Critical paths mapped from all sections including Edge Cases | Critical paths from required sections (including Edge Cases) | Smoke test coverage only |
| **codex-release-checklist** | Open S1, S2 or S3 bug in `production/qa/bugs/` fails its Quality Gates item | Open S1 fails; open S2/S3 listed as risks | Open S1 fails; open S2/S3 listed as risks |
| **codex-launch-checklist** | Zero open S1–S3 bugs, no exceptions | Zero open S1; S2 or a documented exception | Zero open S1; S2 or a documented exception |
| **codex-team-release** | qa-lead verifies no open S1–S3 bugs | qa-lead verifies no open S1 bugs | qa-lead verifies no open S1 bugs |

---

### Support skills

| Skill | full | standard | minimal |
|-------|------|----------|---------|
| **codex-project-stage-detect** | Checks for all doc types; missing art bible or UX specs flagged as gaps | Adjusts expectations — art bible only flagged if visual-asset stories exist; non-core UX specs not flagged | `design/game-brief.md` + engine present = normal state; no gaps flagged for absent GDDs |
| **codex-adopt** | Full format compliance audit across all doc types | Audit scope reduced to required docs only | `design/game-brief.md` format check only |
| **codex-reverse-document** | Generates full 8-section GDD from code | Generates 5-section GDD from code | Generates `design/game-brief.md` from code |
| **codex-propagate-design-change** | Full cascading impact analysis across all ADRs | Checks critical ADRs for references only | Not applicable |
| **codex-help** | Full artifact detection — surfaces all missing docs as next steps | Adjusts "what's missing" to required docs only — optional docs not surfaced as gaps | `design/game-brief.md` + engine present = next step is code |

---

### Workflow change mid-project

When `workflow` changes via `$codex-settings`, the skill emits an informational note:

> "Workflow changed from [old] to [new]. Run `$codex-content-audit` to see what's now
> required or extra. No automatic migration — existing files stay in place."

No documents are auto-deleted, auto-generated, or blocked. The setting only affects
*new* enforcement going forward.

---

## workflow_overrides

**Controls:** Opt-in granular requirements that override the chosen workflow level
**Location:** **top level of `project.yaml`** — a sibling of `modes:`, *not* a child of it
**Values:** object with sub-flags (see below)
**Default:** all false / empty
**Set by:** `$codex-settings`
**Read by:** `$codex-design-system`, `$codex-design-review`, `$codex-art-bible`, `$codex-gate-check`, `$codex-review-all-gdds`, `$codex-qa-plan`

> **Why the location is called out.** `resolve_config` reads
> `workflow_overrides.system_overrides.*` from the document root
> (`yaml-helper.sh`), and all 14 consuming skill files grep the same top-level
> path. Nested under `modes:` it is still valid YAML, so nothing errors — the
> setting is simply never read. If you copied a `workflow_overrides` block from
> anywhere, check its indentation: it belongs at the document root, never under
> `modes:`.

**Priority chain:** the three `workflow_overrides` **boolean flags**
(`edge_cases`, `tuning_knobs`, `art_bible_strict`) are *additive* on top of the
chosen `workflow` level — they make things stricter, never looser. None of them
has a value that opts out of a requirement the workflow level imposes.

> **`workflow_overrides.system_overrides` is not a flag and is not additive — it replaces a tier in both directions.**
> This rule does not extend to it. On a
> `full` project, `system_overrides.inventory: minimal` really does drop that
> system's required sections to zero. Intended — see
> `docs/codex-studio/workflow-modes.md § workflow_overrides`. Stating the additive
> rule over the whole key is wrong: the guarantee never held for
> `system_overrides`, so do not rely on it as a safety net.

---

### Fields

```yaml
workflow_overrides:
  edge_cases: false          # force Edge Cases section required (no-op at standard since already required; relevant at minimal)
  tuning_knobs: false        # force Tuning Knobs section required (relevant at standard, no-op at full)
  art_bible_strict: false    # force all 9 art bible sections required regardless of asset stories
  system_overrides: {}       # per-system tier overrides — see below
```

### Per-system overrides

```yaml
workflow_overrides:
  system_overrides:
    combat: full              # combat-system GDD requires full (8 sections) regardless of project workflow
    boss-encounters: full
    inventory: minimal        # inventory needs no GDD — the game brief covers it (minimal = no required sections)
```

`system_overrides` is a map of `system_name: workflow_level`. The named system uses the override; all other systems use the project-level `workflow`.

---

### Affected skills

| Skill | How workflow_overrides changes behavior |
|-------|----------------------------------------|
| **codex-design-system** | Reads `system_overrides[system_name]` first; falls back to project `workflow`. Applies override-specific section requirements. |
| **codex-design-review** | Same lookup — validates against the override tier, not the project default, for the named system. |
| **codex-art-bible** | If `art_bible_strict: true`, requires all 9 sections regardless of `workflow` level. |
| **codex-gate-check** | Considers `system_overrides` when validating that all required GDDs are complete. A system at `system_overrides.combat: full` blocks the gate until all 8 sections exist for combat. |
| **codex-review-all-gdds** | Validates each GDD against its effective tier (project workflow + any system override). |

---

## modes.automation

**Controls:** Whether skills ask for decisions and approval before acting, or
recommend and proceed — the tradeoff between user control and speed
**Values:** `collaborative` | `guided` | `autonomous`
**Default:** `collaborative`
**Set by:** `$codex-start`, `$codex-settings`
**Read by:** All 68 skills that use a conversation checkpoint or write files

**Priority chain:** `modes.automation` in `project.yaml` → hardcoded default

> **Unlike review_mode and workflow, this setting is not a per-skill table.**
> It defines universal interaction rules that apply across all skills. A
> per-skill breakdown would repeat the same answer 68 times.

> **Overrides COLLABORATIVE-DESIGN-PRINCIPLE.md:** `guided` and `autonomous`
> modes intentionally relax the Q→O→D→Draft→Approval protocol defined in that
> document. This is opt-in. `collaborative` preserves the protocol exactly.

> **Safety net — `automation_always_ask`:** Even in `autonomous` mode, certain
> categories of decision can be configured to always prompt. See next section.

---

### Value intent

| Value | Speed | Control | What changes |
|-------|-------|---------|--------------|
| `collaborative` | Slowest | Full — every decision is the user's | Current behavior. Q→O→D→Draft→Approval strictly followed. |
| `guided` | Balanced | High — major decisions are the user's, minor ones proceed automatically | AI states recommendation and proceeds for minor decisions. a conversation checkpoint reserved for major/irreversible decisions. |
| `autonomous` | Fastest | Low — AI decides, logs, and proceeds | No a conversation checkpoint (except categories in `automation_always_ask`). No draft review. No write approval. All decisions logged to decision log. |

---

### Universal rules per mode

#### collaborative (current behavior — no change)

- a conversation checkpoint presented for every multi-option decision
- 2–4 options presented with pros/cons for every design choice
- Full draft shown and approved before every file write
- "May I write this to [filepath]?" asked before every write
- "May I create [filepath] with skeleton?" asked before skeleton creation
- Section-by-section approval in multi-section authoring skills
- Multi-file changes require explicit approval of the full changeset

#### guided

- a conversation checkpoint presented for **major decisions only** (see classification below)
- Minor decisions: AI states recommendation inline and proceeds — e.g.
  *"Going with a static utility pattern here — it fits the existing architecture.
  Continuing unless you want to change direction."*
- Draft shown briefly before writing — proceeds after a short summary, does not
  wait for explicit "yes"
- "May I write?" asked for **new files only** — updates to existing files proceed
  directly
- Still presents options for major decisions but caps at 2 choices with a clear
  recommendation
- Multi-section authoring: writes each approved section immediately, no per-section
  confirmation prompt

#### autonomous

- No conversation checkpoints **except** for categories listed in `automation_always_ask`
- No draft review
- No "May I write?" prompts — writes directly
- Picks the recommended option for every decision without presenting alternatives
- All decisions logged immediately to `production/session-logs/decision-log.md`
  with: timestamp, skill, decision point, option chosen, reasoning
- User reviews decision log post-session to audit choices made

---

### Major vs minor decision classification (guided mode)

**Major — always use a conversation checkpoint in guided mode:**

| Decision type | Example |
|---------------|---------|
| Choosing a system name or document path | "What should we call this system?" |
| Mutually exclusive design directions | "Real-time or turn-based?" |
| Any choice that gates downstream work | Engine choice, architecture approach |
| Scope changes | "Cut this feature or slip the deadline?" |
| Any decision that can't be changed without significant rework | Core loop mechanic |

**Minor — AI recommends and proceeds in guided mode:**

| Decision type | Example |
|---------------|---------|
| Which section to work on next | "Moving to Edge Cases next" |
| Optional section inclusion | "Adding a Visual Notes section — fits the system" |
| Formatting and structure choices | Heading levels, table vs prose |
| Adding detail to an already-decided direction | Sub-options within an approved approach |
| Next-step routing after a phase completes | "Running design-review now" |

---

### Affected skills by category

**Authoring skills — highest impact.** Each pauses 10–15 times per document in
`collaborative`. Drops to 2–3 in `guided`, zero in `autonomous`.

`codex-brainstorm`, `codex-design-system`, `codex-art-bible`, `codex-create-architecture`, `codex-ux-design`,
`codex-map-systems`, `codex-architecture-decision`, `codex-create-epics`, `codex-create-stories`,
`codex-sprint-plan`, `codex-prototype`

**Review skills — medium impact.** Pause after presenting findings to ask what
to do next. In `guided` routing decisions proceed automatically. In `autonomous`
the recommended path is taken and logged.

`codex-design-review`, `codex-architecture-review`, `codex-gate-check`, `codex-review-all-gdds`,
`codex-story-readiness`, `codex-story-done`, `codex-milestone-review`, `codex-playtest-report`

**Team orchestration skills — medium impact.** Pause between phases for
check-in. In `guided` the pipeline advances automatically unless BLOCKED. In
`autonomous` the full pipeline runs end to end.

`codex-team-combat`, `codex-team-ui`, `codex-team-audio`, `codex-team-qa`, `codex-team-release`,
`codex-team-narrative`, `codex-team-polish`, `codex-team-level`, `codex-team-live-ops`

**Implementation skills — lower impact.** Pause for architectural questions
before writing code. In `guided` only genuinely ambiguous decisions stop. In
`autonomous` the conventional approach is picked and logged.

`codex-dev-story`, `codex-code-review`

**Setup and utility skills — lowest impact.** Pause for initial configuration
or routing questions. In `guided` defaults are applied automatically. In
`autonomous` recommended defaults are taken without prompting.

`codex-start`, `codex-adopt`, `codex-setup-engine`, `codex-retrospective`, `codex-localize`, `codex-propagate-design-change`,
`codex-asset-spec`, `codex-smoke-check`, `codex-qa-plan`, `codex-story-readiness`

---

### Exemptions — skills that ignore the automation setting

These skills always behave as `collaborative` regardless of the setting.
The reasons are noted.

| Skill | Why always collaborative |
|-------|--------------------------|
| **codex-hotfix** | Emergency decisions — user must approve scope and risk before any action |
| **codex-gate-check** | Results must be reviewed — a gate verdict without user acknowledgement defeats the purpose |
| **codex-day-one-patch** | Release-critical — every action needs explicit sign-off |
| **codex-setup-engine** | One-time irreversible choice that affects the entire project |

---

### Decision log format (autonomous mode)

Written to `production/session-logs/decision-log.md` — append-only.

```markdown
## [timestamp] — [skill-name]

**Decision point:** [what was being decided]
**Options considered:** [list of options that would have been presented]
**Chosen:** [what was picked]
**Reason:** [one-line rationale]
**Category:** [scope_changes | file_deletions | schema_changes | etc., or "minor"]
```

If the file does not exist, it is created. It is never truncated — each session
appends to the existing log.

---

## modes.automation_always_ask

**Controls:** Decision categories that ALWAYS trigger a conversation checkpoint regardless of automation mode
**Values:** list of category names
**Default:** `[scope_changes, file_deletions, schema_changes]`
**Set by:** `$codex-settings`
**Read by:** All skills that respect `modes.automation`

> **Makes `autonomous` safe.** Without this, `autonomous` is "AI does literally
> everything, no questions asked." With it, AI does most things but stops on
> destructive or irreversible decisions you specifically named.

---

### Recognized categories

| Category | Examples of decisions in this category |
|----------|----------------------------------------|
| `scope_changes` | Cutting a feature, slipping a deadline, splitting/merging an epic, removing acceptance criteria |
| `file_deletions` | Removing a story, deleting a GDD, removing a system, removing a test file |
| `schema_changes` | Changes to project.yaml, story template, control manifest, ADR template, GDD template |
| `architecture_decisions` | New ADR creation, ADR replacement, system boundary changes |
| `version_bumps` | Engine version change, framework version bump, dependency major version change |
| `external_calls` | Invoking external APIs (asset gen, AI services) when in autonomous mode |

The list is a YAML list of these strings. Skills check whether the current decision falls into one of the configured categories and prompt regardless of `automation` value.

---

### Affected skills

| Skill | Categories typically triggered |
|-------|--------------------------------|
| **codex-scope-check** | `scope_changes` |
| **codex-propagate-design-change** | `schema_changes`, `architecture_decisions` |
| **codex-architecture-decision** | `architecture_decisions` |
| **codex-setup-engine** | `version_bumps`, `schema_changes` |
| **codex-story-done** | `file_deletions` (when removing/replacing test files) |
| **codex-asset-spec** | `external_calls` (when calling external generators) |

---

## modes.story_granularity

**Controls:** How big each story is and how many stories per epic/sprint
**Values:** `coarse` | `balanced` | `fine`
**Default:** *none* — supplied by `modes.rigor` (`minimal`, the default, yields `coarse`; `standard` yields `balanced`; `full` yields `fine`)
**Set by:** `$codex-start` (via `modes.rigor`), `$codex-settings`
**Read by:** `$codex-create-epics`, `$codex-create-stories`, `$codex-dev-story`, `$codex-sprint-plan`, `$codex-story-done`, `$codex-sprint-status`

**Priority chain:** `modes.story_granularity` in `project.yaml` → `modes.rigor` expansion → *(no hardcoded default)*

---

### Value intent

| Value | Story shape | Stories per sprint | Best for |
|-------|-------------|-------------------|----------|
| `coarse` | 1 story = 1 feature. 3–5 days work each. 5–10 ACs per story. The default, from `rigor: minimal`. | 2–4 | Solo devs, prototyping, "I know what I'm building" |
| `balanced` | 1 story = 1 task. 1–2 days work each. 2–4 ACs per story. The `rigor: standard` value. | 6–10 | Most projects |
| `fine` | 1 story = 1 AC. Hours of work each. Easy code review. Frequent $codex-story-done. | 15–25 | Teams, learning, anything needing fine handoffs |

---

### Affected skills

| Skill | coarse | balanced | fine |
|-------|--------|----------|------|
| **codex-create-epics** | Generates 3–5 child stories per epic | Generates 5–10 child stories per epic | Generates 10–20 child stories per epic |
| **codex-create-stories** | Each story carries 5–10 ACs covering an entire feature | Each story carries 2–4 ACs covering one task | Each story carries 1 AC; story name = AC restatement |
| **codex-dev-story** | Routing prompt expects multi-day implementation cycle. Subagent given longer working context. | Standard 1–2 day expectation. | Each story implementable in hours; subagent given tighter context. |
| **codex-sprint-plan** | Allocates 2–4 stories per sprint based on velocity. | Allocates 6–10 stories per sprint. | Allocates 15–25 stories per sprint. |
| **codex-story-done** | Fires every 3–5 days on average. | Fires every 1–2 days on average. | Fires multiple times per day. |
| **codex-sprint-status** | Burn-down reads in feature-sized chunks. | Burn-down reads in task-sized chunks. | Burn-down reads in AC-sized chunks. |

---

## docs.density

**Controls:** How deep each section in authored docs goes — independent of which sections are required
**Values:** `terse` | `balanced` | `thorough`
**Default:** *none* — supplied by `modes.rigor` (`minimal`, the default, yields `terse`; `standard` yields `balanced`; `full` yields `thorough`)
**Set by:** `$codex-start` (via `modes.rigor`), `$codex-settings`
**Read by:** `$codex-design-system`, `$codex-art-bible`, `$codex-create-architecture`, `$codex-ux-design`, `$codex-map-systems`, `$codex-brainstorm`

**Priority chain:** `docs.density` in `project.yaml` → `modes.rigor` expansion → *(no hardcoded default)*

> **Distinct from `workflow`, but no longer independent by default.** `workflow`
> controls which sections exist; `density` controls how deep each section goes.
> `modes.rigor` now sets both together, so the diagonal (`rigor: full` → 8
> sections *and* thorough prose) is what you get without asking. The off-diagonal
> is still reachable and is the reason `rigor` overrides both ways: `rigor: full`
> + an explicit `docs.density: terse` gives "all sections but each is compact" —
> the "comprehensive but tight" mode, which neither knob expresses alone.

---

### Value intent

| Value | Per-section output style |
|-------|--------------------------|
| `terse` | Bullet points. 2–5 lines per section. Skip rationale and narrative framing. Skip preambles like "In this game..." Just facts needed to implement. The default, from `rigor: minimal`. |
| `balanced` | Paragraphs with light rationale. Examples where helpful. The `rigor: standard` value. |
| `thorough` | Full prose. Rationale for every decision. Examples, alternatives considered, design history. |

---

### Combination matrix with workflow

|  | docs.density: terse | balanced | thorough |
|---|---|---|---|
| **workflow: minimal** | Game brief in bullets *(default)* | Game brief in prose | Game brief + rationale |
| **workflow: standard** | 5 sections, bullets | 5 sections, paragraphs | 5 sections + examples |
| **workflow: full** | 8 sections, bullets *(comprehensive but compact)* | 8 sections, paragraphs *(current full)* | 8 sections + rationale + examples |

---

### Affected skills

| Skill | terse | balanced | thorough |
|-------|-------|----------|----------|
| **codex-design-system** | Each GDD section is 2–5 bullets. Skip Player Fantasy preambles. | Paragraphs with key decisions explained. | Full prose, decision history, alternatives considered. |
| **codex-art-bible** | Each art bible section is a bulleted list of constraints + references. | Paragraphs explaining each visual choice. | Full prose including style explorations, references, rationale per choice. |
| **codex-create-architecture** | Layer diagrams + decision bullets. No essays. | Diagrams + paragraph explanations of layer choices. | Full prose with rationale, trade-offs, alternatives considered per layer. |
| **codex-ux-design** | Wireframe descriptions + interaction bullets. | Wireframes + paragraph descriptions of flows. | Full prose including user research summaries, alternative flow considerations. |
| **codex-map-systems** | One-line system descriptions. | Brief paragraph per system + dependency notes. | Full system-by-system rationale + relationship analysis. |
| **codex-brainstorm** | Pillar bullets + concept bullets. | Pillars + concept with brief rationale. | Pillars + concept + extensive rationale + alternatives. |

---

## testing.framework

**Controls:** Which test framework the project uses — drives test-runner commands and per-engine assumptions in CI
**Values:** engine-specific (see table)
**Default:** auto-populated by `$codex-setup-engine` based on engine choice
**Set by:** `$codex-setup-engine`, `$codex-settings`
**Read by:** `$codex-test-helpers` — the only skill that references it. `$codex-qa-plan`, `$codex-dev-story`, `$codex-regression-suite`, `$codex-test-setup` and `$codex-smoke-check` do **not** name the key, despite being plausible readers.
  *(Derived by grep. A helper-based read through `resolve_setting` may not show the full key, so treat this list as the verified floor, not a ceiling.)*

**Priority chain:** `testing.framework` in `project.yaml` → engine default

> **Migrated from `technical-preferences.md`.**

---

### Engine defaults

| Engine | Default test framework | Alternatives |
|--------|------------------------|--------------|
| Godot | `gdunit4` | `godot-test`, `WAT` |
| Unity | `unity-test-framework` | `nunit`, custom |
| Unreal | `unreal-automation` | Google Test, custom |

---

### Affected skills

| Skill | How `testing.framework` is used |
|-------|--------------------------------|
| **codex-qa-plan** | Test plan tailored to framework's idioms (assertion style, fixture pattern, parameterized tests) |
| **codex-dev-story** | Test framework name passed to programmer subagent in implementation brief |
| **codex-regression-suite** | Test file naming and discovery patterns match framework conventions |
| **codex-test-setup** | Scaffolds the right test layout for the engine (gdUnit4 under `addons/gdUnit4/` + `tests/` for Godot; `Assets/Tests/` asmdefs for Unity; `Source/<Module>/Private/Tests/` for Unreal) |
| **codex-smoke-check** | Invokes framework-appropriate test runner |

---

## testing.strict

**Controls:** Whether failing or missing test evidence blocks a story from
closing, or produces a warning and lets work continue — per test type
**Values:** map of `{logic, integration, visual, ui, config}` → `true | false`
**Default:** `{logic: true, integration: true, visual: true, ui: true, config: false}`
**Set by:** `$codex-settings`
**Read by:** `codex-story-done`, `codex-story-readiness`, `codex-gate-check`, `codex-smoke-check`, `codex-dev-story`, `codex-test-evidence-review`

> **Per-type, not a single bool.** A global `testing.strict: true|false` forces
> all-or-nothing: either all test failures block or none do. Per-type matches how
> most teams actually work — strict logic and visual gates, an advisory smoke check.

> **Composes with `qa.level`:** `qa.level` controls whether evidence is REQUIRED.
> `testing.strict` controls whether failures BLOCK when evidence exists. If
> `qa.level: minimal`, the strict map is effectively ignored (no evidence required
> means nothing to be strict about).

---

### Value intent per type

| Type | `true` | `false` |
|------|--------|---------|
| `logic` (formulas, AI, state machines) | Unit test failures BLOCK — story cannot close | Failures WARN — story can close with warning |
| `integration` (multi-system) | Integration test failures BLOCK | Failures WARN |
| `visual` (animation, VFX, feel) | Missing/failing screenshot evidence BLOCKS (default) | Advisory only — story can close |
| `ui` (menus, HUD, screens) | Missing screenshot of the screen BLOCKS (default) | Advisory only — story can close |
| `config` (balance tuning) | Failing smoke check BLOCKS | Advisory only — story can close (default) |

---

### Affected skills

| Skill | strict.[type]: true | strict.[type]: false |
|-------|---------------------|----------------------|
| **codex-story-done** | Story of that type cannot close on test/evidence failure | Story can close; warning logged in story file |
| **codex-story-readiness** | Validates test requirements exist before implementation — blocks if absent | Validates but does not block — surfaces as warnings |
| **codex-gate-check** | CI failures of that type block phase transition | CI failures of that type surfaced as concerns, not blockers |
| **codex-smoke-check** | Failing smoke (config strict) blocks QA handoff | Failing smoke flagged but handoff proceeds |
| **codex-dev-story** | References test requirements — flags story as unverifiable if absent | References test requirements — advisory only |
| **codex-test-evidence-review** | A gap in that type's evidence is a BLOCKING item (the run ends CONCERNS) | The gap is ADVISORY |

> **Unset-key resolution.** Each skill reads `testing.strict.<type>`; if absent
> it reads `testing.strict` as a plain boolean (legacy form); if still absent it
> falls back to a hardcoded default. For `codex-story-done`, `codex-story-readiness`,
> `codex-gate-check`, and `codex-dev-story` the hardcoded default is the per-type default map
> above (logic/integration/visual/ui strict, config advisory). **`codex-smoke-check` is
> the exception**: it is a build-health gate, so an unset `testing.strict.config`
> defaults to *strict* (a FAIL blocks QA hand-off) — preserving its v1.0 behavior.
> Only an explicit `testing.strict.config: false` makes a failing smoke advisory.

---

## qa.level

**Controls:** What test evidence is required to mark stories Done
**Values:** `minimal` | `standard` | `full`
**Default:** *none* — supplied by `modes.rigor` (`minimal`, the default, yields `minimal`; `standard` yields `standard`; `full` yields `full`)
**Set by:** `$codex-start` (via `modes.rigor`), `$codex-settings`
**Read by:** `$codex-story-done`, `$codex-story-readiness`, `$codex-dev-story`, `$codex-smoke-check`, `$codex-gate-check`, `$codex-qa-plan`, `$codex-regression-suite`, `$codex-team-qa`, `$codex-test-evidence-review`, `$codex-create-stories`, `$codex-retrospective`, `$codex-test-setup`

**Priority chain:** `qa.level` in `project.yaml` → `modes.rigor` expansion → *(no hardcoded default)*

> **Different axis from `testing.strict`.** `qa.level` = what evidence is required.
> `testing.strict` = do failures block. A user wanting "minimal QA" sets
> `qa.level: minimal` and the strict map becomes effectively a no-op.

---

### Value intent

| Aspect | minimal | standard | full |
|--------|---------|----------|------|
| Logic stories | No test required, no gap flagged | Unit test required (strict.logic controls block) | Unit test + coverage minimum |
| Integration stories | No test required | Integration test or playtest doc required | Same + regression coverage |
| Visual stories | Screenshot + lead sign-off required — the look is never waived (strict.visual controls block) | Same | Same |
| UI stories | Screenshot of each screen touched required — never waived (strict.ui controls block) | Same | Same |
| Config/Data stories | No evidence required | Smoke check advisory | Smoke check required |
| $codex-story-done test gate | Acceptance criteria only, except the UI and Visual/Feel screenshot, which is never waived | Enforced per story type | Enforced for every story type |
| $codex-gate-check phase enforcement | No test gates | Logic + integration must pass | Full coverage + regression suite |
| $codex-dev-story routing prompt | No "Test required: ..." line | Per-type test requirement included | Per-type + coverage target included |
| Regression suite required by | Never | Polish stage | Production stage |
| Best for | Jam games, throwaway prototypes, fast iteration | Most projects | Commercial, console cert, learning, paranoid teams |

---

### Affected skills

| Skill | minimal | standard | full |
|-------|---------|----------|------|
| **codex-story-done** | Acceptance criteria check only — no test evidence required, except the UI and Visual/Feel screenshot, which is never waived | Per-type evidence required; strictness from `testing.strict` | All types require evidence; strictness from `testing.strict` |
| **codex-story-readiness** | No test requirement validated, except the UI and Visual/Feel screenshot requirement | Test requirement per story type validated | Test requirement + coverage target validated |
| **codex-dev-story** | Routing prompt has no "Test required" line | Per-type test requirement passed to programmer agent | Coverage target passed to programmer agent |
| **codex-smoke-check** | Optional; with no game tests (WAIVED), `commands.smoke` (else `commands.build`) when set and the launch and critical-path checks carry the verdict; a build nobody launched is NOT ASSESSED | Required before phase transition | Required before every commit |
| **codex-gate-check** | No test enforcement at phase transitions | Logic + integration tests must pass | Full coverage check + regression suite |
| **codex-qa-plan** | Skipped entirely or minimal smoke plan | Full plan per story type | Full plan + coverage targets per system |
| **codex-regression-suite** | Not generated | Generated at Polish stage entry | Generated at Production stage entry |
| **codex-team-qa** | A Logic, Integration or Config/Data story without a test is WAIVED; its acceptance-criteria walk in manual QA is its evidence | The automated test is the evidence for those types | Same |
| **codex-test-evidence-review** | A story with no test evidence is WAIVED, not MISSING; gaps in existing tests are ADVISORY; screenshots never waived | Per-type evidence reviewed; BLOCKING/ADVISORY from `testing.strict` | Same |

---

## qa.coverage_minimum

**Controls:** Minimum code coverage percentage enforced at `qa.level: full`
**Values:** integer 0–100, or `null` for unset
**Default:** `null`
**Set by:** `$codex-settings`
**Read by:** `$codex-gate-check` only. `$codex-story-done` does not reference the key, and no CI runner reads it.
  *(Derived by grep. A helper-based read through `resolve_setting` may not show the full key, so treat this list as the verified floor, not a ceiling.)*

**Priority chain:** `qa.coverage_minimum` in `project.yaml` → no enforcement if `null`

> **Only meaningful at `qa.level: full`.** Ignored at minimal and standard. A
> skill that encounters a non-null value outside full QA should explain that
> it is not enforcing the threshold. No session-start warning is installed.

> **Implementation is engine-specific.** Coverage measurement is different per engine:
> - Godot: gdunit4 coverage report (markdown export)
> - Unity: Unity Test Framework coverage (xml export)
> - Unreal: gcov-style coverage from clang flags
> Codex Game Studios does not unify these — gate-check reads the engine-appropriate report.

---

## strict_gate_checks

> ### RESERVED - NOT IMPLEMENTED
>
> **No shipped skill or runtime consumer reads this setting. Setting it has no effect.** Everything
> below describes the intended design, not current behaviour.
>
> The value is checked for valid spelling when you set it, and then ignored.

**Controls:** Whether phase gate failures block stage transition or just warn
**Values:** `true` | `false`
**Default:** `true`
**Set by:** `$codex-settings`
**Read by:** nothing yet (intended reader: `$codex-gate-check`)

**Priority chain:** `strict_gate_checks` in `project.yaml` → hardcoded default of `true`

> **Different from `review_mode: solo`.** `review_mode: solo` skips the gate
> *entirely* — directors don't even run. `strict_gate_checks: false` runs the
> gate normally but treats the verdict as advisory.

---

### Value intent

| Value | Behavior |
|-------|----------|
| `true` | Default. FAIL or BLOCKING-CONCERNS verdict stops the stage transition. `project.stage` is not advanced. User must address findings and re-run gate. |
| `false` | All gate verdicts are advisory. `$codex-gate-check` still runs and reports findings. `project.stage` advances on user confirmation regardless of verdict. |

---

### Affected skills

| Skill | true | false |
|-------|------|-------|
| **codex-gate-check** | FAIL verdict stops execution before writing new stage; CONCERNS verdict prompts user but defaults to "stay at current stage." | All verdicts surfaced as informational; user is asked "advance anyway?" with default Yes. |

---

## team.size

**Controls:** Which agents are active by default — solo devs shouldn't get studio-grade gating on every change
**Values:** `individual` | `small` | `studio`
**Default:** *none* — supplied by `modes.rigor` (`minimal`/`standard` yield `individual`, `full` yields `studio`)
**Set by:** `$codex-start` (via `modes.rigor`), `$codex-settings`
**Read by:** All `team-*` skills, `$codex-gate-check`, all skills that spawn agents by spawning the named Codex subagent

**Priority chain:** `team.size` in `project.local.yaml` → `project.yaml` → the `modes.rigor` expansion (`full` → `studio`, else `individual`) → no terminal default. Locally overridable — it is a personal-experience knob, not an on-disk artifact.

> **`individual` at `minimal`/`standard`, `studio` at `full`.** Codex Game Studios's audience is
> overwhelmingly solo indie developers, so the two lighter rigor tiers resolve
> `team.size` to `individual` — a `minimal` (default) or `standard` project gets one active agent
> per role, not 15 (directors and leads included). Only `rigor: full` opts into the
> full `studio` roster; a smaller team on a big project sets `team.size: small`
> explicitly, which wins over the rigor-derived value.

> **Different axis from `workflow`.** `workflow` controls *what docs are required.*
> `team.size` controls *which agents exist to make them.* A solo dev on
> `workflow: full` still doesn't need all 49 agents — they need the same coverage
> from a smaller active set.

---

### Active agent set per value

| Value | Active set | Notes |
|-------|-----------|-------|
| `individual` | Core 8: `producer`, `game-designer`, `gameplay-programmer`, engine-specialist (engine-driven), `technical-artist`, `sound-designer`, `qa-tester`, `writer`. **Default.** | Directors and lead-* run only on explicit invocation (e.g. via `$codex-architecture-decision`). Specialists outside the core 8 routed through their nearest core agent. Each `team-*` skill names its own set per value, which can sit outside the core 8 (`codex-team-release` runs `release-manager`); each skill's own `team.size` list is authoritative, and the Affected skills table below mirrors it. |
| `small` | Core 15: directors (CD, TD, PR) + leads (LP, AD, QL, ND) + game-designer + systems-designer + engine-specialist + technical-artist + sound-designer + qa-tester + ux-designer + writer | `team-*` skills add their `small` set (below); most reach their full pipeline only at `studio`. |
| `studio` | All 49 agents available. Engine sub-specialists (e.g. `unity-dots-specialist` separate from `unity-specialist`) routed when relevant. The adversarial review pass in `codex-team-combat`, `codex-team-ui` and `codex-team-polish`. | Commercial titles, learning the full org chart, large teams with parallel work. |

---

### Affected skills

| Skill | individual | small | studio |
|-------|------|-------|--------|
| **codex-team-combat** | Single agent (gameplay-programmer) runs the pipeline; ai-programmer escalated only if AI work flagged | Default pipeline as documented | Default + the primary engine specialist may use its sub-specialists + adversarial review pass (Phase 5's qa-tester looks for how it breaks) |
| **codex-team-narrative** | writer only; narrative-director invoked only on explicit pillar conflict | narrative-director + writer, + localization-lead and world-builder at `review_mode: full` | All six narrative agents, whatever the review mode |
| **codex-team-ui** | ui-programmer + ux-designer | + accessibility-specialist + art-director | + engine UI specialist + adversarial review pass (Phase 4's reviewers look for where it fails its spec) |
| **codex-team-audio** | sound-designer only | + audio-director + technical-artist + gameplay-programmer | + accessibility-specialist + the primary engine specialist |
| **codex-team-level** | level-designer only | + systems-designer + art-director + qa-tester | + narrative-director + world-builder + accessibility-specialist |
| **codex-team-qa** | qa-tester only; qa-lead invoked at phase gates only | qa-lead + qa-tester pipeline | qa-lead + per-story qa-tester spawn + sign-off |
| **codex-team-release** | release-manager only | + producer + devops-engineer + qa-lead + community-manager | + security-engineer + analytics-engineer + localization-lead + performance-analyst, and network-programmer when the game is multiplayer |
| **codex-team-polish** | performance-analyst + technical-artist; no programmer is active, so Phase 2's optimisation list is handed to `$codex-dev-story` | + sound-designer + qa-tester + engine-programmer (implements Phase 2's optimisation list), and tools-programmer when Phase 1 traces a cause to a content authoring tool | engine-programmer, as at small, + adversarial review pass (Phase 5's qa-tester looks for how it breaks) |
| **codex-team-live-ops** | live-ops-designer + economy-designer | + analytics-engineer + community-manager | + writer + narrative-director |
| **codex-gate-check** | Panel width is `modes.workflow`'s axis, not this one (gates always run) — `team.size` affects only specialist depth within each director's review | Same as individual for directors; specialists within directors' reviews use small set | Same plus engine sub-specialists |
| **codex-architecture-decision** | TD-ADR (in `full` review mode) + the primary engine specialist | Same | Same — no sub-specialist or adversarial reviewer at any size |

---

### Special cases

- `team.size` does not decide whether directors run: `$codex-gate-check`'s panel follows `review_mode` and `modes.workflow`, and no `team-*` pipeline spawns a director phase gate. In a team skill, a "phase gate" is one of the decision points its own pipeline lists, whatever the `automation` mode.
- `individual` does not disable agents — it just changes which are active by default. Any agent can still be invoked by name.
- When `team.size: individual` and a non-core agent is needed (e.g. `network-programmer` for a multiplayer story), the skill emits an informational note and routes through the nearest active core agent.

---

## platform.multiplayer

**Controls:** Whether the project includes real-time online multiplayer — determines
which specialists are routed and which architecture sections are required
**Values:** `true` | `false`
**Default:** none — unset is not `false`
**Set by:** `$codex-settings`
**Read by:** `codex-security-audit`, `codex-team-release` (and the `security-engineer` agent)

**Priority chain:** `platform.multiplayer` in `project.yaml` → unset (`platform.*` is locked to `project.yaml`, so `project.local.yaml` cannot set it). Nothing writes it except `$codex-settings`, so on most projects it is unset: `$codex-security-audit` and `$codex-team-release` ask whether the game is multiplayer rather than reading unset as `false`.

> **Distinct from `platform.online`.** `multiplayer` is *real-time multiplayer
> specifically* (network specialist, netcode review, replication architecture).
> `platform.online` covers everything else online (cloud saves, leaderboards,
> telemetry). See next section.

> **This is a project attribute, not a mode.** It describes what the game is,
> not how the pipeline operates. It lives in `platform` alongside `targets`,
> `primary_input`, and `gamepad_support` — not in `modes`.

---

### Value intent

| Value | Meaning |
|-------|---------|
| `true` | Game has real-time online multiplayer. `$codex-security-audit` runs its netcode category and rates a HIGH finding as release-blocking; `$codex-team-release` adds `network-programmer`'s sign-off. |
| `false` | No real-time multiplayer. `$codex-security-audit` skips the netcode category and says so; `$codex-team-release` does not spawn `network-programmer`. |

---

### Affected skills

| Skill | multiplayer: true | multiplayer: false |
|-------|------------------|-------------------|
| **codex-security-audit** | Includes netcode review — authentication, replication, cheat vectors | Netcode review skipped, and the report says so |
| **codex-team-release** | `network-programmer` included in release sign-off pipeline | `network-programmer` excluded |

No other skill reads this key: `$codex-dev-story`, `$codex-create-architecture` and `$codex-gate-check`
decide networking scope from the story, GDD or architecture in front of them.

---

## platform.online

**Controls:** Whether the project has any online features (leaderboards, cloud saves, telemetry, IAP)
**Values:** `true` | `false`
**Default:** none — unset is not `false`
**Set by:** `$codex-settings`
**Read by:** `codex-security-audit`, `codex-team-release` (and the `security-engineer` agent)

**Priority chain:** `platform.online` in `project.yaml` → unset (`platform.*` is locked to `project.yaml`, so `project.local.yaml` cannot set it). Nothing writes it except `$codex-settings`: `$codex-security-audit` and `$codex-team-release` ask rather than reading unset as `false`.

> **Independent of `platform.multiplayer`.** A single-player game with Steam
> Cloud and leaderboards is `online: true, multiplayer: false`. The two settings
> have different specialist routing implications.

---

### Value intent

| Value | Meaning |
|-------|---------|
| `true` | Project includes online services (cloud saves, leaderboards, achievements, telemetry, IAP, anything calling external APIs at runtime). `$codex-security-audit` runs Category 2 (network and multiplayer — including a plaintext-token check) when this or `platform.multiplayer` is true or unset; `$codex-team-release` adds a `security-engineer` sign-off. |
| `false` | Project is fully offline. `$codex-security-audit` skips Category 2 only when `platform.multiplayer` is also false. |

---

### Affected skills

| Skill | online: true | online: false |
|-------|--------------|---------------|
| **codex-security-audit** | Category 2 (network) runs — server authority, packet validation, rate limits, plaintext tokens | Category 2 skipped only when `platform.multiplayer` is also false |
| **codex-team-release** | `security-engineer` sign-off when the game is online or stores player data | No online-driven security sign-off |

No other skill reads this key: `$codex-create-architecture`, `$codex-dev-story`, `$codex-team-live-ops`
and `$codex-gate-check` decide online scope from the documents in front of them.

---

## platform.cert_tier

> ### WIRED — this setting is live
>
> `$codex-launch-checklist` and `$codex-release-checklist` both resolve it and branch on its
> four values — `none` emits no certification section, `itch` and `steam` their
> storefront's requirements, `console` full platform certification — and ask which
> platforms are in scope when it is unset.

**Controls:** Certification target — scopes what `$codex-launch-checklist` asks for
**Values:** `none` | `itch` | `steam` | `console`
**Default:** *none* — unset stays unset, so the skills ask
**Set by:** `$codex-settings` — nothing else writes it, so it stays unset (and the skills ask) until you set it
**Read by:** `$codex-launch-checklist`, `$codex-release-checklist`

**Priority chain:** `platform.cert_tier` in `project.yaml` → unset (no default is
substituted: unset is a missing decision, `none` is a made one, and the skills
must tell them apart)

---

### Value intent

| Value | Required compliance | Best for |
|-------|---------------------|----------|
| `none` | No certification — internal release, alpha, jam game | Default |
| `itch` | itch.io upload requirements (build size, page setup, age tags) | Indie web/desktop releases |
| `steam` | Steamworks integration, store page, achievements, depot build, system requirements, common content rules | Commercial PC releases |
| `console` | Platform certification (PlayStation/Xbox/Switch) — heavy compliance: TRC/XR/Lotcheck, save data rules, controller mapping rules, age rating boards | Console releases |

---

### Affected skills

| Skill | none | itch | steam | console |
|-------|------|------|-------|---------|
| **codex-launch-checklist** | Internal launch only — no external requirements | + itch.io page setup, butler upload, build size | + Steamworks integration, store page, achievements depot, common content checks | + Platform-specific TRC, certification submission, console save format compliance |
| **codex-release-checklist** | Smoke pass + version bump only | + itch.io page live, build uploaded to butler | + Steam store page live, depot pushed, achievements live | + Platform submission accepted, age rating boards cleared |
| **/pre-cert** (future) | Not applicable | Lightweight readiness check | Steam common content audit | Full TRC compliance audit |

---

## accessibility.target

> ### RESERVED - NOT IMPLEMENTED
>
> **No shipped skill or runtime consumer reads this setting. Setting it has no effect.** Everything
> below describes the intended design, not current behaviour.
>
> The value is checked for valid spelling when you set it, and then ignored.
> The accessibility-specialist routing and the Polish-stage audit described
> below **do not happen at any level** — `$codex-team-ui`, `$codex-team-level`,
> `$codex-team-polish` and `$codex-gate-check` do not read this setting, and `$codex-start`
> does not ask for it.

**Controls:** Accessibility commitment level — routes accessibility specialist and gates audit requirements
**Values:** `none` | `standard` | `aaa`
**Default:** `none`
**Set by:** `$codex-settings`
**Read by:** nothing yet (intended readers: `$codex-team-ui`, `$codex-team-level`, `$codex-team-polish`, `$codex-gate-check`)

**Priority chain:** `accessibility.target` in `project.yaml` → hardcoded default of `none`

> **Default is `none`, not `standard`.** Most Codex Game Studios users are solo devs and jam-game
> makers — defaulting to `standard` would auto-spawn the accessibility specialist
> for projects where it's overhead. `$codex-start` asks the question explicitly so users
> who care can opt into `standard` or `aaa` consciously.

---

### Value intent

| Value | Required features | Specialist routing |
|-------|-------------------|--------------------|
| `none` | None enforced | `accessibility-specialist` not spawned |
| `standard` | Colorblind-safe palette, subtitles for any voice content, key remapping | `accessibility-specialist` runs in team-ui, team-level |
| `aaa` | Full Game Accessibility Guidelines: motor, vision, hearing, cognitive categories | `accessibility-specialist` runs in all team-* skills; mandatory audit at Polish stage |

---

### Affected skills

| Skill | none | standard | aaa |
|-------|------|----------|-----|
| **codex-team-ui** | accessibility-specialist not spawned | accessibility-specialist included for HUD/menu reviews | accessibility-specialist included for every screen + accessibility audit pass |
| **codex-team-level** | accessibility-specialist not spawned | accessibility-specialist reviews level for colorblind safety and signposting | accessibility-specialist reviews for full mobility/audio/cognitive considerations |
| **codex-team-polish** | No accessibility pass | Final accessibility pass added | Full accessibility audit required before completion |
| **codex-gate-check** | No accessibility check at any stage | Polish gate checks for the standard required features | Polish gate requires full Game Accessibility Guidelines compliance audit |

---

## cadence.sprint_length and cadence.milestone_length

> ### RESERVED - NOT IMPLEMENTED
>
> **No shipped skill or runtime consumer reads this setting. Setting it has no effect.** Everything
> below describes the intended design, not current behaviour.
>
> No reference anywhere outside this file.

**Controls:** Default sprint and milestone durations for planning
**Values:**
- `sprint_length`: `1w` | `2w` | `3w` | `4w` | `none`
- `milestone_length`: `4w` | `6w` | `8w` | `12w`
**Defaults:** `sprint_length: 2w`, `milestone_length: 8w`
**Set by:** `$codex-settings`
**Read by:** nothing yet (intended readers: `$codex-sprint-plan`, `$codex-milestone-review`, `$codex-sprint-status`, future velocity tracking)

**Priority chain:** `cadence.*` in `project.yaml` → hardcoded defaults

> **`none` for `sprint_length`** means continuous-flow / kanban-style — no sprint boundaries.
> `$codex-sprint-plan` is then invoked manually as needed. Velocity tracking
> is per-week rather than per-sprint.

---

### Affected skills

| Skill | What changes |
|-------|--------------|
| **codex-sprint-plan** | Capacity calculated as `sprint_length × team.size velocity baseline`. `none` makes the skill emit a continuous-flow plan instead. |
| **codex-milestone-review** | Milestone window for retrospective scope = `milestone_length`. |
| **codex-sprint-status** | Burn-down chart x-axis spans `sprint_length`. |
| **codex-retrospective** | Sprint retro fires at `sprint_length` cadence (or weekly when sprint_length is `none`). |

---

## performance.target_framerate and performance.frame_budget_ms

**Controls:** The frame-rate target and its per-frame millisecond budget
**Values:** integers (e.g. `60`, `16.67`)
**Default:** none — unset means no budget was ever committed to
**Set by:** the user, by hand or via `$codex-settings`
**Read by:** `$codex-perf-profile`, `$codex-gate-check`, `$codex-team-polish`

## performance.draw_call_limit and performance.memory_ceiling_mb

**Controls:** Per-frame draw-call ceiling and total memory ceiling
**Values:** integers
**Default:** none — unset means no budget was ever committed to
**Set by:** the user, by hand or via `$codex-settings`
**Read by:** `$codex-perf-profile`, `$codex-gate-check`, `$codex-team-polish`

> **Every setting needs its own `## ` heading in this file, not just a table
> row.** The dead-settings audit derives what it checks from those headings, so
> a setting mentioned only inside a table is invisible to it — it can neither be
> reported DEAD if it loses its reader, nor caught if it gains one. A setting
> outside the audit's field of view is exactly how a documented-but-dead entry,
> or a working-but-listed-as-dead one, survives unnoticed.
>
> **Unset is not zero and not a default.** A budget nobody set is not a budget
> that was met — `$codex-perf-profile` must report `NOT ASSESSED` for a metric with no
> committed target rather than measuring against a placeholder. That exact
> failure (">99% headroom against a 16.67ms budget", from zero profiler data)
> is one of the two instances that motivated `docs/codex-studio/rules/skill-authoring.md`.

## performance.enforce

**Controls:** Whether performance budget violations warn or block
**Values:** `warn` | `block` | `off`
**Default:** `warn`
**Set by:** `$codex-settings`
**Read by:** `$codex-perf-profile`, `$codex-gate-check`, CI runner

**Priority chain:** `performance.enforce` in `project.local.yaml` → `project.yaml` → hardcoded default of `warn`, resolved by `resolve_config --keys performance.enforce`

> **Read it from the resolved block, never from `project.yaml` directly.** The key is on the `$codex-settings --local` whitelist. `$codex-perf-profile` Phase 0 and `$codex-gate-check` Section 3 are the two readers the table above promises — a key that is enum-validated, accepted and displayed while nothing reads it is exactly the failure this warning guards against.

> **Mirrors the `testing.strict` pattern.** Defines what happens when a budget
> defined in `performance.target_framerate`, `frame_budget_ms`, `draw_call_limit`,
> or `memory_ceiling_mb` is exceeded.

---

### Value intent

| Value | Behavior |
|-------|----------|
| `warn` | Default. Profile runs flag violations as findings. CI logs them but doesn't fail. `$codex-gate-check` surfaces them as concerns, not blockers. |
| `block` | Profile failures block CI. `$codex-gate-check` treats violations as FAIL verdict (Polish stage onward). |
| `off` | Performance budgets are informational only — no profile runs gated, no findings surfaced. |

---

## project.stage

**Controls:** The current development phase — determines which gate-check
validates and what artifacts are expected to exist
**Values:** `Concept` | `Systems Design` | `Technical Setup` | `Pre-Production` | `Production` | `Polish` | `Release`
**Default:** `Concept`
**Set by:** `$codex-gate-check` on a PASS, or on a CONCERNS the user explicitly accepts (the accepted risks are recorded); a FAIL never advances it — never set manually
**Read by:** `codex-gate-check`, `codex-project-stage-detect`, `codex-help`, `codex-day-one-patch`, `codex-team-release`, `codex-launch-checklist`, `codex-release-checklist`, `codex-map-systems`, `codex-team-qa`, `codex-adopt`

> **Stage count:** This document uses the
> 7-stage reality implemented by gate-check:
> `Concept | Systems Design | Technical Setup | Pre-Production | Production | Polish | Release`

> **This is a project attribute, not a mode.** It records where the project is
> in its lifecycle. Only `$codex-start` (at onboarding) and `$codex-gate-check` write it —
> `$codex-gate-check` on a PASS verdict with user confirmation, or on a CONCERNS
> verdict whose risks the user explicitly accepts (they are recorded); a FAIL never advances it.
> Never write it manually mid-session except to correct an incorrect auto-detect.

> **Legacy fallback + dual-write.** Stage is read from `project.stage` in
> `project.yaml` first, then legacy `production/stage.txt`, then artifact
> auto-detection. When `$codex-gate-check` advances the stage it dual-writes BOTH
> `project.yaml` and `production/stage.txt`, for compatibility with readers that still use the legacy mirror. `$codex-start` also dual-writes the initial stage. The
> legacy `.txt` file is retired at `tools/codex-studio/scripts/migrate-v1-config.sh --finalize`.

---

### Stage progression and gate requirements

Each row is the gate that must be passed to advance FROM that stage.

| From stage | Key artifacts required to pass | gate-check writes |
|------------|-------------------------------|-------------------|
| **Concept** | `game-concept.md`, design pillars, Visual Identity Anchor | `Systems Design` |
| **Systems Design** | `systems-index.md`, all MVP GDDs reviewed, cross-GDD consistency check | `Technical Setup` |
| **Technical Setup** | Engine configured, art bible sections 1–4 (at `standard`, only if visual stories exist), 3+ ADRs, architecture doc, traceability index, test framework, accessibility and interaction-pattern docs | `Pre-Production` |
| **Pre-Production** | Epics defined, first sprint plan, UX specs, control manifest (a Vertical Slice is recommended, not required) | `Production` |
| **Production** | Core mechanics implemented, main path playable, smoke check passes, QA sign-off | `Polish` |
| **Polish** | All features complete, content complete, localization, security audit, no open S1–S3 bugs | `Release` |

Gates adjust per `modes.workflow` — see `modes.workflow` section for what is
required at `standard` and `minimal` levels.

---

### Affected skills

| Skill | How it uses stage |
|-------|------------------|
| **codex-gate-check** | Reads current stage to determine which gate to validate. Writes next stage on PASS, or on a CONCERNS the user explicitly accepts. |
| **codex-project-stage-detect** | Reads `project.stage` first — if set, uses it as authoritative. Falls back to heuristic detection only if absent. |
| **codex-help** | Uses stage to determine "where are you in the pipeline" and surfaces the correct next steps. |
| **codex-sprint-status** | Displays current stage in status summary. |
| **codex-day-one-patch** | Proceeds only when the stage is `Release` or `Polish`; otherwise says it is not appropriate yet. |
| **codex-team-release** | Stops before Phase 1 unless the stage is `Release` ("run `$codex-gate-check release` first"); proceeding takes an explicit override, recorded in the go/no-go record and the report. Never writes the stage. |

---

## project.kind

> ### RESERVED - NOT IMPLEMENTED
>
> **No shipped skill or runtime consumer reads this setting. Setting it has no effect.** Everything
> below describes the intended design, not current behaviour.
>
> No reference anywhere outside this file.

**Controls:** What type of project this is — routes skill subsets
**Values:** `game` | `tool` | `engine` | `mod` | `library`
**Default:** `game`
**Set by:** `$codex-start`, `$codex-setup-engine`
**Read by:** Many skills (advisory routing — see below)

**Priority chain:** `project.kind` in `project.yaml` → hardcoded default of `game`

---

### Value intent

| Value | Meaning | What's deactivated |
|-------|---------|-------------------|
| `game` | Default. Full Codex Game Studios framework applies. | Nothing |
| `tool` | Developer tool, not a game | Skip art bible, narrative, level design, playtesting |
| `engine` | Custom engine or library underneath games | Skip game-specific concerns entirely (narrative, art, playtest) |
| `mod` | Mod for an existing game | Skip engine setup; assume parent engine; reduce architecture scope |
| `library` | Reusable library | Emphasize tests + API design; design docs lighter; no asset pipeline |

---

### Affected skills

| Skill | game | tool | engine | mod | library |
|-------|------|------|--------|-----|---------|
| **codex-brainstorm** | Full game-concept output | Tool concept output (user, problem, solution) | Engine concept (target use cases, scope) | Mod concept (what changes) | Library concept (API surface, target consumers) |
| **codex-art-bible** | Required at appropriate workflow level | Skipped | Skipped | Optional (depends on visual scope) | Skipped |
| **codex-map-systems** | Full game systems decomposition | Tool subsystems | Engine subsystems | Modified-system map | Library module map |
| **codex-playtest-report** | Required at appropriate stages | Skipped or replaced with user testing | Skipped | Required (compatibility testing) | Skipped or replaced with API usage testing |
| **codex-setup-engine** | Game engine setup | Skipped or replaced with build tool setup | Self-referential — engine IS the project | Parent engine assumed | Skipped or replaced with library scaffolding |

---

## engine.name and specialists

**Controls:** Which engine-specific specialist agents are routed to for code
implementation, review, and architecture validation
**Values:** `Godot` | `Unity` | `Unreal`
**Default:** `[UNSET]` — must be configured via `$codex-setup-engine`
**Set by:** `$codex-setup-engine`
**Read by:** `codex-dev-story`, `codex-code-review`, `codex-architecture-decision`, `codex-create-architecture`, `codex-team-combat`, `codex-team-ui`, `codex-team-audio`

> **Currently stored in `technical-preferences.md`**, not `project.yaml`. After
> YAML expansion, `engine.name` and the specialist routing table move to
> `project.yaml specialists` block. Skill behavior is unchanged — only the
> source file changes.

> **This is a project attribute, not a mode.** Engine choice drives specialist
> routing the same way `platform.multiplayer` drives network routing — skills
> respond to a fact about the project, not a process preference.

---

### Specialist routing by engine

| Engine | Language/code specialist | Shader specialist | UI specialist | Additional specialists |
|--------|--------------------------|-------------------|---------------|----------------------|
| **Godot** | `godot-gdscript-specialist` (GDScript) or `godot-csharp-specialist` (C#) — driven by `engine.language` | `godot-shader-specialist` | `godot-specialist` | `godot-gdextension-specialist` |
| **Unity** | `unity-specialist` | `unity-shader-specialist` | `unity-ui-specialist` | `unity-addressables-specialist`, `unity-dots-specialist` |
| **Unreal** | `unreal-specialist` | `unreal-specialist` | `ue-umg-specialist` | `ue-gas-specialist`, `ue-blueprint-specialist`, `ue-replication-specialist` |
| **[UNSET]** | No specialist spawned — warning emitted | No specialist spawned | No specialist spawned | None |

---

### Affected skills

| Skill | How engine.name is used |
|-------|------------------------|
| **codex-dev-story** | Routes code stories to language specialist. Spawns engine specialist alongside for HIGH engine-risk stories or engine-specific API usage. |
| **codex-code-review** | Routes review to language, shader, or UI specialist based on file type being reviewed. |
| **codex-architecture-decision** | Loads `docs/engine-reference/[engine]/VERSION.md` before authoring. Spawns engine specialist to validate ADR for API correctness and post-cutoff compatibility. |
| **codex-create-architecture** | Includes engine-specific constraints and patterns in architecture doc based on engine choice. |
| **team-combat / team-ui / team-audio** | Spawn the engine specialist their pipeline names: team-combat the primary engine specialist (from `team.size: small`), team-ui the engine UI specialist (`specialists.ui`, at `studio`), team-audio the primary engine specialist (at `studio`). The other six `team-*` skills spawn none. |

---

## commands

> **Live since the run-and-observe step.** This block was RESERVED — written by
> `$codex-setup-engine`, read by nothing — through most of v1.1. `test`, `smoke` and
> `build` gained readers as the parse-check and smoke gates landed; `run` gained
> its reader last, when `$codex-dev-story` Phase 6 step 4 started launching the game to
> look at it. The per-skill table at the bottom is now current behaviour, not
> intent. `validate-push.sh` was once named as a reader and never was.

**Controls:** Explicit shell commands to build, test, run, and smoke-test the project
**Values:** strings — shell-executable commands
**Default:** `[UNSET]` — populated by `$codex-setup-engine` with engine-typical defaults
**Set by:** `$codex-setup-engine`, `$codex-settings`
**Written by:** `$codex-setup-engine`, `$codex-settings`. **Read by:** `test` — `$codex-smoke-check`, `$codex-hotfix` (narrowed to the affected suite), `$codex-bug-report` (verify mode, narrowed to the affected suite), `$codex-day-one-patch` (targeted fix and, when set, the broader regression — NOT ASSESSED if unset), `$codex-dev-story` (Godot parse-check executable resolution), `$codex-test-setup` (the `<Project>.` filter root on Unreal), `project-coherence.sh`; `smoke` — `$codex-dev-story` (Unity parse check), `$codex-smoke-check` (build check when tests are WAIVED); `build` — `$codex-smoke-check` (build check when tests are WAIVED and `smoke` is unset), `project-coherence.sh`; `run` — `$codex-dev-story` (Phase 6 step 4, the run-and-observe step). `$codex-launch-checklist` and `$codex-regression-suite` name these commands but do not run them.
  *(Derived by grep. A helper-based read would not show up, so treat this list as the verified floor, not a ceiling.)*

**Priority chain:** `commands.*` in `project.yaml` → engine-typical default → no command available

> **Why explicit:** Without this block, Codex Game Studios has to guess engine-typical conventions
> for invoking the project. Better to be explicit per-project — covers cases where
> projects customize their build (e.g., a Godot project using gdunit4 for tests but
> a custom export script for builds).

---

### Fields

Each command can be a simple string (used on all OSes) or an OS-aware map:

**Simple form** (one command, used on every OS):
```yaml
commands:
  build: "godot --headless --export-debug '<PRESET>'"   # ask; see the note below
  test:  "godot --headless -s -d --remote-debug tcp://127.0.0.1:0 res://addons/gdUnit4/bin/GdUnitCmdTool.gd -a res://tests --ignoreHeadlessMode"
  run:   "godot --path . --windowed --resolution 1280x720"
  smoke: "godot --headless --quit-after 5"
```

Note that `build` is the one row the simple form suits least: an export preset
names a *platform*, so a single build string is portable only for a project that
builds one platform. The other three rows are genuinely OS-independent.

**OS-aware form** (different commands per OS):
```yaml
commands:
  build:
    default: "godot --headless --export-debug 'Linux/X11'"
    windows: "godot.exe --headless --export-debug 'Windows Desktop'"
    macos:   "godot --headless --export-debug 'macOS'"
  test:
    default: "godot --headless -s -d --remote-debug tcp://127.0.0.1:0 res://addons/gdUnit4/bin/GdUnitCmdTool.gd -a res://tests --ignoreHeadlessMode"
  run:
    default: "godot --path . --windowed --resolution 1280x720"
  smoke:
    default: "godot --headless --quit-after 5"
```

**Resolution rule:** if the value is a string, use it as-is on any OS. If the
value is a map, skills or explicit helpers read the current OS and pick the matching key
(`linux`, `windows`, `macos`). Fall back to `default` if no OS-specific key
matches.

This solves the Windows/Linux/macOS path-and-binary-name differences without
breaking the whitelist (commands stays locked to project.yaml — the OS-specific
keys are inside the locked file, not a local override).

| Field | Purpose |
|-------|---------|
| `build` | Full project build for CI or release. `$codex-smoke-check` runs it only as the WAIVED-path build check when `commands.smoke` is unset; `project-coherence.sh` (which `$codex-smoke-check` runs first) checks the export preset it names, and `$codex-launch-checklist` only asks whether the build produces a valid artifact. |
| `test` | Run the full test suite. Run by `$codex-smoke-check` and, narrowed to the affected suite, by `$codex-hotfix`, `$codex-bug-report` (verify mode) and `$codex-day-one-patch`; `project-coherence.sh` checks the runner it names. `$codex-regression-suite` does **not** run it. |
| `run` | Launch the **game** windowed at a fixed resolution — not the editor. Used by `$codex-dev-story` Phase 6 step 4 to observe the feature and retain a screenshot; see `docs/codex-studio/run-and-observe.md` for the per-engine capture flags that are appended to it. |
| `smoke` | Minimal "does it boot?" check. Run by `$codex-dev-story` as the Unity parse check (Phase 6 step 2), and by `$codex-smoke-check` as the build check when `qa.level: minimal` waives tests. |

---

### Engine defaults

When `$codex-setup-engine` runs, it populates `commands` based on engine choice — except
the **build** row, which it must **ask** for. The build artifact is named by a
project-defined string (a Godot export preset, a Unity build target), and no
engine reference in this repo can source it. See `$codex-setup-engine` §"The Godot
`build` row must not hardcode `'Linux/X11'`".

| Engine | build | test | run | smoke |
|--------|-------|------|-----|-------|
| Godot | `godot --headless --export-debug '<PRESET>'` | `godot --headless -s -d --remote-debug tcp://127.0.0.1:0 res://addons/gdUnit4/bin/GdUnitCmdTool.gd -a res://tests --ignoreHeadlessMode` | `godot --path . --windowed --resolution 1280x720` | `godot --headless --quit-after 5` |
| Unity | `"<Unity editor>" -batchmode -quit -projectPath . -buildTarget <TARGET> -build<PLATFORM>Player Builds/<Target>/<Game>.exe` | `"<Unity editor>" -batchmode -runTests -projectPath . -testPlatform EditMode -testResults test-results/editmode.xml` | `Builds/<Target>/<Game>.exe -screen-width 1280 -screen-height 720 -screen-fullscreen 0` | `"<Unity editor>" -batchmode -quit -projectPath . -logFile -` |
| Unreal | `"<UE root>/Engine/Binaries/DotNET/AutomationTool/AutomationTool.exe" BuildCookRun -project="$(pwd -W 2>/dev/null || pwd)/<project>.uproject" -platform=Win64 -build -cook` (confirm per project) | `"<UE root>/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" "$(pwd -W 2>/dev/null || pwd)/<project>.uproject" -ExecCmds="Automation RunTests <project>.; Quit" -unattended -nullrhi -stdout -FullStdOutLogOutput` | `"<UE root>/Engine/Binaries/Win64/UnrealEditor.exe" "$(pwd -W 2>/dev/null || pwd)/<project>.uproject" -game -windowed -ResX=1280 -ResY=720` | `"<UE root>/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" "$(pwd -W 2>/dev/null || pwd)/<project>.uproject" -game -nullrhi -unattended -stdout -ExecCmds="Quit"` |

The Unreal row is Windows'. `$codex-setup-engine` writes the Linux block (`Engine/Build/BatchFiles/RunUAT.sh`,
`Engine/Binaries/Linux/UnrealEditor`) on Linux, and on macOS only `build`, leaving `test`, `run` and
`smoke` as TODOs — see `docs/engine-reference/unreal/current-best-practices.md`, "Command Line".

> **`<PRESET>` and `<TARGET>` are placeholders, not values to copy.** A Godot
> export preset is whatever string the operator typed into `export_presets.cfg`;
> the shipped defaults are per-platform (`Windows Desktop`, `macOS`, `Web`,
> `Linux/X11`). Copying a preset name you do not have gives you a build command
> that fails with `Unknown export preset`; copying one you *do* have, but did not
> mean, gives you a command that succeeds and builds the wrong platform. The
> second is the dangerous one. If no presets exist yet — common, since
> `$codex-setup-engine` usually runs before the project has any — write
> `[TO BE CONFIGURED]` rather than guessing a name.

Users override per-project as needed via `$codex-settings commands.<field>=<value>` or by editing `project.yaml` directly.

---

### Affected skills

| Skill | How `commands` is used |
|-------|------------------------|
| **codex-smoke-check** | Runs `commands.test`, or the engine's default when it is unset; on Unreal it builds the editor target first. Critical path for QA hand-off. |
| **codex-launch-checklist** | Emits a checklist **item** asking whether the build produces a valid artifact. It does **not** run `commands.build`; the verification is a human step. |
| **codex-dev-story** | Phase 6 step 2 is the parse check: `tools/codex-studio/scripts/godot-parse-check.gd` on Godot, `commands.smoke` on Unity, the editor-target build on Unreal. Phase 6 step 4 runs `commands.run` — the windowed game launch — to observe the feature and retain a screenshot (`docs/codex-studio/run-and-observe.md`). |
| **codex-regression-suite** | Maps coverage by **globbing test filenames**. It does **not** invoke `commands.test`, so coverage here means "a test file exists", never "a test passed". |

---

## naming

**Controls:** Code naming conventions for the project
**Values:** see field list below
**Default:** engine-specific (auto-populated by `$codex-setup-engine`)
**Set by:** `$codex-setup-engine`, `$codex-settings`
**Read by:** `$codex-adopt`, `$codex-architecture-review`, `$codex-asset-spec`,
`$codex-create-architecture`, `$codex-create-control-manifest`, `$codex-dev-story`,
`$codex-vertical-slice` — each reads `naming.*` from `project.yaml` and feeds the
conventions into a brief, manifest, spec, or explicit audit.

> **These conventions do not install an enforcement gate.** They reach project
> artifacts through the skills that explicitly read them. No bundled commit,
> push, or asset lifecycle hook checks filenames. Cite an actual skill check or
> separately configured CI result rather than treating configured conventions
> as proof of compliance.
>
> `naming.files` describes source filenames. State asset filename conventions
> explicitly in the asset specification; do not assume an absent hook applies
> Godot's naming scheme to Unity or Unreal assets.

> **Moved from `technical-preferences.md`**, which is being deleted. Naming
> conventions are project-level facts shared by everyone on the project, so they
> belong in `project.yaml` alongside the rest of your structured config.

---

### Fields

| Field | Values | Godot default | Unity default | Unreal default |
|-------|--------|---------------|---------------|----------------|
| `classes` | `PascalCase` \| `snake_case` \| `camelCase` | PascalCase | PascalCase | PascalCase |
| `variables` | `snake_case` \| `camelCase` | snake_case | camelCase | camelCase |
| `constants` | `SCREAMING_SNAKE` \| `PascalCase` | SCREAMING_SNAKE | SCREAMING_SNAKE | SCREAMING_SNAKE |
| `signals` (Godot) / `events` (Unity, Unreal) | `past_tense` \| `on_event_name` | past_tense | on_event_name | OnEventName |
| `files` | `snake_case` \| `PascalCase` \| `kebab-case` | snake_case | PascalCase | PascalCase |
| `scenes` / `prefabs` | `snake_case` \| `PascalCase` | snake_case | PascalCase | PascalCase |

> **`signals` vs `events`:** Godot uses signals natively; Unity uses C# events
> or UnityEvents; Unreal uses delegates and dynamic multicast. The field stays
> named `signals` in project.yaml for consistency across engines — interpret as
> "event-like callbacks" regardless of engine.

---

### Affected skills

| Skill | How naming is used |
|-------|--------------------|
| **codex-dev-story** | Passes the naming conventions to the programmer subagent as part of the implementation context |
| **codex-create-control-manifest** | Emits the conventions as manifest rows (classes, variables, signals/events, files, constants) |
| **codex-asset-spec** | Specifies asset naming per the configured convention |
| **codex-create-architecture** / **codex-architecture-review** | Read as project config alongside `performance.*` |
| **codex-vertical-slice** / **codex-adopt** | Read as project config; `$codex-adopt` audits conformance at MEDIUM severity |

No automatic validator enforces these conventions. Skills apply the checks
explicitly documented in their own workflow; naming guidance alone is not a
passing audit result.

---

## features.session_state

> ### RESERVED - COMPATIBILITY ONLY
>
> **No shipped skill or runtime consumer uses this flag to enable session
> tracking.** The resolver retains it for compatibility, but setting it does
> not register lifecycle events, inject context, create logs, or change Codex UI.

**Values:** `off` | `on`
**Compatibility default:** `on` (stored/resolved value only)
**Set by:** `$codex-settings`
**Runtime consumer:** none. The retained `session_state_enabled()` helper is
not called by an installed session pipeline.

**Priority chain:** allowlisted `project.local.yaml` value → `project.yaml` →
compatibility default. Both values have the same runtime effect: none.

Skills such as `$codex-dev-story` and `$codex-story-done` explicitly maintain
`production/session-state/active.md` as part of their workflow, regardless of
this flag. A returning agent explicitly reads the checkpoint and verifies its
facts before continuing. Merely opening Codex, spawning a child agent, compacting
context, or ending a session performs no project-owned checkpoint operation.

### Explicit checkpoint workflow

1. Read the existing `active.md` and the artifacts named by the user's task.
2. After the invoking skill's write approval, update the bounded
   `<!-- CHECKPOINT -->` block with the current task, next action, blockers,
   paths, and observed results. Overwrite the block rather than adding duplicates.
3. Keep optional Epic/Feature/Task focus in the `<!-- STATUS -->` block. These
   fields are file data, not an installed Codex status-bar integration.
4. Reopen the file after writing. On recovery, verify recorded paths and results
   instead of treating an old checkpoint as current evidence.

Create the file from `docs/codex-studio/templates/session-state.md`. There is no
`active.yaml` state contract in this project. No automatic session archive,
compaction log, agent-spawn log, or agent-completion log is installed.
Imported `agent_logging` flags are **RESERVED compatibility data with no bundled
consumer**, not a supported way to enable logging; do not add them to new
configuration. No valid-value or default contract is defined for those imported
keys. Codex's own activity UI and any host-level logging are separate features.

### Manual narrative rotation

When checkpoint notes grow too long, preview the explicit helper:

```bash
bash tools/codex-studio/scripts/rotate-session-state.sh --dry-run
```

After approval to archive the reported notes, invoke the same script without
`--dry-run`. It preserves the checkpoint and moves narrative notes into a dated
file under `production/session-logs/`. Nothing watches file length or calls this
helper in the background. Existing log files remain historical artifacts, not
proof that a lifecycle integration is active.

### Skeleton-first recovery

A multi-section authoring skill may create an approved document skeleton and
fill sections incrementally. This complements the checkpoint; it is not an
alternate runtime selected by the compatibility flag. Follow the invoking
skill's own approval and writing sequence rather than generating every artifact
at startup.

```markdown
# Combat System — GDD

## Overview
<!-- STATUS: incomplete -->

## Player Fantasy
<!-- STATUS: incomplete -->

## Detailed Rules
<!-- STATUS: incomplete -->
```

After a section is approved and written, update its progress marker. On recovery,
read the actual document and required decisions, then resume the next incomplete
section. Do not infer approved decisions from a blank skeleton.

| Skill | Output artifact | Writing contract |
| --- | --- | --- |
| `$codex-design-system` | `design/gdd/[system].md` | Approved skeleton and incremental section writes |
| `$codex-art-bible` | `design/art/art-bible.md` | Template-based, after the skill's write approval |
| `$codex-ux-design` | `design/ux/[screen].md` | Section-by-section authoring and approval |
| `$codex-create-architecture` | `docs/architecture/architecture.md` | Final approved write, not a startup skeleton |
| `$codex-create-stories` | `production/epics/[epic-slug]/story-NNN-[slug].md` | Write after approval names the file set |
| `$codex-create-epics` | `production/epics/[epic-slug]/EPIC.md` | Per-epic approval also names the index update |

### Skills and session files

Session file operations are explicit instructions in the relevant skill, not
subscriptions to an event. Examples include:

| Skill | Explicit session use |
| --- | --- |
| `$codex-dev-story` | Read the active story when present; write checkpoint and observed `Run result:` |
| `$codex-story-done` | Read story/run evidence; update the checkpoint with verdict and next action |
| `$codex-help` | Read existing task context when useful; otherwise inspect project artifacts |
| `$codex-architecture-review` | Record review findings and report paths when its write protocol authorizes it |
| `$codex-team-qa` | Read relevant sprint/checkpoint data and record QA progress when authorized |

If a required argument is absent and the checkpoint provides no reliable value,
ask the user or report `NOT ASSESSED` according to that skill. Do not fabricate a
story, sprint, release version, or previous result. There is no measured token
saving associated with either compatibility value; cost depends on the actual
files read and work performed.

---

## features.token_budget_warn_at

> ### RESERVED - NOT IMPLEMENTED
>
> **No shipped runtime consumer reads this threshold.** Storing it does not
> enable a warning, status-line color, compaction event, or cost monitor.

**Compatibility value:** float between `0.0` and `1.0`
**Compatibility default:** `0.7`
**Set by:** `$codex-settings`
**Runtime consumer:** none

The intended threshold is retained as compatibility data only. The allowlisted
local value may shadow the project value; neither value controls Codex's own
context display, usage limits, or logging. Validation or successful storage of
a value is not evidence that monitoring has started. Use the host's actual
usage/context information when available and report unavailable measurements
explicitly rather than inventing a threshold event.

---

## schema_version

**Controls:** Which version of the project.yaml schema this file conforms to
**Values:** integer
**Default:** `1` (for v1.1 of Codex Game Studios)
**Set by:** `$codex-start`, `$codex-adopt`
**Read by:** Explicit configuration validation and migration helpers; skills that inspect project metadata

> Lets future Codex Game Studios versions detect and migrate old project.yaml files. The
> migration logic compares `schema_version` in the file against the current
> Codex Game Studios's expected version. If newer, warn. If older, run migrations.

---

### Migration behavior

| project.yaml schema_version | Current Codex Game Studios expects | Behavior |
|----------------------------|---------------------|----------|
| Matches expected | — | Normal operation |
| Lower than expected | — | `$codex-adopt` warns and offers migration; skills run with deprecation warnings |
| Higher than expected | — | All skills warn: "This project.yaml was created by a newer Codex Game Studios version. Some settings may be ignored." |
| Missing | — | Treated as legacy (pre-v1.1); migration prompted on next `$codex-start` or `$codex-adopt` |

---

## framework

**Controls:** Tracks which Codex Game Studios version created or last touched this project
**Values:** `framework.version` (semver string) + `framework.last_upgraded` (ISO date)
**Default:** stamped in the template's `project.yaml` at each release
**Set by:** the template; `$codex-start` (Phase 3c), `$codex-setup-engine` and `$codex-gate-check` write the block into a `project.yaml` they create, and `migrate-v1-config.sh` (which `$codex-adopt` runs) writes `framework.version` into the one it builds
**Read by:** no skill branches on it — it is file metadata, not a behavioural setting. It appears in `$codex-start`, `$codex-gate-check`, `$codex-settings` and `$codex-setup-engine` as part of the `project.yaml` block they **write or display**, and in `yaml-helper.sh`.
  *(The four skills above were verified to name it; whether each reads it or merely emits it was NOT separated, so this says 'appears in', not 'read by'.)*

---

### Fields

```yaml
framework:
  version: "1.1.0"
  last_upgraded: "2026-05-14"
```

| Field | Purpose |
|-------|---------|
| `version` | The Codex Game Studios version that created the project (or was last updated to — see `docs/codex-studio/MAINTENANCE.md`). |
| `last_upgraded` | ISO date of the most recent template update. |

---

### Affected skills

None. No runtime consumer acts on `framework.version` or `last_upgraded` — `$codex-adopt`
does not consult them and no background check evaluates their age. They record which template
version the project came from; `docs/codex-studio/MAINTENANCE.md` is the upgrade path.

---

## Migration from v1.0 → v1.1

Here **v1.0/v1.1 refer to inherited configuration format generations**, not
standalone Codex Game Studios release numbers; the current release is recorded
in `codex-studio.toml`.

When a project using the v1.0 configuration format migrates to the v1.1 format,
migration tooling (run via `$codex-adopt`) converts legacy files to `project.yaml`.
This section specifies the intended behavior.

### Detection

A project is detected as needing migration when:
- `project.yaml` does **NOT** exist at the repo root, AND
- One or more legacy files exists:
  - `production/stage.txt`
  - `production/review-mode.txt`
  - `docs/codex-studio/technical-preferences.md`

### Preservation

| Legacy source | Migrates to |
|---------------|-------------|
| `production/stage.txt` (single line) | `project.stage` |
| `production/review-mode.txt` (single line) | `modes.review_mode` |
| `docs/codex-studio/technical-preferences.md` → "Engine & Language" section | `engine.name`, `engine.version`, `engine.language`, `engine.rendering`, `engine.physics` |
| `technical-preferences.md` → "Input & Platform" section | `platform.targets`, `platform.primary_input`, `platform.gamepad_support`, `platform.touch_support` |
| `technical-preferences.md` → "Naming Conventions" section | `naming.classes`, `naming.variables`, `naming.constants`, `naming.signals`, `naming.files`, `naming.scenes` |
| `technical-preferences.md` → "Performance Budgets" section | `performance.target_framerate`, `performance.frame_budget_ms`, `performance.draw_call_limit`, `performance.memory_ceiling_mb` |
| `technical-preferences.md` → "Testing" section | `testing.framework`, `qa.coverage_minimum` (bare number only — prose is reported for manual entry) |
| `technical-preferences.md` → "Engine Specialists" section | `specialists.code`, `specialists.shader`, `specialists.ui`, `specialists.additional` |

**Value rename — `review_mode: none` → `solo`.** v1.0 used `none` for the "no
director reviews" tier; v1.1 renamed that tier to `solo` (the enum is
`full | lean | solo`). Migration **coerces** a legacy `none` to `solo` and reports
the rename in the migration report's Warnings. This is the one documented value
rename, so it is mapped-and-flagged rather than preserved raw: writing `none`
verbatim would produce an enum-invalid `project.yaml` that `resolve_config` rejects
and falls back to the `modes.rigor` value — at `standard` that is `lean`, reviews *on* —
inverting the user's intent. The
`--finalize` preservation check applies the same mapping so it does not falsely
refuse. Every *other* non-v1.1 stage/review value is a fork, not a rename:
preserved raw and flagged for manual resolution, never coerced.

Settings absent from the legacy files (new v1.1 settings like `qa.level`,
`docs.density`, `team.size`, etc.) get hardcoded defaults from the v1.1 schema.

### Cleanup (deferred, non-destructive)

Migration is **non-destructive in v1.1**: legacy files are NOT auto-deleted.
Migration produces `project.yaml` and leaves the legacy files in place. Explicit
configuration readers use `project.yaml` first; they fall back to the legacy file if a
specific key is missing.

Legacy files are deleted only when the user runs
`tools/codex-studio/scripts/migrate-v1-config.sh --finalize` (driven by `$codex-adopt`, which
detects a v1.0 project automatically at Phase 2g). The cleanup step verifies
that every legacy file's content has been preserved in `project.yaml` before
deleting.

### Failure modes

| Problem | Behavior |
|---------|----------|
| Legacy file is malformed (can't parse) | Migration emits warning per file, leaves it untouched, continues with the others. `project.yaml` gets the parseable values + defaults for the rest. |
| Parsed value doesn't match v1.1 enum (e.g. `stage: Alpha` from a fork) | Migration writes the raw value with a `_migration_warning` comment in `project.yaml`. User resolves manually. |
| Both `project.yaml` AND a legacy file exist (split-brain) | Migration tooling refuses to run. Error: "Both project.yaml and legacy files exist — resolve which is authoritative before migrating." |
| Custom sections in forked `technical-preferences.md` | Custom content logged to `production/migration-report.md` as "not migrated — please integrate manually." |

### Migration report

Every migration run writes `production/migration-report.md`:

- Source files detected
- Values preserved (per file → per setting)
- Defaults applied (for v1.1-new settings)
- Warnings encountered (malformed, mismatched enums, etc.)
- Manual review items

User reads the report before running `--finalize`.

---

## Complete example `project.yaml`

A full project.yaml with every setting, showing sensible defaults for a solo
Godot project. Use this as the reference shape when authoring or migrating.

```yaml
schema_version: 1

framework:
  version: "1.1.0"
  last_upgraded: "2026-05-15"

project:
  name: "Forge Knights"
  genre: "ARPG"
  version: "0.1.0"
  stage: Concept             # Concept | Systems Design | Technical Setup | Pre-Production | Production | Polish | Release
  kind: game                 # game | tool | engine | mod | library

modes:
  review_mode: lean          # full | lean | solo
  workflow: standard         # minimal | standard | full
  automation: collaborative  # collaborative | guided | autonomous
  automation_always_ask:     # decision categories that always prompt regardless of mode
    - scope_changes
    - file_deletions
    - schema_changes
  story_granularity: balanced  # coarse | balanced | fine

# TOP-LEVEL, not nested under `modes:` — resolve_config reads
# `workflow_overrides.system_overrides.*` from the document root
# (yaml-helper.sh), and every skill greps the same top-level path.
# Nesting it under `modes:` parses as valid YAML and is silently never read.
workflow_overrides:
  edge_cases: false          # force GDD Edge Cases section required
  tuning_knobs: false        # force GDD Tuning Knobs section required
  art_bible_strict: false    # force all 9 art bible sections regardless of asset stories
  system_overrides: {}       # { combat: full, inventory: minimal }

docs:
  density: balanced          # terse | balanced | thorough

testing:
  framework: gdunit4         # engine-specific — auto-populated by $codex-setup-engine
  strict:
    logic: true              # unit test failures BLOCK story closure
    integration: true        # integration test failures BLOCK
    visual: true             # missing screenshot BLOCKS
    ui: true                 # missing screenshot BLOCKS
    config: false            # advisory only

qa:
  level: standard            # minimal | standard | full
  coverage_minimum: null     # integer 0-100; only enforced at level: full

strict_gate_checks: true     # phase gate failures block stage transition

team:
  size: individual           # individual | small | studio

platform:
  multiplayer: false         # real-time multiplayer
  online: false              # any online features (leaderboards, cloud, telemetry)
  targets: [PC]              # [PC, Mobile, Web, Console]
  primary_input: "Keyboard/Mouse"
  gamepad_support: "Full"    # Full | Partial | None
  touch_support: "None"      # Full | Partial | None
  cert_tier: none            # none | itch | steam | console

engine:
  name: "Godot"              # Godot | Unity | Unreal — set by $codex-setup-engine
  version: "4.6"
  language: "GDScript"       # GDScript | C# | C++ | Blueprint
  rendering: "Forward+"
  physics: "Jolt"

specialists:                 # auto-populated by $codex-setup-engine
  code: "godot-gdscript-specialist"
  shader: "godot-shader-specialist"
  ui: "godot-specialist"
  additional: ["godot-gdextension-specialist"]

naming:
  classes: PascalCase        # PascalCase | snake_case | camelCase
  variables: snake_case
  constants: SCREAMING_SNAKE
  signals: past_tense        # past_tense | on_event_name (engine-interpreted)
  files: snake_case
  scenes: snake_case

accessibility:
  target: none               # none | standard | aaa

cadence:
  sprint_length: "2w"        # 1w | 2w | 3w | 4w | none
  milestone_length: "8w"     # 4w | 6w | 8w | 12w

performance:
  target_framerate: 60
  frame_budget_ms: 16.67
  draw_call_limit: null
  memory_ceiling_mb: null
  enforce: warn              # warn | block | off

commands:                    # simple string OR OS-aware map per command
  build: "godot --headless --export-debug '<PRESET>'"   # your export_presets.cfg name
  test: "godot --headless -s -d --remote-debug tcp://127.0.0.1:0 res://addons/gdUnit4/bin/GdUnitCmdTool.gd -a res://tests --ignoreHeadlessMode"
  run: "godot --path . --windowed --resolution 1280x720"
  smoke: "godot --headless --quit-after 5"

features:
  session_state: on          # RESERVED: stored compatibility value only
  token_budget_warn_at: 0.7   # RESERVED: no warning or monitor is installed
```

And a minimal sparse `project.local.yaml` example — a single developer who wants autonomous mode locally:

```yaml
modes:
  automation: autonomous
```

Only the overridden keys are present; everything else cascades from `project.yaml`.
See "Local Override Pattern" section for full whitelist of what can/cannot be overridden locally.
