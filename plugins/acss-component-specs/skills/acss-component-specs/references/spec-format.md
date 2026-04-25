# Spec Format Reference — acss-component-specs v0.1

Every component spec is a Markdown file with YAML frontmatter. The body contains LLM-native prose sections including the SCSS pattern and usage examples. The frontmatter is the machine-readable contract; the body is the renderer's knowledge base.

---

## Top-Level Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `format_version` | integer | Always `1` for v0.1 specs. **Any schema change bumps this.** |
| `name` | string | Lowercase slug (e.g. `button`, `card-title`) |
| `display_name` | string | PascalCase component name (e.g. `Button`, `Card.Title`) |
| `description` | string | One-line description of the component |
| `fpkit_source` | string | Full HTTPS GitHub URL to fpkit source (must use `main` ref) |
| `fpkit_version` | string | SHA or release tag this spec was authored against |
| `a11y` | mapping | Accessibility block — see below |

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `component_type` | string | `interactive` or `layout` — affects a11y validation |
| `props` | list | Prop descriptors — see below |
| `events` | list | Event handler descriptors |
| `framework_notes` | mapping | Per-framework `{strategy, dependencies, caveats}` |
| `css_vars` | list | CSS custom property descriptors |
| `theme_dependencies` | list | Auto-derived by `parse_spec.py`; do not edit by hand |

---

## The `maps_to` Discriminator (7 kinds)

Every prop entry must declare a `maps_to` that tells the renderer how to wire it to each framework target.

| Kind | When to use | Example prop |
|------|-------------|--------------|
| `data-attr` | Prop maps to a `data-*` attribute value (space token) | `size` → `data-btn~="sm"` |
| `data-attr-token` | Prop maps to a semantic token via `data-*` attribute | `color` → `data-color="primary"` |
| `aria` | Prop maps to an ARIA attribute | `disabled` → `aria-disabled` |
| `prop` | Prop is passed directly to the underlying element | `type` → `type="button"` |
| `class` | Prop maps to a CSS class (the `classes` custom prop) | `classes` → `className` |
| `element` | Prop changes the rendered HTML element (polymorphic `as`) | `as` → `React.ElementType` |
| `css-var` | Prop maps to inline CSS variable overrides | `styles` → `style={{...}}` |

Events are **not** included in `props` — they use the separate `events:` array.

---

## `props` Entry Shape

```yaml
props:
  - name: size
    type: "'xs' | 'sm' | 'md' | 'lg' | 'xl'"
    required: false
    maps_to: data-attr
    data_attr: data-btn
    description: Size token added to data-btn space-separated list
```

For `aria` kind, add `aria_attr`:
```yaml
  - name: disabled
    type: boolean
    required: false
    maps_to: aria
    aria_attr: aria-disabled
    description: Accessible disabled (keeps element in tab order, WCAG 2.1.1)
```

For `element` kind, add `default`:
```yaml
  - name: as
    type: React.ElementType
    required: false
    maps_to: element
    default: button
    description: Polymorphic element override
```

---

## `events` Array

Events are separate from props. They do not use `maps_to`.

```yaml
events:
  - name: onClick
    type: React.MouseEventHandler
  - name: onKeyDown
    type: React.KeyboardEventHandler
```

---

## `a11y` Block

Required for all interactive components. Exempt layout-only primitives with `layout_only: true`.

```yaml
a11y:
  wcag: ['2.1.1', '1.4.3', '4.1.2']    # non-empty for interactive components
  accessible_name: children or aria-label # how the component gets its accessible name
  described_by: description prop          # logical reference — not a DOM id
```

### `layout_only` exemption

```yaml
a11y:
  layout_only: true
```

When `layout_only: true` is set:
- `validate_spec.py` skips the WCAG requirement check.
- No `wcag` array is required.
- Renderers do not emit ARIA landmark roles automatically.

### `described_by` semantic

`described_by` is a **logical reference** to another field's role — not a DOM id. Renderers interpret it per framework convention. For example, a Dialog spec setting `described_by: description prop` tells the React renderer to wire `aria-describedby` to a generated description element id; the HTML renderer adds the same via `aria-describedby` on the native `<dialog>` element.

---

## `framework_notes` Nested Schema

```yaml
framework_notes:
  react:
    strategy: "Use UI base with aria-disabled pattern"
    dependencies: [ui.tsx, useDisabledState inline]
    caveats: "Omit native disabled from ButtonProps"
  html:
    strategy: "Native <button> with aria-disabled"
    dependencies: []
    caveats: "No framework dependencies"
  astro:
    strategy: "Astro component wrapping native button"
    dependencies: [button.scss]
    caveats: "No useDisabledState — JS snippet handles on client"
```

Renderers extract `dependencies` for import generation and `strategy` for prose context.

---

## `fpkit_source` + `fpkit_version` Pinning

Both fields are required. `fpkit_source` is the canonical file URL using the `main` ref — it must start with `https://`.

```yaml
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/buttons/btn.tsx
fpkit_version: main
```

After running `fetch_fpkit_source.py`, replace `main` with the resolved short SHA:

```yaml
fpkit_version: abc1234
```

`validate_spec.py --stale` greps project files for `// generated from button.md@abc1234` stamps and flags mismatches against the spec's current version.

---

## `theme_dependencies` (auto-derived)

Do not edit this field by hand. `parse_spec.py` populates it by scanning the spec body for `var(--color-*, ...)` patterns. The validator checks that every `--color-*` reference resolves to a token that `acss-theme-builder` is known to emit.

```yaml
theme_dependencies: []   # populated by parse_spec.py
```

---

## `format_version` and the Strict-Bump Policy

Every spec must declare `format_version: 1`. **Any schema change that would break existing specs bumps the version.** Additive changes (new optional field) increment by 1; breaking changes (removing a field, changing a type) require a migration plan.

v0.1 ships `format_version: 1`. Spec migration tooling (`/spec-migrate`) lands in v0.2.

---

## Version Stamps in Generated Files

Every renderer must prepend a stamp to generated files:

```tsx
// generated from button.md@0.1.0
```

This is both human-readable and machine-parseable by `validate_spec.py --stale`.

---

## Full Button Spec Example (frontmatter only)

```yaml
---
format_version: 1
name: button
display_name: Button
description: Primary interactive element with size/style/color variants via data attributes
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/buttons/btn.tsx
fpkit_version: main
component_type: interactive
a11y:
  wcag: ['2.1.1', '1.4.3', '4.1.2']
  accessible_name: children content or aria-label
props:
  - name: type
    type: "'button' | 'submit' | 'reset'"
    required: true
    maps_to: prop
    description: Prevents implicit form submit
  - name: disabled
    type: boolean
    required: false
    maps_to: aria
    aria_attr: aria-disabled
events:
  - name: onClick
    type: React.MouseEventHandler
framework_notes:
  react:
    strategy: Use UI base with useDisabledState inline
    dependencies: [ui.tsx]
    caveats: Omit native disabled from ButtonProps
  html:
    strategy: Native <button> with aria-disabled
    dependencies: []
    caveats: ""
  astro:
    strategy: Button.astro wrapping native button; SCSS sidecar
    dependencies: [button.scss]
    caveats: ""
theme_dependencies: []
---
```
