# Framework Reference: Astro + SCSS

This document tells the renderer how to translate any acss-component-spec into an Astro component with a SCSS sidecar. The SCSS sidecar pattern is used (not inline `<style>`) for parity with the React+SCSS pipeline.

---

## Render Outputs

For each component, produce two files in `.acss-staging/astro/<component>/`:

- `<ComponentName>.astro` — Astro component (PascalCase filename)
- `<component>.scss` — SCSS sidecar (lowercase slug)

Prepend stamp comment: `---\n// generated from <component>.md@<version>` inside the frontmatter fence.
Prepend stamp comment: `/* generated from <component>.md@<version> */` in SCSS.

---

## Astro Component File Template

```astro
---
// generated from <component>.md@<version>
export interface Props {
  // Props from spec, matching React interface shape
  type?: 'button' | 'submit' | 'reset'
  children?: unknown
  disabled?: boolean
  // ... other props
  class?: string
}

const {
  type = 'button',
  disabled = false,
  class: className,
  ...rest
} = Astro.props
---

<button
  type={type}
  aria-disabled={disabled}
  class:list={['btn', className, { 'is-disabled': disabled }]}
  {...rest}
>
  <slot />
</button>

<script>
// Handle aria-disabled click prevention
document.querySelectorAll('[aria-disabled="true"]').forEach(function(el) {
  el.addEventListener('click', function(e) {
    if (el.getAttribute('aria-disabled') === 'true') {
      e.preventDefault();
      e.stopPropagation();
    }
  });
});
</script>
```

---

## Prop Mapping by `maps_to` Kind

### `prop`
Declare in `Props` interface and spread onto native element.
```astro
---
export interface Props { type?: string }
const { type = 'button' } = Astro.props
---
<button type={type}>...</button>
```

### `data-attr`
Declare in `Props`, build attribute string in frontmatter.
```astro
---
export interface Props { size?: string; block?: boolean }
const { size, block } = Astro.props
const dataBtnValue = [size, block ? 'block' : undefined].filter(Boolean).join(' ') || undefined
---
<button data-btn={dataBtnValue}>...</button>
```

### `data-attr-token`
Direct attribute from prop value.
```astro
---
export interface Props { color?: string }
const { color } = Astro.props
---
<button data-color={color}>...</button>
```

### `aria`
Map to ARIA attribute. For `disabled`, Astro renders server-side so use a `<script>` for the click-prevention side effect.
```astro
---
export interface Props { disabled?: boolean }
const { disabled = false } = Astro.props
---
<button aria-disabled={disabled} class:list={[{ 'is-disabled': disabled }]}>...</button>
```

### `class`
Use Astro's `class:list` directive for merging.
```astro
---
export interface Props { class?: string }
const { class: className } = Astro.props
---
<button class:list={['btn', className]}>...</button>
```

### `element`
Astro components use a `tag` or `as` prop. Use Astro's dynamic tag syntax.
```astro
---
const { as: Tag = 'div' } = Astro.props
---
<Tag class="card">...</Tag>
```

### `css-var`
Use `style` attribute.
```astro
---
export interface Props { styles?: Record<string, string> }
const { styles } = Astro.props
---
<button style={styles}>...</button>
```

---

## SCSS Sidecar Rationale

Astro supports inline `<style>` blocks (scoped by default) and global SCSS via `<style is:global>`. The acss-component-specs renderer uses an **external SCSS sidecar** (`button.scss` imported in the Astro page or layout) rather than an inline block. Rationale:

1. **Pipeline parity** — React and Astro renderers produce identical SCSS; only the component file differs.
2. **No scoping collision** — The data-attr selectors (`[data-btn~="sm"]`) are global by nature; Astro's scoped styles would break them.
3. **Reuse** — The same `button.scss` can be imported by the HTML renderer's demo page.

Inline `<style is:global>` support is deferred to v0.2 as an opt-in flag (`--astro-style=inline`).

To import the sidecar in an Astro page or layout:
```astro
---
import '../components/fpkit/button/button.scss'
---
```

---

## Compound Components in Astro

Astro does not support static property attachment (`Card.Title`) in the React sense. Instead, render compound sub-components as separate `.astro` files in the same directory:

```
astro/card/
  Card.astro
  CardTitle.astro
  CardContent.astro
  CardFooter.astro
  card.scss
```

Usage in consuming pages:
```astro
---
import Card from './components/fpkit/card/Card.astro'
import CardTitle from './components/fpkit/card/CardTitle.astro'
import CardContent from './components/fpkit/card/CardContent.astro'
---

<Card>
  <CardTitle>Product Name</CardTitle>
  <CardContent>
    <p>Description here.</p>
  </CardContent>
</Card>
```

---

## Slot Usage

Use `<slot />` for `children`-equivalent content. Named slots for compound children:
```astro
<!-- Card.astro -->
<div class="card">
  <slot name="title" />
  <slot />
  <slot name="footer" />
</div>
```

---

## Events in Astro

Astro components render server-side. Event handlers must use `<script>` blocks or Astro's `client:*` directives.

For interactive components, emit a client script block:
```astro
<script>
  // Event handler for <ComponentName>
  document.querySelectorAll('.btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      if (btn.getAttribute('aria-disabled') === 'true') {
        e.preventDefault(); e.stopPropagation();
      }
    });
  });
</script>
```

---

## Theme Degradation Warning

Same as React renderer: if `theme_dependencies` is non-empty and no theme is detected, prepend a comment to the SCSS file warning about hardcoded fallbacks.

---

## SCSS File

The SCSS for Astro is **identical to the React SCSS sidecar** — same file content, same naming. Copy the React SCSS output verbatim to the Astro staging directory. This is intentional: one source of CSS truth, two framework consumers.
