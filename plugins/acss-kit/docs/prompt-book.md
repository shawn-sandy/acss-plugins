# Prompt Book

A catalogue of copy-paste prompts for using the `acss-kit` and `acss-utilities` plugins inside Claude Code.

Each entry has:

- **When to use** — the situation this prompt fits.
- **Prompt** — copy, paste, edit the bracketed parts, send.
- **What you get** — the expected outcome.

Prompts are written as natural language for Claude Code to interpret; most resolve to a shipped slash command. Either form works — type the command directly, or describe what you want.

> **Prerequisites.** Install the plugins first:
> ```text
> /plugin marketplace add shawn-sandy/agentic-acss-plugins
> /plugin install acss-kit@shawn-sandy-agentic-acss-plugins
> /plugin install acss-utilities@shawn-sandy-agentic-acss-plugins
> ```

---

## 1. Bootstrap a new project

**When to use:** First time using `acss-kit` in a React project — before generating any components or themes.

**Prompt:**

```text
Set up this React project for acss-kit. Install sass, copy the foundation
ui.tsx into src/ui/fpkit/, write .acss-target.json, and seed a starter
light/dark theme.
```

**What you get:** `sass` added to devDependencies, `src/ui/fpkit/ui.tsx` copied in, `.acss-target.json` recording the install location, and `src/styles/theme/{light,dark}.css` generated. Backed by `/setup`.

---

## 2. Generate a known component

**When to use:** You need a specific fpkit component (Button, Alert, Card, Dialog, Input, Field, Checkbox, Link, Img, Icon, IconButton, List, Table, Popover, Nav) dropped into your project.

**Prompt:**

```text
Add the [button] and [alert] components to my project using acss-kit.
```

**What you get:** TSX + SCSS files written under your kit target directory, with local imports of `ui.tsx` and the SCSS contract honoured. Backed by `/kit-add`.

---

## 2a. Generate static HTML versions of components (no React)

**When to use:** You want fpkit-style components in a project that doesn't use React — server-rendered apps, static sites, design-system docs, email templates, prototypes.

**Prompt:**

```text
Add static HTML versions of the [button] and [dialog] components using
acss-kit — no React, just markup + SCSS + a tiny vanilla-JS file for
behavior.
```

