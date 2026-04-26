# Consolidate to `acss-kit` (single plugin, two skills)

> Filename note: this file should be renamed `acss-consolidate-to-acss-kit.md` and moved to `docs/plans/` per the project plan-mode rule. Done as the first commit during execution (see Phase F step 22).

## Context

The repo today carries **four** plugins with overlapping concerns:

- `acss-app-builder` — project init, layouts, pages, forms, patterns, compose
- `acss-kit-builder` — markdown-as-source component generation (`/kit-add`)
- `acss-theme-builder` — CSS theme generation (`/theme-create`, etc.)
- `acss-component-specs` — framework-agnostic specs (React/HTML/Astro)

The user wants to **focus on accessible React components styled with @fpkit/acss**, simplified to a single plugin (`acss-kit`) with two top-level skills:

- **`components`** — accessible React components, generated from markdown specs (markdown-as-source).
- **`styles`** — themes and CSS tokens for fpkit/acss projects.

`acss-app-builder` and `acss-component-specs` are **deleted entirely** with a hard-cut from the marketplace. `acss-kit-builder` and `acss-theme-builder` content is **rehomed**, then the old plugin folders are deleted.

This plan **extends** `docs/plans/acss-markdown-as-source-refactor.md`, which is largely already executed: 15 component reference docs already have embedded `## TSX Template` / `## SCSS Template` / `## Accessibility` sections, and the `component-form` pilot skill exists. Phases 2–3 of that plan (npm soft-deprecation + cross-plugin `/app-form` delegation) are **superseded** because their target — app-builder — is being deleted.

### Decisions and alternatives

- **Plugin name `acss-kit`** (vs. reusing `acss-kit-builder`): chosen because the consolidated plugin is broader than just components. The `-builder` suffix becomes misleading once styles join.
- **Start at `0.3.0`** (vs. `0.1.0` / `1.0.0` / `0.2.0`): continues the 0.2.0 line of the predecessors. Signals "next minor" for users migrating from kit-builder/theme-builder. Fits semver since the plugin reorg is backward-incompatible.
- **3 skills (components + component-form + styles)** vs. **2 skills**: keeping `component-form` separate — the pilot earned its keep in 0.2.0; auto-trigger reliability has held. Merging is reconsidered only if trigger drift appears.
- **`detect_component_source.py` follows the components skill into acss-kit** as `detect_target.py` (strip npm/deprecation logic). Inlining detection or deferring would either bloat the skill or block Phase A.
- **Move `acss-kit-builder/docs/` to `acss-kit/docs/`** (vs. merge into README / delete): preserves the 6 developer guides; `acss-component-specs/docs/` is dropped with its plugin.
- **Hard-cut marketplace** (vs. deprecation entries): accepted; existing installs need a manual `/plugin install acss-kit`.

## Objective

Land one consolidated `acss-kit` plugin at `0.3.0`, delete the four predecessors, and update the marketplace, READMEs, and CLAUDE.md to reflect the new shape.

## Steps

### Phase A — Scaffold `plugins/acss-kit` (components)

1. **Create `plugins/acss-kit/.claude-plugin/plugin.json`** at `version: 0.3.0`, `name: "acss-kit"`. Why: continues the predecessors' 0.2.0 line; this consolidation is the "next minor".
2. **Create `plugins/acss-kit/skills/components/SKILL.md`** by adapting `plugins/acss-kit-builder/skills/acss-kit-builder/SKILL.md` — update path references, skill name, and frontmatter. Keep markdown-as-source pattern and the Reference-vs-Skill rule.
3. **Move component reference docs**: `plugins/acss-kit-builder/skills/acss-kit-builder/references/components/*.md` (18 files) → `plugins/acss-kit/skills/components/references/components/`. Why: these are the markdown-as-source templates; already complete.
4. **Move other component knowledge-base docs** (`accessibility.md`, `architecture.md`, `composition.md`, `css-variables.md`) from kit-builder to `plugins/acss-kit/skills/components/references/`.
5. **Move the `component-form` skill**: `plugins/acss-kit-builder/skills/component-form/` → `plugins/acss-kit/skills/component-form/`. Update internal references. Why: preserves the Form auto-trigger pilot.
6. **Move kit-builder asset** if present: `plugins/acss-kit-builder/assets/foundation/ui.tsx` → `plugins/acss-kit/assets/foundation/ui.tsx`. Inspect first; the in-flight refactor may have already deleted it (Phase 1 step 9 of the existing plan).
7. **Move `/kit-add` command**: `plugins/acss-kit-builder/commands/kit-add.md` → `plugins/acss-kit/commands/kit-add.md`. Update `${CLAUDE_PLUGIN_ROOT}` references and any internal paths.

