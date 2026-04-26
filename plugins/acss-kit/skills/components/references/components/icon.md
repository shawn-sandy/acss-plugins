# Component: Icon

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). **Intentional divergence**: upstream Icon is a polymorphic span wrapper that hosts externally-imported icon components as static properties (`Icon.Add`, `Icon.ArrowDown`, etc.), pulling in 30+ separate icon files. The vendored Icon is a `name`-prop dispatcher with a small built-in SVG set (info, success, warning, error, close, chevron-down, chevron-right, check, external-link). Self-contained, much smaller, and covers the icons the rest of the kit-builder components depend on. If a project needs the larger fpkit icon library, it can extend the `ICON_SVGS` map locally.

## Overview

A lightweight inline-SVG icon component. Each icon is rendered as a `<svg>` inside the Icon component, sized via `size` prop, colored via `color` (default `currentColor`), and accessible-named via `aria-hidden` (decorative) or `aria-label` (standalone).

## Generation Contract

```
export_name: Icon
file: icon.tsx
scss: (none — Icon styles via props/className; no separate SCSS file)
imports: React (only)
dependencies: []
```

Icon has no SCSS file. Sizing and color come through props or via `currentColor` from the parent context.

## Props Interface

```tsx
export type IconName =
  | 'info'
  | 'success'
  | 'warning'
  | 'error'
  | 'close'
  | 'chevron-down'
  | 'chevron-right'
  | 'check'
  | 'external-link'

export type IconProps = {
  /** Icon name from the built-in set */
  name: IconName
  /** SVG width/height in pixels (default: 16) */
  size?: number
  /** Stroke / fill color (default: currentColor) */
  color?: string
  /** Decorative icon — true means screen readers skip it (default: true) */
  'aria-hidden'?: boolean
  /** Required for non-decorative standalone icons */
  'aria-label'?: string
} & Omit<React.SVGProps<SVGSVGElement>, 'aria-hidden' | 'aria-label'>
```

## TSX Template

```tsx
import React from 'react'

export type IconName =
  | 'info'
  | 'success'
  | 'warning'
  | 'error'
  | 'close'
  | 'chevron-down'
  | 'chevron-right'
  | 'check'
  | 'external-link'

export type IconProps = {
  name: IconName
  size?: number
  color?: string
  'aria-hidden'?: boolean
  'aria-label'?: string
} & Omit<React.SVGProps<SVGSVGElement>, 'aria-hidden' | 'aria-label'>

const ICON_PATHS: Record<IconName, React.ReactNode> = {
  info: (
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
  ),
  success: (
    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
  ),
  warning: (
    <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
  ),
  error: (
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
  ),
  close: (
    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
  ),
  'chevron-down': (
    <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z" />
  ),
  'chevron-right': (
    <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6z" />
  ),
  check: (
    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
  ),
  'external-link': (
    <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z" />
  ),
}

export const Icon = ({
  name,
  size = 16,
  color = 'currentColor',
  'aria-hidden': ariaHidden = true,
  'aria-label': ariaLabel,
  ...props
}: IconProps) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill={color}
    aria-hidden={ariaLabel ? undefined : ariaHidden}
    aria-label={ariaLabel}
    role={ariaLabel ? 'img' : undefined}
    {...props}
  >
    {ICON_PATHS[name]}
  </svg>
)

Icon.displayName = 'Icon'
export default Icon
```

## CSS Variables

(None — Icon doesn't have a dedicated SCSS file. Color comes from `currentColor` by default and can be overridden via the `color` prop. Size comes from the `size` prop in pixels. If you need theme-driven sizing, set `--icon-size` in your theme and pass `size={parseInt(getComputedStyle(...).getPropertyValue('--icon-size'))}` — but typically the prop is fine.)

## Accessibility

WCAG 2.2 AA compliance for the generated `Icon` component.

**Decorative vs informative**
- **Decorative** (default): `aria-hidden="true"` so screen readers skip the SVG entirely. Use for icons that accompany visible text — the text already conveys the meaning. Example: an info icon next to "Tip: ..." text.
- **Informative / standalone**: pass `aria-label="..."` to give the icon an accessible name, and the component automatically swaps `aria-hidden` for `role="img"`. Use for icons that carry meaning by themselves, like a trash icon with no adjacent label.
- Never both: if `aria-label` is passed, the component drops `aria-hidden` so the label is read.

**Color contrast**
- Default `color="currentColor"` inherits the parent's text color. Pair with the surrounding text contrast — same 4.5:1 / 3:1 rules apply.
- For purely-graphical icons (chevron, close, external-link), 3:1 against the surrounding background is sufficient (WCAG 1.4.11 Non-text Contrast).
- For icons that convey state (success/warning/error), the icon's color carries information — but color must NOT be the only indicator. Always pair with text or a different shape (WCAG 1.4.1 Use of Color).

**Size policy**
- Default `size={16}` is suitable for inline-with-text usage (next to a label).
- For touch targets where the icon is the *only* clickable area, the surrounding interactive element must meet WCAG 2.5.8 (44 px minimum). Don't rely on a 16 px icon as a touch target; wrap it in `IconButton` or `Button`.

**Built-in icon set**
- The 9 built-in icons (info, success, warning, error, close, chevron-down, chevron-right, check, external-link) cover the icons the rest of the kit-builder components consume internally (Alert, Dialog close button, Details collapse marker, etc.). They're not exhaustive — if a project needs more icons, add them to `ICON_PATHS` locally.
- The vendored set deliberately doesn't include the larger fpkit icon library to keep the dependency footprint small.

**WCAG 2.2 AA criteria addressed**
- 1.1.1 Non-text Content (decorative `aria-hidden` or informative `aria-label` + `role="img"`)
- 1.4.1 Use of Color (icon color is supplementary; don't use color alone)
- 1.4.11 Non-text Contrast (icon glyph at 3:1)

## Usage Examples

```tsx
import Icon from './icon/icon'

// Decorative — screen readers skip
<Icon name="info" aria-hidden size={16} />

// Inside a label that already carries meaning
<button type="button">
  <Icon name="check" aria-hidden /> Save
</button>

// Standalone — needs accessible name
<button type="button" aria-label="Close dialog">
  <Icon name="close" aria-hidden size={20} />
</button>

// Or label the icon directly when there's no surrounding interactive element
<Icon name="warning" aria-label="Warning" size={24} color="var(--color-warning)" />

// Inline with custom color
<Icon name="external-link" aria-hidden size={12} color="var(--color-primary)" />
```
