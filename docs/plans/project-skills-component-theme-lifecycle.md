---
title: Project-level skills and agents for component & theme lifecycle
status: completed
type: standard
plugins-touched: project-level (.claude/) only — no plugin code changed
---

# Project-level skills and agents for component & theme lifecycle

## Context

The `acss-kit` plugin (currently v0.3.0) ships three skills (`components`, `styles`, `component-form`), 6 user-facing slash commands (`/kit-add`, `/kit-list`, `/theme-create`, `/theme-brand`, `/theme-update`, `/theme-extract`), and 5 Python scripts. The plugin is in active iteration — recent commits show frequent component reference doc additions, canonical-shape backfills, and Codex review cycles.

Project-level (`.claude/`) tooling currently covers **release** (`release-plugin`, `release-check`) and **structural validation** (`validate-plugin`, `verify-plugins`, `add-command`), plus two reviewer agents (`skill-quality-reviewer`, `python-script-reviewer`). What is **missing** is tooling to streamline the day-to-day authoring loop: scaffolding new component reference docs in the canonical embedded-markdown shape, scaffolding new theme assets/roles, re-validating existing assets after edits, and getting a single-glance plugin-health audit before release.

This plan adds five maintainer-side skills and two reviewer agents (with two thin command wrappers) to close that gap. All new tooling lives at the project level (`.claude/`), so it is invisible to plugin end users and only loads when the maintainer is working in this repo.

## Objective

Make it cheap and predictable for the maintainer to add or update components and themes without re-reading the canonical shape spec each time, and without forgetting catalog updates, fpkit verification banners, or downstream re-validation.

## Scope

Five skills, two agents, two command wrappers, one README touch-up. Nine new files plus one edit. No changes to the `acss-kit` plugin itself.

| Type    | Path                                                          | Trigger / use                                                                |
| ------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Skill   | `.claude/skills/component-author/SKILL.md`                    | Scaffold a new component reference doc + catalog entry                       |
| Skill   | `.claude/skills/component-update/SKILL.md`                    | Re-verify and refresh an existing component reference doc                    |
| Skill   | `.claude/skills/style-author/SKILL.md`                        | Scaffold a new bundled brand preset, palette role, or theme-schema field     |
| Skill   | `.claude/skills/style-update/SKILL.md`                        | Re-validate and roll forward existing theme assets after edits               |
| Skill   | `.claude/skills/plugin-health/SKILL.md`                       | One-shot plugin audit dashboard (validate + canonical-shape + catalog drift) |
| Agent   | `.claude/agents/component-reference-reviewer.md`              | Audit a single component reference doc against canonical shape rules         |
| Agent   | `.claude/agents/theme-reference-reviewer.md`                  | Audit theme references (role-catalogue, palette-algorithm, theme-schema)     |
| Command | `.claude/commands/review-component.md`                        | Slash wrapper for `component-reference-reviewer`                             |
| Command | `.claude/commands/review-themes.md`                           | Slash wrapper for `theme-reference-reviewer`                                 |
| Edit    | `.claude/agents/README.md`                                    | Document the two new agents alongside existing entries                       |

## Design rationale (alternatives considered)

- **Author/update split vs. unified `component-edit`.** Chose split. Splitting gives Claude unambiguous trigger phrases ("add Tabs component" → `component-author`; "update button to support aria-pressed" → `component-update`), and the workflows differ enough (scaffolding vs. re-verification) that one merged skill would either bloat or under-specify both flows. Cost: two skill files instead of one.
- **Skills vs. agents vs. commands.** Mirrors the existing pattern: skills for multi-step workflows, agents for read-only review, commands as thin slash wrappers around agents (the `review-script` / `python-script-reviewer` pair is the precedent). Skills auto-discover by name and don't need command files unless we want a short slash invocation — left out here to keep scope tight.
- **Auto-trigger via hooks.** Deferred to Next Steps. The reviewer agents are designed to work both manually and as hook callbacks; wiring the PostToolUse hook on `references/components/*.md` is a separate one-line `settings.json` edit.
- **New Python helpers.** Not added. The reviewer agents do canonical-shape checking in Markdown by reading section headers — adequate for the current 17-component catalog. A `verify_canonical_shape.py` helper is on the Next Steps list if the agent's checks become slow or noisy.

