# acss-kit — Command Reference

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
4. Copies `assets/foundation/ui.tsx` to `<target>/ui.tsx` if that file does not already exist.

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
