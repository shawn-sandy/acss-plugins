# acss-kit-builder

A Claude Code plugin that generates fpkit-style React components directly into your project. No `@fpkit/acss` npm package required -- only React and sass.

## Why

Installing `@fpkit/acss` from npm creates coupling: updates require package bumps, customization means forking or overriding, and the full bundle ships even if you only use a few components. This plugin takes a different approach -- it uses fpkit component source as **reference material** and generates **self-contained implementations** that you own and can freely modify.

Generated components follow the same patterns as `@fpkit/acss`:

- Polymorphic `UI` base component (renders as any HTML element via the `as` prop)
- CSS custom properties with hardcoded fallbacks for zero-config theming
- `data-*` attribute selectors for variants (not BEM modifiers)
- `aria-disabled` pattern for WCAG 2.1.1 compliance on interactive elements
- TypeScript + SCSS with all sizes in rem units

## Prerequisites

- React + TypeScript project
- `sass` or `sass-embedded` in devDependencies

```bash
npm install -D sass
```

## Installation

### Marketplace install (recommended)

```shell
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-kit-builder@shawn-sandy-acss-plugins
```

### Manual install via GitHub clone

```bash
git clone https://github.com/shawn-sandy/acss-plugins.git
mkdir -p ~/.claude/plugins/
cp -r acss-plugins/acss-kit-builder ~/.claude/plugins/
```

For project-level install, substitute `~/.claude/plugins/` with `.claude/plugins/` inside your project.

## Commands

### `/kit-add <component> [component2 ...]`

Generate one or more components into your project.

```
/kit-add badge
/kit-add button
/kit-add dialog
/kit-add button card alert
```

**What happens:**

1. **Init check** -- Verifies sass is in devDependencies and copies `ui.tsx` (the foundation component) to your target directory if not already present
2. **Target directory** -- Asks where to generate files on first run (default: `src/components/fpkit/`)
3. **Dependency resolution** -- Reads the component's Generation Contract, walks its dependency tree recursively
4. **Preview** -- Shows the full file tree that will be created and waits for confirmation
5. **Bottom-up generation** -- Generates leaf dependencies first (e.g., `icon.tsx` before `icon-button.tsx` before `dialog.tsx`)
6. **Skip existing** -- Files that already exist are skipped and imported from instead of overwritten
7. **Summary** -- Displays created/skipped files and an import/usage snippet

### `/kit-list [component]`

List available components or inspect a specific one.

```
/kit-list              # Show all available components by category
/kit-list badge        # Show Badge's props, CSS variables, dependencies, and usage
/kit-list dialog       # Show Dialog's full dependency tree
```

## Available Components

| Category | Components | Dependencies |
|----------|-----------|--------------|
| **Simple** | badge, tag, heading, text, link, icon | None (leaf components) |
| **Interactive** | button | None (uses inlined `useDisabledState`) |
| **Layout** | card, nav | None (compound components) |
| **Complex** | alert, dialog, form (input, textarea, select, checkbox, toggle) | Varies (e.g., dialog needs button + icon-button + icon) |

Run `/kit-list` for the full categorized listing with descriptions.

## Generated Code

### File structure

Each component generates a `.tsx` and `.scss` file pair:

```
src/components/fpkit/         # Default target directory
  ui.tsx                      # Foundation component (copied once)
  badge/
    badge.tsx                 # Component + inlined types
    badge.scss                # Styles with CSS variable fallbacks
  button/
    button.tsx
    button.scss
  dialog/
    dialog.tsx
    dialog.scss
```

### TypeScript (.tsx)

- All types are **inlined** in the component file (never imported from other generated components)
- Imports use **local paths only** -- never `@fpkit/acss`
- The `UI` base component is always imported from `../ui`
- Interactive components inline a condensed `useDisabledState` hook (~50 lines) for WCAG-compliant disabled handling

```tsx
import UI from '../ui'
import React from 'react'

export type ButtonProps = {
  children?: React.ReactNode
  disabled?: boolean
  // ...all standard button attributes
} & React.ComponentPropsWithoutRef<'button'>

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, disabled, ...props }, ref) => {
    // Uses aria-disabled instead of native disabled
    // to maintain keyboard tab order (WCAG 2.1.1)
    const { disabledProps, handlers } = useDisabledState(disabled, props)

    return (
      <UI as="button" ref={ref} {...disabledProps} {...handlers} {...props}>
        {children}
      </UI>
    )
  }
)
```

