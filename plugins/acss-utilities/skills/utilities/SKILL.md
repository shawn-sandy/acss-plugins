---
name: utilities
description: Generate, list, tune, and bridge Tailwind-style atomic CSS utility classes for fpkit/acss projects. Mirrors fpkit upstream conventions (kebab-case, no prefix, responsive `sm:`/`md:`/`lg:`/`xl:` variants). Pairs with acss-kit via a token-bridge that aliases acss-kit's OKLCH role names to fpkit-style names in both light and dark modes. Use when the developer wants to add utility classes to their project, list which utilities are available, adjust the spacing baseline or breakpoints, or regenerate the bridge after a theme change.
allowed-tools: AskUserQuestion, Bash, Edit, Glob, Grep, Read, Write
metadata:
  version: "0.1.0"
---

# utilities

Atomic-CSS utility-class generation and management for **fpkit/acss** projects. Routes between four flows depending on which slash command was invoked. Bundles a single `utilities.css` (full atomic suite) and a `token-bridge.css` (acss-kit ↔ fpkit alias layer).

**Naming and class catalogue:** see [`references/utility-catalogue.md`](references/utility-catalogue.md) and [`references/naming-convention.md`](references/naming-convention.md).
**Breakpoints and responsive syntax:** see [`references/breakpoints.md`](references/breakpoints.md).
**Token bridge mapping:** see [`references/token-bridge.md`](references/token-bridge.md).

---

## Source-of-truth

The plugin's atomic suite is generated from [`assets/utilities.tokens.json`](../../assets/utilities.tokens.json). Edits to that file (manual or via `/utility-tune`) should be followed by `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate_utilities.py --tokens ${CLAUDE_PLUGIN_ROOT}/assets/utilities.tokens.json --out-dir ${CLAUDE_PLUGIN_ROOT}/assets/` to regenerate the committed bundle.

The committed `assets/utilities.css` and `assets/utilities/<family>.css` partials are the **canonical artifacts** — `tests/run.sh` enforces idempotency by regenerating and diffing.

---

## `/utility-add [--target=<dir>] [--families=<list>] [--no-bridge]`

**Purpose:** Copy `utilities.css` (and `token-bridge.css` unless `--no-bridge`) into the user's React project.

### Workflow

1. Run `${CLAUDE_PLUGIN_ROOT}/scripts/detect_utility_target.py`. Capture JSON.
   - `source: "configured"` or `"default"` → use `utilitiesDir` from result.
   - `source: "none"` (exit 1) → halt with the reasons array; suggest `--target=<dir>`.
2. If `--target=<dir>` was passed, override the detected `utilitiesDir`.
3. If `--families=<list>` was passed:
   - Parse comma-separated family names. Validate against `assets/utilities/`.
   - Concatenate the requested family partials in canonical order (the order in `FAMILY_ORDER` in `generate_utilities.py`) plus the bundle header.
   - Write the concatenated result to `<target>/utilities.css`.
4. Otherwise copy the prebuilt `${CLAUDE_PLUGIN_ROOT}/assets/utilities.css` verbatim to `<target>/utilities.css`.
5. Unless `--no-bridge`, copy `${CLAUDE_PLUGIN_ROOT}/assets/token-bridge.css` to `<target>/token-bridge.css`.
6. Print the import snippet:
   ```ts
   import "./styles/token-bridge.css";   // first
   import "./styles/utilities.css";       // then
   ```
7. Print a summary: files written, total bundle size in KB, families included.

### References to load

- `references/utility-catalogue.md` — full family list, every class, every CSS custom property referenced.
- `references/token-bridge.md` — required when `--no-bridge` is **not** set, so the assistant can explain the bridge's role.

---

## `/utility-list [family]`

**Purpose:** Read-only catalogue printer. No side effects.

### Workflow

#### `/utility-list` (no arguments)

1. Read `assets/utilities.tokens.json` from `${CLAUDE_PLUGIN_ROOT}/`.
2. Print every family from `families` with its `enabled` and `responsive` status.
3. Print the spacing scale and breakpoints inline, since they parameterize multiple families.
4. Suggest `/utility-list <family>` for class-level detail.

#### `/utility-list <family>`

1. Look up the family's per-family partial at `${CLAUDE_PLUGIN_ROOT}/assets/utilities/<family>.css`.
2. Print every selector and the property it sets (one line per class). For families with token references, also print the `var()` chain — e.g. `.bg-error` → `var(--color-error, transparent)` → resolved via `token-bridge.css` to `var(--color-danger, #dc2626)`.
3. Print the count of classes and the file size.

