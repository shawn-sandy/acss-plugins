# Component: Button

## Overview

The primary interactive element. Supports size, style, and color variants via data attributes. Uses `aria-disabled` instead of native `disabled` to maintain keyboard accessibility (WCAG 2.1.1).

## Generation Contract

```
export_name: Button
file: button.tsx
scss: button.scss
imports: UI from '../ui'
dependencies: []   (useDisabledState is inlined, not a separate file)
```

## Props Interface

```tsx
export type ButtonProps = {
  /** Required — prevents implicit submit in forms */
  type: 'button' | 'submit' | 'reset'

  /** Button content */
  children?: React.ReactNode

  /** Accessible disabled — keeps element in tab order (WCAG 2.1.1) */
  disabled?: boolean

  /** Legacy compat. `disabled` takes precedence. */
  isDisabled?: boolean

  /** Maps to data-btn attribute: xs | sm | md | lg | xl | 2xl */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'

  /** Maps to data-style attribute: outline | pill | text | icon */
  variant?: 'text' | 'pill' | 'icon' | 'outline'

  /** Maps to data-color attribute: primary | secondary | danger | success | warning */
  color?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning'

  /** Stretches button to 100% width (adds 'block' to data-btn) */
  block?: boolean

  /** CSS class name via classes prop (takes precedence over className) */
  classes?: string

  /** Inline styles (passed to UI) */
  styles?: React.CSSProperties

  /** Raw data-btn tokens merged with size/block */
  'data-btn'?: string

  onClick?: React.MouseEventHandler<HTMLButtonElement>
  onKeyDown?: React.KeyboardEventHandler<HTMLButtonElement>
  onPointerDown?: React.PointerEventHandler<HTMLButtonElement>
  onPointerOver?: React.PointerEventHandler<HTMLButtonElement>
  onPointerLeave?: React.PointerEventHandler<HTMLButtonElement>
} & Omit<React.ComponentPropsWithoutRef<'button'>, 'disabled'>
```

Note: `Omit<..., 'disabled'>` removes the native disabled from button props since we handle it ourselves.

## Key Pattern: Condensed useDisabledState

Inline this condensed version (read `references/accessibility.md` for the full ~50-line version):

```tsx
// Inline in button.tsx — do not create a separate file
function useDisabledState<T extends HTMLElement = HTMLButtonElement>(
  disabled: boolean | undefined,
  handlers: {
    onClick?: (e: React.MouseEvent<T>) => void
    onKeyDown?: (e: React.KeyboardEvent<T>) => void
    onPointerDown?: (e: React.PointerEvent<T>) => void
  } = {},
  className?: string
) {
  const isDisabled = Boolean(disabled)
  const mergedClassName = [isDisabled ? 'is-disabled' : '', className]
    .filter(Boolean).join(' ')

  const wrap = <E,>(fn?: (e: E) => void) => fn
    ? (e: any) => { if (isDisabled) { e.preventDefault(); e.stopPropagation(); return } fn(e) }
    : undefined

  return {
    disabledProps: { 'aria-disabled': isDisabled, className: mergedClassName },
    handlers: {
      onClick: wrap(handlers.onClick),
      onKeyDown: wrap(handlers.onKeyDown),
      onPointerDown: wrap(handlers.onPointerDown),
    },
  }
}
```

## Key Pattern: resolveDisabledState

```tsx
// One-liner helper — inline in button.tsx
const resolveDisabledState = (d?: boolean, id?: boolean) => d ?? id ?? false
```

## Key Pattern: data-btn Merging

```tsx
// Merge size, block, and explicit data-btn into one space-separated string
const { 'data-btn': dataBtnProp, ...restProps } = props
const dataBtnValue = [size, block ? 'block' : undefined, dataBtnProp]
  .filter(Boolean).join(' ') || undefined
```

## Full Implementation Reference