### SCSS (.scss)

- All values in **rem units** (never px; conversion: px / 16 = rem)
- Every CSS variable includes a **hardcoded fallback** so components work without global tokens
- Variants use `data-*` attribute selectors
- Disabled state uses `[aria-disabled="true"]`

```scss
.btn {
  font-size: var(--btn-fs, 0.9375rem);
  padding-block: var(--btn-padding-block, calc(var(--btn-fs, 0.9375rem) * 0.5));
  padding-inline: var(--btn-padding-inline, calc(var(--btn-fs, 0.9375rem) * 1.5));
  border-radius: var(--btn-radius, 0.375rem);
  background: var(--btn-bg, transparent);
  color: var(--btn-color, currentColor);

  &[data-color="primary"] {
    background: var(--btn-primary-bg, var(--color-primary, #0066cc));
    color: var(--btn-primary-color, var(--color-text-inverse, #fff));
  }

  &[aria-disabled="true"],
  &.is-disabled {
    opacity: var(--btn-disabled-opacity, 0.6);
    cursor: not-allowed;
    pointer-events: none;
  }

  &:focus-visible {
    outline: var(--btn-focus-outline, 2px solid currentColor);
    outline-offset: var(--btn-focus-outline-offset, 2px);
  }
}
```

## Customization

Generated components are fully customizable through CSS variables. Override at any scope:

```css
/* Global overrides */
:root {
  --btn-primary-bg: #7c3aed;
  --btn-radius: 2rem;
}

/* Scoped overrides */
.dark-theme {
  --card-bg: #2d2d2d;
  --card-border: 1px solid #404040;
}

/* Context-specific */
.pricing-section {
  --btn-padding-inline: 2.5rem;
  --btn-fw: 700;
}
```

CSS variable naming follows the pattern: `--{component}-{element?}-{variant?}-{property}`. See [references/css-variables.md](skills/acss-kit-builder/references/css-variables.md) for the full naming convention and approved abbreviations.

## The UI Foundation Component

`ui.tsx` is the only file copied verbatim from fpkit. It is a **polymorphic React component** (~333 lines, zero dependencies beyond React) that:

- Renders as any HTML element via the `as` prop (`<UI as="button">`, `<UI as="nav">`)
- Forwards all props (including ARIA attributes) to the rendered element
- Provides type-safe refs matching the rendered element type
- Supports `classes` (alias for className) and `styles`/`defaultStyles` for style merging

All generated components build on top of `UI`. It is copied to your target directory on first `/kit-add` run and should not be deleted.

## Plugin Structure

```
.claude/plugins/acss-kit-builder/
  .claude-plugin/
    plugin.json                          # Plugin metadata (name, version, author)
  assets/
    foundation/
      ui.tsx                             # UI base component (copied to developer projects)
  commands/
    kit-add.md                           # /kit-add command definition
    kit-list.md                          # /kit-list command definition
  skills/
    acss-kit-builder/
      SKILL.md                           # Full generation workflow for Claude
      references/
        architecture.md                  # UI component internals, polymorphic pattern
        accessibility.md                 # WCAG patterns, aria-disabled, useDisabledState
        composition.md                   # Compound component patterns, decision tree
        css-variables.md                 # Naming conventions, fallback strategy
        components/
          alert.md                       # Alert reference + Generation Contract
          button.md                      # Button reference + Generation Contract
          card.md                        # Card reference + Generation Contract
          catalog.md                     # Badge, Tag, Heading, Text, Link, Icon
          dialog.md                      # Dialog reference + Generation Contract
          form.md                        # Form controls reference + Generation Contract
          nav.md                         # Nav reference + Generation Contract
```

## How It Differs from fpkit-developer

| | fpkit-developer | acss-kit-builder |
|---|---|---|
| **Requires `@fpkit/acss`** | Yes | No |
| **Generated imports** | `import { Button } from '@fpkit/acss'` | `import Button from '../button/button'` |
| **Code ownership** | Library owns the code | Developer owns the code |
| **Customization** | CSS variable overrides only | Full source modification |
| **Bundle size** | Entire package ships | Only generated components ship |
| **Updates** | npm version bumps | Re-run `/kit-add` or edit directly |

## License

MIT
