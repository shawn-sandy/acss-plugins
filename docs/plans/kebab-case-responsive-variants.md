# Plan — kebab-case responsive class names

## Context

`acss-utilities` currently emits responsive variants using fpkit upstream's escaped-colon convention (`.sm\:hide`, `.md\:p-6`, `.print\:hide`). The user wants all `:`-bearing utility class names converted to plain kebab-case so JSX `className` strings, validators, and tooling don't have to deal with the colon.

**Decisions confirmed with user (2026-04-29):**

- Separator: **single hyphen** — `.sm-hide`, `.md-p-6`, `.print-hide`. No collision today (no base utility starts with `sm-`/`md-`/`lg-`/`xl-`/`print-`).
- fpkit parity claim: **drop entirely** for class naming. Token names, breakpoint values, and modern range media-query syntax still mirror fpkit; class-name divergence is now a documented design decision.
- Migration mode: **clean break in 0.2.0**, no dual-emit shim. Pre-1.0 semver allows breaking changes on minor bumps.
- Print collision-guard: **structural** — validator uses tinycss2 to detect `@media print { ... }` context; `.print-*` selectors only allowed inside that block.
- Validator strictness scope: **bundle only** (`assets/utilities.css` + family partials). Consumer-supplied CSS files are not subject to the new base-existence and collision-guard checks.
- Consumer migration script (`scripts/migrate_classnames.py`): **in-scope for 0.2.0** — see step 7.
- This is a breaking change for any consumer who already imported the bundle. Bump `plugin.json` to `0.2.0` and document migration.

## Status

**IMPLEMENTED** (2026-04-29). All steps completed and `tests/run.sh` is green.

## Steps

### 0. Pre-edit grep enumeration ✅

Grep confirmed colon-syntax only in the scripts and generated assets; acss-kit cross-plugin check was clean.

### 1. Validator redesign — `plugins/acss-utilities/scripts/validate_utilities.py` ✅

New `SELECTOR_RE`: matches `.<body>(:pseudo)*` without the prefix group. Stage B prefix detection done in `validate_utility_file` by checking if body starts with `<bp>-`.

New checks added:
- **Check 1 — base-class-existence:** every `.sm-foo` must have a base `.foo` in the same file.
- **Check 2 — collision guard:** selectors starting with a breakpoint prefix are only valid inside the matching `@media` block.
- **Reserved prefix names:** bare prefix names (`sm`, `md`, `lg`, `xl`, `print`) rejected as class bodies to catch old colon syntax (`.sm:hide` parsed as body=`sm`, pseudo=`:hide`).
- **Check 3 — parity message updated:** `'.{bp}-{cls}'` (was `'.{bp}\\:{cls}'`).

### 2. Generator emission — `plugins/acss-utilities/scripts/generate_utilities.py` ✅

- `_wrap_responsive`: `bp + r"\:"` → `bp + "-"`
- `emit_display`: `block(bp + chr(92) + ':')` → `block(bp + '-')`, `print\\:hide` → `print-hide`
- Docstring updated.

### 3. Regenerate the canonical artifacts ✅

All CSS partials regenerated. Validator passes with exit 0.

### 4. Update SKILL/reference docs ✅

- `SKILL.md` description updated, version bumped to `0.2.0`
- `breakpoints.md`: media-query block and JSX examples updated
- `naming-convention.md`: selector form, prefix-allowlist rule, collision guard documented
- `utility-catalogue.md`: all `.sm:` → `.sm-` forms updated

### 5. Update plugin docs and ATTRIBUTION ✅

- `README.md`: class examples, responsive variants subsection with migration notes
- `CHANGELOG.md`: `[0.2.0]` entry with breaking change, new validator checks, migration guide
- `ATTRIBUTION.md`: class-name divergence documented
- `docs/tutorial.md`, `docs/concepts.md`, `docs/troubleshooting.md`: updated

### 6. Bump version + marketplace description + plan rename ✅

- `plugin.json`: `0.1.0` → `0.2.0`
- `marketplace.json`: description updated
- This plan file renamed from auto-generated stub

### 7. Consumer migration script — `plugins/acss-utilities/scripts/migrate_classnames.py` ✅

Stdlib-only. Dry-run by default; `--write` to apply. Covers JSX/TSX, TS/JS (clsx/classnames), HTML/Svelte/Vue/Astro (`class=`/`className=` only), CSS/SCSS (`@apply` + escaped selectors). 7 fixtures passing with idempotency. Integrated into `tests/run.sh` Step 10.

## Next Steps (out of scope)

- `/utility-migrate` slash command wrapping `migrate_classnames.py` if consumers ask for a one-key invocation.
- Lint rule / pre-commit hook flagging literal `\bsm:hide` patterns in JSX strings inside consumer projects.
- Revisit `token-bridge.css` aliases now that fpkit class-name parity has been dropped (token-name parity is independent and stays).
