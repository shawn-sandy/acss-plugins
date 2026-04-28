---
paths:
  - "plugins/*/scripts/**"
---

# Python Script Contracts

Current scripts in `plugins/acss-kit/scripts/`:

- `detect_target.py` — detects the target project type (Vite, etc.) for skill routing
- `detect_package_manager.py` — detects the active package manager (pnpm/yarn/bun/npm) via lockfile inspection; outputs install command
- `generate_palette.py` — OKLCH palette math; outputs palette JSON
- `oklch_shift.py` — shifts a hex color in OKLCH space (`--hue`, `--chroma`, `--lightness`); used by the `style-tune` skill for color deltas
- `_oklch.py` — internal shared module exposing `hex_to_oklch`, `oklch_to_hex`, `in_gamut`. Imported by `generate_palette.py` and `oklch_shift.py`. Underscore prefix marks it as internal — no CLI, no detector contract.
- `css_to_tokens.py` — converts CSS custom properties to palette JSON
- `tokens_to_css.py` — converts palette JSON to CSS custom property files
- `validate_theme.py` — checks theme CSS files for WCAG 2.2 AA contrast on semantic role pairs

Current scripts in `plugins/acss-utilities/scripts/`:

- `detect_utility_target.py` — detects the target React project + drop directory for `utilities.css`. Mirrors `acss-kit/scripts/detect_target.py`'s ancestor-walk and reads the same `.acss-target.json` (with an added `utilitiesDir` field)
- `generate_utilities.py` — reads `utilities.tokens.json` and emits per-family CSS partials + a concatenated `utilities.css`. Generator/validator contract; either streams the bundle to stdout or writes to a directory via `--out-dir`
- `validate_utilities.py` — validates utility CSS files: kebab-case selectors, `var()` fallbacks, no duplicate selectors, responsive parity across breakpoints, bundle-size budget, and `token-bridge.css` `:root` ↔ `[data-theme="dark"]` parity. Generator/validator contract (data + reasons array on stdout, exit 0/1/2)

## Detector contract (machine-callable, structured)

For scripts whose output is parsed by slash commands or skills.

- Output JSON to stdout
- Exit 0 on success, 1 on logical failure (e.g. nothing detected)
- Always include a `"reasons"` array in the JSON — empty `[]` on success, populated on failure

Detectors: `detect_target.py`, `detect_package_manager.py`, `detect_utility_target.py`.

## Generator / validator contract (pipeline-friendly, human-readable)

For scripts that emit data or human-readable validation results.

- Data on stdout (JSON for `generate_palette.py` / `css_to_tokens.py` / `oklch_shift.py`; CSS files for `tokens_to_css.py`; text for `validate_theme.py`)
- Errors on stderr
- Exit 0 on success, 1 on logical failure, 2 on usage / IO errors

Generators / validators: `generate_palette.py`, `oklch_shift.py`, `tokens_to_css.py`, `css_to_tokens.py`, `validate_theme.py`.

`oklch_shift.py` follows this contract — it transforms an input hex into a shifted hex and emits structured JSON. It exits 0 whenever a usable hex was produced (even when chroma or lightness was clamped to stay in sRGB gamut — `clamped: true` and a populated `reasons` array surface the warning), reserves exit 1 for hard failures where no hex can be produced, and exits 2 on usage / IO errors.

## Internal module contract

`_oklch.py` is a private module — not callable from a slash command or shell. No exit codes, no stdout, no JSON. Test by importing into a sibling script and calling the helpers directly.
