---
name: components
description: Use when generating fpkit-style React components into a developer's project. Markdown-as-source templates with embedded TSX/SCSS and accessibility patterns. No @fpkit/acss package required — only React + sass.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  version: "0.3.0"
---

# SKILL: components

Generate fpkit-style React components directly into a developer's project. No `@fpkit/acss` npm package required. Only React + sass needed.

## Purpose

This skill generates self-contained, production-quality React components from markdown specs that embed the actual TSX/SCSS code as fenced code blocks alongside accessibility documentation. The developer owns the generated code and can freely modify it. Components use local imports — never `@fpkit/acss`.

## Prerequisites

- React + TypeScript project
- `sass` or `sass-embedded` in `devDependencies`

---

## Step 0 — Exit plan mode

If the session is in plan mode, call `ExitPlanMode` before doing anything else. Every subsequent step writes files (`ui.tsx`, component TSX/SCSS), edits `.acss-target.json`, or runs Python scripts via Bash — plan mode would block all of it.

Stay in plan mode only when it is absolutely necessary — i.e. the user explicitly asked for a dry-run / preview ("show me the plan first", "what would `/kit-add` do", "don't generate yet"). In that case, narrate the dependency tree and file list from Step B4 without invoking Write/Edit/Bash, and wait for approval before re-entering this skill.

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

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <project_root>` to read or initialize `.acss-target.json`.

1. If the script returns `"source": "generated"`, use the reported `componentsDir`. Skip the prompt.
2. If the script returns `"source": "none"`, ask:

   ```
   Where should components be generated? (default: src/components/fpkit/)
   ```

3. After the developer answers (or accepts the default), write `.acss-target.json` at the project root:

   ```json
   { "componentsDir": "src/components/fpkit" }
   ```

   Commit this file — `/kit-add` reads it on subsequent runs as the source of truth for import paths.

Remember the answer for the current session as well, so subsequent `/kit-add` calls don't re-read the file unnecessarily.

### A3.1. Detect the build stack

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_stack.py <project_root>` to classify framework, bundler, CSS pipeline, and entrypoint. Capture the JSON.

1. If `source: "detected"`, merge the result into `.acss-target.json` under a `stack` key (preserve existing `componentsDir`/`utilitiesDir`):

   ```json
   {
     "componentsDir": "src/components/fpkit",
     "stack": {
       "framework": "vite",
       "bundler": "vite",
       "cssPipeline": ["sass"],
       "tsconfig": true,
       "entrypointFile": "src/main.tsx",
       "detectedAt": "2026-05-01T00:00:00Z"
     }
   }
   ```

   Skip re-detection on later runs unless `package.json`'s mtime is newer than `stack.detectedAt`.

2. If `source: "unknown"`, surface the `reasons` array verbatim and ask the developer to confirm framework + entrypoint by hand. Record their answer under `stack` so subsequent runs skip the prompt.

3. If `source: "none"` (no React project root), halt — `/kit-add` cannot proceed.

Use `stack.cssPipeline` to tailor advice: when it contains `"tailwind"`, note that fpkit components and Tailwind utilities coexist but the user should not migrate component SCSS into `@apply`. When it omits `"sass"`, fall through to Step A2's install instruction.

### A4. Copy UI foundation

Check if `ui.tsx` exists in the target directory.

If not found:
- Copy `${CLAUDE_PLUGIN_ROOT}/assets/foundation/ui.tsx` into `<target>/ui.tsx`
- Inform the developer: `Created ui.tsx (foundation component — do not delete)`

---

## Step B — Component Generation Workflow

### B1. Lookup the component

Read the component's reference doc:
- Detailed refs: `references/components/{name}.md`
- Catalog: `references/components/catalog.md`

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

### B2.1. Read the canonical sections

Reference docs follow the canonical embedded-markdown shape with three required sections beyond the Generation Contract — read them all before writing any files:

- **`## TSX Template`** — fenced ```tsx``` block with the full component implementation. Copy this verbatim into the generated `.tsx` file. Substitute `{{IMPORT_SOURCE:...}}` / `{{NAME}}` / `{{FIELDS}}` placeholders at write time when present.
- **`## SCSS Template`** — fenced ```scss``` block with the canonical styles. Copy verbatim into the generated `.scss` file.
- **`## Accessibility`** — WCAG 2.2 AA criteria the component addresses (keyboard, ARIA, focus, contrast, target size). Don't strip a11y patterns out of the TSX/SCSS during generation; they're load-bearing.

If a reference doc is missing any of these three sections, fall back to the older "Key Pattern" / "Full Implementation Reference" / "SCSS Pattern" shape. The catalog.md "Verification Status" table records which components have been migrated to the canonical shape; treat any others as legacy and synthesize from the available pieces.

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

Why: Native `disabled` removes the element from keyboard tab order — keyboard and screen-reader users can't reach the control to discover it's disabled or access any explanation. `aria-disabled` keeps it focusable so screen readers can announce the disabled state.

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

## Step G — Verify Integration

