# acss-utilities — Commands

Four slash commands ship with the plugin. Each delegates to a section of [`skills/utilities/SKILL.md`](../skills/utilities/SKILL.md); this page is the user-facing reference.

| Command | Side effects | Argument hint |
|---|---|---|
| [`/utility-add`](#utility-add) | Writes `utilities.css` and `token-bridge.css` into your project | `[--target=<dir>] [--families=<comma-list>] [--no-bridge]` |
| [`/utility-list`](#utility-list) | None — read-only catalogue | `[family]` |
| [`/utility-tune`](#utility-tune) | Edits `utilities.tokens.json`, regenerates the bundle, validates | `<natural-language description>` |
| [`/utility-bridge`](#utility-bridge) | Writes `token-bridge.css` against your active acss-kit theme | `[--theme=<file>]` |

---

## `/utility-add`

Copy the prebuilt `utilities.css` (and `token-bridge.css` unless `--no-bridge`) into a target React project.

**Signature:** `/utility-add [--target=<dir>] [--families=<comma-list>] [--no-bridge]`

**Reads:** `assets/utilities.css`, `assets/utilities/<family>.css`, `assets/token-bridge.css`, the active `.acss-target.json` if present.

**Writes:** `<target>/utilities.css`, `<target>/token-bridge.css`.

### Workflow

| Step | What happens |
|---|---|
| 1 | Run `scripts/detect_utility_target.py`. The detector walks ancestors looking for a React `package.json`, then reads `.acss-target.json#utilitiesDir` if present and the directory exists. Falls back to `src/styles`. |
| 2 | If `--target=<dir>` is passed, override the detected drop location. |
| 3a | If `--families=` is passed, concatenate the requested partials in canonical order plus the bundle header. Write to `<target>/utilities.css`. |
| 3b | Otherwise copy `assets/utilities.css` verbatim. |
| 4 | Unless `--no-bridge`, copy `assets/token-bridge.css` to `<target>/token-bridge.css`. |
| 5 | Print the import order: `token-bridge.css` first, `utilities.css` second. |
| 6 | Print a summary: files written, total size, families included. |

### Examples

```text
/utility-add                                           # full bundle, default target
/utility-add --target=apps/web/src/styles              # explicit target
/utility-add --families=color-bg,color-text,spacing    # filtered subset
/utility-add --no-bridge                               # standalone with your own theme
```

### Family ids accepted by `--families=`

`color-bg`, `color-text`, `color-border`, `spacing`, `display`, `flex`, `grid`, `type`, `radius`, `shadow`, `position`, `z-index`. There is **no** `color` alias group — pass the three color families explicitly if you want them all.

---

## `/utility-list`

Read-only catalogue printer. Writes nothing.

**Signature:** `/utility-list [family]`

**Reads:** `assets/utilities.tokens.json`, `assets/utilities/<family>.css`.

### `/utility-list` (no argument)

Prints every family from `tokens.families` with its `enabled` and `responsive` flags, the spacing scale, and the breakpoint values. Suggests `/utility-list <family>` for class-level detail.

### `/utility-list <family>`

Prints every selector in the per-family partial with the property it sets and the `var()` chain it references. For color families, also prints how the bridge resolves the alias against `acss-kit`.

### Examples

```text
/utility-list             # print the family inventory
/utility-list color-bg    # every .bg-* class with its var() chain
/utility-list spacing     # every .m-*, .p-*, .gap-* class
/utility-list display     # hide/show/invisible + sr-only utilities + responsive variants
```

---

## `/utility-tune`

Adjust `utilities.tokens.json` via natural language, regenerate the bundle, and validate.

**Signature:** `/utility-tune <natural-language description>`

**Reads:** `assets/utilities.tokens.json`.

**Writes:** `assets/utilities.tokens.json`, `assets/utilities.css`, `assets/utilities/<family>.css` (regenerated). Reverts the tokens edit if validation fails.

### Examples

| Phrase | Effect |
|---|---|
| `use a 4px spacing baseline` | `spacing.baseline = "0.25rem"` |
| `use an 8px spacing baseline` | `spacing.baseline = "0.5rem"` |
| `add an xs breakpoint at 20rem` | `breakpoints.xs = "20rem"` |
| `disable shadow utilities` | `families.shadow.enabled = false` |
| `drop responsive variants from spacing` | `families.spacing.responsive = false` |
| `add a 'soft' radius value at 1rem` | `radius.soft = "1rem"` |

### Workflow

| Step | What happens |
|---|---|
| 1 | Parse the request into concrete edits. If ambiguous, the assistant asks one clarifying question via `AskUserQuestion`. |
| 2 | Read `assets/utilities.tokens.json` and apply edits in memory. |
| 3 | Write the updated tokens back to disk. |
| 4 | Run `scripts/generate_utilities.py --tokens <file> --out-dir assets/`. |
| 5 | Run `scripts/validate_utilities.py assets/`. On `ok: false`, revert the tokens edit and report the reasons. |
| 6 | Print a summary: which fields changed, new bundle size, classes added/removed. |

The committed bundle is contract-protected: tokens edits are only persisted if the regenerated bundle passes the validator.

---

## `/utility-bridge`

Regenerate `token-bridge.css` against the user's active `acss-kit` theme. Always emits both `:root` and `[data-theme="dark"]` blocks.

**Signature:** `/utility-bridge [--theme=<file>]`

**Reads:** the source theme(s) — by default `<projectRoot>/src/styles/theme/light.css` and `dark.css`, or whatever `--theme=` points at.

**Writes:** `<projectRoot>/<utilitiesDir>/token-bridge.css` (default `src/styles/token-bridge.css`).

### Workflow

| Step | What happens |
|---|---|
| 1 | Resolve the source theme. With `--theme=<file>`, use it. Otherwise auto-detect `src/styles/theme/{light,dark}.css`. If nothing is found, fall back to the bundled defaults and warn. |
| 2 | Extract `--color-danger`, `--color-primary`, `--color-success`, `--color-warning`, `--color-info` for both light and dark modes. |
| 3 | Build the bridge with `var()` chains and embedded hex fallbacks. Synthesize `-bg` and `-light` variants via `color-mix(in oklch, …)`. |
| 4 | Write the file to the resolved target. Always emit both `:root` and `[data-theme="dark"]` blocks; if the source theme has no dark block, warn and use the same values. |
| 5 | Run `scripts/validate_utilities.py <bridge-file>` to enforce parity. Halt on any reason. |
| 6 | Print a summary: which roles were aliased, dark-mode parity status, fallback hex values used. |

### Examples

```text
/utility-bridge                                        # auto-detect theme files
/utility-bridge --theme=apps/web/src/styles/theme/light.css
```

The bridge's job is to **define** fallbacks for utilities, so the validator does **not** require `var()` fallbacks inside `token-bridge.css` itself — only the dark-mode parity check applies.
