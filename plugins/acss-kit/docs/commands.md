# acss-kit — Command Reference

## /setup

One-time first-run bootstrap. Run once after installing the plugin so subsequent `/kit-add` and `/theme-create` calls are pure generation. Per-step idempotent — re-running is safe and skips anything already present.

**Signature**

```text
/setup [--no-theme] [--target=<dir>]
```

**Tools used:** `Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion`

**Flags**

| Flag | Description |
|------|-------------|
| `--no-theme` | Skip Step 7 (theme generation) and Step 7.5 (theme-import wiring). Initializes the component foundation only. |
| `--target=<dir>` | Override the components target directory (default `src/components/fpkit/`). The chosen value is persisted to `.acss-target.json`. |

### What happens step by step

Step labels below match the canonical sequence in [`skills/setup/SKILL.md`](../skills/setup/SKILL.md) (Steps 1–8, with Step 7.5 between Steps 7 and 8).

- **Step 1 — Verify React + TypeScript project.** Runs `scripts/detect_target.py`; halts if no `package.json` with `react` is found or if `tsconfig.json` is missing.
- **Step 2 — Detect React version.** Warns if React 19+ is detected (the bundled `ui.tsx` may need the `ElementInstance<C>` adaptation).
- **Step 3 — Detect package manager.** Runs `scripts/detect_package_manager.py` and captures `installCommand` for the next step.
- **Step 4 — Print sass install command.** Checks `devDependencies` for `sass` / `sass-embedded`. If missing, prints the exact `<pm> add -D sass` command and halts (no side effects). If `node-sass` only is present, warns and continues.
- **Step 5 — Determine target directory.** Reads `.acss-target.json` if it exists; otherwise prompts (default `src/components/fpkit/`) and writes the file.
- **Step 6 — Copy `ui.tsx`.** Reads `assets/foundation/ui.tsx` from the plugin and writes it verbatim to `<componentsDir>/ui.tsx`. Skipped if the destination already exists.
- **Step 7 — Seed starter theme** *(skipped under `--no-theme`)*. Prompts for a seed hex color (default `#4f46e5`), runs `scripts/generate_palette.py | scripts/tokens_to_css.py`, then `scripts/validate_theme.py` for WCAG 2.2 AA contrast. Writes `src/styles/theme/light.css` and `dark.css`.
- **Step 7.5 — Wire theme imports** *(skipped under `--no-theme`)*. Runs `scripts/detect_css_entry.py` to locate candidate CSS/SCSS entry files. Branches:
  - **One candidate** — uses it without prompting.
  - **Multiple candidates** — `AskUserQuestion` lists each path with a hint about which `light.css` / `dark.css` / `token-bridge.css` / `utilities.css` imports it already carries; the user picks one. "Other" accepts a free-text path.
  - **No candidate** — `AskUserQuestion` asks for a path (default `src/styles/index.scss`); the file is created if missing.

  Then idempotently appends an `@import` block at the top of the chosen file (after any `@charset` / leading comment / existing `@use` lines):

  ```scss
  /* acss-kit theme — managed by /setup */
  @import "<rel>/theme/light.css";
  @import "<rel>/theme/dark.css";
  /* token-bridge.css + utilities.css load here once /utility-* runs */
  ```

  Lines whose basename is already present in the file are skipped, so re-runs never duplicate. The chosen file is persisted at `stack.cssEntryFile` in `.acss-target.json` so `verify_integration.py` accepts theme imports (including `token-bridge.css` and `utilities.css` once `/utility-*` has run) living in SCSS rather than `main.tsx`.
- **Step 8 — Print summary.** Tabulates `Created` vs `Kept` artifacts. If Step 4 halted, instead prints the install command and exits cleanly.

### Examples

```text
/setup                                # full bootstrap with prompts
/setup --no-theme                     # only init the component foundation
/setup --target=src/ui/fpkit/         # override the components target
```

### After /setup

