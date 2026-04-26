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
