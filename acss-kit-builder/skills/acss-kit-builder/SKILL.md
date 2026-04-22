# SKILL: acss-kit-builder

Generate fpkit-style React components directly into a developer's project. No `@fpkit/acss` npm package required. Only React + sass needed.

## Purpose

This skill generates self-contained, production-quality React components inspired by fpkit patterns. The developer owns the generated code and can freely modify it. Components use local imports — never `@fpkit/acss`.

## Prerequisites

- React + TypeScript project
- `sass` or `sass-embedded` in `devDependencies`

---

## Step A — First-Run Initialization

Run this check at the start of every `/kit-add` invocation.

### A1. Detect project type

Read `tsconfig.json` and `package.json` to confirm React + TypeScript is present.

### A2. Check sass

Read `package.json`. Look for `sass` or `sass-embedded` in `devDependencies`.

If neither is found, output:

```
sass or sass-embedded not found in devDependencies.
Run: npm install -D sass
Then re-run: /kit-add <component>
```

Stop. Do not generate any files.

### A3. Determine target directory

Target-directory resolution is **shared with the `acss-app-builder` plugin** via a `.acss-target.json` file at the project root (committed to git).

1. If `.acss-target.json` exists at the project root, read `componentsDir` from it and use that as the target. Skip the prompt.
2. Otherwise, ask:

   ```
   Where should components be generated? (default: src/components/fpkit/)
   ```

3. After the developer answers (or accepts the default), write `.acss-target.json` at the project root:

   ```json
   { "componentsDir": "src/components/fpkit" }
   ```

   Commit this file — both `/kit-add` and every `acss-app-builder` command (`/app-page`, `/app-layout`, etc.) read it as the source of truth. Without it, page templates and generated components would disagree on import paths.

Remember the answer for the current session as well, so subsequent `/kit-add` calls don't re-read the file unnecessarily.

### A4. Copy UI foundation

Check if `ui.tsx` exists in the target directory.

If not found:
- Copy `assets/foundation/ui.tsx` into `<target>/ui.tsx`
- Inform the developer: `Created ui.tsx (foundation component — do not delete)`

---

## Step B — Component Generation Workflow

### B1. Lookup the component

Read the component's reference doc:
- Detailed refs: `references/components/{name}.md`
- Simple components: `references/components/catalog.md`

If the component is not in either, inform the developer. Run `/kit-list` to show available components.

### B2. Read the Generation Contract

Every reference doc has a **Generation Contract** section:

```
## Generation Contract
export_name: ComponentName
file: component-name.tsx
scss: component-name.scss
imports: UI from '../ui'
dependencies: [dep1, dep2]
```

This tells Claude exactly what files to create and what dependencies to resolve.

### B3. Resolve the dependency tree

Walk dependencies recursively using each dependency's own Generation Contract. Build the full list of files that will be created.

Example for Dialog:
```
dialog.tsx + dialog.scss
  → button.tsx + button.scss
  → icon-button.tsx + icon-button.scss
    → icon.tsx (no scss)
```

### B4. Show the dependency tree

Before generating any files, display:

```
Generating the following files in src/components/fpkit/:

  New:
    ui.tsx              (foundation — React only)
    icon.tsx
    button.tsx + button.scss
    icon-button.tsx + icon-button.scss
    dialog.tsx + dialog.scss

  Skipped (already exist):
    (none)

Proceed? [Enter to continue, Ctrl+C to cancel]
```

Wait for confirmation before proceeding.

### B5. Generate files bottom-up

Generate leaf dependencies first, then composite components.

Order example:
1. `icon.tsx` (no deps)
2. `button.tsx` + `button.scss`
3. `icon-button.tsx` + `icon-button.scss`
4. `dialog.tsx` + `dialog.scss`

For each file:
- **If it already exists:** Skip generation. Note it in the summary. Wire import from existing file.
- **If it does not exist:** Generate it following the patterns in Step C.

---

