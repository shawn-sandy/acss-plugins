# acss-component-specs — Core Concepts

This page covers the mental model you need before working with `acss-component-specs`. Understanding these ideas helps you reason about what specs are, how rendering works, and where things can go wrong.

## The problem this plugin solves

`acss-kit-builder` generates React-only output using bundled reference docs. Teams working with HTML-first or Astro-based projects had no authoritative source of truth. This plugin adds a layer above kit-builder: a single YAML+Markdown spec per component that produces valid React+SCSS, HTML+CSS, *or* Astro+SCSS output — authored once.

Do not use this plugin for pure React-only projects that are already satisfied with kit-builder's output. The extra abstraction is warranted only when you need multi-framework output or want a formal schema that survives framework migrations.

## Specs as source of truth

A spec is a single `.md` file with two parts:

- **YAML frontmatter** — the machine-readable contract. Declares props, events, accessibility requirements, CSS variables, and framework-specific notes. The Python scripts and the LLM renderer both consume this.
- **Markdown body** — the LLM's knowledge base. Contains the complete SCSS pattern, usage examples, and any prose notes that don't fit a structured field.

Generated files are stamped `// generated from button.md@0.1.0`. The spec version is the authority; generated files are derivatives.

## The 7-kind maps_to discriminator

Every prop in the spec frontmatter declares how it maps to the rendered output via a `maps_to` field. There are exactly 7 kinds:

| Kind | What it produces in the output |
|------|-------------------------------|
| `prop` | A React prop or HTML attribute passed through directly |
| `aria` | An ARIA attribute (`aria-label`, `aria-disabled`, etc.) |
| `data-attr` | A `data-*` attribute on the root element |
| `data-attr-token` | A space-separated token inside a `data-*` attribute (for `[attr~="value"]` selectors) |
| `element` | Determines which HTML element to render |
| `class` | Adds a class to the element |
| `css-var` | A CSS custom property that controls a visual aspect |

This table is the discriminator for all three renderers. The React renderer maps `aria` → `aria-*` React prop; the HTML renderer maps `aria` → the same attribute on the element; the Astro renderer maps it to a prop.

See [`references/spec-format.md`](../skills/acss-component-specs/references/spec-format.md) for the full schema including the `framework_notes` shape, `fpkit_source` / `fpkit_version` pinning, and the `format_version` strict-bump policy.

## The a11y block

Every spec must include an `a11y` block declaring the WCAG 2.2 success criteria the component addresses. The `validate_spec.py` script checks that all listed SCs are valid WCAG 2.2 identifiers and that the list is non-empty — unless `a11y.layout_only: true` is set, which exempts layout primitives like Stack.

The a11y block also carries per-target notes (e.g., which ARIA roles to use in HTML vs React) and the `wcag` list of applicable SCs.

## The 3-step render flow

Rendering is always a staged, explicit three-step process:

```
/spec-render <component> [--target=react|html|astro|all]
/spec-diff <component>
/spec-promote <component>
```

`/spec-render` writes to `.acss-staging/<framework>/`. It never touches your project files. `/spec-diff` shows a unified diff between staging and your project. `/spec-promote` moves staged files to their final destination under `componentsDir`.

**Promotion is never automatic.** The `/spec-diff` step is intentional: you review before committing changes to your project. Always run `/spec-diff` before `/spec-promote`.

## Atomic failure

If a render fails partway through (e.g., a dependency spec is missing or a script exits 1), all staged output for that invocation is rolled back. Staging is all-or-nothing — a partial staging directory is never left behind.

## Version stamps

Every generated file carries a version stamp on the first line:

```tsx
// generated from button.md@0.1.0
```

Run `/spec-validate --stale` to find project files whose stamps are behind the current spec version. This is the mechanism for tracking which project files need to be re-rendered after a spec update.

## Spec wins over kit-builder

When both `acss-component-specs` and `acss-kit-builder` are installed, kit-builder probes for a spec file before falling back to its bundled reference doc. If a spec exists, it takes precedence. No configuration is required — this is a passive upgrade. Kit-builder's bundled reference docs carry a "Legacy reference" banner to signal this relationship.

## Passive theme integration

Generated SCSS uses CSS custom properties with multi-level fallbacks:

```scss
background: var(--btn-primary-bg, var(--color-primary, #0066cc));
```

When `acss-theme-builder` output is present in your project (a `:root { --color-primary: … }` block), theme values propagate via the CSS cascade — no `@import` is needed. When no theme is found, hardcoded fallbacks apply and `/spec-render` warns you. The warning is informational; components are functional either way.

## .acss-target.json — project config

This file (written to the project root on first `/kit-add` or `/spec-render`) is the shared configuration between `acss-component-specs`, `acss-kit-builder`, and `acss-app-builder`:

```json
{
  "componentsDir": "src/components/fpkit",
  "framework": "react"
}
```

The optional `framework` field sets the default render target for `/spec-render` — without it, all three targets are rendered. Override per-invocation with `--target`. Commit this file to git.