The next `/kit-add` finds `.acss-target.json`, `ui.tsx`, and the theme already wired and skips straight to component generation. To regenerate or tune the theme, use `/theme-create` (re-roll from a hex) or `/style-tune` (natural-language token edits) — neither of those rewires the entry file because Step 7.5 already did it.

If you ever need to change which CSS/SCSS file owns the theme imports, edit `stack.cssEntryFile` in `.acss-target.json` (or delete the key and re-run `/setup`); the next run will detect the absence and prompt again.

---

## /kit-add

Generate one or more fpkit-style components into your project.

**Signature**

```
/kit-add <component> [component2 ...]
```

**Tools used:** `Read, Glob, Grep, Write, Edit, AskUserQuestion`

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `<component>` | Yes | Name of the component to generate (e.g., `button`, `dialog`, `badge`). Case-insensitive. Pass multiple names to generate several in one invocation. |

No flags. Component names map directly to the reference catalog — run `/kit-list` to see available names.

### What happens step by step

These steps correspond to Steps A–F in [`SKILL.md`](../skills/components/SKILL.md).

**Step A — First-run init (runs once per project)**

1. Reads `package.json` to confirm this is a React + TypeScript project.
2. Checks `devDependencies` for `sass` or `sass-embedded`. Aborts with an install hint if neither is found.
3. Reads `.acss-target.json` from the project root. If the file does not exist, asks: "Where should components be generated? (default: `src/components/fpkit/`)" and writes the file.
4. Runs `scripts/detect_stack.py` to classify framework (vite/next/remix/astro/cra), bundler, CSS pipeline, and entrypoint file. Persists the result into `.acss-target.json` under a `stack` key so later runs skip re-detection.
5. Copies `assets/foundation/ui.tsx` to `<target>/ui.tsx` if that file does not already exist.

**Step B — Generation workflow**

1. **B1 — Reference lookup:** Reads the component's reference doc from `references/components/`.
2. **B2 — Dependency resolution:** Reads the Generation Contract (`export_name`, `file`, `scss`, `imports`, `dependencies`). Walks the dependency tree recursively until all leaf components are identified.
3. **B3–B4 — Preview + confirmation:** Displays the full file tree that will be created or skipped. Waits for confirmation before writing anything.
4. **B5 — Bottom-up generation:** Generates leaf dependencies first. Skips any file that already exists and uses the existing file's import path instead.

**Steps C–E — Code generation**

Claude applies the constraints from [`references/`](../skills/components/references/) when writing the output:

- TypeScript: all types inlined, local imports only, `useDisabledState` inlined for interactive components.
- SCSS: CSS-var fallbacks on every property, rem units only, `data-*` attribute selectors for variants.
- Accessibility: `aria-disabled` over native `disabled`, `:focus-visible` indicators.

**Step F — Summary**

Prints created and skipped files, plus an import and JSX usage snippet.

**Step G — Verify integration**

Runs `scripts/verify_integration.py`. Reads `stack.entrypointFile` (TSX) and the optional `stack.cssEntryFile` (SCSS/CSS) recorded during `/setup`, then runs two flavours of check (whichever artifacts are present on disk):

- **`token-bridge.css`, `utilities.css`, theme CSS (`light.css` / `dark.css`)** — the verifier scans both `entrypointFile` and `cssEntryFile` and accepts an `import` / `require()` / `@import` / `@use` line in either file. The bridge-before-utilities ordering check runs inside whichever file holds both imports.
- **`<componentsDir>/ui.tsx`** — the verifier walks every `*.tsx` / `*.ts` / `*.jsx` / `*.js` file under `src/` (not just the entrypoint) and considers the foundation "used" as soon as any of them imports a path containing `componentsDir`. This avoids false negatives when the entrypoint only renders a router and the actual fpkit usage lives in feature files.

Missing imports are printed as a numbered fix-up list with concrete suggestions — the plugin never auto-edits user code.

