# Changelog

All notable changes to the `acss-kit` plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the plugin adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.9.0] - 2026-05-03

### Added

- **`/kit-sync` command and `kit-sync` skill** — bulk-install every shipped acss-kit component, the `ui.tsx` foundation, and a starter OKLCH theme into a project in a single command. Walks `references/components/catalog.md`, resolves each component's Generation Contract `dependencies:` recursively, dedupes the union, and generates files bottom-up. Then copies `assets/foundation/ui.tsx`, runs `generate_palette.py` + `tokens_to_css.py` on a seed hex (prompted, or via `--seed=<hex>`), and writes the result to `<projectRoot>/.acss-kit/manifest.json` so subsequent runs can detect drift. Flags: `--target=<dir>`, `--styles-dir=<dir>`, `--seed=<hex>`, `--skip-styles`, `--dry-run`. If the manifest already exists, every file is routed through the `/kit-update` drift check before writing — modified files are skipped, clean files overwritten, no user customizations clobbered.
- **`/kit-update` command** — safe re-copy after a plugin upgrade. Reads `.acss-kit/manifest.json`, computes drift via `diff_status.py` (normalized sha256 comparison), and overwrites only files whose on-disk content still matches the recorded hash. Modified files are skipped by default and listed in the summary. Flags: `<component>...` (filter), `--check` (report only, no writes), `--force` (overwrite modified files too, writes `<file>.bak` first).
- **`scripts/hash_file.py`** — generator/validator that hashes a file or stdin content with sha256 after applying the kit-sync normalization rules (LF endings, strip trailing whitespace per line, collapse trailing blank lines to one). Stdlib only. Both written content and on-disk content during drift detection share the same normalization, so a Prettier or editor save doesn't trigger spurious "modified" classifications.
- **`scripts/manifest_read.py`** — detector that reads `.acss-kit/manifest.json` from a project root and emits its contents as JSON. Returns `exists: false` with a `reasons` array when the manifest is missing, malformed, or has a mismatched `schemaVersion`. Detector contract; exit 0/1.
- **`scripts/manifest_write.py`** — generator/validator that atomically merges a stdin JSON payload into `.acss-kit/manifest.json` (write-temp + rename). Preserves entries not mentioned in the payload, accepts a `removePaths` array for pruning, and stamps `generatedAt` with the current UTC timestamp on every write.
- **`scripts/diff_status.py`** — detector that classifies every file recorded in the manifest as `clean`, `modified`, or `missing` by comparing the normalized on-disk sha256 to the recorded hash. Includes `--self-test` that exercises the full hash → write → read → diff (clean / edited / deleted) round-trip plus the CRLF-vs-LF normalization invariant. Wired into `tests/run.sh` as Step 7d so the manifest contract is verified on every harness run.

## [0.8.0] - 2026-05-03

### Added

- **`/prompt-book` command and bundled prompt book** — a copy-paste catalogue of natural-language prompts mapped to every shipped slash command across `acss-kit` and `acss-utilities`. Run `/prompt-book` to print the full book, or `/prompt-book <section-number>` to print a single section. The book itself lives at `plugins/acss-kit/docs/prompt-book.md`, ships with the plugin install, and is the canonical entry point for new users who want to see what they can ask Claude Code to do without memorising command syntax.

## [0.7.0] - 2026-05-02

### Added

