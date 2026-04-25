# acss-component-specs — Command Reference

All six commands delegate to the corresponding section in [`SKILL.md`](../skills/acss-component-specs/SKILL.md). This file is the human-readable reference; the SKILL.md is the authoritative Claude workflow.

---

## /spec-add

Scaffold a new component spec by fetching the fpkit component source from GitHub.

**Signature**

```
/spec-add <component> [--refresh]
```

**Tools used:** `WebFetch, Write, Read, Bash`

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `<component>` | Yes | Component name (e.g., `button`, `stack`). Used to look up the fpkit source path and name the output spec file. |
| `--refresh` | No | Force a re-fetch from GitHub, bypassing the 7-day cache in `assets/fpkit-cache/`. Use when the upstream fpkit source has changed. |

### What happens

1. Runs `scripts/fetch_fpkit_source.py <component> [--refresh]`. Hits the GitHub API to resolve the current `main` SHA, then fetches the component source from `https://raw.githubusercontent.com/shawn-sandy/acss/main/packages/fpkit/src/components/...`. Caches the result under `assets/fpkit-cache/<sha>/`.
2. Reads the cached source. Extracts props, events, CSS variables, and state patterns.
3. Reads [`references/spec-format.md`](../skills/acss-component-specs/references/spec-format.md) to confirm the frontmatter schema.
4. Writes `specs/<component>.md` with `format_version: 1`, the resolved SHA in `fpkit_version`, and the extracted data structured into the spec frontmatter + Markdown body.
5. Runs `scripts/validate_spec.py specs/<component>.md` to confirm the new spec passes schema validation.

### Example

```
/spec-add stack                # Fetch stack.tsx, scaffold specs/stack.md, validate
/spec-add button --refresh     # Re-fetch button source, update specs/button.md
```

---

## /spec-render

Render a component spec into framework-specific files in the staging directory.

**Signature**

```
/spec-render <component> [--target=react|html|astro|all]
```

**Tools used:** `Read, Write, Edit, Bash, Glob`

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `<component>` | Yes | Spec name to render. A `specs/<component>.md` file must exist. |
| `--target` | No | Framework to render for. Defaults to the `framework` field in `.acss-target.json`; if absent, renders all three. |

### What happens (steps R1–R6)

1. **R1 — Target resolution:** `--target` wins over `.acss-target.json.framework`, which wins over the default (all).
2. **R2 — Plan:** Runs `scripts/plan_render.py specs/<component>.md --target=<target>`. Returns the dependency order and the file manifest (which `.tsx`/`.scss` or `.html`/`.css` or `.astro`/`.scss` files to write).
3. **R3 — Reference load:** Reads the appropriate `references/frameworks/<target>.md` lazily. Reads the spec file.
4. **R4 — Emit:** Writes each file to `.acss-staging/<framework>/`. Every generated file is stamped `// generated from <component>.md@<version>` on the first line. Atomic: if any file fails, all staged output is rolled back.
5. **R5 — Theme check:** Scans project SCSS/CSS for `:root { --color-primary: …`. If missing and the spec declares `theme_dependencies`, prepends a warning comment to the SCSS and logs a console warning.
6. **R6 — Gitignore prompt:** On first render, checks the project `.gitignore` for `.acss-staging/`. If absent, prompts to add it.

### Example

```
/spec-render button                    # Render to all targets (or the .acss-target.json default)
/spec-render dialog --target=react     # React+SCSS only
/spec-render card --target=astro       # Astro+SCSS only
```

---

## /spec-diff

Preview the diff between staged render output and existing project files. Never writes.

**Signature**

```
/spec-diff <component> [--target=react|html|astro]
```

**Tools used:** `Bash, Read`

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `<component>` | Yes | Component name. Staged files must exist in `.acss-staging/<framework>/`. |
| `--target` | No | Which staged target to diff. Defaults to the same resolution as `/spec-render`. |

### What happens

Locates files under `.acss-staging/<framework>/<component>/`, compares each against the corresponding file under `componentsDir`, and prints a unified diff block per file pair. If a project file does not yet exist, the diff shows the full new file as a diff against nothing.

Run this before every `/spec-promote`. It is your last chance to review before staged files overwrite project files.

### Example

```
/spec-diff button
/spec-diff dialog --target=react
```

---

## /spec-promote

Move staged render output into project component directories.

**Signature**

```
/spec-promote <component> [--target=react|html|astro|all]
```

**Tools used:** `Bash, Read, Write, Edit`

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `<component>` | Yes | Component name. Staged files must exist. |
| `--target` | No | Which staged target to promote. |

### What happens

Reads `componentsDir` from `.acss-target.json`. **Moves** (not copies) each staging file to its final destination under `componentsDir`, overwriting the existing file and reporting the outcome. The staging directory for that component is left empty after a successful promotion.

Always run `/spec-diff` first.

### Example

```
/spec-promote button
/spec-promote card --target=react
```

---

## /spec-validate

Validate component specs against the schema. Optionally flag stale project stamps.

**Signature**

```
/spec-validate [<component>] [--stale]
```

**Tools used:** `Bash, Read`

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `[<component>]` | No | Spec to validate. Without an argument, validates all `specs/*.md`. |
| `--stale` | No | After schema validation, scan project files for `// generated from <spec>.md@<ver>` stamps and flag any whose version is behind the current spec. |

### What happens

Runs `scripts/validate_spec.py` with the appropriate arguments. Exit 0 = clean. Exit 1 = errors or stale files found.

Checks include: required frontmatter fields, `format_version == 1`, `a11y.wcag` non-empty (unless `a11y.layout_only: true`), WCAG 2.2 SC identifiers, props have `name` + `maps_to`, `maps_to` is one of the 7 valid kinds, `fpkit_source` starts with `https://`.

### Example

```
/spec-validate                 # Validate all specs
/spec-validate button          # Validate only button.md
/spec-validate --stale         # Validate all + find outdated generated files
```

---

## /spec-list

List all available component specs and their status, or dump full details for one spec.

**Signature**

```
/spec-list [<component>]
```

**Tools used:** `Read, Bash, Glob`

### What happens

**Without an argument:** Globs `specs/*.md`, runs `scripts/parse_spec.py` on each, and prints a table of `name`, `format_version`, and `fpkit_version`. If no specs exist, prompts to run `/spec-add`.

**With a component name:** Reads `specs/<component>.md` and prints a full summary: frontmatter fields, props table, events, CSS vars, a11y block, framework notes.

### Example

```
/spec-list                     # Table of all available specs
/spec-list button              # Full details for button.md
```
