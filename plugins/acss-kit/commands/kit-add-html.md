---
description: Generate static HTML versions of fpkit-style components (markup + SCSS + optional vanilla JS) for non-React projects
argument-hint: <component> [component2 ...]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /kit-add-html

Generate **static HTML** versions of fpkit-style components for projects that don't use React — server-rendered apps, static sites, design-system docs, email templates, prototypes. The same component reference docs power both `/kit-add` (React TSX) and this command (HTML).

## Usage

```
/kit-add-html <component> [component2 ...]
```

**Examples:**

```
/kit-add-html button
/kit-add-html card alert
/kit-add-html dialog
/kit-add-html button card alert dialog
```

## Workflow

When this command is invoked, follow the **full generation workflow** documented in the `components-html` skill at `${CLAUDE_PLUGIN_ROOT}/skills/components-html/SKILL.md`.

### Quick Reference

1. **Init check** — Run `detect_html_target.py` to read or initialize `.acss-html-target.json` (default `componentsHtmlDir: components/html`); copy `_stateful.js` foundation helper if missing.
2. **Lookup** — Find the component in `${CLAUDE_PLUGIN_ROOT}/skills/components/references/components/<name>.md`.
3. **Read sections** — `## HTML Template`, `## SCSS Template`, and (for stateful components) `## Vanilla JS`.
4. **Dependency tree** — Walk the Generation Contract recursively (same algorithm as `/kit-add`).
5. **Show tree** — Display all `.html` / `.scss` / `.js` files that will be created.
6. **Generate bottom-up** — Leaf dependencies first.
7. **Skip existing** — Never overwrite. Note skipped files in the summary.
8. **Verify** — Run `verify_html_integration.py` and report any pages missing `<link>` / `<script>` references.

### First-Run Setup

If this is the first time running `/kit-add-html` in a project:

1. Ask the developer for the target directory (default: `components/html`).
2. Write `.acss-html-target.json` at the project root.
3. Copy `${CLAUDE_PLUGIN_ROOT}/assets/html-foundation/_stateful.js` into the target directory.

### Output

For each requested component:

- `<componentsHtmlDir>/<name>.html` — fragment markup. Paste into a page or template.
- `<componentsHtmlDir>/<name>.scss` — byte-identical to `/kit-add`'s SCSS. Compile with Sass or rename to `.css`.
- `<componentsHtmlDir>/<name>.js` — only for stateful components (Button, Dialog, Popover, Checkbox, Input, IconButton). Plain ES module.

See `SKILL.md` for the complete workflow including dependency resolution, conflict handling, accessibility patterns, and the integration verification step.
