# Changelog

All notable changes to the `acss-kit` plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the plugin adheres to [Semantic Versioning](https://semver.org/).

## [0.3.1] - 2026-04-26

### Fixed

- **Plugin README** — documented `/kit-list` command. The command file (`commands/kit-list.md`) and full reference (`docs/commands.md`) already shipped in 0.3.0, but the plugin-level README omitted it from both the Component commands section and the Plugin Structure file-tree diagram.
- **WCAG success-criterion citations** — corrected ambiguous and overstated SC references across reference docs and developer guides:
  - `docs/concepts.md` and `skills/components/SKILL.md` — softened the `aria-disabled` rationale. Previous "fails / violates WCAG 2.1.1" framing was stronger than WCAG actually states (a control being unfocusable when disabled is not automatically a 2.1.1 keyboard-operability failure). Replaced with concrete UX framing — unfocusable disabled controls can't be reached by keyboard or screen-reader users to discover state or read any explanation.
  - `skills/components/references/components/icon-button.md` (×4) and `catalog.md` — clarified the XOR type's accessible-name guarantee. The constraint genuinely covers two SCs simultaneously: WCAG 1.1.1 (text alternative for the non-text icon glyph) and WCAG 4.1.2 (programmatic accessible name for the interactive button). Previous wording cited only 1.1.1 (later 2.1.1, in the original incorrect form) and was inconsistent with the file's own "criteria addressed" section that already lists 4.1.2.
  - `skills/styles/references/role-catalogue.md` — `WCAG 2.1 AA` → `WCAG 2.2 AA` for plugin-wide consistency. Contrast ratio targets (4.5:1 normal, 3.0:1 large/UI) are identical across both spec versions; this is a wording fix only.

## [0.3.0] - 2026-04-26

### Added

- **`acss-kit` consolidated plugin.** Replaces four predecessor plugins (`acss-kit-builder`, `acss-theme-builder`, `acss-app-builder`, `acss-component-specs`) with a single plugin focused on accessible React components and CSS themes for fpkit/acss projects.
- **`components` skill** — accessible React component generation from markdown specs (rehomed from `acss-kit-builder`). 18 component reference docs with embedded TSX/SCSS/Accessibility sections.
- **`styles` skill** — CSS theme generation with OKLCH palette math and WCAG 2.2 AA contrast validation (rehomed from `acss-theme-builder`). Four slash commands: `/theme-create`, `/theme-brand`, `/theme-update`, `/theme-extract`.
- **`component-form` pilot skill** — natural-language form generation (rehomed from `acss-kit-builder`). Auto-triggers on phrases like "create a signup form".
- **`scripts/detect_target.py`** — replaces the previous `acss-app-builder/scripts/detect_component_source.py`. Manages `.acss-target.json` for component output directory resolution. Stripped of all `@fpkit/acss` npm-package detection logic; the script now only resolves locally-vendored sources.

### Removed

- **`acss-app-builder` plugin removed entirely.** Project init (`/app-init`), layouts (`/app-layout`), pages (`/app-page`), forms slash command (`/app-form`), patterns (`/app-pattern`), and compose (`/app-compose`) are no longer included. Users wanting these features can rebuild them on top of `acss-kit`'s components.
- **`acss-component-specs` plugin removed entirely.** Framework-agnostic spec generation (`/spec-add`, `/spec-render`, `/spec-validate`, `/spec-list`, `/spec-promote`, `/spec-diff`) is out of scope for the React-only focus.
- **`@fpkit/acss` npm package detection** — `detect_target.py` no longer detects or warns about npm-installed `@fpkit/acss`. The npm path is gone; components are vendored locally only.
- **Spec-bridge probe** — the previous `Step B0 — Probe acss-component-specs` workflow in the components skill is removed. No more cross-plugin spec lookups.
- **Cross-plugin `/app-form` delegation** — `component-form` skill no longer documents the cross-plugin invocation contract. The skill is invoked directly via auto-trigger.
- **Legacy reference banners** — every component reference doc previously carried a "Legacy reference" banner pointing to `acss-component-specs`. All banners removed.

### Changed

- **Plugin name** from `acss-kit-builder` → `acss-kit`.
- **Skill naming** — top-level skills are now `components` and `styles` (was `acss-kit-builder` and `acss-theme-builder`).
- **Path references** updated throughout: `${CLAUDE_PLUGIN_ROOT}/skills/components/...` and `${CLAUDE_PLUGIN_ROOT}/skills/styles/...`.
- **Theme schema deprecation** — `assets/theme.schema.json` retains `"deprecated": true` to discourage user authoring; the previous `"x-sunset-version": "0.3.0"` removed (we are at 0.3.0). The schema remains as an internal contract for the round-trip scripts.

### Migration notes

Users on any of the predecessor plugins should:

1. Uninstall the old plugins:

   ```shell
   /plugin uninstall acss-kit-builder
   /plugin uninstall acss-theme-builder
   /plugin uninstall acss-app-builder
   /plugin uninstall acss-component-specs
   ```

2. Install `acss-kit`:

   ```shell
   /plugin install acss-kit@shawn-sandy-acss-plugins
   ```

3. Existing `.acss-target.json` files at project roots remain compatible — the schema (`{ "componentsDir": "..." }`) is unchanged.

4. Existing generated component files in your project are not affected — the rename is purely on the plugin side.

5. If you used `/app-init`, `/app-layout`, `/app-page`, `/app-form`, `/app-pattern`, `/app-compose`, `/spec-add`, or any other deleted slash command — those features no longer exist. The form auto-trigger ("create a signup form") still works via the `component-form` skill.
