# acss-kit-builder — Command Reference

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

These steps correspond to Steps A–F in [`SKILL.md`](../skills/acss-kit-builder/SKILL.md).

**Step A — First-run init (runs once per project)**

1. Reads `package.json` to confirm this is a React + TypeScript project.
2. Checks `devDependencies` for `sass` or `sass-embedded`. Aborts with an install hint if neither is found.
3. Reads `.acss-target.json` from the project root. If the file does not exist, asks: "Where should components be generated? (default: `src/components/fpkit/`)" and writes the file.
4. Copies `assets/foundation/ui.tsx` to `<target>/ui.tsx` if that file does not already exist.

**Step B — Generation workflow**

1. **B0 — Spec bridge:** Probes for an `acss-component-specs` spec at two locations (see [concepts.md](concepts.md#the-acss-component-specs-bridge)). Uses the spec if found; silently falls back to the bundled reference doc.
2. **B1 — Reference lookup:** Reads the component's reference doc from `references/components/`.
3. **B2 — Dependency resolution:** Reads the Generation Contract (`export_name`, `file`, `scss`, `imports`, `dependencies`). Walks the dependency tree recursively until all leaf components are identified.
4. **B3–B4 — Preview + confirmation:** Displays the full file tree that will be created or skipped. Waits for confirmation before writing anything.
5. **B5 — Bottom-up generation:** Generates leaf dependencies first. Skips any file that already exists and uses the existing file's import path instead.

**Steps C–E — Code generation**

Claude applies the constraints from [`references/`](../skills/acss-kit-builder/references/) when writing the output:

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

Reads [`references/components/catalog.md`](../skills/acss-kit-builder/references/components/catalog.md) and prints all components grouped by category (Simple / Interactive / Layout / Complex) with a one-line description of each.

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
