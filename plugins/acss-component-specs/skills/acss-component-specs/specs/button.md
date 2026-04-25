---
format_version: 1
name: button
display_name: Button
description: Primary interactive element with size, style, and color variants via data attributes. Uses polymorphic UI base.
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/buttons/btn.tsx
fpkit_version: main
component_type: interactive
a11y:
  wcag: ['2.1.1', '1.4.3', '4.1.2']
  accessible_name: children content or aria-label attribute
props:
  - name: type
    type: "'button' | 'submit' | 'reset'"
    required: true
    maps_to: prop
    description: Prevents implicit form submit
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Button label content; provides accessible name
  - name: disabled
    type: boolean
    required: false
    maps_to: aria
    aria_attr: aria-disabled
    description: Accessible disabled. Keeps element in tab order (WCAG 2.1.1). Never use native disabled.
  - name: isDisabled
    type: boolean
    required: false
    maps_to: aria
    aria_attr: aria-disabled
    description: Legacy compat. disabled takes precedence. Resolved via resolveDisabledState().
  - name: size
    type: "'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'"
    required: false
    maps_to: data-attr
    data_attr: data-btn
    description: Size token added to data-btn space-separated value
  - name: variant
    type: "'text' | 'pill' | 'icon' | 'outline'"
    required: false
    maps_to: data-attr
    data_attr: data-style
    description: Style variant via data-style attribute
  - name: color
    type: "'primary' | 'secondary' | 'danger' | 'success' | 'warning'"
    required: false
    maps_to: data-attr-token
    data_attr: data-color
    description: Color variant mapped to semantic token via data-color
  - name: block
    type: boolean
    required: false
    maps_to: data-attr
    data_attr: data-btn
    data_value: block
    description: Adds 'block' to data-btn; stretches button to 100% width
  - name: as
    type: React.ElementType
    required: false
    maps_to: element
    default: button
    description: Polymorphic element override via UI base
  - name: classes
    type: string
    required: false
    maps_to: class
    description: CSS class names (custom prop, takes precedence over className)
  - name: styles
    type: React.CSSProperties
    required: false
    maps_to: css-var
    description: Inline styles override passed to UI base
events:
  - name: onClick
    type: React.MouseEventHandler<HTMLButtonElement>
  - name: onKeyDown
    type: React.KeyboardEventHandler<HTMLButtonElement>
  - name: onPointerDown
    type: React.PointerEventHandler<HTMLButtonElement>
  - name: onPointerOver
    type: React.PointerEventHandler<HTMLButtonElement>
  - name: onPointerLeave
    type: React.PointerEventHandler<HTMLButtonElement>
framework_notes:
  react:
    strategy: Wrap UI base as button. Inline useDisabledState to convert disabled → aria-disabled and wrap event handlers. Merge size/block/data-btn into single data-btn string.
    dependencies: [ui.tsx]
    caveats: Omit native disabled from ButtonProps (Omit<ComponentPropsWithoutRef<'button'>, 'disabled'>). Use resolveDisabledState(disabled, isDisabled) to normalize both props.
  html:
    strategy: Native <button> with aria-disabled. Inline JS snippet prevents clicks when aria-disabled is true. Same SCSS data-attr selectors apply.
    dependencies: []
    caveats: Include the aria-disabled click-prevention script block. CSS is identical to React SCSS output.
  astro:
    strategy: Button.astro wraps native <button>. Props interface mirrors React. SCSS sidecar button.scss (identical to React output).
    dependencies: [button.scss]
    caveats: No useDisabledState — Astro renders server-side. Client script handles aria-disabled click prevention. Use class:list directive for class merging.
css_vars:
  - name: --btn-fs
    default: 0.9375rem
    description: Base font size (md size)
  - name: --btn-padding-block
    default: "calc(var(--btn-fs, 0.9375rem) * 0.5)"
    description: Vertical padding scales with font size
  - name: --btn-padding-inline
    default: "calc(var(--btn-fs, 0.9375rem) * 1.5)"
    description: Horizontal padding scales with font size
  - name: --btn-radius
    default: 0.375rem
    description: Border radius
  - name: --btn-bg
    default: transparent
    description: Background color
  - name: --btn-color
    default: currentColor
    description: Text color
  - name: --btn-border
    default: 1px solid currentColor
    description: Border
  - name: --btn-primary-bg
    default: "var(--color-primary, #0066cc)"
    description: Primary variant background (semantic token)
  - name: --btn-primary-color
    default: "var(--color-text-inverse, #fff)"
    description: Primary variant text (semantic token)
  - name: --btn-danger-bg
    default: "var(--color-danger, #dc3545)"
    description: Danger variant background
  - name: --btn-focus-outline
    default: 2px solid currentColor
    description: Focus-visible outline
  - name: --btn-focus-outline-offset
    default: 2px
    description: Focus-visible outline offset
  - name: --btn-disabled-opacity
    default: "0.6"
    description: Opacity when disabled
