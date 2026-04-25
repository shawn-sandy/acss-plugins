# Authoring Guide — Adding a New Component Spec

End-to-end walkthrough for contributors adding a new component spec to acss-component-specs.

---

## Prerequisites

- Plugin installed: `acss-component-specs` visible in Claude Code
- At least one existing spec to reference (e.g. `specs/button.md`)
- Local sibling clone of fpkit at `~/devbox/acss/packages/fpkit/` (for local verification)

---

## Step 1: Fetch the fpkit Source

```bash
# In a project with the plugin installed:
python scripts/fetch_fpkit_source.py <component>
```

This caches the source under `assets/fpkit-cache/<sha>/<component>.tsx` and returns the SHA to use in `fpkit_version`.

Use `--refresh` to force a new fetch even if a cached version exists.

---

## Step 2: Create the Spec File

Run `/spec-add <component>` to scaffold the spec, or copy an existing spec as a starting point.

The spec lives at `specs/<component>.md`. Frontmatter must include all required fields from `references/spec-format.md`.

### Minimal valid spec template

```markdown
---
format_version: 1
name: <slug>
display_name: <PascalCase>
description: One-line description
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/<path>.tsx
fpkit_version: <sha-from-fetch>
component_type: interactive   # or layout
a11y:
  wcag: ['2.1.1']             # required for interactive; use layout_only: true for layout
props:
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Component content
events: []
framework_notes:
  react:
    strategy: ""
    dependencies: []
    caveats: ""
  html:
    strategy: ""
    dependencies: []
    caveats: ""
  astro:
    strategy: ""
    dependencies: []
    caveats: ""
css_vars: []
theme_dependencies: []
---

## SCSS

```scss
/* Component SCSS — write the full SCSS pattern here */
```

## Usage

```tsx
/* Usage examples */
```
```

---

## Step 3: Fill in the Props

For each prop in the fpkit component's TypeScript interface:

1. Determine the `maps_to` kind (see `references/spec-format.md` for the 7-kind table)
2. Add the prop entry with `name`, `type`, `required`, `maps_to`, and `description`
3. For `data-attr` props, add `data_attr` and optionally `data_value`
4. For `aria` props, add `aria_attr`

Move event handler props (`onClick`, `onKeyDown`, etc.) to the `events:` array.

---

## Step 4: Document the SCSS

Add the complete SCSS pattern in the `## SCSS` body section.

Include all CSS custom properties following the naming convention:
- `--<component>-<property>` (e.g. `--btn-fs`)
- `--<component>-<variant>-<property>` (e.g. `--btn-primary-bg`)
- Always use `var(--<component>-<prop>, var(--color-<token>, #hardcoded))` for color tokens

`parse_spec.py` auto-derives `theme_dependencies` by scanning the SCSS section for `var(--color-*, ...)` patterns. Do not populate `theme_dependencies` by hand.

---

## Step 5: Fill in framework_notes

For each framework (`react`, `html`, `astro`), provide:
- `strategy`: One sentence describing how this component is rendered
- `dependencies`: List of files/packages the renderer needs
- `caveats`: Any framework-specific gotchas (empty string if none)

The renderer reads `strategy` for prose context and extracts `dependencies` for import generation.

---

## Step 6: Validate

```bash
python scripts/validate_spec.py specs/<component>.md
```

Common errors:
- Missing `a11y.wcag` for interactive components — add at least one WCAG SC
- Invalid WCAG SC (e.g. `9.9.9`) — check https://www.w3.org/TR/WCAG22/
- Unknown `maps_to` kind — must be one of 7 documented kinds
- `fpkit_source` not starting with `https://` — use full GitHub URL

---

## Step 7: De-risk Render (first new component)

For the first render of a new component, test against all three targets before authoring additional specs:

```
/spec-render <component> --target=react
/spec-diff <component> --target=react
```

Review the output. If the frontmatter alone produces good code, the format is working. If the body prose (SCSS section) is load-bearing, ensure it's complete.

---

## Step 8: Render and Review

```
/spec-render <component>            # renders to .acss-staging/
/spec-diff <component>              # review diffs
/spec-promote <component>           # move to project
```

---

## Step 9: Verify Kit-Builder Parity (if applicable)

If the component also exists in kit-builder:

```bash
python scripts/check_kitbuilder_parity.py <component>
```

Exit 0 = parity confirmed. Exit 1 = SCSS drift (investigate before promoting).

---

## Step 10: Commit the Spec

Add the spec file to version control:

```bash
git add specs/<component>.md
git commit -m "feat(specs): add <component> spec (format_version 1)"
```

The pre-commit hook will run `check_kitbuilder_parity.py` automatically for any modified spec that has a kit-builder counterpart.

---

## Compound Component Authoring

For compound components (Card, Dialog, Nav), create the root spec first, then the sub-component specs:

```bash
/spec-add card       # creates specs/card.md
/spec-add card-title # creates specs/card-title.md
```

Sub-component specs should reference their parent via:
```yaml
parent: card
maps_to_parent: compound-part
```

Sub-components are emitted inside the root component file (React) or as sibling files (Astro).

---

## Naming Conventions

- Spec filenames: `<component>.md` (lowercase slug, hyphens for compound parts)
- Compound sub-components: `<parent>-<part>.md` (e.g. `card-title.md`, not `card.title.md`)
- CSS class names: `.card-title` (hyphen separator, not `.card__title` or `.cardTitle`)
- SCSS variable names: `--<component>-<property>` (see kit-builder `references/css-variables.md`)

---

## Checklist Before PR

- [ ] `format_version: 1` declared
- [ ] `fpkit_source` is a valid HTTPS GitHub URL
- [ ] `fpkit_version` is a real SHA (not just `main`) for production specs
- [ ] `a11y.wcag` is non-empty for interactive components (or `layout_only: true` set)
- [ ] All WCAG SCs are valid 2.2 identifiers
- [ ] All `maps_to` values are from the 7-kind set
- [ ] `## SCSS` body section is present with full CSS custom properties
- [ ] `python scripts/validate_spec.py specs/<component>.md` exits 0
- [ ] `/spec-render <component>` produces valid code for at least one target
- [ ] `check_kitbuilder_parity.py` exits 0 (if kit-builder counterpart exists)