## Step C — Generated Code Characteristics

### C1. TypeScript file (`.tsx`)

**Imports:**
```tsx
// Always import UI from local path
import UI from '../ui'
import React from 'react'
// Other local deps
import Button from '../button/button'
```

**Types:**
```tsx
// Inline all types in the component file
// Never import types from other generated components
export type ButtonProps = {
  children?: React.ReactNode
  disabled?: boolean
  // ...
} & React.ComponentPropsWithoutRef<'button'>
```

**No external imports** other than React and local project files.

**Condensed utilities:**
- `useDisabledState` — Inline the condensed ~50-line version from `references/accessibility.md`
- `resolveDisabledState` — Inline as a one-liner: `const resolveDisabledState = (d?: boolean, id?: boolean) => d ?? id ?? false`

### C2. SCSS file (`.scss`)

**Always use CSS custom properties with hardcoded fallbacks:**
```scss
.btn {
  font-size: var(--btn-fs, 0.9375rem);
  padding-block: var(--btn-padding-block, calc(var(--btn-fs, 0.9375rem) * 0.5));
  padding-inline: var(--btn-padding-inline, calc(var(--btn-fs, 0.9375rem) * 1.5));
  border-radius: var(--btn-radius, 0.375rem);
  background: var(--btn-bg, transparent);
  color: var(--btn-color, var(--color-text, currentColor));
  // Global token references MUST have fallbacks:
  background: var(--btn-primary-bg, var(--color-primary, #0066cc));
}
```

**Rules:**
- All values in **rem units** (never px). Conversion: px ÷ 16 = rem.
- CSS variable naming: `--{component}-{element?}-{variant?}-{property}`
- Global token refs (like `--color-primary`) always get hardcoded fallbacks
- See `references/css-variables.md` for full naming conventions

---

## Step D — Accessibility Patterns

### D1. aria-disabled pattern (interactive components)

**Always use `aria-disabled` instead of the native `disabled` attribute for buttons and interactive elements.**

Why: Native `disabled` removes the element from keyboard tab order (violates WCAG 2.1.1). `aria-disabled` keeps it focusable so screen readers can discover and announce the disabled state.

**Condensed useDisabledState** (inline in button.tsx and any interactive component):

```tsx
// Condensed useDisabledState — WCAG 2.1.1 compliant disabled pattern
// Uses aria-disabled instead of native disabled to maintain keyboard access
function useDisabledState(
  disabled: boolean | undefined,
  handlers: { onClick?: React.MouseEventHandler<HTMLButtonElement>; onKeyDown?: React.KeyboardEventHandler<HTMLButtonElement> } = {}
) {
  const isDisabled = Boolean(disabled)

  const disabledProps = {
    'aria-disabled': isDisabled,
    className: isDisabled ? 'is-disabled' : '',
  }

  const wrappedHandlers = {
    onClick: handlers.onClick
      ? (e: React.MouseEvent<HTMLButtonElement>) => {
          if (isDisabled) { e.preventDefault(); e.stopPropagation(); return }
          handlers.onClick!(e)
        }
      : undefined,
    onKeyDown: handlers.onKeyDown
      ? (e: React.KeyboardEvent<HTMLButtonElement>) => {
          if (isDisabled) { e.preventDefault(); e.stopPropagation(); return }
          handlers.onKeyDown!(e)
        }
      : undefined,
  }

  return { disabledProps, handlers: wrappedHandlers }
}
```

**SCSS disabled styling:**
```scss
.btn {
  &[aria-disabled="true"],
  &.is-disabled {
    opacity: var(--btn-disabled-opacity, 0.6);
    cursor: var(--btn-disabled-cursor, not-allowed);
    pointer-events: none;
  }
}
```

### D2. Focus management

Always include visible focus indicators:
```scss
.btn:focus-visible {
  outline: var(--btn-focus-outline, 2px solid currentColor);
  outline-offset: var(--btn-focus-outline-offset, 2px);
}
```

