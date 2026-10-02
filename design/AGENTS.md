# Design Directory

When authoring or editing files in this directory, follow these standards.

## GDD Files (`design/gdd/`)

The 8 GDD sections, in order:
1. Overview — one-paragraph summary
2. Player Fantasy — intended feeling and experience
3. Detailed Rules — unambiguous mechanics
4. Formulas — all math defined with variables
5. Edge Cases — unusual situations handled
6. Dependencies — other systems listed
7. Tuning Knobs — configurable values identified
8. Acceptance Criteria — testable success conditions

**How many are REQUIRED depends on `modes.workflow`** — all 8 at `full`; 5 at
`standard` (Overview, Detailed Rules, Edge Cases, Dependencies, Acceptance
Criteria, plus Formulas when the system has math); none at `minimal`, where
`design/game-brief.md` is the design record instead of a GDD. Resolve the tier
before flagging a section as missing — see `docs/codex-studio/workflow-modes.md`.

> **Three other places already encode the tier rule** —
> `docs/codex-studio/coding-standards.md`, `docs/codex-studio/rules/design-docs.md` and
> `tools/codex-studio/scripts/project-coherence.sh` and the explicit Codex verifier. This file is the copy a session working in
> `design/` reads first, so it must agree with them: demanding all 8 at
> `minimal` warns a jam project about six sections its own configuration says it
> does not need, which trains the user to ignore the warning.

**Section-name alias:** the GDD template and `$codex-design-system` author section 3
as `## Detailed Design`; the standard calls it **Detailed Rules**. Same required
section — accept either heading, never rewrite one into the other.

**File naming:** `[system-slug].md` (e.g. `movement-system.md`, `combat-system.md`)

**Systems index:** `design/gdd/systems-index.md` — update when adding a new GDD.

**Design order:** Foundation → Core → Feature → Presentation → Polish

**Validation:** Run `$codex-design-review [path]` after authoring any GDD.
Run `$codex-review-all-gdds` after completing a set of related GDDs.

## Quick Specs (`design/quick-specs/`)

Lightweight specs for tuning changes, minor mechanics, or balance adjustments.
Use `$codex-quick-design` to author.

## UX Specs (`design/ux/`)

- Per-screen specs: `design/ux/[screen-name].md`
- HUD design: `design/ux/hud.md`
- Interaction pattern library: `design/ux/interaction-patterns.md`
- Accessibility requirements: `design/accessibility-requirements.md`

Use `$codex-ux-design` to author. Validate with `$codex-ux-review` before passing to `$codex-team-ui`.

> **Accessibility requirements sit OUTSIDE `design/ux/` on purpose.** They are a
> project-wide standard the per-screen specs consult, not a spec for one screen.
> `docs/codex-studio/workflow-catalog.yaml`, the Pre-Production, Production and Polish
> gates, and `$codex-architecture-review` all check `design/accessibility-requirements.md`
> at that exact path. Do not "tidy" it under `design/ux/` — every one of those
> checks would stop matching, and the Technical Setup → Pre-Production gate would
> become unpassable. `$codex-ux-design` states the same rule at its `accessibility` mode.