### Examples

```
/kit-add badge                 # Single leaf component, no deps
/kit-add button                # Interactive; inlines useDisabledState
/kit-add dialog                # Complex; resolves and generates button first
/kit-add badge button card     # Multiple components in one pass
```

### Available components

Run `/kit-list` for the full categorized listing. The shortlist:

| Category | Components |
|----------|-----------|
| Simple | badge, tag, heading, text, link, list, details, progress, icon |
| Interactive | button |
| Layout | card, nav |
| Complex | alert, dialog, form |

---

## /kit-list

List available components or inspect a specific one.

**Signature**

```
/kit-list [component]
```

**Tools used:** `Read` only — this command never writes files.

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `[component]` | No | Name of a specific component to inspect. Omit to list all. |

### What happens step by step

**Without an argument**

Reads [`references/components/catalog.md`](../skills/components/references/components/catalog.md) and prints all components grouped by category (Simple / Interactive / Layout / Complex) with a one-line description of each.

**With a component name**

Reads that component's reference doc (either from `catalog.md` or from a dedicated `references/components/{name}.md`) and prints:

- Generation Contract (`export_name`, `file`, `scss`, `imports`, `dependencies`)
- Props interface
- CSS variables with their fallback values
- A usage snippet

Nothing is written to disk.

### Examples

```
/kit-list                      # Print all available components by category
/kit-list badge                # Show Badge's Generation Contract, props, CSS vars, and usage
/kit-list dialog               # Show Dialog's full dependency tree (button)
/kit-list form                 # Show which sub-controls form.tsx contains
```

---

## /kit-create

Generate any acss-kit component from a natural-language description (creator mode). Loads the matched component's reference doc at runtime, parses its Props Interface, and resolves the user's phrases against the declared prop set. Snippet output by default; standalone component file on opt-in.

The skill (`component-creator`) auto-triggers on phrases like *"create a primary pill button that says 'Add to cart'"*, *"make me a soft warning alert titled 'Heads up'"*, *"build a card with a heading 'Plan'"*. `/kit-create` is the explicit fallback when you want to invoke creator mode by name.

**Signature**

```text
/kit-create <description>
```

**Tools used:** `Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion`

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `<description>` | Yes | A natural-language description naming a component in [`references/components/catalog.md`](../skills/components/references/components/catalog.md) and any combination of colour / size / variant / boolean / slot content. Quoted strings are content. |

### What happens step by step

The full workflow lives in [`skills/component-creator/SKILL.md`](../skills/component-creator/SKILL.md). Quick view:

- **Step A — Parse.** Dispatch the component noun against `catalog.md`; load the matched reference doc; resolve phrases against its Props Interface using two global synonym tables (colour family, size family) plus per-prop union literals.
- **Step B — Resolve target.** Run `scripts/detect_target.py` to read `componentsDir` and learn whether the project has been initialized (`source: "generated"` vs `"none"`).
- **Step C — Vendor.** Run `/kit-add <component> [...dependencies]` whenever Step B reported a clean project (`source: "none"` — first-run bootstrap) or any of the matched component's vendored files are missing in an existing project. After `/kit-add` completes, re-run `detect_target.py` to confirm `source` is now `"generated"` before proceeding.
- **Step D — Validate.** Generic rules (empty slots, > 80-char content, two-axis conflicts, missing required props) plus any `## Generation Notes — Creator Mode` rules the matched reference doc declares (v0.2).
- **Step E — Generate.** Single-element components emit a flat JSX block; compound components (Card, Table, List) emit dotted children only when the description named the slot. Snippet imports use the project's entrypoint-relative path; file mode writes `src/components/<Name>.tsx`.
- **Step F — Accessibility.** Delegated to the matched reference doc's `## Accessibility` section; the skill enforces only that generation doesn't strip those guarantees.
- **Step G — Refinement turns.** Imperative follow-ups ("make it larger", "swap to secondary", "change the title to '<X>'") merge into the in-memory spec and re-emit. Saying *"start over"* clears the spec.

