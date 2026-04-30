# acss-utilities — Troubleshooting

---

## "tinycss2 not installed"

**Symptom:** `validate_utilities.py` exits 2 immediately with:

```json
{ "ok": false, "reasons": ["tinycss2 not installed: run `pip3 install --user tinycss2`"] }
```

**Fix:**

```bash
pip3 install --user tinycss2
```

`tinycss2` is the only non-stdlib dependency in the plugin's scripts and is also used by `tests/run.sh` for the SCSS contract check, so installing it once unblocks both.

---

## `.sm-hide` is not firing

**Symptom:** A class like `.md-show` or `.lg-hide` does not match any element.

**Cause (migrating from 0.1.x):** You may still be using the old colon-based class names in JSX (`md:show`) while the new bundle ships only `.md-show`. The colon form is no longer valid.

**Fix:** Run the migration script to update all JSX/CSS references:

```bash
python3 plugins/acss-utilities/scripts/migrate_classnames.py src/ --write
```

Or do a manual search-and-replace: `sm:` → `sm-`, `md:` → `md-`, `lg:` → `lg-`, `xl:` → `xl-`, `print:` → `print-` in all JSX `className` strings.

**Cause (hand-authored CSS):** If you write `.md-show` in a custom stylesheet at the top level (outside any `@media` block), the validator will reject it with "collides with breakpoint prefix". Move it inside `@media (width >= 48rem)` or rename it to avoid the `md-` prefix.

---

## Bundle exceeds the size budget

**Symptom:** `validate_utilities.py` reports:

```text
utilities.css: bundle size 84520 bytes exceeds budget 80 KB (81920 bytes)
```

**Causes:**

1. You added a new family or extended the spacing scale; the bundle grew past 80 KB.
2. You raised `bundleSizeBudgetKb` in your fork of the tokens file but the validator is still reading the old value.

**Fix:**

- Raise `bundleSizeBudgetKb` in `assets/utilities.tokens.json` (recipes: [Raise the bundle-size budget](recipes.md#raise-the-bundle-size-budget)).
- Pass `--max-kb 120` for a one-off override.
- Or trim the bundle with `/utility-add --families=…` — every family you drop reduces the file.

Resolution order: explicit `--max-kb` → tokens file → 80 KB fallback.

---

## Bridge dark-mode parity gap

**Symptom:**

```text
token-bridge.css: bridge dark-mode parity gap — declared in :root
but missing in [data-theme="dark"]: --color-error, --color-success-bg
```

**Cause:** Every alias defined in `:root` of the bridge **must** also be defined in `[data-theme="dark"]`. Missing aliases silently fall back to their `:root` values when the page is in dark mode, which usually looks broken.

**Fix:**

- If you ran `/utility-bridge`, the tool always emits both blocks — re-run it.
- If you hand-edited `token-bridge.css`, copy each new `:root` declaration into the `[data-theme="dark"]` block (with a dark-appropriate fallback). Then re-run `validate_utilities.py path/to/token-bridge.css` to confirm.

---

## `var()` always resolves to the hex fallback

**Symptom:** `.bg-primary` always renders the same color whether you toggle `data-theme="dark"` or not. `acss-kit` is installed but the bridge doesn't seem to be working.

**Causes:**

1. **Wrong import order.** `utilities.css` is imported before `token-bridge.css`, so the aliases aren't defined when utilities resolve them.
2. **acss-kit theme is not loaded.** `acss-kit`'s role variables (`--color-danger`, `--color-primary`) aren't on the page, so the bridge's `var()` chain falls through to the hex fallback every time.
3. **`data-theme="dark"` is on the wrong element.** It needs to be on `<html>` or a parent of the styled element — putting it on `<body>` works; putting it on a sibling does not.

**Fix:**

```ts
import "./styles/token-bridge.css";   // first
import "./styles/utilities.css";       // then
// plus whatever loads acss-kit's theme.css
```

Inspect the rendered element in dev tools. If `--color-primary` is `inherit`/`initial` on `:root`, the theme isn't loaded. If it's defined but the utility still uses the fallback, the import order is wrong.

---

## `.acss-target.json#utilitiesDir` is being ignored

**Symptom:** You set `"utilitiesDir": "src/css"` in `.acss-target.json` but `/utility-add` still writes to `src/styles/`.

**Cause (since commit `2af654e`):** The detector now validates that `(projectRoot / utilitiesDir)` actually exists before honoring it. If the directory doesn't exist on disk, the detector silently falls back to the default (`src/styles`) so `/utility-add` cannot write into an unintended location.

**Fix:** Create the directory first:

```bash
mkdir -p src/css
```

Then re-run `/utility-add`. The detector will return `source: "configured"` and use your path. Or pass `--target=src/css` to override the detection entirely.

---

## "no project root containing react was found"

**Symptom:** `detect_utility_target.py` (or the slash command that wraps it) exits 1 with:

```json
{
  "source": "none",
  "projectRoot": null,
  "reasons": ["No project root containing react was found."]
}
```

**Cause:** The detector walks ancestors looking for a `package.json` with `react` in `dependencies` or `devDependencies`. If you're in a repo that doesn't have one (e.g. a monorepo from above the app, or a non-React project), it fails by design.

**Fix:**

- Run the command from inside the React app's directory tree (so the ancestor walk finds the right `package.json`).
- Or pass `--target=<dir>` explicitly to bypass detection:

```text
/utility-add --target=apps/web/src/styles
```

---

## Validator complains about a duplicate selector

**Symptom:**

```text
utilities.css: duplicate selector .bg-primary in top-level (2×)
```

**Cause:** Two rules with the same selector in the same nesting context. Usually means a hand-edit appended a second `.bg-primary { … }` block instead of replacing the first.

**Fix:** Search the file for the duplicate and merge the declarations. Then re-run `generate_utilities.py` if you wanted the change to come from the tokens file rather than a hand-edit — that way the next generator run won't reintroduce the duplicate.

---

## A generator-emitted class is missing at one breakpoint but not another

**Symptom:**

```text
utilities.css: responsive parity gap — '.lg\:p-4' is declared but missing at: sm, md, xl
```

**Cause:** Every utility that has a responsive variant at one declared breakpoint must have it at every other declared breakpoint. The generator emits these in lockstep; if you're seeing a parity gap, something hand-edited the bundle.

**Fix:** Re-run the generator from the source tokens — it will produce a complete set:

```bash
python3 plugins/acss-utilities/scripts/generate_utilities.py \
  --tokens plugins/acss-utilities/assets/utilities.tokens.json \
  --out-dir plugins/acss-utilities/assets/
```

Then commit the regenerated bundle.
