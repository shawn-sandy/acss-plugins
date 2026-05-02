# acss-kit

A Claude Code plugin for building accessible React applications with the [fpkit/acss](https://github.com/shawn-sandy/acss) design system. Generates components and CSS themes directly into your project — no `@fpkit/acss` npm package required.

## What you get

Two top-level skills, one cross-domain setup skill, and three pilot skills:

- **`components`** — accessible React components from markdown specs. `/kit-add <component>` walks the dependency tree and writes self-contained TSX + SCSS into your project.
- **`styles`** — CSS theme generation. `/theme-create`, `/theme-brand`, `/theme-update`, `/theme-extract` for OKLCH palettes with WCAG 2.2 AA validation.
- **`setup`** — cross-domain first-run skill backing `/setup`. Runs the sass check, copies `ui.tsx`, and seeds light/dark theme. Idempotent.
- **`component-form`** — pilot per-component skill that auto-triggers on phrases like "create a signup form", "add a contact form".
- **`component-creator`** — pilot creator-mode skill that auto-triggers on phrases like "create a primary pill button that says 'Add to cart'", "make me a soft warning alert titled 'Heads up'", "build a card with a heading 'Plan'". `/kit-create` is the explicit fallback. Loads the matched component's reference doc at runtime, resolves the user's phrases against its Props Interface (colour/size synonyms map onto whichever colour-family / size-family prop the component declares), and emits a paste-ready TSX snippet or a standalone component file. Works with any component that has a dedicated `references/components/<name>.md` reference doc (Button, Alert, Card, Dialog, Link, Input, Field, Checkbox, IconButton, Img, Icon, List, Table, Popover, Nav); components that exist only as inline `catalog.md` entries (Badge, Tag, Heading, Text/Paragraph, Details, Progress) are deferred to v0.2.
- **`style-tune`** — pilot per-feel skill that auto-triggers on phrases like "warmer button", "softer card", "tone down the primary", "more spacious cards", "more elevated dialog". `/style-tune` is the explicit fallback. Routes between theme-role and component-SCSS edits with atomic WCAG pre-validation.

## Why

Installing `@fpkit/acss` from npm creates coupling: updates require package bumps, customization means forking or overriding, and the full bundle ships even if you only use a few components. This plugin uses fpkit component source as **reference material** and generates **self-contained implementations** that you own and can freely modify.

Generated components follow the same patterns as fpkit:

- Polymorphic `UI` base component (renders as any HTML element via the `as` prop)
- CSS custom properties with hardcoded fallbacks for zero-config theming
- `data-*` attribute selectors for variants (not BEM modifiers)
- `aria-disabled` pattern for WCAG 2.1.1 compliance on interactive elements
- TypeScript + SCSS with all sizes in rem units

## Migration from prior plugins

`acss-kit` consolidates and replaces four predecessors:

| Predecessor | Status |
|-------------|--------|
| `acss-kit-builder` | Rehomed into `acss-kit` (components skill + `component-form` pilot) |
| `acss-theme-builder` | Rehomed into `acss-kit` (styles skill) |
| `acss-app-builder` | Removed. Project init, page templates, layouts, patterns no longer included |
| `acss-component-specs` | Removed. Framework-agnostic specs not in scope |

If you have any of the old plugins installed:

```shell
/plugin uninstall acss-kit-builder
/plugin uninstall acss-theme-builder
/plugin uninstall acss-app-builder
/plugin uninstall acss-component-specs
/plugin install acss-kit@shawn-sandy-agentic-acss-plugins
```

Existing `.acss-target.json` files at project roots remain compatible — `/kit-add` reads the same shape.

## Prerequisites

- React + TypeScript project
- `sass` or `sass-embedded` in devDependencies (acss-kit will tell you the exact command if missing)

## Installation

```shell
/plugin marketplace add shawn-sandy/agentic-acss-plugins
/plugin install acss-kit@shawn-sandy-agentic-acss-plugins
```

## First-run setup

**Run `/setup` once after installing the plugin.** It front-loads the one-time configuration so subsequent `/kit-add` and `/theme-create` calls are pure generation.

```
/setup
```

What it does:

1. Detects your package manager from the lockfile (`pnpm-lock.yaml`, `yarn.lock`, `bun.lock`, `package-lock.json`).
2. Checks for `sass`/`sass-embedded` in `devDependencies`. If missing, prints the exact install command and stops — no side effects.
3. Writes `.acss-target.json` at your project root (or reuses existing).
4. Copies `ui.tsx` (the polymorphic foundation component) verbatim to your target directory.
5. Seeds `src/styles/theme/light.css` and `dark.css` from a prompt for a seed hex color.
6. Detects your project's main CSS/SCSS entry (`src/styles/index.scss`, `src/index.css`, `app/globals.css`, etc.), prompts you to pick when multiple candidates exist or to specify a path when none are found, and idempotently appends `@import` lines for the new theme files. The chosen file is recorded under `stack.cssEntryFile` in `.acss-target.json`.

Pass `--no-theme` to skip theme generation, or `--target=<dir>` to override the component output directory.

**Generated artifacts are committed — developer owns the code.** `.acss-target.json`, `src/components/fpkit/`, and `src/styles/theme/` should be in version control, not `.gitignore`.

`/setup` is idempotent: re-running it checks each artifact and skips anything already present.

## Component commands

### `/kit-list [component]`

List available components or inspect one without writing any files. Read-only — useful for discovering names, props, CSS variables, and dependencies before running `/kit-add`. The full reference (signature, examples, output shape) is in [`docs/commands.md`](docs/commands.md).

```
/kit-list
/kit-list dialog
```

### `/kit-add <component> [component2 ...]`

Generate one or more components into your project.

```
/kit-add badge
/kit-add button
/kit-add dialog
/kit-add button card alert
```

**What happens:**

1. **Init check** — verifies sass is in devDependencies; copies `ui.tsx` (the foundation component) to your target directory if not already present.
2. **Target directory** — runs `scripts/detect_target.py`. If `.acss-target.json` is missing, asks where to generate files (default: `src/components/fpkit/`).
3. **Stack detection** — runs `scripts/detect_stack.py` to classify framework (vite/next/remix/astro/cra), CSS pipeline, and entrypoint file; persists the result into `.acss-target.json` under a `stack` key.
4. **Dependency resolution** — reads the component's Generation Contract, walks the dependency tree recursively.
5. **Preview** — shows the full file tree that will be created and waits for confirmation.
6. **Bottom-up generation** — generates leaf dependencies first (e.g., `icon.tsx` before `icon-button.tsx` before `dialog.tsx`).
7. **Skip existing** — files that already exist are skipped and imported from instead of overwritten.
8. **Summary** — displays created/skipped files and an import/usage snippet.
9. **Verify integration** — runs `scripts/verify_integration.py` against the recorded `stack.entrypointFile`. Missing imports are surfaced as a numbered fix-up list; the plugin never auto-edits the entrypoint.

### `/kit-create <description>`

Creator mode — generate any acss-kit component from a natural-language description. The underlying `component-creator` skill also auto-triggers on the same phrasing without the slash command.

```text
/kit-create primary pill button that says "Add to cart"
/kit-create soft warning alert titled "Heads up" with body "Your card expires next month"
/kit-create card with a heading "Plan" and content "Premium tier with all features"
/kit-create small outline icon-button with aria-label "Close"
```

Loads the matched component's reference doc at runtime, parses its `## Props Interface`, resolves the user's phrases against the declared prop set, and emits a paste-ready TSX snippet (default) or a standalone component file. Works with any component that has a dedicated `references/components/<name>.md` doc — Button, Alert, Card, Dialog, Link, Input, Field, Checkbox, IconButton, Img, Icon, List, Table, Popover, Nav. Refinement turns ("make it larger", "swap to secondary", "change the title to 'Save'") merge into the in-memory spec and re-emit. Full reference in [`docs/commands.md`](docs/commands.md#kit-create).

### Auto-trigger: form generation

The `component-form` skill auto-triggers when you ask for a form in plain English:

> "Create a signup form with email, password, and a role select."

It derives the field list, runs `/kit-add field input button checkbox` if any of those aren't vendored yet, and writes a self-contained accessible form.

## Theme commands

### `/theme-create <hex-color> [--mode=light|dark|both]`

Generate `light.css` and `dark.css` from a seed color using OKLCH palette math. Produces WCAG 2.2 AA-validated semantic role tokens.

```shell
/theme-create "#4f46e5"
/theme-create "#0f766e" --mode=light
```

### `/theme-brand <name> [--from=<hex-color>]`

Scaffold a `brand-<name>.css` file with primary/accent overrides that layer on top of `light.css` and `dark.css`.

```shell
/theme-brand forest --from="#0f766e"
/theme-brand coral
```

### `/theme-update <file> <--color-role=#hex> [...]`

Edit specific role values in an existing theme file and re-validate. Reverts any change that fails WCAG AA.

```shell
/theme-update src/styles/theme/light.css --color-primary="#2563eb"
/theme-update src/styles/theme/dark.css --color-primary="#7dd3fc" --color-focus-ring="#7dd3fc"
```

### `/theme-extract <image-path|figma-url>`

Extract brand colors from an image or Figma design and generate full theme CSS.

```shell
/theme-extract ~/Downloads/brand-moodboard.png
/theme-extract https://figma.com/design/abc123/Brand-Guide
```

### `/style-tune <natural-language description>`

Adjust visual feel using natural language. Auto-triggers on phrases like "warmer button" / "softer card" / "more elevated dialog" — the slash form is the explicit fallback. Six v1 token families: color, radius, spacing, elevation, size, height.

```shell
/style-tune make the button feel softer and warmer
/style-tune tone down the primary color a touch
/style-tune more spacious cards
```

Theme-layer edits delegate to `/theme-update` after a pre-validation pass; component-layer edits write the targeted `--{component}-*` tokens in place. Paired roles and light/dark mirrors are atomic — either every role applies or none do.

## Available components

| Category | Components | Notes |
|----------|-----------|-------|
| **Simple** | badge, tag, heading, text, link, list, icon, img | Leaf components |
| **Interactive** | button, icon-button | Inlined `useDisabledState` |
| **Form** | field, input, checkbox | `checkbox` depends on input |
| **Layout** | card, nav | Compound components |
| **Complex** | alert, dialog, popover, table | Varies (e.g. dialog needs button + icon-button + icon) |
| **Form (skill)** | `component-form` | Auto-triggers on form-related natural-language prompts |

The full catalog with verification status against the upstream `@fpkit/acss` source is in [`skills/components/references/components/catalog.md`](skills/components/references/components/catalog.md).

## Theme structure

Generated theme files follow the three-layer token cascade:

- `light.css` — semantic role tokens under `:root`
- `dark.css` — semantic role tokens under `[data-theme="dark"]`
- `brand-<name>.css` — primary/accent overrides layered on top

Toggle dark mode by setting `data-theme="dark"` on the `<html>` element.

The full CSS Token Convention — 18 defined `--color-*` properties (15 required + 3 optional), grouped by purpose, with the WCAG 2.2 AA Required Contrast Pairings table — is documented in [`skills/styles/SKILL.md`](skills/styles/SKILL.md#css-token-convention).

## Generated code characteristics

### TypeScript (.tsx)

- All types are **inlined** in the component file (never imported from other generated components).
- Imports use **local paths only** — never `@fpkit/acss`.
- The `UI` base component is always imported from `../ui`.
- Interactive components inline a condensed `useDisabledState` hook (~50 lines) for WCAG-compliant disabled handling.

### SCSS (.scss)

- All values in **rem units** (never px; conversion: px / 16 = rem).
- Every CSS variable includes a **hardcoded fallback** so components work without global tokens.
- Variants use `data-*` attribute selectors.
- Disabled state uses `[aria-disabled="true"]`.

```scss
.btn {
  font-size: var(--btn-fs, 0.9375rem);
  padding-inline: var(--btn-padding-inline, calc(var(--btn-fs, 0.9375rem) * 1.5));
  background: var(--btn-bg, transparent);
  color: var(--btn-color, currentColor);

  &[data-color="primary"] {
    background: var(--btn-primary-bg, var(--color-primary, #0066cc));
    color: var(--btn-primary-color, var(--color-text-inverse, #fff));
  }

  &[aria-disabled="true"] {
    opacity: var(--btn-disabled-opacity, 0.6);
    pointer-events: none;
  }

  &:focus-visible {
    outline: var(--btn-focus-outline, 2px solid currentColor);
    outline-offset: var(--btn-focus-outline-offset, 2px);
  }
}
```

## The UI Foundation Component

`ui.tsx` is the only file copied verbatim from fpkit. It is a polymorphic React component (~170 lines, zero dependencies beyond React) that renders as any HTML element via the `as` prop, forwards all props (including ARIA attributes), and provides type-safe refs matching the rendered element type.

All generated components build on top of `UI`. It is copied to your target directory on first `/kit-add` run and should not be deleted.

## Adding a new component (contributor recipe)

When adding or updating a component reference doc, follow the canonical embedded-markdown shape. Each component is a single markdown document — spec, code, and accessibility guidance all in one file.

### 1. Verify against fpkit source

1. Capture the current `@fpkit/acss` version: `npm view @fpkit/acss version`.
2. Resolve to the matching git tag in [`shawn-sandy/acss`](https://github.com/shawn-sandy/acss). If no matching tag exists, use the closest and note the gap.
3. Fetch the upstream source from `https://github.com/shawn-sandy/acss/blob/<tag-or-sha>/packages/fpkit/src/components/<component>/<component>.tsx` (full GitHub URL, never `blob/main`).
4. Compare upstream behavior to what you intend to vendor. Note any intentional divergence (inlined hooks, simplified compound APIs, dropped subcomponents) — these are features, not bugs.

### 2. Author the canonical sections

Create `skills/components/references/components/<name>.md` with these sections in order:

- **Verification banner** — top-of-file blockquote starting `**Verified against fpkit source:** \`@fpkit/acss@<version>\``. Document any intentional divergence.
- **`## Overview`** — one-paragraph summary.
- **`## Generation Contract`** — `export_name`, `file`, `scss`, `imports`, `dependencies`.
- **`## Props Interface`** — TypeScript types.
- **`## TSX Template`** — fenced ```tsx``` block with the full implementation. Imports use relative paths only; never `@fpkit/acss`.
- **`## CSS Variables`** — fenced ```scss``` listing custom properties.
- **`## SCSS Template`** — fenced ```scss``` with the actual rules.
- **`## Accessibility`** — required. Cover keyboard interaction, ARIA, focus management, target size, color contrast, and the WCAG 2.2 AA criteria addressed.
- **`## Usage Examples`** — fenced ```tsx``` with common patterns.

The required `## Accessibility` section is load-bearing — don't strip a11y patterns from the TSX/SCSS. Reviewers reject reference docs without it.

### 3. Reference vs Skill

Most components live as reference docs. Composable, complex, or high-iteration components can be promoted to their own skill at `skills/component-<name>/SKILL.md` with discovery-friendly trigger phrases in the frontmatter `description`.

Currently, the only component promoted to a skill is `Form` (see `skills/component-form/SKILL.md`). It serves as a pilot — adopt the per-component skill pattern for additional components only after observing trigger reliability in real usage.

### 4. Log verification status

Add an entry to the verification status table in [`catalog.md`](skills/components/references/components/catalog.md):

```md
| Foo | [`foo.md`](foo.md) | `@fpkit/acss@<version>` | New / Verified — <intentional divergences if any> |
```

This table is the single source of truth for which components have been migrated to the canonical shape.

### 5. Verify locally

For automated structural validation (the default before opening a PR):

```sh
tests/run.sh
```

This extracts the new reference doc, syntax-checks the TSX, validates the SCSS contract (var fallbacks), and confirms the manifest is intact. See [`tests/README.md`](../../tests/README.md) for first-time setup.

For end-to-end smoke testing — confirming `/kit-add <component>` actually writes a usable file — bootstrap the demo sandbox: `tests/setup.sh` from the repo root, then `cd tests/sandbox && claude` and run `/kit-add <component>`.

## Plugin Structure

```
.claude/plugins/acss-kit/
  .claude-plugin/
    plugin.json                            # Plugin metadata (name, version, author)
  assets/
    foundation/ui.tsx                      # UI base component (copied to user projects)
    brand-template.css                     # Brand preset placeholder (theme-brand)
    theme.schema.json                      # Internal contract for round-trip scripts
  commands/
    setup.md                               # /setup  ← start here after install
    kit-list.md                            # /kit-list
    kit-add.md                             # /kit-add
    kit-create.md                          # /kit-create  (creator mode)
    theme-create.md                        # /theme-create
    theme-brand.md                         # /theme-brand
    theme-update.md                        # /theme-update
    theme-extract.md                       # /theme-extract
    style-tune.md                          # /style-tune
  scripts/
    detect_target.py                       # Manages .acss-target.json
    detect_package_manager.py             # Detects pnpm/yarn/bun/npm from lockfile
    detect_stack.py                        # Classifies framework/bundler/cssPipeline/entrypoint into .acss-target.json#stack
    verify_integration.py                  # Read-only post-step: checks entrypoint imports the artifacts that were written
    generate_palette.py                    # OKLCH palette math
    oklch_shift.py                         # Hex + per-channel OKLCH offsets → hex
    _oklch.py                              # Internal hex↔OKLCH helpers (shared by generate_palette + oklch_shift)
    tokens_to_css.py                       # Palette JSON → CSS theme
    css_to_tokens.py                       # CSS theme → palette JSON (round-trip)
    validate_theme.py                      # WCAG 2.2 AA contrast pair validator
  skills/
    components/
      SKILL.md                             # Components skill workflow
      references/
        accessibility.md                   # WCAG patterns, useDisabledState
        architecture.md                    # UI internals, polymorphic pattern
        composition.md                     # Compound patterns, decision tree
        css-variables.md                   # Naming + fallback strategy
        components/                        # 16 component reference docs + catalog.md + foundation.md
    styles/
      SKILL.md                             # Styles skill workflow
      references/
        role-catalogue.md                  # 18 semantic color roles + contrast targets
        palette-algorithm.md               # OKLCH lightness targets
        theme-schema.md                    # Internal JSON schema reference
    component-form/
      SKILL.md                             # Form pilot — auto-triggers on natural language
    component-creator/
      SKILL.md                             # Creator-mode pilot — backs /kit-create; auto-triggers on "create a <component>" phrasing
    style-tune/
      SKILL.md                             # Style-feel pilot — auto-triggers on adjective + component
      references/
        intent-vocabulary.md               # Modifier → token-family table
    setup/
      SKILL.md                             # Cross-domain setup skill (/setup command)
  docs/                                    # Developer guides (architecture, recipes, troubleshooting)
```

## Developer guides

Detailed guides are in [`docs/`](docs/):

- [concepts.md](docs/concepts.md) — mental model: UI base, data-\* variants, CSS-var fallbacks, aria-disabled, generation flow
- [commands.md](docs/commands.md) — full reference for every slash command (`/setup`, `/kit-list`, `/kit-add`, `/kit-create`, `/style-tune`, `/theme-create`, `/theme-brand`, `/theme-update`, `/theme-extract`)
- [recipes.md](docs/recipes.md) — step-by-step walkthroughs for common tasks
- [troubleshooting.md](docs/troubleshooting.md) — concrete failure modes and fixes
- [architecture.md](docs/architecture.md) — contributor guide: adding components, version-bump checklist
- [tutorial.md](docs/tutorial.md) — start-to-finish walkthrough

## License

MIT