### Carve-outs

Two carve-outs from the no-silent-defaults rule:

- **A3.5 — state-control props** (`open`, `expanded`, `visible`, `checked`): emit a demo default and a paired summary TODO so the snippet renders something. Their `on*` callback siblings get a no-op `() => {}` placeholder.
- **A3.6 — component-declared safe defaults** (currently Button's `type="button"`): emit unconditionally; no halt, no summary note.

### Examples

```text
/kit-create primary pill button that says "Add to cart"
/kit-create soft warning alert titled "Heads up" with body "Your card expires next month"
/kit-create card with a heading "Plan" and content "Premium tier with all features"
/kit-create danger badge with the text "3"
/kit-create small outline icon-button with aria-label "Close"
```

### Out of scope for v0.1

- **Multi-component compositions in one prompt** ("a card with a switch and a slider") — generate the outer component, then refine to add inner components one at a time. Multi-component prompts land in v0.3.
- **Form-shaped descriptions** ("signup form with email and password") — handled by the `component-form` skill instead.

---

## /style-tune

Adjust the visual feel of acss-kit components or theme roles using natural language. Routes between theme-role edits (delegated to `/theme-update` with WCAG pre-validation) and component SCSS token edits.

**Signature**

```
/style-tune <natural-language description>
```

**Tools used:** `Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion`

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `<natural-language description>` | Yes | One or more sentences naming a component (button, card, alert, dialog, input, nav) or theme role (primary, accent, danger, warning, info, success, brand) plus a modifier from the intent vocabulary (softer, warmer, calmer, spacious, elevated, smaller, narrower, etc.). |

The skill also auto-triggers on the same phrases without the slash command — see the SKILL.md front-matter for the full trigger surface.

### What happens step by step

These steps correspond to Steps A–F in [`SKILL.md`](../skills/style-tune/SKILL.md).

**Step A — Resolve intent**

1. Read `references/intent-vocabulary.md` to load the modifier table.
2. Tokenize the prompt; match modifiers to token families.
3. Map subject nouns to a layer: theme-role names route to the theme layer, component names route to the component layer.
4. AskUserQuestion when the prompt is ambiguous, contradictory, or missing a subject.

**Step B — Locate files**

1. Run `scripts/detect_target.py` to capture `componentsDir`.
2. Theme layer: locate `light.css` + `dark.css`; auto-mirror when both exist.
3. Component layer: probe `<componentsDir>/<component>/<component>.scss`; halt with a `/kit-add` hint if missing.

**Step C — Compute deltas**

1. Theme layer: read current hex via `scripts/css_to_tokens.py`; compute new hex via `scripts/oklch_shift.py`. Apply paired-role and dark-mirror rules.
2. Component layer: apply scalar deltas (radius × 1.5, padding × 0.66, etc.). Var-only references auto-route to the underlying theme role.

**Step D — Apply edits**

1. Theme batch: stage proposed values into a tmp directory and run `scripts/validate_theme.py` against each staged file. Halt the entire batch on any contrast failure (atomic — paired roles never desync).
2. Component batch: build the updated SCSS in memory; Edit atomically. Preserve all `var()` wrappers.

**Step E — Validate**

1. Theme: D's pre-validation guarantees no in-flight reverts.
2. Component: structural integrity check (`var(` count unchanged; each token still appears exactly once on a declaration LHS).
3. Drift hint when a tuned color's chroma drops below 0.05 or its hue diverges >30° from its palette-derived reference.

**Step F — Summary**

Print a `Modifier / Token / Old / New / Status` table plus next-step hints.

### Examples

```
/style-tune make the button feel softer and warmer
/style-tune tone down the primary color a touch
/style-tune more spacious cards
/style-tune style the dialog to feel more elevated
/style-tune narrower dialog
/style-tune smaller buttons
```
