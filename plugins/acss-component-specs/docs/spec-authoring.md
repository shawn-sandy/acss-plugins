# acss-component-specs — Authoring a Spec

This page walks through the full flow of creating a new component spec. For the authoritative schema reference, see [`references/spec-format.md`](../skills/acss-component-specs/references/spec-format.md). For the 10-step contributor walkthrough, see [`references/authoring-guide.md`](../skills/acss-component-specs/references/authoring-guide.md).

## Overview

Authoring a spec is a three-step process:

```
/spec-add <component>     # fetch source, scaffold spec
/spec-validate <component> # confirm schema is valid
/spec-render <component>  # render to staging to verify output
```

## Step 1: Scaffold with /spec-add

```
/spec-add stack
```

`/spec-add` runs `scripts/fetch_fpkit_source.py stack` to:

1. Resolve the current `main` SHA via the GitHub API.
2. Fetch the component source from `https://raw.githubusercontent.com/shawn-sandy/acss/main/packages/fpkit/src/components/stack/stack.tsx` (falling back to `<comp>s/<comp>.tsx` or `<comp>/<comp>.tsx` if the primary path fails).
3. Cache the source under `assets/fpkit-cache/<sha>/stack.tsx` (valid 7 days; `--refresh` forces re-fetch).

Claude reads the cached source, extracts the component structure, and writes `specs/stack.md` with the full frontmatter populated.

## Step 2: Understand the frontmatter schema

A spec file (`specs/<component>.md`) opens with YAML frontmatter followed by a Markdown body.

**Required frontmatter fields:**

```yaml
format_version: 1
name: stack
display_name: Stack
description: "A layout primitive that stacks children with consistent spacing."
fpkit_source: "https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/stack/stack.tsx"
fpkit_version: "abc1234"   # resolved short SHA from fetch_fpkit_source.py
a11y:
  layout_only: true        # omit wcag list for layout-only primitives
  wcag: []
```

**Props array:**

```yaml
props:
  - name: gap
    type: string
    default: "1rem"
    description: "Spacing between children"
    maps_to: css-var
    css_var: "--stack-gap"
  - name: as
    type: string
    default: "div"
    description: "HTML element to render"
    maps_to: element
```

## The 7-kind maps_to reference

Every prop must declare `maps_to`. Use this table to choose the right kind:

| Kind | When to use | Example |
|------|-------------|---------|
| `prop` | A React prop or HTML attribute passed straight through | `className`, `id`, `onClick` |
| `aria` | An ARIA attribute on the root element | `aria-label`, `aria-expanded` |
| `data-attr` | A `data-*` attribute used for styling variants | `data-color="primary"` |
| `data-attr-token` | A space-separated token inside a `data-*` attribute | `data-btn="lg"` (combines with `data-btn="block"`) |
| `element` | Determines which HTML element to render (the `as` prop) | `<UI as="nav">` |
| `class` | Adds a CSS class to the root element | `class="btn"` |
| `css-var` | A CSS custom property controlling a visual aspect | `--stack-gap` |

When a prop maps to `css-var`, include a `css_var` field naming the variable. When it maps to `data-attr` or `data-attr-token`, include a `data_attr` field naming the attribute.

## Step 3: Fill in the Markdown body

The Markdown body is the LLM renderer's knowledge base. It is not parsed structurally — write it for a developer reader. The body should include at minimum:

- The full SCSS pattern (the complete block that will be emitted, including all variants)
- A usage example for React (and HTML/Astro if they differ meaningfully)
- Any generation notes (e.g., "This component has no SCSS; it is a layout wrapper")

```markdown
## SCSS Pattern

```scss
.stack {
  display: flex;
  flex-direction: column;
  gap: var(--stack-gap, 1rem);
}
```

## Usage

```tsx
<Stack gap="2rem">
  <Card>...</Card>
  <Card>...</Card>
</Stack>
```
```

## Compound components

For components with sub-parts (Card + Card.Title + Card.Content + Card.Footer), author a parent spec and separate sub-specs:

```
specs/card.md          # parent spec; props for the Card wrapper
specs/card-title.md    # sub-spec with parent: card + maps_to_parent: compound-part
specs/card-content.md
specs/card-footer.md
```

The sub-specs use two additional frontmatter fields:

```yaml
parent: card
maps_to_parent: compound-part
```

`plan_render.py` knows about the `COMPOUND_PARTS` set and treats compound parts as output that lives *inside* the parent component file rather than in their own files. See [`references/compound-components.md`](../skills/acss-component-specs/references/compound-components.md) for the full pattern including React `Object.assign`, HTML semantic nesting, and Astro slot conventions.

## Stateful components

For components with interactive state (Dialog, Alert, interactive Card), the body should document the state management approach for each renderer. Key patterns are in [`references/state-and-events.md`](../skills/acss-component-specs/references/state-and-events.md).

The `a11y` block should list all applicable WCAG 2.2 SCs. For Dialog:

```yaml
a11y:
  wcag: ["2.1.1", "4.1.2", "2.4.3", "2.4.7", "1.3.1"]
  notes: "Use native <dialog> + showModal() for built-in focus trap and Escape key handling."
```

## Step 4: Validate

```
/spec-validate stack
```

`validate_spec.py` checks:

- Required fields are present.
- `format_version == 1`.
- `a11y.wcag` is non-empty (unless `a11y.layout_only: true`).
- All WCAG SCs are valid WCAG 2.2 identifiers.
- Every prop has `name` + `maps_to`.
- `maps_to` is one of the 7 valid kinds.
- `fpkit_source` starts with `https://`.

Exit 0 = clean. Fix any reported errors before proceeding.

## Step 5: Render to confirm output

```
/spec-render stack --target=react
/spec-diff stack
```

Review the diff. If the emitted output looks correct, you can promote or discard staging — the goal here is to confirm the spec produces sensible code before committing it.

## Versioning your spec

The `fpkit_version` field is a short SHA resolved by `fetch_fpkit_source.py`. It pins the spec to the exact fpkit commit it was authored from. When upstream fpkit changes, run `/spec-add <component> --refresh` to update the spec and re-pin to the new SHA.

`format_version` tracks the spec schema version, not the component version. It starts at `1` and bumps only when the schema itself breaks backward compatibility (a rare event managed by the plugin maintainer, not individual spec authors).