## Critical files (read before implementing)

Implementer should skim these to keep new content consistent:

- [plugins/acss-kit/skills/components/SKILL.md](plugins/acss-kit/skills/components/SKILL.md) — canonical 9-section spec lives in the "Authoring New Components" section at the bottom (line ~414).
- [plugins/acss-kit/skills/components/references/components/button.md](plugins/acss-kit/skills/components/references/components/button.md) — reference example of the canonical shape (verification banner at line 3, generation contract at line 9).
- [plugins/acss-kit/skills/components/references/components/catalog.md](plugins/acss-kit/skills/components/references/components/catalog.md) — single source of truth for verification status table.
- [plugins/acss-kit/skills/styles/SKILL.md](plugins/acss-kit/skills/styles/SKILL.md) — role catalogue (15 required + 3 optional roles), 10 WCAG contrast pairs, 4 theme commands.
- [plugins/acss-kit/skills/styles/references/role-catalogue.md](plugins/acss-kit/skills/styles/references/role-catalogue.md) — full role list and contrast targets.
- [plugins/acss-kit/skills/styles/references/palette-algorithm.md](plugins/acss-kit/skills/styles/references/palette-algorithm.md) — OKLCH lightness / hue rules.
- [plugins/acss-kit/skills/styles/references/theme-schema.md](plugins/acss-kit/skills/styles/references/theme-schema.md) — JSON schema and round-trip contract.
- [plugins/acss-kit/assets/brand-template.css](plugins/acss-kit/assets/brand-template.css) — bundled brand template (only one currently; `style-author` may add more).
- [.claude/skills/add-command/SKILL.md](.claude/skills/add-command/SKILL.md) — reference template for a project-level scaffolder skill.
- [.claude/skills/release-plugin/SKILL.md](.claude/skills/release-plugin/SKILL.md) — reference template for a project-level action skill.
- [.claude/agents/skill-quality-reviewer.md](.claude/agents/skill-quality-reviewer.md) — reference template for a reviewer agent (front-matter + check structure + output format).

## Existing tooling that gets reused (do not duplicate)

- `python3 plugins/acss-kit/scripts/generate_palette.py` — used by `style-author` for new brand presets.
- `python3 plugins/acss-kit/scripts/validate_theme.py` — used by `style-author` and `style-update` for WCAG re-validation.
- `python3 plugins/acss-kit/scripts/tokens_to_css.py` — used by `style-author` for palette JSON → CSS conversion.
- `validate-plugin` skill — invoked by `plugin-health` for structural checks.
- `release-check` skill — referenced by `plugin-health` as the "what's left before commit" pointer.
- `skill-quality-reviewer` agent — referenced by `plugin-health` for SKILL.md drift checks.

## Implementation steps

1. **Create `.claude/skills/component-author/SKILL.md`.**
   - Front-matter: `name: component-author`, description matching trigger phrases like "add a new component", "scaffold a component reference doc", "create a Tabs component for acss-kit".
   - Steps: validate `<component-name>` (lowercase, kebab-case, not already in catalog) → ask for fpkit ref version (default the captured ceiling from existing reference docs) → generate `plugins/acss-kit/skills/components/references/components/<name>.md` skeleton with all 9 canonical sections (verification banner, Overview, Generation Contract, Props Interface, TSX Template, CSS Variables, SCSS Template, Accessibility, Usage Examples) → add a row to `catalog.md` "Verification Status" table marked `Status: New — pending fpkit verification` → print summary listing the file paths and a reminder to fill in the TSX Template and Accessibility sections before committing.
   - Do not implement the TSX/SCSS — leave fenced code blocks with `// TODO: copy from fpkit ${ref}` placeholders.

