---
name: acss-component-specs
description: Use when rendering fpkit components from framework-agnostic specs to React+SCSS, HTML+CSS, or Astro+SCSS. Also use when adding new specs, validating specs, or reviewing what components are available.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
metadata:
  version: "0.1.0"
---

# SKILL: acss-component-specs

Author framework-agnostic component specs and render them to React+SCSS, HTML+CSS, or Astro+SCSS. Specs live in `specs/` as Markdown + YAML frontmatter. Rendering is a 3-step flow: `/spec-render` → `/spec-diff` → `/spec-promote`.

---

## When to Use This Skill

- Use when a developer wants to generate components in multiple frameworks from a single source of truth.
- Use when working in an Astro or HTML-first project (not React-only — that's kit-builder's domain).
- Use when generating components for the first time in a project and framework choice hasn't been locked yet.
- Do **not** use for React-only projects that already use `acss-kit-builder` successfully — kit-builder is the passive consumer.

---

## Spec Primer

Every spec is a `.md` file at `specs/<component>.md` with two parts:

1. **YAML frontmatter** — machine-readable contract: props, events, a11y, framework_notes, css_vars.
2. **Markdown body** — LLM-native knowledge: full SCSS pattern, usage examples.

The frontmatter is consumed by Python scripts (parse/validate/plan). The body is consumed by the LLM renderer when reading the spec during `/spec-render`.

Key frontmatter fields:
- `format_version: 1` — required; bumps on any schema change
- `maps_to` discriminator (7 kinds): `data-attr`, `data-attr-token`, `aria`, `prop`, `class`, `element`, `css-var`
- `events:` array — separate from props
- `a11y.wcag` — required for interactive; `a11y.layout_only: true` exempts layout primitives
- `fpkit_source` + `fpkit_version` — full HTTPS URL + SHA/tag

Full schema: read `references/spec-format.md` before authoring or rendering.

---

## /spec-add

**Trigger:** `/spec-add <component> [--refresh]`

1. Run `python scripts/fetch_fpkit_source.py <component> [--refresh]`.
   - Fetches source from GitHub; caches under `assets/fpkit-cache/<sha>/`.
   - Returns SHA for `fpkit_version` field.
2. Read the cached source to extract props, CSS vars, data attributes, events.
3. Scaffold `specs/<component>.md` using the frontmatter shape from `references/spec-format.md`.
   - Set `format_version: 1`
   - Set `fpkit_version` to the returned SHA
   - Populate all props with correct `maps_to` kind
   - Add `a11y.wcag` for interactive components (or `a11y.layout_only: true` for layout)
4. Validate: `python scripts/validate_spec.py specs/<component>.md`
5. Inform the developer which spec file was created and prompt them to review it.

For compound components (Card, Dialog, Nav), create the root spec then sub-component specs.
Sub-component specs declare `parent: <root>` and `maps_to_parent: compound-part`.

---

## /spec-render

**Trigger:** `/spec-render <component> [--target=react|html|astro|all]`

**Canonical 3-step render flow:** `/spec-render` (write staging) → `/spec-diff` (preview) → `/spec-promote` (move to project).

### Step R1. Determine target

1. Check `--target` argument.
2. If not set, read `.acss-target.json`; use `framework` field if present.
3. If neither: render all three frameworks.

### Step R2. Plan the render

Run `python scripts/plan_render.py specs/<component>.md [--target=<target>]`.

Read the returned JSON:
- `dependency_order` — bottom-up order to emit files
- `manifest.<target>` — files to create in staging

### Step R3. Read renderer context

Lazy-load the framework reference(s):
- React: read `references/frameworks/react.md`
- HTML: read `references/frameworks/html.md`
- Astro: read `references/frameworks/astro.md`

Read the component spec: `specs/<component>.md`

For compound components, also read sibling specs (e.g. card-title.md, card-content.md, card-footer.md).

### Step R4. Emit files (bottom-up)

For each component in `dependency_order`:
- If dependency doesn't exist in staging or project: render it first.
- Generate the component file and SCSS sidecar.
- Prepend version stamp: `// generated from <component>.md@0.1.0`
- Write to `.acss-staging/<framework>/<component>/`

**Atomic failure rule:** If any framework fails, halt all and report. Never leave partial staging output.
Delete any partially-written staging files on failure.

### Step R5. Theme check

After all files are written, check if the project has an `acss-theme-builder` theme (look for `:root { --color-primary:` in any CSS/SCSS file in the project).