```tsx
import UI from '../ui'
import React from 'react'

// [inline resolveDisabledState and useDisabledState here]

export const Button = ({
  type = 'button',
  children,
  styles,
  disabled,
  isDisabled,
  classes,
  size,
  variant,
  color,
  block,
  onPointerDown,
  onPointerOver,
  onPointerLeave,
  onClick,
  onKeyDown,
  ...props
}: ButtonProps) => {
  const isActuallyDisabled = resolveDisabledState(disabled, isDisabled)
  const { disabledProps, handlers } = useDisabledState(
    isActuallyDisabled,
    { onClick, onPointerDown, onKeyDown },
    classes,
  )

  const { 'data-btn': dataBtnProp, ...restProps } = props
  const dataBtnValue = [size, block ? 'block' : undefined, dataBtnProp]
    .filter(Boolean).join(' ') || undefined

  return (
    <UI
      as="button"
      type={type}
      data-btn={dataBtnValue}
      data-style={variant}
      data-color={color}
      aria-disabled={disabledProps['aria-disabled']}
      onPointerOver={onPointerOver}
      onPointerLeave={onPointerLeave}
      style={styles}
      className={disabledProps.className}
      {...restProps}
      {...handlers}
    >
      {children}
    </UI>
  )
}

export default Button
Button.displayName = 'Button'
```

## CSS Variables

```scss
// Size tokens
--btn-size-xs: 0.6875rem;
--btn-size-sm: 0.8125rem;
--btn-size-md: 0.9375rem;   // default
--btn-size-lg: 1.125rem;
--btn-size-xl: 1.25rem;

// Base
--btn-display: inline-flex;
--btn-align: center;
--btn-justify: center;
--btn-gap: 0.5rem;
--btn-fs: var(--btn-size-md, 0.9375rem);
--btn-fw: 500;
--btn-radius: 0.375rem;
--btn-padding-block: calc(var(--btn-fs, 0.9375rem) * 0.5);
--btn-padding-inline: calc(var(--btn-fs, 0.9375rem) * 1.5);
--btn-bg: transparent;
--btn-color: currentColor;
--btn-border: 1px solid currentColor;
--btn-cursor: pointer;
--btn-transition: all 0.2s ease-in-out;
--btn-text-decoration: none;
--btn-white-space: nowrap;

// Color: primary
--btn-primary-bg: var(--color-primary, #0066cc);
--btn-primary-color: var(--color-text-inverse, #fff);
--btn-primary-border: none;
--btn-primary-hover-bg: var(--color-primary-dark, #0052a3);

// Color: danger
--btn-danger-bg: var(--color-danger, #dc3545);
--btn-danger-color: #fff;
--btn-danger-border: none;

// States
--btn-hover-transform: translateY(-1px);
--btn-hover-filter: brightness(1.05);
--btn-focus-outline: 2px solid currentColor;
--btn-focus-outline-offset: 2px;
--btn-active-transform: translateY(0);

// Disabled
--btn-disabled-opacity: 0.6;
--btn-disabled-cursor: not-allowed;
```

## SCSS Pattern

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

  // Size variants (data-btn attribute)
  &[data-btn~="xs"] { font-size: var(--btn-size-xs, 0.6875rem); }
  &[data-btn~="sm"] { font-size: var(--btn-size-sm, 0.8125rem); }
  &[data-btn~="lg"] { font-size: var(--btn-size-lg, 1.125rem); }
  &[data-btn~="xl"] { font-size: var(--btn-size-xl, 1.25rem); }
  &[data-btn~="block"] { width: 100%; display: flex; }

  // Style variants (data-style attribute)
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

  // Color variants (data-color attribute)
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

## Usage Examples

```tsx
import Button from './button/button'
import './button/button.scss'

// Basic
<Button type="button" onClick={() => {}}>Click me</Button>

// Color variant
<Button type="button" color="primary">Primary</Button>
<Button type="button" color="danger">Delete</Button>

// Size variant
<Button type="button" size="sm">Small</Button>
<Button type="button" size="lg">Large</Button>

// Combined
<Button type="button" color="primary" size="lg" block>
  Full Width Primary
</Button>

// Accessible disabled (stays in tab order)
<Button type="button" disabled color="primary">
  Cannot click (still focusable)
</Button>

// Style variants
<Button type="button" variant="outline">Outlined</Button>
<Button type="button" variant="text">Text button</Button>
<Button type="button" variant="pill" color="primary">Pill</Button>
```