**What you get:** `<name>.html` (fragment markup with the same classes / `data-*` attributes / ARIA as the React version), `<name>.scss` (byte-identical to `/kit-add`'s SCSS — compile with Sass before linking), and `<name>.js` for components with runtime behavior (Button, Card-interactive, Alert, Dialog). On first run, prompts for the target directory (default `components/html`) and copies a `_stateful.js` foundation helper. Backed by `/kit-add-html`.

---

## 3. Generate a component from a description

**When to use:** You know what the UI should look like in plain English but don't want to wire it up by hand.

**Prompt:**

```text
Create a [primary pill button that says "Add to cart" with a cart icon
on the left]. Generate it as a paste-ready snippet I can drop into a page.
```

**What you get:** A snippet that composes the closest matching component reference (Button, in this case) with the right props, classes, and tokens. Backed by `/kit-create`.

---

## 4. Browse what's available

**When to use:** You want to see the full component catalogue or check the props/variants for one component before generating it.

**Prompt:**

```text
List every acss-kit component available, then show me the full reference
for [dialog].
```

**What you get:** A summary catalogue followed by the props, variants, and SCSS tokens for the named component. Backed by `/kit-list`.

---

## 5. Generate a theme from a brand color

**When to use:** You have a brand hex color and need WCAG-AA-checked light and dark themes.

**Prompt:**

```text
Generate light and dark theme CSS files seeded from [#4f46e5]. Validate
contrast and stop if anything fails.
```

**What you get:** `src/styles/theme/light.css` and `dark.css` written via the OKLCH palette algorithm, with all role contrasts validated. Backed by `/theme-create`.

---

## 6. Extract a theme from a design

**When to use:** You have a Figma file or a brand image and want to derive a theme from it instead of typing in a hex.

**Prompt:**

```text
Extract the brand colors from [https://www.figma.com/design/...] and
generate a matching light/dark theme.
```

or

```text
Extract the brand colors from [./design/hero.png] and generate a matching
theme.
```

**What you get:** A primary color (and optional accents) picked from the source, fed into the same palette pipeline as `/theme-create`. Backed by `/theme-extract`.

---

## 7. Layer a brand preset over an existing theme

**When to use:** Your app already has light/dark themes and you want a switchable secondary brand (say, a seasonal or sub-brand) without regenerating everything.

**Prompt:**

```text
Scaffold a brand preset called [forest] seeded from [#2f7a4d]. It should
layer over my existing light and dark themes.
```

**What you get:** `src/styles/theme/brand-forest.css` with `:root` and `[data-theme="dark"]` blocks overriding only the primary/accent roles. Backed by `/theme-brand`.

---

## 8. Update specific role values

**When to use:** A reviewer wants the primary slightly cooler, or the accent darker — you don't want to regenerate the entire theme.

**Prompt:**

```text
In [src/styles/theme/light.css], change --color-primary to [#2563eb] and
--color-accent to [#a855f7]. Re-validate contrast.
```

**What you get:** In-place edits to those role values, with `validate_theme.py` re-running and reverting any change that breaks AA contrast. Backed by `/theme-update`.

---

## 9. Tune the visual feel

**When to use:** You can describe the change in feel ("warmer", "softer", "more spacious") but not in token values.

**Prompt:**

```text
Make the [buttons] feel [softer and more rounded], and make the [primary]
role feel [warmer].
```

**What you get:** Component SCSS token edits and/or theme role edits, routed automatically. Backed by `/style-tune`.

---

## 10. Add Tailwind-style utilities

**When to use:** You want atomic classes (`bg-primary`, `p-4`, `flex`, `gap-2`) alongside `acss-kit` components.

**Prompt:**

```text
Drop the acss-utilities bundle into my project. Use the default target
and include only the [color-bg, color-text, spacing, display, flex]
families.
```

**What you get:** `utilities.css` (filtered to the requested families) and `token-bridge.css` written into `src/styles/`. Backed by `/utility-add`.

---

## 11. Bridge utilities to your acss-kit theme

**When to use:** You changed your theme (new brand, new roles) and the utility classes now reference stale tokens.

**Prompt:**

```text
Regenerate token-bridge.css against my current acss-kit theme so the
utility classes pick up the new role values. Make sure dark mode is
covered.
```

**What you get:** A fresh `token-bridge.css` with both `:root` and `[data-theme="dark"]` blocks, hex fallbacks embedded, derived `-bg` / `-light` variants via `color-mix`. Backed by `/utility-bridge`.

---

## 12. Tune utility tokens

**When to use:** You want to change the spacing baseline, add a breakpoint, or disable a family.

**Prompt:**

```text
Switch the spacing baseline to [4px], add an [xs breakpoint at 20rem],
and disable the [shadow] family.
```

**What you get:** `utilities.tokens.json` updated, the bundle regenerated, and the result validated. Backed by `/utility-tune`.

---

## 13. Inspect a utility family

**When to use:** You want to see every class a family ships before deciding to enable or disable it.

**Prompt:**

```text
List every class in the [spacing] family, including the CSS property and
custom property each one references.
```

**What you get:** A read-only catalogue printout — no files touched. Backed by `/utility-list`.

---

## 14. Bulk-install every component plus a starter theme

**When to use:** You want every shipped acss-kit component, the `ui.tsx` foundation, and an OKLCH-validated starter theme written into your project in one shot — instead of running `/kit-add` per component.

**Prompt:**

```text
Bulk-install every acss-kit component into my project, with a starter
theme seeded from [#4f46e5]. Track everything in .acss-kit/manifest.json
so I can re-sync safely later.
```

**What you get:** Every catalog component + `ui.tsx` + `light.css` / `dark.css` written via the same generators `/kit-add` and `/theme-create` use, plus `<projectRoot>/.acss-kit/manifest.json` recording the normalized sha256 of each file. Re-runs route every file through the drift check — modified files are skipped, clean files overwritten. Backed by `/kit-sync`. (The `Form` component lives behind the `component-form` skill and is not vendored by `/kit-sync` — use the form-skill prompt above to generate forms on demand.)

---

## 15. Safely re-copy unmodified components after a plugin upgrade

**When to use:** You upgraded `acss-kit` and want the new component / foundation versions, but only for files you haven't customised. Your edits should be preserved.

**Prompt:**

```text
Re-sync every acss-kit component I haven't touched since the last
/kit-sync run. Skip anything I've modified and show me a report of
what got updated, skipped, and recreated.
```

**What you get:** A diff report (clean / modified / missing per file), then in-place overwrites of clean and missing files. Modified files are skipped by default; pass `--force` to overwrite them after writing a `.bak` backup. Backed by `/kit-update`.

---

## Composing prompts

You can chain multiple goals in one message. Claude Code will invoke the matching commands in sequence.

```text
Set up this project for acss-kit, generate a theme from [#4f46e5],
add the [button, card, dialog] components, then drop the utility
bundle in with only the [color-bg, color-text, spacing, flex]
families.
```

---

## Tips

- **Edit the bracketed parts.** Square brackets mark replaceable values.
- **Prefer plain English when you don't know the command.** Claude Code routes to the right skill — you don't have to memorise every slash command.
- **Run `/setup` once per project.** Most other prompts assume the foundation `ui.tsx` is already in place.
- **Validate after theme edits.** Every theme command runs `validate_theme.py` for AA contrast — trust the failures.
- **Read the per-plugin README.** `plugins/acss-kit/README.md` and `plugins/acss-utilities/README.md` cover edge cases and arguments not shown here.