- **Pilot `component-creator` skill and `/kit-create` command** — natural-language creator mode that works on any component with a dedicated `references/components/<name>.md` reference doc (Button, Alert, Card, Dialog, Link, Input, Field, Checkbox, IconButton, Img, Icon, List, Table, Popover, Nav). Describe a UI element ("primary pill button that says 'Add to cart'", "soft warning alert titled 'Heads up' with body 'Your card expires next month'", "card with a heading 'Plan' and content 'Premium tier'") and the skill loads the matched component's reference doc at runtime, parses its Props Interface, and resolves the user's phrases against the declared prop set. Two global synonym tables (colour family and size family) collapse common adjectives onto whichever colour-like / size-like prop the matched component carries, so "primary" maps to `color` on Button and `severity` on Alert without per-component lookup tables in the skill. Single-element components (Button, Alert, Link, IconButton, Img, Icon, Input, Checkbox, Field) and compound components (Card, Table, List with their dotted children) are both supported. Two carve-outs from no-silent-defaults: A3.5 for state-control props (`open`, `expanded`, `visible`, `checked`) with paired `on*` callback no-ops, and A3.6 for component-declared safe defaults (Button's `type="button"`). Refinement turns ("make it larger", "swap to secondary", "change the title to '<X>'") merge into the in-memory spec and re-emit. A two-tier validation matrix (generic rules + any `## Generation Notes — Creator Mode` block on the matched reference doc) blocks broken combinations before any disk write. Components that live only as inline catalog entries (currently Badge, Tag, Heading, Text/Paragraph, Details, Progress) are deferred to v0.2 — promote them via the `component-author` maintainer skill first. Multi-component compositions in a single prompt are deferred to v0.3.
- **`scripts/detect_css_entry.py`** — new detector that locates candidate CSS / SCSS entry files (e.g. `src/styles/index.scss`, `src/index.css`, `app/globals.css`) and reports which `light.css`, `dark.css`, `token-bridge.css`, and `utilities.css` imports each candidate already carries. Detector contract; stdlib only; includes `--self-test`. Used by `/setup` Step 7.5 to wire generated theme imports into the project's main stylesheet without editing the TSX entrypoint.
- **`/setup` Step 7.5 — auto-wire theme imports** — after seeding `light.css` and `dark.css`, `/setup` now detects the project's main CSS/SCSS entry, prompts the user to pick when multiple candidates exist (or to specify a path when none is found), and idempotently appends `@import` lines for the theme files. The chosen path is persisted at `stack.cssEntryFile` in `.acss-target.json` so re-runs and `verify_integration.py` both honor the user's choice. Skipped under `--no-theme`.
- **`scripts/detect_stack.py`** — new detector that classifies the user's build stack so `/kit-add`, `/theme-create`, and `/utility-add` can tailor integration advice. Resolves `framework` (vite, next, remix, astro, cra, or unknown), `bundler`, `cssPipeline` (any of tailwind, sass, postcss, css-modules), `tsconfig` presence, and `entrypointFile`. Detector contract; stdlib only; includes `--self-test` covering all five frameworks plus mixed-pipeline cases. The components and styles SKILLs persist its result into `.acss-target.json` under a `stack` key with `detectedAt` for cheap freshness checks.
- **`scripts/verify_integration.py`** — read-only post-step that checks the user's entrypoint actually imports the artifacts produced by `/kit-add`, `/theme-create`, and `/utility-add`. Verifies `token-bridge.css`, `utilities.css` (and that the bridge import precedes the utilities import on a line-number basis), theme CSS (`light.css`/`dark.css`), and that `<componentsDir>/ui.tsx` is referenced from at least one source file under `src/`. Detector contract — exit 0 on full wire-up, exit 1 with a `reasons` array listing each missing import. Never edits user files; SKILLs surface the reasons as a fix-up list.
- **Components SKILL — Step A3.1 (detect stack) + Step G (verify integration)** — `/kit-add` now writes a `stack` block into `.acss-target.json` on first run and runs `verify_integration.py` after Step F's summary, surfacing missing imports as a numbered fix-up list rather than auto-editing the entrypoint.
- **Styles SKILL — "Integration verification (all flows)" section** — `/theme-create`, `/theme-brand`, `/theme-update`, and `/theme-extract` all run `verify_integration.py` after `validate_theme.py` succeeds, so generated theme CSS is checked against the user's actual entrypoint imports.

- **Pilot `style-tune` skill and `/style-tune` command** — natural-language adjustment of acss-kit components and theme roles. Routes "warmer button", "softer card", "tone down the primary", "more spacious cards", "more elevated dialog", "smaller buttons", "narrower dialog", "taller dialog" between theme-role edits (delegated to `/theme-update` with WCAG pre-validation) and component SCSS token edits. Six v1 token families (color, radius, spacing, elevation, size, height) across six components (button, card, alert, dialog, input, nav). Atomic batch pre-validation guarantees paired roles and light/dark mirrors never desync. `references/intent-vocabulary.md` documents the full modifier → token-family table.
- **`scripts/oklch_shift.py`** — new CLI helper that takes a hex color plus per-channel OKLCH offsets (`--hue`, `--chroma`, `--lightness`) and emits the shifted hex. Generator/validator contract; stdlib only. Exits 0 whenever a usable hex was produced (with `clamped: true` and a populated `reasons` array when the math hit a gamut boundary). Powers `style-tune`'s color deltas.
- **`scripts/_oklch.py`** — internal shared module exposing `hex_to_oklch`, `oklch_to_hex`, `in_gamut`. Extracted from `generate_palette.py` so both palette generation and `oklch_shift.py` use the same conversion math. `oklch_to_hex` defensively clamps `L` to `[0, 1]` upfront and falls back to a directly-synthesized achromatic hex on gamut failure (no recursion).
- **`tests/setup.sh --with-style-tune`** — opt-in fixture flag that seeds `light.css` and `dark.css` from a baseline palette so end-to-end style-tune prompts have a populated theme to edit. Component vendoring (`/kit-add`) still requires an interactive Claude session — `RECIPE.md` walks through that step.

### Changed

- **`.acss-target.json` schema is now additive with a `stack` block** — `{ framework, bundler, cssPipeline, tsconfig, entrypointFile, cssEntryFile, detectedAt }`. Existing `componentsDir` / `utilitiesDir` consumers are unaffected; the detectors and verifiers degrade gracefully when the block is absent (they emit a reason pointing back to `detect_stack.py`). `cssEntryFile` is populated by `/setup` Step 7.5 when the user picks (or supplies) a CSS/SCSS entry.
- **`scripts/verify_integration.py` — accepts wired-up artifacts in `stack.cssEntryFile`** in addition to the TSX `entrypointFile`. The cross-file scan covers `light.css`, `dark.css`, `token-bridge.css`, and `utilities.css` (so `/utility-*` flows that route imports through SCSS no longer trip the verifier). The bridge-before-utilities ordering check now runs inside whichever file holds both imports and is skipped when the imports are split across files. `find_import_line()` recognises Sass `@import`, `@use`, and `@forward` lines. When `stack.cssEntryFile` is configured but the file does not exist, an explicit reason directs the user to re-run `/setup` or remove the stale entry.

### Fixed

- **`detect_stack.py` — Next.js `src/` directory layouts** (`src/app/layout.{tsx,jsx}`, `src/pages/_app.{tsx,jsx}`) are now recognized as entrypoint candidates so stack detection no longer returns `entrypointFile: null` on standard Next projects that use the `src/` convention.
- **`detect_stack.py` — `*.module.sass` (Sass indented syntax) files now register as `css-modules`** in `cssPipeline`, alongside `*.module.css` and `*.module.scss`.
- **`detect_stack.py` — `source: "detected"` now requires a non-null `entrypointFile`.** Known framework + missing entrypoint downgrades to `source: "unknown"` (exit 1) so the SKILL prompts the developer for the entrypoint instead of persisting an unverifiable result.
- **`verify_integration.py` — `find_any_use()` no longer matches the bare last path segment.** Searches restrict to import/require statements containing the normalized component-dir fragment, eliminating false positives (e.g. a comment mentioning "fpkit") and false negatives (imports that omit the segment).
- **`verify_integration.py` — suggested import path now uses `os.path.relpath` from the entrypoint's directory** to the artifact, so the fix-up snippet is correct for entrypoints that live outside `src/` (e.g. Next's `app/layout.tsx` now gets `../src/styles/token-bridge.css` instead of the previous broken `./styles/...` form).
- **`scripts/generate_palette.py` refactored** — its inline OKLCH conversion helpers moved into the new shared `scripts/_oklch.py` module. Public CLI behavior is byte-identical against five canonical seeds (`#2563eb`, `#7c3aed`, `#16a34a`, `#dc2626`, `#0f766e`).
- **Test harness simplified** — replaced the Vite + React + TypeScript demo sandbox (`tests/setup.sh`) with a minimal `package.json` + `tsconfig.json` fixture. No app framework, no `npm create`, no `npm run dev`. Replaced the Storybook + Playwright + axe-playwright deep check (`tests/storybook.sh`, `plugins/acss-kit/.harness/`, `scripts/generate_stories.mjs`) with a browserless `tests/e2e.sh` that runs `tsc --noEmit`, compiles SCSS, validates theme contrast, and runs jsdom + axe-core on rendered components. Faster install footprint, narrower a11y coverage (no real-pixel contrast or focus-indicator detection — see `tests/README.md` for the trade-off table). Plugin runtime behavior unchanged.
- **Marketplace repo renamed** from `shawn-sandy/acss-plugins` to `shawn-sandy/agentic-acss-plugins`. Install commands now use `@shawn-sandy-agentic-acss-plugins` (the marketplace alias is derived from `<owner>-<repo>`). The marketplace `name` field in `.claude-plugin/marketplace.json` also moved from `acss-plugins` to `agentic-acss-plugins` to match. No plugin behavior changed; this is metadata-only.

