# acss-kit — Recipes

Common tasks, step by step. Each recipe assumes the plugin is installed and you are inside a Claude Code session in your project directory.

---

## First run: initializing a project

The first `/kit-add` run in any project triggers a one-time setup sequence.

**Prerequisites:**

- React + TypeScript project with a `package.json`
- `sass` or `sass-embedded` in `devDependencies`

If sass is not installed:

```bash
npm install -D sass
```

**Run:**

```
/kit-add badge
```

The plugin will:

1. Verify sass is present. If not, it aborts here with a message.
2. Ask "Where should components be generated? (default: `src/components/fpkit/`)" — press Enter to accept the default or type a custom path.
3. Write `.acss-target.json` at the project root with the chosen directory.
4. Copy `ui.tsx` (the polymorphic foundation component) to `<target>/ui.tsx`.
5. Generate the Badge component.

Commit `.acss-target.json` to git so subsequent `/kit-add` runs use the same path.

---

## Generate a single leaf component

```
/kit-add badge
```

Badge has no dependencies. The plugin reads `catalog.md`, shows a preview (`badge/badge.tsx + badge/badge.scss`), waits for confirmation, then writes both files.

Import in your project:

```tsx
import Badge from './components/fpkit/badge/badge'
```

---

## Generate a component with dependencies

```
/kit-add dialog
```

Dialog depends on Button. The plugin resolves the full tree and generates bottom-up:

```
Preview:
  ui.tsx                  (already exists — skipped)
  button/button.tsx       (new)
  button/button.scss      (new)
  dialog/dialog.tsx       (new)
  dialog/dialog.scss      (new)
```

Confirm, and all files are written in the correct order. If `button/button.tsx` already exists, it is skipped and Dialog still imports from the existing path.

---

## Regenerate a component after upstream changes

To update a component to the latest reference without losing your edits to other components:

1. Delete only the files you want to regenerate:
   ```bash
   rm src/components/fpkit/badge/badge.tsx src/components/fpkit/badge/badge.scss
   ```
2. Re-run:
   ```
   /kit-add badge
   ```

Files that still exist are skipped. Deleted files are regenerated from the current reference.

---

## Generate multiple components in one pass

```
/kit-add badge button alert
```

Dependencies are resolved across all requested components. Shared deps (Button for Alert, etc.) are deduplicated — Button is generated once even if multiple requested components need it.

---

## Customize a generated component

Generated files are yours. Edit them freely:

```tsx
// button/button.tsx — add a custom isLoading prop
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, isLoading, ...props }, ref) => {
    ...
    return (
      <UI as="button" data-btn={isLoading ? 'loading' : undefined} ...>
        {isLoading ? <Spinner /> : children}
      </UI>
    )
  }
)
```

The skip-existing rule means re-running `/kit-add button` will not overwrite your edits. To get a fresh copy, delete the file first (see "Regenerate" above).

---

## Override a CSS variable

Components use CSS custom properties with hardcoded fallbacks. Override at any scope without touching the generated file:

```css
/* Global — applies everywhere */
:root {
  --btn-primary-bg: #7c3aed;
  --btn-radius: 2rem;
}

/* Scoped to a theme class */
.dark-theme {
  --card-bg: #2d2d2d;
  --card-border: 1px solid #404040;
}

/* Context-specific */
.hero-section .btn {
  --btn-padding-inline: 2.5rem;
}
```

See [`references/css-variables.md`](../skills/components/references/css-variables.md) for the full naming convention and the per-component variable sets.

---

## Change the target directory

Edit `.acss-target.json` at the project root:

```json
{
  "componentsDir": "src/ui/fpkit"
}
```

All future `/kit-add` runs will generate files into the new directory. Existing generated files in the old directory are not moved — do that manually if needed, and update your imports.

---

## Inspect a component before generating

Use `/kit-list` to see props, CSS variables, dependencies, and a usage snippet without writing any files:

```
/kit-list dialog
```

Output includes the Generation Contract (dependency tree), the props interface, all CSS variables with their fallback values, and a basic JSX usage snippet. Useful for planning before running `/kit-add`.

---

## List all available components

```
/kit-list
```

Prints all components organized by category (Simple / Interactive / Layout / Complex) with a one-line description of each.

---

## Preview a generated component in a browser

An opt-in, static-HTML smoke check that exercises the *compiled CSS and `data-*` selectors* of a generated component — no React runtime required. Use it to eyeball variant coverage after generating a new component, not to test event handlers or dynamic behavior.

**Prerequisites:**

- `tests/sandbox/` exists — run `tests/setup.sh` if not ([Demo fixture](../../../tests/README.md#demo-fixture-testssetupsh))
- The target component has been generated via `/kit-add <name>` into the sandbox
- Python 3 on `PATH` (no extra deps — uses `python3 -m http.server`)

**Steps:**

1. From `tests/sandbox/`, compile the component's SCSS to a plain CSS string:

   ```sh
   npx sass --no-source-map src/components/fpkit/<name>/<name>.scss > /tmp/<name>.css
   ```

   This step is optional but useful if the preview renders nothing — you can inspect the compiled output directly to confirm selectors compiled as expected.

2. Write `tests/sandbox/<name>-preview.html` using the template below. Paste the compiled CSS into the `<style>` block and render one `<div class="row">` per variant axis the component supports (`data-color`, `data-style`, `data-<name>`, `aria-disabled`). Omit any axis the component does not use.

3. Start a local HTTP server from `tests/sandbox/`:

   ```sh
   python3 -m http.server 7743 &
   ```

   Background it so the shell stays usable. Stop it later with `kill %1` or by capturing the PID (`python3 -m http.server 7743 & echo $!`).

4. Open the preview — manually in any browser, or in a Claude Code session via the `claude-in-chrome` MCP (`navigate` then `computer screenshot`):

   ```
   http://localhost:7743/<name>-preview.html
   ```

5. Stop the server when done:

   ```sh
   kill %1
   ```

**HTML template:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><Name> Preview — acss-kit</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body {
      font-family: system-ui, sans-serif;
      background: #f8f9fa;
      color: #1a1a1a;
      padding: 2rem;
      margin: 0;
    }
    h1 { font-size: 1.25rem; margin-bottom: 2rem; color: #444; font-weight: 500; }
    h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #888; margin: 2rem 0 0.75rem; }
    .row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }

    /* paste compiled <name>.css output here */
  </style>
</head>
<body>
  <h1><Name> — acss-kit preview</h1>

  <h2>Default</h2>
  <div class="row">
    <!-- default (no variant attributes) -->
  </div>

  <h2>Colors</h2>
  <div class="row">
    <!-- data-color="primary", data-color="danger", etc. — omit if component has no color axis -->
  </div>

  <h2>Style variants</h2>
  <div class="row">
    <!-- data-style="outline", data-style="pill", etc. — omit if component has no style axis -->
  </div>

  <h2>Sizes</h2>
  <div class="row">
    <!-- data-<name>="xs", "sm", "lg", "xl" — omit if component has no size axis -->
  </div>

  <h2>Disabled (aria-disabled — stays focusable)</h2>
  <div class="row">
    <!-- aria-disabled="true" on default and one or two key variants -->
  </div>
</body>
</html>
```

This preview only covers what CSS can render. Behavior (focus management, keyboard activation, React state) is verified by `tests/e2e.sh`'s axe-core run, not here.

`*-preview.html` files are scratch artifacts; either delete them after use or add a `tests/sandbox/*-preview.html` entry to your gitignore (the sandbox itself is gitignored under `.claude/worktrees/`, so committed preview files only matter if you run `tests/setup.sh` outside a worktree).
