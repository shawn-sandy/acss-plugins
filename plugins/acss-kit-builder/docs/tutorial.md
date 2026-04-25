# acss-kit-builder — Tutorial: your first component

Generate, import, and customize a Button in under five minutes. By the end you will have a working, themeable Button component you own outright — no `@fpkit/acss` npm dependency, no boilerplate.

If you want the mental model first, read [concepts.md](concepts.md). Otherwise, start here.

---

## Before you start

Prerequisites:

- React + TypeScript project with a `package.json`
- `sass` or `sass-embedded` in `devDependencies`
- `acss-kit-builder` installed via `/plugin install acss-kit-builder@shawn-sandy-acss-plugins`
- Clean git working tree (commands refuse a dirty tree unless you pass `--force`)

If sass is not installed:

```bash
npm install -D sass
```

This walkthrough uses **Button**. It is a single-file component with no fpkit dependencies, so the only first-run extra is the shared `ui.tsx` foundation — perfect for seeing the setup flow in one command.

---

## Step 1 — Browse the catalog

Open Claude Code in your project directory and run:

```
/kit-list
```

Output groups every available component into four categories:

- **Simple** — leaf components with no dependencies (Badge, Tag, Heading, Text, Link, Icon)
- **Interactive** — Button, Form controls, focus-managed elements
- **Layout** — Card, layout primitives
- **Complex** — Dialog, Nav and other components that depend on simpler ones

Why look first? You don't write what you can generate. The catalog tells you exactly what's available before you commit to writing anything yourself.

---

## Step 2 — Inspect Button before generating

```
/kit-list button
```

This prints Button's full Generation Contract without writing any files:

- **Dependencies:** none — Button only imports the `UI` foundation from `../ui`
- **Props:** `type` (required), `children`, `disabled`, `size`, `variant`, `color`, `block`, plus standard event handlers
- **CSS variables:** `--btn-bg`, `--btn-color`, `--btn-radius`, `--btn-padding-inline`, `--btn-primary-bg`, `--btn-primary-hover-bg`, size tokens (`--btn-size-xs` through `--btn-size-xl`), and state tokens (`--btn-focus-outline`, `--btn-disabled-opacity`)
- **Usage snippet** — a JSX example you can copy

Reading this first means no surprises in the next step.

---

## Step 3 — Generate the component

```
/kit-add button
```

The plugin will:

1. Verify sass is present. If not, it aborts here with a message.
2. Ask "Where should components be generated? (default: `src/components/fpkit/`)" — press Enter to accept the default or type a custom path.
3. Write `.acss-target.json` at the project root with the chosen directory.
4. Copy `ui.tsx` (the polymorphic foundation component) to `<target>/ui.tsx`.
5. Generate `button/button.tsx` and `button/button.scss`.

Commit `.acss-target.json` to git. It is shared with `acss-app-builder` — both plugins read from it.

After the run, your tree looks like:

```
src/components/fpkit/
  ui.tsx              # polymorphic foundation (one per project)
  button/
    button.tsx        # Button + inlined useDisabledState hook
    button.scss       # styles with hardcoded fallbacks for every CSS var
```

The SCSS uses hardcoded fallbacks (e.g. `var(--btn-bg, transparent)`) so the component renders correctly even before you set any custom variables. This is what makes the next step purely additive.

---

## Step 4 — Import and use it

In `src/App.tsx` (or any page file):

```tsx
import Button from './components/fpkit/button/button'
import './components/fpkit/button/button.scss'

export default function App() {
  return (
    <Button type="button" color="primary" onClick={() => alert('hi')}>
      Click me
    </Button>
  )
}
```

Two things to notice:

- **`type` is required.** Button rejects implicit submit semantics — you always declare intent (`button`, `submit`, or `reset`). If TypeScript flags a missing `type`, that's the safety net firing.
- **The SCSS import lives next to the TSX import.** Generated components don't bundle styles, so each component file expects its sibling SCSS to be imported once per app.

---

## Step 5 — Customize via CSS variables

Generated files are yours to edit, but you rarely need to — variants and theming are CSS-variable-first. Override at any scope:

```scss
/* Global — applies everywhere */
:root {
  --btn-primary-bg: #7c3aed;
  --btn-radius: 999px;
}

/* Scoped to a theme class */
.dark-theme {
  --btn-primary-bg: #4c1d95;
  --btn-primary-hover-bg: #6d28d9;
}

/* Context-specific */
.hero-section .btn {
  --btn-padding-inline: 2.5rem;
  --btn-fs: 1.125rem;
}
```

Why prefer overrides over editing `button.scss` directly? The skip-existing rule in `/kit-add` means re-running the command never touches your generated files — but if you ever delete and regenerate (see [recipes.md — Regenerate a component](recipes.md#regenerate-a-component-after-upstream-changes)), customizations stored in `:root` or theme classes survive because they live outside the component file.

The full naming convention and per-component variable sets are in [`references/css-variables.md`](../skills/acss-kit-builder/references/css-variables.md).

---

## Verify

```bash
npx tsc --noEmit
npm run dev
```

You should see:

- TypeScript exits `0`. Button's props are fully typed; the required `type` prop is enforced.
- The dev server renders a button styled by the CSS variables you set in Step 5 (or the built-in fallbacks if you skipped it).
- Clicking it fires the `onClick` handler.
- Tabbing onto the button shows a visible focus ring (`--btn-focus-outline` defaults to `2px solid currentColor`).
- `disabled` buttons stay in tab order and signal state via `aria-disabled` rather than the native `disabled` attribute (WCAG 2.1.1).

If the button renders unstyled, the `import './components/fpkit/button/button.scss'` line is missing.

---

## Where to next

You have generated, imported, and customized one component. From here:

- [recipes.md](recipes.md) — variations: multiple components in one pass, components with dependencies (Dialog pulls in Button), regenerate after an upstream change, change the target directory.
- [concepts.md](concepts.md) — the mental model: the `UI` polymorphic base, `data-*` attribute variants, why `aria-disabled` instead of the native attribute.
- [commands.md](commands.md) — full `/kit-list` and `/kit-add` reference.
- [Button reference](../skills/acss-kit-builder/references/components/button.md) — every prop, every CSS variable, and the full implementation source.
- [troubleshooting.md](troubleshooting.md) — when things don't work.

Ready to compose components into pages or generate themes? Install [`acss-app-builder`](../../acss-app-builder/README.md) — it reads the same `.acss-target.json` and uses your generated source automatically.
