# Changelog

All notable changes to the `acss-utilities` plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the plugin adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **`/utility-add` workflow now classifies the user's build stack and verifies entrypoint wiring.** Step 2 invokes the cross-plugin `acss-kit/scripts/detect_stack.py` to populate `.acss-target.json` with framework, bundler, CSS pipeline, and entrypoint file. Step 9 invokes `acss-kit/scripts/verify_integration.py` after the import snippet is printed; missing `token-bridge.css` / `utilities.css` imports — and out-of-order imports where utilities precedes the bridge — are surfaced as a numbered fix-up list. Both scripts are skipped with a warning when acss-kit is not installed alongside acss-utilities. No auto-edits; the developer keeps ownership of the entrypoint.

## [0.2.0] - 2026-04-29

### Changed

- **Breaking: responsive variant class names now use a plain hyphen separator.** `.sm\:hide` (CSS) / `sm:hide` (JSX) → `.sm-hide` / `sm-hide` in both. Applies to all four viewport breakpoints (`sm`, `md`, `lg`, `xl`) and the print variant (`print:hide` → `print-hide`). No CSS escaping is needed in stylesheets or `className` strings.
- **Validator: new base-class-existence check.** Every responsive variant (e.g. `.sm-foo`) must have a matching base class (`.foo`) in the same file. Violations are reported as `responsive variant '.sm-foo' has no base class '.foo'`. This enforces a soundness property that the old escaped-colon scheme provided implicitly.
- **Validator: new collision guard.** Any selector whose body starts with a breakpoint prefix (`sm-`, `md-`, `lg-`, `xl-`, `print-`) is only valid inside the matching `@media` block. A top-level `.sm-foo` fails with `base class '.sm-foo' collides with breakpoint prefix — rename`.
- **Validator: reserved prefix names.** `sm`, `md`, `lg`, `xl`, and `print` are reserved as class-body strings. A selector like `.sm:hide` (old colon syntax) is rejected as `selector not in canonical form`.
- **fpkit class-name parity claim dropped.** Token values, breakpoints, and modern range-query media syntax still mirror fpkit upstream (`@fpkit/acss@6.5.0`); responsive class names now diverge deliberately. See `ATTRIBUTION.md` for the upstream/plugin split.

### Added

- **`scripts/migrate_classnames.py`** — dry-run migration script that rewrites old colon-based class names to the new hyphen form. Accepts files or directories; `--write` to apply in-place. Covers JSX/TSX, TS/JS (clsx/classnames), HTML (`class=`/`className=` attributes), and CSS/SCSS `@apply` directives. Migration: `sm:` → `sm-`, `md:` → `md-`, `lg:` → `lg-`, `xl:` → `xl-`, `print:` → `print-`. Automated path: `python3 scripts/migrate_classnames.py src/ --write`.
- **`docs/`** — developer guide tree mirroring `acss-kit/docs/`: `README.md`, `tutorial.md`, `concepts.md`, `commands.md`, `recipes.md`, `troubleshooting.md`, `architecture.md`. `visual-guide.md` deferred.
- **`tests/run.sh` integration** — Step 8 runs `validate_utilities.py` over `plugins/acss-utilities/assets/`; Step 9 regenerates the bundle from `utilities.tokens.json` and diffs against the committed copy (idempotency check); Step 10 runs `migrate_classnames.py` fixture round-trip and idempotency tests.

### Fixed

- **README:** add hex fallbacks to the token-bridge snippet so it matches the shipped `assets/token-bridge.css` and the documented bridge contract.
- **README:** replace the non-existent `color` family in `/utility-add --families=…` and `/utility-list` examples with real ids (`color-bg`, `color-text`, `color-border`).
- **`utility-catalogue.md`:** correct the spacing class-count math (`210 base + 210 × 4 bps = 1050`) and the `display` responsive count (only `hide`/`show`/`invisible` get breakpoint variants); fix the `.px-6` example (padding, not margin).
- **`detect_utility_target.py`:** only honor `.acss-target.json#utilitiesDir` when `(projectRoot / utilitiesDir)` actually exists; otherwise fall back to `src/styles`.
- **`utilities.tokens.json`:** drop the dangling `$schema: "./utilities.tokens.schema.json"` pointer — the schema file does not ship in the plugin.
- **`validate_utilities.py`:** read `bundleSizeBudgetKb` from a co-located `utilities.tokens.json` when `--max-kb` is not passed, so the token field is no longer dead. CLI flag still wins.
- **`validate_utilities.py`:** distinct context per `@media` condition for the duplicate-selector check, so a class can legitimately appear under two different breakpoints; reject unrecognised single-file targets with a usage error (exit 2) instead of running the validator against an unrelated stylesheet.

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
- **Validation tooling** — the initial release ships `scripts/validate_utilities.py` and `scripts/generate_utilities.py`. Wiring these into the shared `tests/run.sh` harness (CSS contract + idempotency check) and adding bad-fixture self-tests was deferred past `0.1.0`; see the `[Unreleased]` block.
