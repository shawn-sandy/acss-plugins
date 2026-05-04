---
name: components-html
description: Use when generating static HTML snippets (plus optional vanilla-JS helpers) for fpkit-style components in non-React projects. Reads the same component reference docs as the React generator but emits .html + .scss + .js instead of .tsx.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  version: "0.1.0"
---

# SKILL: components-html

Generate static HTML versions of fpkit-style components for projects that don't use React — server-rendered apps, static sites, design-system docs, email templates, prototypes.

This skill is a sibling to the `components` skill (which generates TSX). Both read the same reference docs at `references/components/<name>.md`. The TSX generator copies the `## TSX Template` block; this generator copies `## HTML Template` and (for stateful components) `## Vanilla JS`. The `## SCSS Template` block is identical for both — the SCSS is framework-agnostic.

## Purpose

Emit:

- `<name>.html` — pure HTML markup. Same classes, same `data-*` attributes, same ARIA as the TSX output. The fragment is meant to be pasted into a page or template — no surrounding `<html>`/`<body>`.
- `<name>.scss` — byte-identical to what `/kit-add` generates. Compile via Sass or rename to `.css` and inline plain CSS.
- `<name>.js` — only for stateful components (Button, Dialog, Popover, Checkbox, Input, IconButton). Tiny ES module that wires behavior via the shared `_stateful.js` helper.

## Prerequisites

- A project root the user can write into. Any framework (or none) works.
- Sass is **optional** — if the user prefers plain CSS, they can rename `.scss` to `.css` and inline the variables that don't have a fallback. Most CSS variables in the templates already have hardcoded fallbacks, so vanilla CSS works for the majority of components.

---

## Step A — First-Run Initialization

Run this check at the start of every `/kit-add-html` invocation.

### A1. Determine target directory

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_html_target.py <project_root>` to read or initialize `.acss-html-target.json`.

1. If the script returns `"source": "configured"`, use the reported `componentsHtmlDir`. Skip the prompt.
2. If the script returns `"source": "none"`, ask:

   ```
   Where should HTML components be generated? (default: components/html)
   ```

3. After the developer answers (or accepts the default), write `.acss-html-target.json` at the project root:

   ```json
   { "componentsHtmlDir": "components/html" }
   ```

   Commit this file — `/kit-add-html` reads it on subsequent runs.

Remember the answer for the current session as well, so subsequent calls don't re-read the file unnecessarily.

### A2. Copy the foundation helper

Check if `_stateful.js` exists in `<componentsHtmlDir>`.

If not found:

- Copy `${CLAUDE_PLUGIN_ROOT}/assets/html-foundation/_stateful.js` into `<componentsHtmlDir>/_stateful.js`.
- Inform the developer: `Created _stateful.js (foundation helper — required by stateful components)`.

This file is the vanilla-JS counterpart to React's inlined `useDisabledState`. Stateful components import `wireDisabled` from `./_stateful.js`.

---

## Step B — Component Generation Workflow

### B1. Look up the component

Read the reference doc at `${CLAUDE_PLUGIN_ROOT}/skills/components/references/components/<name>.md` (the same path the TSX generator uses). The catalog at `references/components/catalog.md` lists every available component plus its HTML status.

If the component is not catalogued, inform the developer and run `/kit-list` (which lists all available components, regardless of output format).

### B2. Read the canonical sections

A reference doc that supports HTML output contains:

- **`## Generation Contract`** — `export_name`, `file`, `scss`, `dependencies`. Reuse this verbatim — the dependency tree is the same for HTML and TSX.
- **`## HTML Template`** — fenced ```html``` block. Copy verbatim into `<name>.html`.
- **`## SCSS Template`** — fenced ```scss``` block. Copy verbatim into `<name>.scss`. (Identical to the TSX generator.)
- **`## Vanilla JS`** — fenced ```js``` block. Only present on stateful components. Copy verbatim into `<name>.js`.
- **`## Accessibility`** — read it. Don't strip ARIA attributes or focus styles out of the templates during generation; they are load-bearing.

If a reference doc is missing `## HTML Template`, fall back gracefully: warn the developer, offer to author the markup from the TSX template by hand, but do not silently skip. The catalog `HTML Status` column tracks which components have been augmented.

### B3. Resolve the dependency tree

Walk dependencies recursively using each dependency's own Generation Contract. Build the full list of files that will be created. Identical to the TSX generator's algorithm — see `${CLAUDE_PLUGIN_ROOT}/skills/components/SKILL.md` Step B3.

Example for Dialog:

```
dialog.html + dialog.scss + dialog.js
  → button.html + button.scss + button.js
  → icon-button.html + icon-button.scss + icon-button.js
    → icon.html (no scss, no js)
```

### B4. Show the dependency tree

Before generating any files, display:

```
Generating the following files in components/html/:

  New:
    _stateful.js              (foundation helper — vanilla JS)
    icon.html
    button.html + button.scss + button.js
    icon-button.html + icon-button.scss + icon-button.js
    dialog.html + dialog.scss + dialog.js

  Skipped (already exist):
    (none)

Proceed? [Enter to continue, Ctrl+C to cancel]
```

Wait for confirmation before proceeding.

### B5. Generate files bottom-up

Generate leaf dependencies first, then composite components.

For each file:

- **If it already exists:** Skip generation. Note it in the summary.
- **If it does not exist:** Write it from the corresponding template section.