## [0.4.0] - 2026-04-26

### Added

- **`/setup` command** — first-run project bootstrap for acss-kit. Detects package manager via lockfile inspection, prints the exact `<pm> add -D sass` command (does not execute), writes `.acss-target.json`, copies `ui.tsx` verbatim, and optionally seeds `src/styles/theme/light.css` + `dark.css` via the OKLCH pipeline. Per-step idempotency: re-running `/setup` skips artifacts that already exist and tabulates `created` vs `kept` in the final summary.
- **`detect_package_manager.py`** — new detector script. Inspects lockfiles in priority order (`pnpm-lock.yaml` → `yarn.lock` → `bun.lock` → `bun.lockb` → `package-lock.json`) then falls back to `package.json#packageManager` field. Outputs `{ manager, lockfile, installCommand, projectRoot, reasons }`. Includes `--self-test` mode for `tests/run.sh` smoke check.
- **`skills/setup/SKILL.md`** — cross-domain setup skill. Deliberately not nested under `components` or `styles`; documents the placement rationale inline for future maintainers.

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
   /plugin install acss-kit@shawn-sandy-agentic-acss-plugins
   ```

3. Existing `.acss-target.json` files at project roots remain compatible — the schema (`{ "componentsDir": "..." }`) is unchanged.

4. Existing generated component files in your project are not affected — the rename is purely on the plugin side.

5. If you used `/app-init`, `/app-layout`, `/app-page`, `/app-form`, `/app-pattern`, `/app-compose`, `/spec-add`, or any other deleted slash command — those features no longer exist. The form auto-trigger ("create a signup form") still works via the `component-form` skill.