8. **Move kit-builder developer guides**: `plugins/acss-kit-builder/docs/` (6 files: `architecture.md`, `recipes.md`, `commands.md`, `concepts.md`, `troubleshooting.md`, `tutorial.md`) → `plugins/acss-kit/docs/`. Update internal references that mention old skill/command paths.

9. **Move and adapt the target-detection script.** Copy `plugins/acss-app-builder/scripts/detect_component_source.py` to `plugins/acss-kit/scripts/detect_target.py`. **Strip the npm/deprecation logic** — remove the `source: "npm"` branch, the `deprecated`/`sunsetVersion` keys, and any references to `@fpkit/acss` package detection. Output reduces to: `componentsDir`, `source: "generated" | "none"`, and `reasons` array. Why: kit-builder's SKILL.md and `component-form` skill read `.acss-target.json`; the script is the only thing that creates/updates it. Without this, components have nowhere to land.

10. **Update components skill and component-form skill references** to point at the new script path (`${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py`) and remove all mentions of `@fpkit/acss`-package detection or npm fallback.

### Phase B — Add the `styles` skill (theme-builder rehome)

11. **Create `plugins/acss-kit/skills/styles/SKILL.md`** by adapting `plugins/acss-theme-builder/skills/acss-theme-builder/SKILL.md`. The "CSS Token Convention" and "Required Contrast Pairings" sections are already present in the source — preserve verbatim.
12. **Move theme references**: `plugins/acss-theme-builder/skills/acss-theme-builder/references/*.md` (3 files: `role-catalogue`, `palette-algorithm`, `theme-schema`) → `plugins/acss-kit/skills/styles/references/`.
13. **Move theme commands**: `plugins/acss-theme-builder/commands/*.md` (4 files: `theme-create`, `theme-brand`, `theme-update`, `theme-extract`) → `plugins/acss-kit/commands/`. Update internal path references.
14. **Move theme scripts**: `plugins/acss-theme-builder/scripts/*.py` (4 files: `generate_palette`, `tokens_to_css`, `css_to_tokens`, `validate_theme`) → `plugins/acss-kit/scripts/`. Update path imports in scripts and the commands that invoke them.
15. **Move theme assets**: `plugins/acss-theme-builder/assets/*` → `plugins/acss-kit/assets/`. The example tokens JSON may already be deleted by the in-flight refactor — skip if absent.

### Phase C — Plugin metadata

16. **Write `plugins/acss-kit/README.md`**: what the plugin does, the two top-level skills + the `component-form` pilot skill, the slash commands (`/kit-add`, `/theme-create`, `/theme-brand`, `/theme-update`, `/theme-extract`), the markdown-as-source contributor recipe (carry over from `acss-kit-builder/README.md`), pointer to `docs/` for developer guides, and a brief migration note for users of the old four plugins.
17. **Write `plugins/acss-kit/CHANGELOG.md`** at `## [0.3.0]`: initial entry documenting the consolidation — which plugins this replaces, what's deleted, and a migration note pointing users to `/plugin install acss-kit`.

### Phase D — Delete old plugins

18. **Delete `plugins/acss-app-builder/`** entirely (manifest, 7 commands, SKILL.md, references, scripts including the now-superseded `detect_component_source.py`, assets).
19. **Delete `plugins/acss-component-specs/`** entirely (manifest, 6 commands, SKILL.md, references, scripts, assets, `docs/`).
20. **Delete `plugins/acss-kit-builder/`** after Phase A confirms all artifacts (skills, references, commands, `docs/`, assets) moved.
21. **Delete `plugins/acss-theme-builder/`** after Phase B confirms all artifacts moved.

### Phase E — Marketplace and root docs

22. **Update `.claude-plugin/marketplace.json`**: remove the four entries (`acss-kit-builder`, `acss-app-builder`, `acss-theme-builder`, `acss-component-specs`); add one entry — `acss-kit` — with description "Generate accessible React components and CSS themes for fpkit/acss projects" plus appropriate tags. Bump marketplace `version` to `0.3.0` to reflect the breaking reorg.
23. **Update repo `README.md`**: replace the "three plugins" section with a single description of `acss-kit`. Add a short Migration section.
24. **Update `CLAUDE.md`** (repo root): rewrite the `## What this repo is` section to describe one plugin with two skills (plus the `component-form` pilot).

### Phase F — Plan housekeeping