After Step F, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <project_root>` to check that the user's entrypoint actually imports the artifacts that were just written.

- Exit 0 → everything is wired up. No further action.
- Exit 1 → the script returns a `reasons` array. Print each reason as a numbered fix-up list. Do **not** auto-edit the entrypoint — the developer must add imports themselves so they retain ownership of the wiring.

The verifier reads `stack.entrypointFile` from `.acss-target.json`, so Step A3.1 must have run successfully. If `stack.entrypointFile` is missing or stale, the verifier exits 1 with a reason pointing back to `detect_stack.py`.

---

## Reference Documents

Read these before generating components:

| Document | Purpose |
|----------|---------|
| `references/architecture.md` | UI base component, polymorphic pattern, `as` prop |
| `references/css-variables.md` | CSS variable naming conventions, fallback strategy |
| `references/accessibility.md` | WCAG patterns, aria-disabled, condensed useDisabledState |
| `references/composition.md` | Compound components, generation decision tree |
| `references/components/catalog.md` | Verification status table + remaining inline components (Badge, Tag, Heading, Text, Details, Progress) |
| `references/components/button.md` | Button — canonical shape ✓ |
| `references/components/icon-button.md` | IconButton (wraps Button + XOR aria-label/aria-labelledby) — canonical shape ✓ |
| `references/components/alert.md` | Alert with severity levels, auto-dismiss — canonical shape ✓ |
| `references/components/card.md` | Card compound component (Title, Content, Footer) — canonical shape ✓ |
| `references/components/dialog.md` | Dialog with native `<dialog>` — canonical shape ✓ |
| `references/components/popover.md` | Popover via native HTML Popover API — canonical shape ✓ |
| `references/components/table.md` | Table compound (Caption, Head, Body, Row, HeaderCell, Cell) — canonical shape ✓ |
| `references/components/img.md` | Img with lazy loading + SVG-gradient placeholder — canonical shape ✓ |
| `references/components/icon.md` | Icon with built-in 9-icon SVG dispatch — canonical shape ✓ |
| `references/components/link.md` | Link with auto security defaults — canonical shape ✓ |
| `references/components/list.md` | List + List.ListItem (ul/ol/dl) — canonical shape ✓ |
| `references/components/field.md` | Field (label + control wrapper) — canonical shape ✓ |
| `references/components/input.md` | Input with validation states — canonical shape ✓ |
| `references/components/checkbox.md` | Checkbox (wraps Input) — canonical shape ✓ |
| `references/components/form.md` | Form composition (legacy bundled reference; superseded by `component-form` skill) |
| `references/components/nav.md` | Nav compound component (List, Item) — legacy shape |

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

---

## Authoring New Components (for contributors)

When adding or updating a component reference doc, follow the canonical embedded-markdown shape.

### Required sections

Every component reference doc must contain (in order):

1. **Verification banner** — top of file, blockquote starting with `**Verified against fpkit source:**`. Records the upstream ref (e.g. `@fpkit/acss@6.5.0`) and any intentional divergences from upstream (inlined hooks, simplified compound APIs, dropped subcomponents). Future maintainers read this to understand *why* the vendored version diverges.
2. **`## Overview`** — one-paragraph summary of the component's purpose.
3. **`## Generation Contract`** — `export_name`, `file`, `scss`, `imports`, `dependencies`. The `/kit-add` workflow reads these fields verbatim.
4. **`## Props Interface`** — TypeScript interface or type alias the component accepts.
5. **`## TSX Template`** — fenced ```tsx``` block containing the full component code. Self-contained: imports only `UI from '../ui'`, React, and other vendored components via relative paths. Never `@fpkit/acss`.
6. **`## CSS Variables`** — fenced ```scss``` block listing the component's CSS custom properties with default values.
7. **`## SCSS Template`** — fenced ```scss``` block containing the actual SCSS rules.
8. **`## Accessibility`** — required. Document keyboard interaction, ARIA, focus management, target size, color contrast, and the WCAG 2.2 AA criteria addressed. The Accessibility section is load-bearing — don't strip a11y patterns out of the TSX/SCSS during generation.
9. **`## Usage Examples`** — fenced ```tsx``` block showing common usage patterns.

### Reference vs Skill (hybrid packaging)

Most components live as reference docs at `references/components/<name>.md`. Composable, complex, or high-iteration components can be promoted to their own skill at `skills/component-<name>/SKILL.md` with discovery-friendly trigger phrases in the frontmatter `description`.

The `component-form` skill is the only per-component skill in 0.3.0. It serves as a pilot — adopt the per-component skill pattern for additional components only after observing the Form skill's trigger reliability in real-world usage.

### Verification log

Every new or migrated component gets an entry in `references/components/catalog.md` under "Verification Status":

```
| Component | Reference | Verified against | Status |
|-----------|-----------|------------------|--------|
| Foo | [`foo.md`](foo.md) | `@fpkit/acss@<version>` | New / Verified — <intentional divergences if any> |
```

This table is the single source of truth for which components have been migrated to the canonical shape.

### fpkit verification workflow

Before authoring or backfilling a reference doc:

1. Resolve the captured `@fpkit/acss` ceiling version to the matching git tag/SHA in the `shawn-sandy/acss` repo. If no matching tag exists for that npm version, use the closest tag and document the gap in the verification banner.
2. Fetch the canonical fpkit source from `https://github.com/shawn-sandy/acss/blob/<tag-or-sha>/packages/fpkit/src/<component>/...` (full GitHub URL per repo policy — never `blob/main`).
3. Compare the upstream behavior to what the existing reference doc describes. Note any intentional divergence (inlined hooks, simplified compound APIs, dropped subcomponents) in the verification banner.
4. Author the canonical sections to match fpkit semantics with relative-path imports — never `@fpkit/acss`.