theme_dependencies: []
---

## SCSS

```scss
// button.scss
.btn {
  display: var(--btn-display, inline-flex);
  align-items: var(--btn-align, center);
  justify-content: var(--btn-justify, center);
  gap: var(--btn-gap, 0.5rem);
  font-size: var(--btn-fs, 0.9375rem);
  font-weight: var(--btn-fw, 500);
  border-radius: var(--btn-radius, 0.375rem);
  padding-block: var(--btn-padding-block, 0.46875rem);
  padding-inline: var(--btn-padding-inline, 1.40625rem);
  background: var(--btn-bg, transparent);
  color: var(--btn-color, currentColor);
  border: var(--btn-border, 1px solid currentColor);
  cursor: var(--btn-cursor, pointer);
  transition: var(--btn-transition, all 0.2s ease-in-out);
  text-decoration: none;
  white-space: nowrap;
  line-height: 1;

  &:hover {
    transform: var(--btn-hover-transform, translateY(-1px));
    filter: var(--btn-hover-filter, brightness(1.05));
  }

  &:focus-visible {
    outline: var(--btn-focus-outline, 2px solid currentColor);
    outline-offset: var(--btn-focus-outline-offset, 2px);
  }

  &:active {
    transform: var(--btn-active-transform, translateY(0));
  }

  &[aria-disabled="true"],
  &.is-disabled {
    opacity: var(--btn-disabled-opacity, 0.6);
    cursor: var(--btn-disabled-cursor, not-allowed);
    pointer-events: none;
  }

  // Size variants (data-btn space-separated token)
  &[data-btn~="xs"] { font-size: var(--btn-size-xs, 0.6875rem); }
  &[data-btn~="sm"] { font-size: var(--btn-size-sm, 0.8125rem); }
  &[data-btn~="lg"] { font-size: var(--btn-size-lg, 1.125rem); }
  &[data-btn~="xl"] { font-size: var(--btn-size-xl, 1.25rem); }
  &[data-btn~="block"] { width: 100%; display: flex; }

  // Style variants (data-style exact match)
  &[data-style="outline"] {
    background: transparent;
    border: 1px solid currentColor;
    color: currentColor;
  }

  &[data-style="text"] {
    background: transparent;
    border: none;
    &:hover { text-decoration: underline; }
  }

  &[data-style="pill"] {
    border-radius: 999px;
  }

  &[data-style="icon"] {
    padding: var(--btn-icon-padding, 0.5rem);
    border-radius: var(--btn-icon-radius, 50%);
    border: none;
    background: transparent;
  }

  // Color variants (data-color exact match — semantic token)
  &[data-color="primary"] {
    background: var(--btn-primary-bg, var(--color-primary, #0066cc));
    color: var(--btn-primary-color, var(--color-text-inverse, #fff));
    border: var(--btn-primary-border, none);
    &:hover { background: var(--btn-primary-hover-bg, var(--color-primary-dark, #0052a3)); }
  }

  &[data-color="danger"] {
    background: var(--btn-danger-bg, var(--color-danger, #dc3545));
    color: var(--btn-danger-color, #fff);
    border: none;
  }

  &[data-color="success"] {
    background: var(--btn-success-bg, var(--color-success, #28a745));
    color: var(--btn-success-color, #fff);
    border: none;
  }
}
```

## Usage

```tsx
import Button from './button/button'
import './button/button.scss'

// Basic
<Button type="button" onClick={() => {}}>Click me</Button>

// Color variants
<Button type="button" color="primary">Primary</Button>
<Button type="button" color="danger">Delete</Button>

// Size variants
<Button type="button" size="sm">Small</Button>
<Button type="button" size="lg">Large</Button>

// Block (full width)
<Button type="button" color="primary" size="lg" block>Full Width</Button>

// Accessible disabled (stays in tab order, WCAG 2.1.1)
<Button type="button" disabled color="primary">Cannot click (still focusable)</Button>

// Style variants
<Button type="button" variant="outline">Outlined</Button>
<Button type="button" variant="text">Text</Button>
<Button type="button" variant="pill" color="primary">Pill</Button>
```
