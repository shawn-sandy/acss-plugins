# Changelog

All notable changes to the `acss-utilities` plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the plugin adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-04-28

### Added

- **Initial release.** Sibling plugin to `acss-kit` providing a Tailwind-style atomic CSS layer for fpkit/acss projects. Mirrors fpkit upstream class conventions (kebab-case, no prefix, responsive `sm:`/`md:`/`lg:`/`xl:` variants via escaped colons).
- **`/utility-add [--target=<dir>] [--families=<list>] [--no-bridge]`** — copy `utilities.css` (and `token-bridge.css` unless `--no-bridge`) into a target React project. Defaults to the bundled full atomic suite; `--families=color,spacing` filters.
- **`/utility-list [family]`** — read-only catalogue printer. No-arg lists every utility family; with a family argument prints every class and the CSS custom property it references.
- **`/utility-tune <natural-language>`** — adjust the spacing baseline, breakpoints, or family list via natural language. Edits `assets/utilities.tokens.json`, regenerates the bundle, runs the validator.
- **`/utility-bridge [--theme=<file>]`** — regenerate `token-bridge.css` aliases against the user's active acss-kit theme. Always emits both `:root` and `[data-theme="dark"]` blocks.
- **`scripts/generate_utilities.py`** — generator that reads `utilities.tokens.json` and emits `utilities.css` + per-family partials. Stdlib only; data on stdout, errors on stderr; exit 0/1/2.
- **`scripts/validate_utilities.py`** — validator for utility CSS. Enforces kebab-case selectors, mandatory `var()` fallbacks, dark-mode bridge parity, no duplicate selectors, and an 80&nbsp;KB bundle-size budget. Exit 0 on pass.
- **`scripts/detect_utility_target.py`** — detector for the React target project. Mirrors `acss-kit/scripts/detect_target.py`'s ancestor-walk and `.acss-target.json` schema; suggests a default drop location at `src/styles/utilities.css`.
- **Token bridge** — `assets/token-bridge.css` aliases acss-kit's `--color-danger`, `--color-primary`, etc. to fpkit-style names (`--color-error`, `--color-error-bg`, `--color-primary-light`) in both `:root` and `[data-theme="dark"]`.
- **Source-of-truth** — `assets/utilities.tokens.json` is the canonical input for the generator. Includes spacing scale, breakpoints, color role list, family-enable map, and bundle-size budget.
- **Maintainer skills** — `.claude/skills/utility-author/` (scaffold a new family) and `.claude/skills/utility-update/` (re-validate after token-bridge or naming changes) live in the project, not the plugin.
- **Tests** — `tests/run.sh` adds a CSS contract check, an idempotency check (regenerate + diff against committed bundle), and four bad-fixture self-tests (PascalCase selector, missing `var()` fallback, missing `[data-theme="dark"]` alias, oversize bundle).
