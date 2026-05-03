---
paths:
  - "plugins/*/scripts/**"
---

# Python Script Contracts

Current scripts in `plugins/acss-kit/scripts/`:

- `detect_target.py` — detects the target project type (Vite, etc.) for skill routing
- `detect_package_manager.py` — detects the active package manager (pnpm/yarn/bun/npm) via lockfile inspection; outputs install command
- `detect_stack.py` — classifies framework (vite/next/remix/astro/cra), bundler, CSS pipeline (tailwind/sass/postcss/css-modules), tsconfig presence, and entrypoint file. Detector contract; includes `--self-test`. Persisted by SKILLs into `.acss-target.json` under a `stack` key
- `detect_css_entry.py` — finds candidate CSS / SCSS entry files (e.g. `src/styles/index.scss`, `src/index.css`, `app/globals.css`) and reports which `light.css` / `dark.css` / `token-bridge.css` / `utilities.css` imports each candidate already carries. Used by `/setup` Step 7.5 to wire theme imports. Detector contract; includes `--self-test`. The chosen file is persisted at `stack.cssEntryFile` in `.acss-target.json`
- `verify_integration.py` — read-only post-step that checks the user's entrypoint imports the artifacts written by `/kit-add`, `/theme-create`, and `/utility-add` (token-bridge.css, utilities.css, theme css, components dir). Also accepts theme imports living in `stack.cssEntryFile` (SCSS/CSS) instead of the TSX entrypoint. Exit 0 when all wired up, exit 1 with `reasons` listing each missing import. Detector contract; report-only — never edits user files
- `generate_palette.py` — OKLCH palette math; outputs palette JSON
- `oklch_shift.py` — shifts a hex color in OKLCH space (`--hue`, `--chroma`, `--lightness`); used by the `style-tune` skill for color deltas
- `_oklch.py` — internal shared module exposing `hex_to_oklch`, `oklch_to_hex`, `in_gamut`. Imported by `generate_palette.py` and `oklch_shift.py`. Underscore prefix marks it as internal — no CLI, no detector contract.
- `css_to_tokens.py` — converts CSS custom properties to palette JSON
- `tokens_to_css.py` — converts palette JSON to CSS custom property files
- `validate_theme.py` — checks theme CSS files for WCAG 2.2 AA contrast on semantic role pairs
- `hash_file.py` — hashes a file or stdin content with sha256 after the kit-sync normalization rules (LF endings, strip trailing whitespace per line, single trailing newline). Used by `/kit-sync` to record manifest entries and by `/kit-update` to compare on-disk content. Generator/validator contract
- `manifest_read.py` — reads `.acss-kit/manifest.json` from a project root and emits its contents as JSON. Detector contract
- `manifest_write.py` — atomically merges a stdin JSON payload into `.acss-kit/manifest.json` (write-temp + rename). Preserves entries not mentioned in the payload; accepts `removePaths` for pruning. Generator/validator contract
- `diff_status.py` — drift detector for `/kit-update`: compares each file recorded in the manifest against its current normalized sha256 and classifies it as `clean`, `modified`, or `missing`. Detector contract; includes `--self-test` that exercises the full hash → write → read → diff round-trip plus the CRLF-vs-LF normalization invariant

Current scripts in `plugins/acss-utilities/scripts/`:

- `detect_utility_target.py` — detects the target React project + drop directory for `utilities.css`. Mirrors `acss-kit/scripts/detect_target.py`'s ancestor-walk and reads the same `.acss-target.json` (with an added `utilitiesDir` field)
- `generate_utilities.py` — reads `utilities.tokens.json` and emits per-family CSS partials + a concatenated `utilities.css`. Generator/validator contract; either streams the bundle to stdout or writes to a directory via `--out-dir`
- `validate_utilities.py` — validates utility CSS files: kebab-case selectors, `var()` fallbacks, no duplicate selectors, responsive parity across breakpoints, bundle-size budget, and `token-bridge.css` `:root` ↔ `[data-theme="dark"]` parity. Detector contract (JSON `{ok, reasons}` to stdout, exit 0/1/2)
- `migrate_classnames.py` — rewrites 0.1.x colon-form utility classes (`sm:hide`) to 0.2.0 hyphen form (`sm-hide`) across source files. Default dry-run prints unified diff; `--write` applies in place. Generator/validator contract: exit 0 = success (no changes needed, or changes applied via `--write`); exit 1 = dry-run with changes pending (`--write` to apply); exit 2 = usage / IO error

## Detector contract (machine-callable, structured)

For scripts whose output is parsed by slash commands or skills.

- Output JSON to stdout
- Exit 0 on success, 1 on logical failure (e.g. nothing detected)
- Always include a `"reasons"` array in the JSON — empty `[]` on success, populated on failure

Detectors: `detect_target.py`, `detect_package_manager.py`, `detect_stack.py`, `detect_css_entry.py`, `verify_integration.py`, `manifest_read.py`, `diff_status.py`, `detect_utility_target.py`, `validate_utilities.py`.

## Generator / validator contract (pipeline-friendly, human-readable)

For scripts that emit data or human-readable validation results.

- Data on stdout (JSON for `generate_palette.py` / `css_to_tokens.py` / `oklch_shift.py`; CSS files for `tokens_to_css.py`; text for `validate_theme.py`)
- Errors on stderr
- Exit 0 on success, 1 on logical failure, 2 on usage / IO errors

Generators / validators: `generate_palette.py`, `oklch_shift.py`, `tokens_to_css.py`, `css_to_tokens.py`, `validate_theme.py`, `hash_file.py`, `manifest_write.py`, `generate_utilities.py`, `migrate_classnames.py`.

`oklch_shift.py` follows this contract — it transforms an input hex into a shifted hex and emits structured JSON. It exits 0 whenever a usable hex was produced (even when chroma or lightness was clamped to stay in sRGB gamut — `clamped: true` and a populated `reasons` array surface the warning), reserves exit 1 for hard failures where no hex can be produced, and exits 2 on usage / IO errors.

## Internal module contract

`_oklch.py` is a private module — not callable from a slash command or shell. No exit codes, no stdout, no JSON. Test by importing into a sibling script and calling the helpers directly.
