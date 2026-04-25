# Framework Reference: HTML + CSS

This document tells the renderer how to translate any acss-component-spec into static HTML snippets with a CSS sidecar. Native HTML elements are always preferred over JavaScript shims.

---

## Render Outputs

For each component, produce two files in `.acss-staging/html/<component>/`:

- `<component>.html` — HTML snippet (no doctype; embeddable fragment)
- `<component>.css` — CSS sidecar with CSS custom properties

Prepend stamp comment: `<!-- generated from <component>.md@<version> -->` in HTML.
Prepend stamp comment: `/* generated from <component>.md@<version> */` in CSS.

---

## Native Element Catalog

Prefer native HTML elements and attributes before reaching for JavaScript shims.

| Pattern | Native element / attribute | Notes |
|---------|---------------------------|-------|
| Modal dialog with focus trap | `<dialog>` + `showModal()` | Built-in focus trap and `::backdrop` |
| Dismissable non-modal dialog | `<dialog open>` | No focus trap |
| Disclosure widget | `<details>` + `<summary>` | Built-in open/close, no JS needed |
| Popover | `popover` attribute + `popovertarget` | Chrome 114+, progressive enhancement |
| Progress indicator | `<progress value="n" max="100">` | Native semantics |
| Meter / gauge | `<meter value="n" min="0" max="100">` | Native semantics |
| Navigation landmark | `<nav>` | No role="navigation" override needed |
| Button action | `<button type="button">` | Never `<div role="button">` |
| Form toggle | `<input type="checkbox">` or `<button aria-pressed>` | Depends on state model |
| Accordion | `<details>` | Before reaching for JS-driven expand/collapse |

For focus trapping: `<dialog>` via `showModal()` traps focus automatically — no `focus-trap` package needed.

When no native element covers the pattern, emit a JS script block with a comment explaining why the native path was exhausted.

---

## Prop Mapping by `maps_to` Kind

### `prop`
Becomes an HTML attribute.
```html
<!-- maps_to: prop, name: type -->
<button type="button">...</button>
```

### `data-attr`
Becomes a `data-*` attribute with space-separated tokens.
```html
<!-- maps_to: data-attr, data_attr: data-btn, name: size -->
<button data-btn="sm">...</button>
<button data-btn="lg block">...</button>
```

### `data-attr-token`
Becomes a `data-*` attribute with exact value.
```html
<!-- maps_to: data-attr-token, data_attr: data-color, name: color -->
<button data-color="primary">...</button>
```

### `aria`
Becomes an ARIA attribute.
```html
<!-- maps_to: aria, aria_attr: aria-disabled -->
<button aria-disabled="true">...</button>
```

Include a minimal JS snippet to prevent action when `aria-disabled` is true:
```html
<script>
document.querySelectorAll('[aria-disabled="true"]').forEach(function(el) {
  el.addEventListener('click', function(e) { e.preventDefault(); e.stopPropagation(); });
});
</script>
```

### `class`
Becomes a `class` attribute.
```html
<button class="btn my-custom-class">...</button>
```

### `element`
Determines the rendered HTML element.
```html
<!-- maps_to: element, default: button -->
<button>...</button>
<!-- When as="a": -->
<a role="button">...</a>
```

### `css-var`
Becomes an inline `style` attribute.
```html
<button style="--btn-fs: 1.2rem;">...</button>
```

---

## HTML Snippet Structure

```html
<!-- generated from <component>.md@<version> -->
<!-- <ComponentName> — usage: copy this snippet into your project -->

<button
  type="button"
  class="btn"
  aria-label="Button label"
>
  Button text
</button>
```

For compound components (Card, Dialog, Nav), emit the full compound structure:

```html
<!-- Card compound -->
<article class="card" aria-labelledby="card-title-1">
  <h3 class="card-title" id="card-title-1">Card Title</h3>
  <div class="card-content">
    <p>Card content here.</p>
  </div>
  <div class="card-footer">
    <!-- footer actions -->
  </div>
</article>
```

---

## CSS File Template

```css
/* generated from <component>.md@<version> */
/* <ComponentName> component — CSS custom properties with fallback defaults */

.<component> {
  /* All values in rem */
  /* Every var() has a hardcoded fallback */
  /* Global semantic tokens use double-fallback:
     var(--<component>-<prop>, var(--color-<token>, #hardcoded)) */
}

/* Data attribute variants */
.<component>[data-<name>~="<value>"] { ... }

/* Focus visible */
.<component>:focus-visible {
  outline: var(--<component>-focus-outline, 2px solid currentColor);
  outline-offset: var(--<component>-focus-outline-offset, 2px);
}

/* Disabled */
.<component>[aria-disabled="true"],
.<component>.is-disabled {
  opacity: var(--<component>-disabled-opacity, 0.6);
  cursor: var(--<component>-disabled-cursor, not-allowed);
  pointer-events: none;
}
```

---

## Dialog — Native `<dialog>` Pattern

For the Dialog spec, always use native `<dialog>` (no JS shim):

```html
<!-- Dialog snippet -->
<button type="button" id="open-dialog-btn" onclick="document.getElementById('my-dialog').showModal()">
  Open Dialog
</button>

<dialog id="my-dialog" class="dialog" aria-labelledby="dialog-title-1">
  <div class="dialog-header">
    <h2 class="dialog-title" id="dialog-title-1">Dialog Title</h2>
    <button type="button" class="btn dialog-close" aria-label="Close dialog"
            onclick="document.getElementById('my-dialog').close()">×</button>
  </div>
  <div class="dialog-body">
    <p>Dialog content here.</p>
  </div>
  <div class="dialog-footer">
    <button type="button" class="btn" onclick="document.getElementById('my-dialog').close()">Cancel</button>
    <button type="button" class="btn" data-color="primary">Confirm</button>
  </div>
</dialog>

<script>
// Backdrop click closes dialog
document.getElementById('my-dialog').addEventListener('click', function(e) {
  if (e.target === e.currentTarget) e.currentTarget.close();
});
</script>
```

The `<dialog>` element provides:
- Automatic focus trapping via `showModal()`
- Escape key fires `cancel` event → `close()`
- `::backdrop` pseudo-element for overlay
- `aria-modal` semantics built in

---

## Details/Summary — Disclosure Pattern

For collapsible/accordion patterns, use native `<details>`:

```html
<details class="disclosure">
  <summary class="disclosure-trigger">Section title</summary>
  <div class="disclosure-content">
    <p>Content here.</p>
  </div>
</details>
```

No JavaScript needed. CSS transitions on `[open]` state:
```css
details.disclosure[open] .disclosure-content {
  animation: var(--disclosure-open-animation, slideDown 0.2s ease);
}
```

---

## Theme Degradation Warning

Same as React renderer: if `theme_dependencies` is non-empty and no theme is detected, prepend a comment to the CSS file warning about hardcoded fallbacks.

---

## Accessibility in HTML Output

For interactive HTML components:

- Use semantic elements (`<button>`, `<nav>`, `<dialog>`) — never `<div role="button">`
- Include `aria-label` placeholder when accessible name comes from attribute (not text content)
- Include `aria-labelledby` + matching `id` for compound components (Card, Dialog)
- `aria-disabled="true"` instead of native `disabled` for the JS-handled disabled pattern
- Include a `<script>` block for the `aria-disabled` click-prevention when applicable (the script is minimal and inlineable)