If not found AND `theme_dependencies` in the spec is non-empty, warn:
```
Warning: no acss-theme-builder theme detected.
Components rely on hardcoded color fallbacks. Run /theme-generate to create a theme.
```

### Step R6. Auto-gitignore

On first invocation, check if `.acss-staging/` is in the project's `.gitignore`.
If not found, prompt:
```
Add '.acss-staging/' to .gitignore? [Enter to add, Ctrl+C to skip]
```

---

## /spec-diff

**Trigger:** `/spec-diff <component> [--target=react|html|astro]`

1. Locate staging files in `.acss-staging/<framework>/<component>/`.
2. For each staging file, find the corresponding project file via `.acss-target.json` `componentsDir`.
3. If no project file exists: show full content as a new-file diff.
4. Output a unified diff block per file pair.
5. No files are written.

If no `--target`, diff all frameworks present in staging.

---

## /spec-promote

**Trigger:** `/spec-promote <component> [--target=react|html|astro|all]`

1. Read `.acss-target.json` for `componentsDir`.
2. For each file in `.acss-staging/<framework>/<component>/`:
   - Determine destination: `<componentsDir>/<component>/<filename>`
   - Move (not copy) to destination.
   - If destination exists: overwrite and note it.
3. Report promoted files and their final paths.
4. Confirm staging directory for the component is now empty.

Promotion is explicit. Always run `/spec-diff` first.

---

## /spec-validate

**Trigger:** `/spec-validate [<component>] [--stale]`

Run `python scripts/validate_spec.py [specs/<component>.md] [--stale]`.

- Without a component argument: validates all `specs/*.md`.
- Reports schema errors, missing a11y blocks, invalid WCAG SCs, format_version mismatches.
- `--stale`: scans project component files for `// generated from` stamps with versions older than the current spec.

Exit 0 = all valid. Relay validation output to the developer.

---

## /spec-list

**Trigger:** `/spec-list [<component>]`

1. Glob `specs/*.md`.
2. For each spec, run `python scripts/parse_spec.py specs/<component>.md` to extract name, format_version, fpkit_version.
3. Output a table:

```
Component       format_version  fpkit_version
-----------     ----            --------
button          1               abc1234
card            1               abc1234
dialog          1               abc1234
alert           1               abc1234
stack           1               abc1234
nav             1               abc1234
```

If a component name is given, output the full spec summary (props, events, css_vars).

Empty state (no specs):
```
No specs found. Run /spec-add <component> to scaffold your first spec.
Install hint: /plugin install acss-component-specs@acss-plugins
```

---

## Coordination with kit-builder and app-builder

### kit-builder bridge

When `/kit-add <component>` is invoked from `acss-kit-builder`:

1. Probe `$CLAUDE_PLUGIN_ROOT/../acss-component-specs/skills/acss-component-specs/specs/` for the component spec.
2. If absent, fallback to `~/.claude/plugins/cache/acss-component-specs/...`
3. If a spec is found: prefer it over the bundled kit-builder reference doc. **Spec wins.**
4. If no spec is found: fall back to bundled kit-builder references silently. No warning in v0.1.

### app-builder .acss-target.json extension

The new plugin reads `.acss-target.json` for `componentsDir` (shared with kit-builder and app-builder) and also recognizes:

```json
{
  "componentsDir": "src/components/fpkit",
  "framework": "react"
}
```

The `framework` field is optional. When set, it drives `/spec-render`'s default target. Valid values: `react`, `html`, `astro`. When unset, all three frameworks are rendered.

### theme-builder integration

Component SCSS uses `var(--color-primary, #0066cc)` patterns. When `acss-theme-builder` output is present (`:root { --color-primary: ... }`), theme values override the CSS cascade. When absent, hardcoded fallbacks apply. Component SCSS does **not** `@import` theme files — it relies on natural CSS cascade.

---

## Reference Documents (lazy-load as needed)

| Document | When to read |
|----------|--------------|
| `references/spec-format.md` | Before authoring or validating any spec |
| `references/frameworks/react.md` | When rendering to React |
| `references/frameworks/html.md` | When rendering to HTML |
| `references/frameworks/astro.md` | When rendering to Astro |
| `references/compound-components.md` | When rendering Card, Dialog, Nav |
| `references/state-and-events.md` | When rendering Dialog, Alert, interactive Card |
| `references/authoring-guide.md` | When adding a new spec for the first time |
