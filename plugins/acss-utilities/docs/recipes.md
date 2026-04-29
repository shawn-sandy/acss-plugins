# acss-utilities — Recipes

Short, task-oriented walkthroughs for the most common workflows. Each recipe assumes you've already installed the plugin (`/plugin install acss-utilities@shawn-sandy-agentic-acss-plugins`).

---

## First-run install on a fresh project

```text
/utility-add
```

The plugin walks ancestors looking for a React `package.json`. If found, it drops `utilities.css` and `token-bridge.css` into `src/styles/`. If your styles directory is named differently, override:

```text
/utility-add --target=src/css
```

Then add the two import lines to your app entry — `token-bridge.css` first, `utilities.css` second. See [tutorial.md](tutorial.md) for the full walkthrough.

---

## Install a filtered subset

Every family is enabled by default. To ship only colors, spacing, and display:

```text
/utility-add --families=color-bg,color-text,color-border,spacing,display
```

The selected partials are concatenated into a single `utilities.css` (still one import, still cached as one file). Family ids are exact: `color-bg` ≠ `color`, `display` ≠ `visibility`.

---

## Regenerate after editing `utilities.tokens.json`

If you hand-edit the source-of-truth (e.g. add a custom radius token), run the generator to refresh the committed bundle:

```bash
python3 plugins/acss-utilities/scripts/generate_utilities.py \
  --tokens plugins/acss-utilities/assets/utilities.tokens.json \
  --out-dir plugins/acss-utilities/assets/
```

Then validate:

```bash
python3 plugins/acss-utilities/scripts/validate_utilities.py \
  plugins/acss-utilities/assets/
```

`tests/run.sh` runs an idempotency check that fails if the committed bundle drifts from what the generator emits — keep them in sync.

---

## Switch the spacing baseline to 4px

```text
/utility-tune use a 4px spacing baseline
```

The skill edits `assets/utilities.tokens.json`:

```jsonc
"spacing": { "baseline": "0.25rem", … }
```

…regenerates `utilities.css` (every `.m-1`, `.p-2`, `.gap-4` recomputes), and runs the validator. If the new bundle exceeds `bundleSizeBudgetKb` or breaks any contract, the tokens edit is reverted.

For an 8px baseline use `use an 8px spacing baseline`.

---

## Add an extra breakpoint

```text
/utility-tune add an xs breakpoint at 20rem
```

Adds `breakpoints.xs = "20rem"` to the tokens file. The generator emits `.xs\:hide`, `.xs\:p-4`, etc. The validator's allowed-prefix list extends automatically because `--prefixes` defaults to whatever is in the tokens file.

In JSX, write `<div className="xs:hide">…`. In CSS the rule is `@media (width >= 20rem) { .xs\:hide { … } }`.

---

## Disable a family

```text
/utility-tune disable shadow utilities
```

Sets `families.shadow.enabled = false`. The next generator run drops `assets/utilities/shadow.css` from the bundle and shrinks `utilities.css` accordingly. No `.shadow-*` classes are emitted.

To re-enable: `/utility-tune enable shadow utilities`.

---

## Regenerate the token bridge after a theme change

If you've edited `acss-kit`'s theme files (or run `/theme-create` to swap brand presets), the bundled bridge may resolve to stale fallbacks. Regenerate:

```text
/utility-bridge
```

The skill auto-detects `<projectRoot>/src/styles/theme/light.css` and `dark.css`, extracts the role colors, and writes a new `token-bridge.css` with both `:root` and `[data-theme="dark"]` blocks. The validator's parity check runs automatically.

To point at a specific file:

```text
/utility-bridge --theme=apps/web/src/styles/theme/brand-warm-light.css
```

---

## Raise the bundle-size budget

The default is 80 KB unminified. If you've enabled a custom family or extended the spacing scale and the bundle exceeds budget, edit `assets/utilities.tokens.json`:

```jsonc
"bundleSizeBudgetKb": 120
```

Or pass `--max-kb` to the validator for a one-off check:

```bash
python3 plugins/acss-utilities/scripts/validate_utilities.py \
  plugins/acss-utilities/assets/ --max-kb 120
```

Resolution order: explicit `--max-kb` flag → tokens file → 80 KB fallback. The flag always wins.

---

## Standalone mode (no acss-kit)

If you're using a hand-written theme or another design-token system, skip the bridge:

```text
/utility-add --no-bridge
```

Then either:

- Define the fpkit-style names yourself (`--color-error`, `--color-error-bg`, `--color-primary-light`) in your theme — utilities will pick them up.
- Lean on the embedded hex fallbacks in `utilities.css`. Every `var()` has one, so the bundle renders something visible without any theme.

You can also use the bridge with your own values: copy `assets/token-bridge.css` to your project, edit the `:root` and `[data-theme="dark"]` blocks to point at your token names, and import it before `utilities.css`.

---

## Inspect a single family

```text
/utility-list spacing
```

Prints every spacing class with the property it sets. For color families, also shows the `var()` chain and how the bridge resolves it.

```text
/utility-list
```

(no argument) prints the family inventory with `enabled`/`responsive` flags, the spacing scale, and the breakpoint table. Useful for sanity-checking what `/utility-tune` did.

---

## Custom drop location with `.acss-target.json`

If your project keeps styles outside `src/styles/`, drop a `.acss-target.json` at the project root:

```json
{
  "componentsDir": "src/components/fpkit",
  "utilitiesDir": "src/css"
}
```

`utilitiesDir` is honored by `/utility-add` and `/utility-bridge`. The detector validates that the path exists before using it; a stale entry pointing at a deleted directory falls back to `src/styles/` automatically (so you won't write into an unintended location).

`componentsDir` is `acss-kit`'s field; it's safe to share the same file between both plugins.