25. **Move this plan** to `docs/plans/acss-consolidate-to-acss-kit.md` per the project plan-mode rule.
26. **Mark `docs/plans/acss-markdown-as-source-refactor.md` superseded** by adding a top-of-file callout: "Superseded by `acss-consolidate-to-acss-kit.md` — Phase 0/1/4 work was inherited; Phases 2/3 dropped because acss-app-builder is deleted."

## Verification

Smoke-test in the sandbox per `tests/README.md`:

1. **Install the new plugin.** `tests/setup.sh`, then in the sandbox install `acss-kit` from the local repo. Confirm only `acss-kit` appears in `/plugin list` and version reads `0.3.0`.
2. **Target detection works.** From a fresh sandbox, run `python3 plugins/acss-kit/scripts/detect_target.py tests/sandbox`. Expect JSON with `componentsDir`, `source: "none"`, and a `reasons` array — **no npm-related keys**. Then `/kit-add button` and re-run; expect `source: "generated"` and `.acss-target.json` updated.
3. **Component generation.** `/kit-add button`, `/kit-add card`, `/kit-add dialog`. Files generate from markdown specs at the new path; imports are relative local paths only.
4. **Form skill auto-triggers.** "Create a signup form with email, password, role select." The `component-form` skill triggers and produces a working form (without explicit slash command).
5. **Theme commands.** `/theme-create #4f46e5 --mode=both` writes `light.css` + `dark.css` and passes `validate_theme.py`. `/theme-update src/styles/theme/light.css --color-primary=#0066cc` updates in place.
6. **Old commands gone.** `/app-init`, `/spec-add`, `/app-form` are unrecognized (clean deletion).
7. **Plugin structure validates.** `/verify-plugins` (or `/validate-plugin acss-kit`) passes.
8. **Marketplace integrity.** `marketplace.json` validates against the schema; only the `acss-kit` entry present.
9. **Developer guides reachable.** Confirm `plugins/acss-kit/docs/{architecture,recipes,commands,concepts,troubleshooting,tutorial}.md` exist with internal links updated to the new plugin name.

## Critical files

**Create:**
- `plugins/acss-kit/.claude-plugin/plugin.json`
- `plugins/acss-kit/skills/components/SKILL.md`
- `plugins/acss-kit/skills/styles/SKILL.md`
- `plugins/acss-kit/README.md`
- `plugins/acss-kit/CHANGELOG.md`

**Move (old → new):**
- `acss-kit-builder/skills/acss-kit-builder/references/components/` → `acss-kit/skills/components/references/components/` (18 files)
- `acss-kit-builder/skills/acss-kit-builder/references/{accessibility,architecture,composition,css-variables}.md` → `acss-kit/skills/components/references/`
- `acss-kit-builder/skills/component-form/` → `acss-kit/skills/component-form/`
- `acss-kit-builder/commands/kit-add.md` → `acss-kit/commands/kit-add.md`
- `acss-kit-builder/docs/` → `acss-kit/docs/` (6 developer guides)
- `acss-app-builder/scripts/detect_component_source.py` → `acss-kit/scripts/detect_target.py` (rename + strip npm logic)
- `acss-theme-builder/skills/acss-theme-builder/references/` → `acss-kit/skills/styles/references/` (3 files)
- `acss-theme-builder/commands/` → `acss-kit/commands/` (4 theme-* files)
- `acss-theme-builder/scripts/` → `acss-kit/scripts/` (4 .py files)
- `acss-theme-builder/assets/` → `acss-kit/assets/`

**Edit:**
- `.claude-plugin/marketplace.json`
- `README.md` (repo root)
- `CLAUDE.md` (repo root)
- `docs/plans/acss-markdown-as-source-refactor.md` (superseded callout)

**Delete (entire trees):**
- `plugins/acss-app-builder/`
- `plugins/acss-component-specs/`
- `plugins/acss-kit-builder/`
- `plugins/acss-theme-builder/`

## Next steps (out of scope)

- **Re-add page/layout/pattern features** (deleted with app-builder) only if usage signals demand. If revived, candidates for new `/kit-*` commands or a third skill.
- **Reconsider `component-form` merge into `components`** if trigger reliability drifts. No action required for 0.3.0.
- **Promote additional per-component skills** (Dialog, Table, Popover) only after the Form pilot keeps validating in 0.3.0.
- **Migration breadcrumbs** for users on old plugins, if support questions appear.
- **Python test infra** for the moved theme + target-detection scripts, deferred from the existing refactor.

## Unresolved Questions

None — all open decisions resolved during planning. The plan is ready to execute.