The HTML output is a **fragment**, not a full document. It begins with the component's root element and contains slot placeholders as plain text where the React version interpolates `{children}` — for example, `<!-- slot: children -->`. Users replace those comments with their content.

---

## Step C — Output Characteristics

### C1. HTML file (`.html`)

- Fragment — no `<html>` / `<head>` / `<body>` wrapper.
- Same class names as the TSX output (`btn`, `card`, `alert`, etc.) so the SCSS works unchanged.
- Same `data-*` attributes (`data-btn`, `data-style`, `data-color`, `data-card`, `data-severity`).
- Same ARIA attributes (`aria-disabled`, `aria-labelledby`, `role` only when needed).
- Slot placeholders use HTML comments: `<!-- slot: children -->`, `<!-- slot: title -->`.
- Multiple variants in a single file are separated by an HTML comment header: `<!-- variant: primary -->`.

### C2. SCSS file (`.scss`)

Byte-identical to the TSX generator's output. The framework-agnostic CSS is the foundation that lets both generators coexist.

Rules — same as the TSX skill:

- All values in **rem** (never px).
- CSS variable naming: `--{component}-{element?}-{variant?}-{property}`.
- Global token references always have a hardcoded fallback.
- `[aria-disabled="true"]` styles are present on every interactive component.

### C3. JS file (`.js`) — stateful components only

- Plain ES module — no bundler required.
- Imports `wireDisabled` from `./_stateful.js` when the component participates in the disabled-state pattern.
- Exports an `init` function that the user calls (e.g. `import { init } from './components/html/dialog.js'; init();`).
- Idempotent — `init()` may be called multiple times without double-binding listeners.

See `references/stateful-js-patterns.md` for the canonical patterns (disabled state, dialog open/close, popover wiring, input validation messages).

---

## Step D — Accessibility Patterns

The same patterns as the TSX generator — see `${CLAUDE_PLUGIN_ROOT}/skills/components/references/accessibility.md`. The HTML output preserves them:

- `aria-disabled="true"` (paired with the `is-disabled` class) — never the native `disabled` attribute, so disabled controls stay focusable (WCAG 2.1.1).
- `:focus-visible` outline preserved by the SCSS.
- Semantic HTML preferred over roles (`<button>` not `<div role="button">`, `<dialog>` not `<div role="dialog">`).
- Icon-only controls require `aria-label`.

---

## Step E — Post-Generation Summary

After all files are generated, show:

```
Generated HTML components in components/html/:

  Created:
    button.html
    button.scss
    button.js

  Skipped (already existed):
    _stateful.js

How to wire it up:

  1. <link rel="stylesheet" href="components/html/button.scss">
     (compile with Sass first, or rename .scss → .css if you don't use Sass)
  2. <script type="module" src="components/html/button.js"></script>
  3. Paste the markup from button.html into your page or template.
```

---

## Step F — Verify Integration

After Step E, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_html_integration.py <project_root>` to check whether the user's pages reference the generated artifacts.

- Exit 0 → every `.scss` / `.js` artifact is referenced by at least one page (`.html`, `.css`, `.scss`, `.tsx`, `.vue`, `.svelte`, etc.). No further action.
- Exit 1 → the script returns a `reasons` array. Print each reason as a numbered fix-up list with the suggested `<link>` / `<script>` snippet. **Do not** auto-edit the user's pages — the user must add the references themselves.

`*.html` snippets are listed but not checked — they're fragments meant to be copy-pasted, so absence of an automatic reference is expected.

---

## Reference Documents

| Document | Purpose |
|----------|---------|
| `references/stateful-js-patterns.md` | Vanilla-JS recipes (disabled state, dialog showModal, popover wiring, input validation) |
| `${CLAUDE_PLUGIN_ROOT}/skills/components/references/components/catalog.md` | Component catalog + HTML Status column |
| `${CLAUDE_PLUGIN_ROOT}/skills/components/references/accessibility.md` | WCAG patterns (shared with the TSX generator) |
| `${CLAUDE_PLUGIN_ROOT}/skills/components/references/css-variables.md` | CSS variable conventions (shared with the TSX generator) |

---

## Key Rules Summary

1. **Fragments only** — no `<html>`/`<body>` wrappers; the user owns the page shell.
2. **Same classes, same data attributes, same ARIA** as TSX — so SCSS is reused unchanged.
3. **Vanilla JS for stateful components** — no React, no bundler, no framework runtime.
4. **`_stateful.js` is the disabled-state helper** — copied once per project, imported by stateful components.
5. **Skip existing** — never overwrite a file that already exists; the user owns the generated code.
6. **Bottom-up dependency order** — leaf components first.
7. **No auto-edits to user pages** — Step F reports missing references but never patches them.

---

## Authoring HTML support for a new component (for contributors)

When a component reference doc gains HTML output:

1. Add a `## HTML Template` section after `## TSX Template`. Use a fenced ```html``` block. Mirror the TSX output exactly — same root element, same classes, same `data-*` attributes, same ARIA. Use HTML comments for slot placeholders (`<!-- slot: children -->`).
2. If the component is stateful, add a `## Vanilla JS` section with a fenced ```js``` block. Import `wireDisabled` from `./_stateful.js` when relevant. Export an idempotent `init()` function.
3. Update `references/components/catalog.md` — set `HTML Status` to `Verified` for that component, with any intentional divergences noted (e.g. "controlled state not represented; user must wire their own").
4. Run `tests/run.sh` to confirm the SCSS contract still passes.
