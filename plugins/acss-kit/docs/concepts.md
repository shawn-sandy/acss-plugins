# acss-kit — Core Concepts

This page covers the mental model you need before running `/kit-add`. Understanding these ideas will help you reason about what gets generated, why the generated code looks the way it does, and what to do when something unexpected happens.

## Why generated code instead of an npm package

`@fpkit/acss` is a real npm package. This plugin deliberately does not install it. Instead, Claude reads fpkit component patterns from bundled reference documents and writes self-contained TypeScript + SCSS files directly into your project. You own the output — you can edit it freely, and there is nothing to update via npm. The trade-off is that updates require re-running `/kit-add` (which respects existing files; see [skip-existing](#bottom-up-generation-and-skip-existing) below).

## The UI foundation component

Every generated component imports a single shared file: `ui.tsx`. This is the only file the plugin copies verbatim from the fpkit source rather than generating from a reference doc. It is a **polymorphic React component** that:

- Renders as any HTML element via the `as` prop (`<UI as="button">`, `<UI as="nav">`)
- Forwards all props (including ARIA attributes) to the rendered element
- Provides type-safe refs that match the rendered element type
- Supports a `classes` alias for `className` — when both are provided, `classes` wins

`ui.tsx` is copied to your target directory on the first `/kit-add` run. All generated components import it with a local relative path (`import UI from '../ui'`). Never import it from an npm package.

See [`references/architecture.md`](../skills/components/references/architecture.md) for the full polymorphic type chain.

## data-\* attribute variants (not BEM)

Generated components use `data-*` attribute selectors for styling variants instead of BEM modifier classes. For example, a button's size and color:

```tsx
<Button data-btn="lg" data-color="primary">Submit</Button>
```

```scss
.btn {
  &[data-btn~="lg"] { font-size: var(--btn-lg-fs, 1.125rem); }
  &[data-color="primary"] { background: var(--btn-primary-bg, var(--color-primary, #0066cc)); }
}
```

The `~=` selector matches a space-separated word, which lets you compose multiple variants: `data-btn="lg block"` activates both `lg` and `block` rules simultaneously.

## CSS custom properties with mandatory fallbacks

Every CSS variable in generated SCSS **must** include a hardcoded fallback value. This makes components work in isolation without a global tokens file:

```scss
font-size: var(--btn-fs, 0.9375rem);           /* correct */
font-size: var(--btn-fs);                       /* wrong — breaks without a token file */
```

Variable naming follows the pattern `--{component}-{element?}-{variant?}-{property}`. For example: `--btn-primary-bg`, `--card-title-fs`, `--dialog-backdrop-bg`.

All sizes use **rem** (never px). Conversion: `px / 16 = rem`.

See [`references/css-variables.md`](../skills/components/references/css-variables.md) for the full naming convention, approved abbreviations, and logical-property rules.

## aria-disabled and useDisabledState

Interactive components (Button, any component with a clickable surface) use `aria-disabled="true"` instead of the native `disabled` attribute. The reason: native `disabled` removes an element from the keyboard tab order, which fails WCAG 2.1.1 (Non-text Contrast) and breaks the expected experience for keyboard and screen-reader users.

The plugin inlines a condensed `useDisabledState<T>` hook (~50 lines) directly into each interactive component file. It is never a shared import — each component that needs it carries its own copy. This keeps generated files self-contained.

See [`references/accessibility.md`](../skills/components/references/accessibility.md) for the full hook source, the `resolveDisabledState` one-liner, focus management guidelines, and the WCAG checklist per component category.

## Types inline, imports local-only

Generated `.tsx` files have two hard rules:

- **All TypeScript types are inlined** — no cross-component type imports. Each file defines its own `ButtonProps`, `CardProps`, and so on.
- **All imports use local relative paths** — never `@fpkit/acss`. The only imports in a generated file are `import React from 'react'` and `import UI from '../ui'` (plus sibling component imports for compounds like `import Button from '../button/button'`).

## The Generation Contract

Every component in the reference catalog has a **Generation Contract** block. It is the stable interface between the component reference docs and the generation workflow:

```
export_name:  Button
file:         button/button.tsx
scss:         button/button.scss
imports:      [../ui]
dependencies: []
```

Five fields. `dependencies` is the key one: it lists the component names that must exist before this component can be generated. The plugin resolves this recursively to build a full dependency tree before writing any files.

## Bottom-up generation and skip-existing

When you run `/kit-add dialog`, the plugin resolves that Dialog depends on Button (and Button has no dependencies). It then generates in **bottom-up order**: Button first, Dialog second. If `button/button.tsx` already exists, it is **skipped** — the existing file is used as-is and the Dialog import path resolves to it without modification.

This means you can safely re-run `/kit-add dialog` after editing `button/button.tsx`; your edits are preserved.

## .acss-target.json — project config

On the first `/kit-add` run in a project, the plugin writes a `.acss-target.json` file at the project root:

```json
{
  "componentsDir": "src/components/fpkit"
}
```

This file tells the SKILL where to write generated components. Commit it to git so subsequent `/kit-add` runs use the same path. If you need to change the target directory, edit the file directly or delete it and re-run `/kit-add` (you will be prompted again).