### References to load

- `references/utility-catalogue.md`

---

## `/utility-tune <natural-language>`

**Purpose:** Adjust the spacing baseline, breakpoints, or family-enable map via natural language. Edits `assets/utilities.tokens.json`, regenerates the bundle, runs the validator.

### Examples

| Phrase | Effect on tokens.json |
|---|---|
| "use a 4px spacing baseline" | `spacing.baseline = "0.25rem"` |
| "use an 8px spacing baseline" | `spacing.baseline = "0.5rem"` |
| "add an xs breakpoint at 20rem" | `breakpoints.xs = "20rem"` (validator extends `--prefixes`) |
| "disable shadow utilities" | `families.shadow.enabled = false` |
| "drop responsive variants from spacing" | `families.spacing.responsive = false` |
| "add a 'soft' radius value at 1rem" | `radius.soft = "1rem"` |

### Workflow

1. Parse the natural-language request into one or more concrete edits to `utilities.tokens.json`. If the intent is ambiguous, ask one clarifying question via `AskUserQuestion` before making edits.
2. Read `${CLAUDE_PLUGIN_ROOT}/assets/utilities.tokens.json`. Apply the edits in memory.
3. Write the updated tokens back to disk (preserving JSON key order where possible — use a stable serializer).
4. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate_utilities.py --tokens ${CLAUDE_PLUGIN_ROOT}/assets/utilities.tokens.json --out-dir ${CLAUDE_PLUGIN_ROOT}/assets/`.
5. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_utilities.py ${CLAUDE_PLUGIN_ROOT}/assets/`.
   - On `ok: false`, print the reasons array and **revert** the tokens.json edit. The committed bundle should never go out of contract.
6. Print a summary: which fields changed, new bundle size, number of classes added/removed.

### References to load

- `references/utility-catalogue.md`, `references/breakpoints.md`, `references/naming-convention.md`

---

## `/utility-bridge [--theme=<file>]`

**Purpose:** Regenerate `token-bridge.css` aliases against the user's active acss-kit theme. Always emits both `:root` and `[data-theme="dark"]` blocks.

### Workflow

1. If `--theme=<file>` was passed, use that as the source theme. Otherwise look in priority order:
   - `<projectRoot>/src/styles/theme/light.css` and `dark.css`
   - `<projectRoot>/src/styles/theme/*.css`
   - If nothing found, fall back to the bundled `${CLAUDE_PLUGIN_ROOT}/assets/token-bridge.css` defaults and warn the user.
2. Read the source theme(s) and extract the `--color-danger`, `--color-primary`, `--color-success`, etc. values for both light and dark modes.
3. Build the bridge file with the fpkit-style aliases — `--color-error: var(--color-danger, <resolved-hex>)`, `--color-error-bg: color-mix(in oklch, var(--color-danger, <hex>) 12%, var(--color-background, <bg-hex>))`, and so on.
4. Always emit both blocks; if the source theme has no `[data-theme="dark"]`, fall back to the same values for dark (and warn).
5. Write to `<projectRoot>/<utilitiesDir>/token-bridge.css` (default `src/styles/token-bridge.css`).
6. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_utilities.py <bridge-file>` to enforce parity.
7. Print a summary: which roles were aliased, which had explicit fallbacks, dark-mode parity status.

### References to load

- `references/token-bridge.md` — full alias mapping and rationale.

---

## Quality gates (post-flow)

Every flow ends with a contract check. The plugin's hooks and `tests/run.sh` enforce these automatically; the skill should run them locally too:

- **Bundle integrity** — `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_utilities.py ${CLAUDE_PLUGIN_ROOT}/assets/` exits 0.
- **Idempotency** — regenerating from `utilities.tokens.json` produces the same bytes as the committed `utilities.css`.
- **Bridge parity** — every alias in `:root` is also defined in `[data-theme="dark"]`.

If any of these fail, the user-visible flow halts and the assistant reports the reasons array verbatim.

---

## Out of scope (deferred to v2)

- Scan-and-emit (JIT / purge) — the bundle is full by default; `--families` provides static filtering.
- Auto-trigger on natural language ("make this padded") — `/utility-tune` is the explicit invocation.
- Theme-mode utilities (`dark:bg-primary`, etc.) — fpkit doesn't ship these upstream.
- Generating React components — `acss-kit` owns components.