2. **Create `.claude/skills/component-update/SKILL.md`.**
   - Front-matter: `name: component-update`, description matching "update an existing component", "refresh button reference doc", "bump fpkit verification on a component".
   - Steps: confirm the reference doc exists → re-fetch the upstream fpkit source at the captured ref (full GitHub URL, never `blob/main`) → diff against the local TSX/SCSS templates and surface drift → prompt the user to update the verification banner and bump the catalog entry status → call the `component-reference-reviewer` agent on the file → if generation_contract.export_name changed, warn that downstream `/kit-add` consumers may break.
   - Preserves the canonical shape; does not introduce new sections.

3. **Create `.claude/skills/style-author/SKILL.md`.**
   - Front-matter: `name: style-author`, description matching "add a brand preset", "add a new theme role", "scaffold a bundled brand template", "extend the role catalogue".
   - Three sub-flows (the user picks one via AskUserQuestion at the start):
     - **Brand preset** — generate `plugins/acss-kit/assets/brand-presets/<name>.css` from a seed hex by running `generate_palette.py <hex> --mode=brand` and writing the CSS, then re-validating with `validate_theme.py`. Updates the `styles` SKILL.md "Bundled brand presets" list (creating that section on first run).
     - **New role** — guided edit of `references/role-catalogue.md`, `references/theme-schema.md`, and `assets/theme.schema.json` to add a new optional role. Reminds the user to update `tokens_to_css.py:ROLE_GROUPS` and to flag whether the new role should be required (default: optional).
     - **Palette algorithm tweak** — guided edit of `references/palette-algorithm.md` followed by regeneration of the bundled brand template via `generate_palette.py` and re-validation.
   - All flows finish with a contrast-pair re-validation summary.

