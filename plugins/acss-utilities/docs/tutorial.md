# acss-utilities — Tutorial: your first utility class

Drop the bundle into a React project, import it, and use a couple of classes — including one that resolves through the token bridge to confirm dark mode is wired up. About five minutes.

If you want the mental model first, read [concepts.md](concepts.md). Otherwise, start here.

---

## Before you start

Prerequisites:

- A React project with a `package.json` that has `react` in `dependencies` or `devDependencies`
- `acss-utilities` installed via `/plugin install acss-utilities@shawn-sandy-agentic-acss-plugins`
- (Optional but recommended) `acss-kit` installed for OKLCH theme tokens

There is **no SCSS / sass requirement** — utilities are plain CSS. There is no JS runtime to install either.

---

## Step 1 — Drop the bundle into your project

Open Claude Code in your project directory and run:

```text
/utility-add
```

The plugin auto-detects your React root, resolves a drop directory (default `src/styles/`), and writes two files:

```text
src/styles/token-bridge.css     # acss-kit ↔ fpkit alias layer
src/styles/utilities.css        # the atomic suite (~58 KB unminified)
```

The summary it prints lists the files written, the total bundle size, and the families included. By default every family ships; pass `--families=color-bg,spacing,display` to copy a filtered subset.

---

## Step 2 — Import in the right order

Add these two lines to your app entry (`src/main.tsx`, `src/index.tsx`, or wherever you import global CSS). **Order matters** — the bridge defines aliases that the bundle consumes.

```ts
import "./styles/token-bridge.css";   // first — defines the aliases
import "./styles/utilities.css";       // then — utility classes consume them
```

If you reverse the order, color utilities still render — but they fall back to their hex defaults instead of resolving against your acss-kit theme.

---

## Step 3 — Use a class

Pick any component and apply a few utilities:

```tsx
export function Hero() {
  return (
    <section className="bg-surface p-6 rounded-lg">
      <h1 className="text-primary text-2xl font-bold">Welcome back</h1>
      <p className="text-muted">Sign in to continue.</p>
    </section>
  );
}
```

Run your dev server. You should see:

- Padding around the section (`p-6` → `padding: 1.5rem`)
- A rounded corner (`rounded-lg` → `border-radius: 0.5rem`)
- The heading colored by your active primary token

Every class in the bundle is documented in [`references/utility-catalogue.md`](../skills/utilities/references/utility-catalogue.md).

---

## Step 4 — Hide a class on small screens

Responsive prefixes use `sm:`, `md:`, `lg:`, `xl:`. In your JSX, the colon is **not** escaped:

```tsx
<aside className="hide md:show">…</aside>
```

This element is hidden by default and revealed at `≥ 48rem` (the `md` breakpoint). The CSS rule it matches looks like:

```css
@media (width >= 48rem) {
  .md\:show { display: revert !important; }
}
```

Note the `\:` in the CSS file — that's the escaped form. JSX/HTML always uses the unescaped `md:show`.

See [`references/breakpoints.md`](../skills/utilities/references/breakpoints.md) for the full breakpoint table.

---

## Step 5 — Confirm dark mode resolves

Toggle the theme on the document root:

```tsx
<html data-theme="dark">
```

Try a class that goes through the bridge:

```tsx
<div className="bg-error text-base p-4">Something went wrong.</div>
```

`.bg-error` reads `var(--color-error, transparent)`. The bridge defines `--color-error` differently for `:root` vs. `[data-theme="dark"]`, so the rendered background should visibly shift when you toggle the data attribute.

If it does not shift, check:

1. `token-bridge.css` is imported **before** `utilities.css`
2. `acss-kit` is loaded (or the bridge's hex fallbacks are reaching the element)
3. `data-theme="dark"` is on `<html>` or a parent of the styled element

[Troubleshooting](troubleshooting.md) covers each of these in detail.

---

## Where to next

- **Filter the bundle** — `/utility-add --families=color-bg,spacing,display` if you don't need flex, grid, type, etc.
- **Tune the spacing scale** — `/utility-tune use a 4px spacing baseline` ([recipes.md](recipes.md#switch-the-spacing-baseline-to-4px)).
- **Regenerate the bridge after a theme change** — `/utility-bridge` ([commands.md](commands.md#utility-bridge)).
- **List a family in detail** — `/utility-list spacing` to see every spacing class.