### D3. Semantic HTML

Prefer semantic elements over roles:
- `<button>` not `<div role="button">`
- `<nav>` not `<div role="navigation">`
- `<dialog>` not `<div role="dialog">`

---

## Step E — Style Generation

### E1. SCSS structure template

```scss
// {Component} component
// CSS variables with fallback defaults — override in :root or scoped selectors

.{component} {
  // Layout
  display: var(--{component}-display, block);

  // Spacing
  padding-block: var(--{component}-padding-block, 1rem);
  padding-inline: var(--{component}-padding-inline, 1rem);

  // Typography
  font-size: var(--{component}-fs, 1rem);
  font-weight: var(--{component}-fw, 400);

  // Visual
  background: var(--{component}-bg, transparent);
  color: var(--{component}-color, currentColor);
  border: var(--{component}-border, none);
  border-radius: var(--{component}-radius, 0);
}
```

### E2. Data attribute selectors

fpkit uses `data-*` attributes for variants (not BEM modifiers):

```scss
// Size variants via data-btn attribute
.btn[data-btn~="sm"] { font-size: var(--btn-size-sm, 0.8125rem); }
.btn[data-btn~="lg"] { font-size: var(--btn-size-lg, 1.125rem); }
.btn[data-btn~="block"] { width: 100%; }

// Style variants via data-style attribute
.btn[data-style="outline"] {
  background: var(--btn-outline-bg, transparent);
  border: var(--btn-outline-border, 1px solid currentColor);
}

// Color variants via data-color attribute
.btn[data-color="primary"] {
  background: var(--btn-primary-bg, var(--color-primary, #0066cc));
  color: var(--btn-primary-color, var(--color-text-inverse, #fff));
}
```

The `[data-btn~="value"]` selector matches space-separated words — `data-btn="sm block"` matches both `[data-btn~="sm"]` and `[data-btn~="block"]`.

---

## Step F — Post-Generation Summary

After all files are generated, show:

```
Generated components in src/components/fpkit/:

  Created:
    button/button.tsx
    button/button.scss

  Skipped (already existed):
    (none)

Import and usage:

  import Button from './components/fpkit/button/button'
  import './components/fpkit/button/button.scss'

  <Button type="button" onClick={handleClick}>Click me</Button>
  <Button type="button" disabled>Disabled (stays focusable)</Button>
  <Button type="button" data-color="primary" data-btn="lg">Primary Large</Button>
```

---

## Reference Documents

Read these before generating components:

| Document | Purpose |
|----------|---------|
| `references/architecture.md` | UI base component, polymorphic pattern, `as` prop |
| `references/css-variables.md` | CSS variable naming conventions, fallback strategy |
| `references/accessibility.md` | WCAG patterns, aria-disabled, condensed useDisabledState |
| `references/composition.md` | Compound components, generation decision tree |
| `references/components/button.md` | Button props, variants, data attributes |
| `references/components/dialog.md` | Dialog with native `<dialog>`, dependency tree |
| `references/components/alert.md` | Alert with severity levels, auto-dismiss |
| `references/components/card.md` | Card compound component (Title, Content, Footer) |
| `references/components/form.md` | Form controls: input, textarea, select, checkbox |
| `references/components/nav.md` | Nav compound component (List, Item) |
| `references/components/catalog.md` | Badge, Tag, Heading, Text, Link, Icon, and others |

---

## Key Rules Summary

1. **No `@fpkit/acss` imports** — all imports are local
2. **Types inline** — never import types from another generated file
3. **rem units only** — all sizes and spacing in rem
4. **CSS var fallbacks** — every `var(--token)` has a hardcoded fallback
5. **aria-disabled** — never native `disabled` for interactive components
6. **Skip existing** — if a file exists, import from it, don't overwrite
7. **Bottom-up order** — generate leaf dependencies before composites
8. **Condensed utilities** — inline useDisabledState as ~50 lines, not 247