4. **Create `.claude/skills/style-update/SKILL.md`.**
   - Front-matter: `name: style-update`, description matching "update theme reference", "refine the palette algorithm", "re-validate themes after a role change".
   - Steps: detect which file the user is editing (role-catalogue / palette-algorithm / theme-schema / brand-presets/*) → run the appropriate downstream re-validation (e.g., role catalogue change → re-run `tokens_to_css.py` + `validate_theme.py` on bundled presets; schema change → confirm `theme.schema.json` is in sync; algorithm change → regenerate bundled presets) → call `theme-reference-reviewer` agent.

5. **Create `.claude/skills/plugin-health/SKILL.md`.**
   - Front-matter: `name: plugin-health`, description matching "audit acss-kit", "plugin health check", "what's missing before release".
   - Steps: invoke `validate-plugin acss-kit` (existing skill) → walk `references/components/*.md` and report any missing canonical sections → cross-check `catalog.md` Verification Status against actual files → run `validate_theme.py` on bundled brand presets → summarize "OK / FIX" per category → if any failures, suggest the precise sub-skill to fix (e.g., "5 components missing canonical Accessibility sections — run `/component-update <name>` for each").
   - Output is a single dashboard, no edits.

6. **Create `.claude/agents/component-reference-reviewer.md`.**
   - Front-matter: `name: component-reference-reviewer`, description "Reviews a single component reference doc against the canonical embedded-markdown shape and catalog.md verification table. Use when authoring or editing references/components/<name>.md."
   - Checks: (1) verification banner present at top with `**Verified against fpkit source:**` blockquote; (2) all 9 canonical sections present in correct order; (3) Generation Contract has `export_name`, `file`, `scss`, `imports`, `dependencies`; (4) all fpkit URLs are full `https://github.com/shawn-sandy/acss/...` links pinned to a tag/SHA (not `blob/main`); (5) component appears in `catalog.md` Verification Status table; (6) TSX Template imports only `UI from '../ui'`, React, and other vendored components — never `@fpkit/acss`.
   - Output: PASS / FAIL per check, exact line numbers for failures, no file modifications.

7. **Create `.claude/agents/theme-reference-reviewer.md`.**
   - Front-matter: `name: theme-reference-reviewer`, description "Reviews theme references (role-catalogue, palette-algorithm, theme-schema) for internal consistency and parity with the Python scripts."
   - Checks: (1) every role in `role-catalogue.md` appears in `assets/theme.schema.json` `$defs/palette` and in `tokens_to_css.py:ROLE_GROUPS`; (2) the 10 WCAG contrast pairs in `styles/SKILL.md` match `validate_theme.py:PAIRS`; (3) the OKLCH lightness anchors in `palette-algorithm.md` match constants in `generate_palette.py`; (4) bundled brand presets validate cleanly via `validate_theme.py`.
   - Output: PASS / FAIL per check with file:line citations.

8. **Create `.claude/commands/review-component.md`.**
   - Thin wrapper: `argument-hint: <path/to/references/components/file.md>`, body delegates to `component-reference-reviewer` agent. Mirror the structure of `review-script.md`.

9. **Create `.claude/commands/review-themes.md`.**
   - Thin wrapper: no arguments, body delegates to `theme-reference-reviewer` agent. Mirror the structure of `review-scripts.md`.

10. **Edit `.claude/agents/README.md`.**
    - Add two entries (one paragraph each) describing the new agents, mirroring the existing entry style. Keep the file index-shaped; long content lives in the agent files themselves.

## Verification

After implementation, exercise each new skill end-to-end:

1. **`component-author` smoke test.** Run on a fictional component (e.g., `tabs-test`). Confirm the file is created with all 9 sections and that `catalog.md` gets a new row. Delete the test file and revert the catalog edit.
2. **`component-update` smoke test.** Run against `references/components/button.md` (which is already canonical-shape ✓). The skill should report "no drift detected" and re-run the reviewer agent cleanly.
3. **`style-author` brand preset smoke test.** Run with a seed hex (e.g., `#0f766e`). Confirm a new file lands under `assets/brand-presets/`, palette JSON is valid, and `validate_theme.py` reports passing pairs.
4. **`style-update` smoke test.** Edit a comment-only line in `role-catalogue.md`, run the skill, confirm it re-validates without spurious failures.
5. **`plugin-health` smoke test.** Run on the current branch. Output should be a clean dashboard with mostly OK status (the catalog has known legacy `nav.md` and `form.md` entries — these should appear as "FIX" with a pointer to `/component-update`).
6. **`component-reference-reviewer` direct invocation.** `/review-component plugins/acss-kit/skills/components/references/components/button.md` — should report all PASS.
7. **`theme-reference-reviewer` direct invocation.** `/review-themes` — should report all PASS against the current state.

After verification, do the standard pre-submit checklist: bump `acss-kit` plugin? **No** — these are project-level files only, no plugin version bump required. Do update the root `CLAUDE.md` if it documents the project-level toolchain (it currently mentions some skills by name; check for additions worth listing).

## Next Steps (out of scope)

- **Auto-trigger reviewer agents via hooks.** Add PostToolUse hook entries in `.claude/settings.json` matching `references/components/*.md` and `references/{role-catalogue,palette-algorithm,theme-schema}.md` paths to auto-invoke the reviewer agents on save.
- **`verify_canonical_shape.py` helper.** A stdlib Python script that asserts the 9 sections are present in correct order; replaces the agent's markdown-grep approach if it becomes slow.
- **`/release-check` integration.** Have `release-check` call `plugin-health` automatically and surface the dashboard before clearing the release.
- **Component spec extraction.** If the legacy `acss-component-specs` parity check is reactivated in the future, add a `/component-sync` skill that pulls upstream spec changes into reference docs.
- **Maintainer command index.** Add a project-level `/help-maint` command that lists every project-level skill and one-line usage.

## Unresolved Questions

- Should `style-author` create a new `assets/brand-presets/` directory for bundled brand presets, or extend the existing `assets/brand-template.css` pattern? (Plan currently assumes a new `brand-presets/` directory; flagging because this introduces a new convention.)
- Should the reviewer agents auto-load via `disable-model-invocation: false` so they trigger on natural-language phrases ("review this component"), or should they only run when explicitly invoked from a skill or `/review-*` command?
- Should I bump the project-wide tooling under a new `tools/` umbrella (e.g., `.claude/skills/maint/component-author/`) instead of flat at `.claude/skills/`? Existing project skills are flat, so the plan keeps the flat layout — confirm.
