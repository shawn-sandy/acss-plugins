# Component: Link

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). Vendored Link preserves the upstream automatic-security behavior for `target="_blank"` (merging `noopener noreferrer` with any user-provided `rel` tokens) and the optional `prefetch` hint. **Intentional simplification**: the upstream `IconLink` and `LinkButton` compound subcomponents are dropped from the default vendoring — they're trivial enough to add inline if needed (each is ~5 lines), and most consumers want one or the other but rarely both.

## Overview

A semantic anchor wrapper with automatic security defaults for external links. Renders a native `<a>` via the polymorphic `UI` component. When `target="_blank"` is set, the component automatically merges `rel="noopener noreferrer"` with any user-provided rel tokens, preventing window.opener exploitation and referrer-header leakage. Supports an optional `prefetch` hint for faster navigation.

## Generation Contract

```
export_name: Link
file: link.tsx
scss: link.scss
imports: UI from '../ui'
dependencies: []
```

## Props Interface

```tsx
export type LinkProps = {
  /** Required href */
  href: string
  /** Link target (e.g. "_blank") */
  target?: string
  /** rel tokens — merged with security defaults when target="_blank" */
  rel?: string
  /** Whether to add a prefetch hint (default: false) */
  prefetch?: boolean
  /** Maps to data-btn attribute for button-style links */
  btnStyle?: string
  /** Inline styles */
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'a'>, 'href' | 'target' | 'rel'>
```

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

export type LinkProps = {
  href: string
  target?: string
  rel?: string
  prefetch?: boolean
  btnStyle?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'a'>, 'href' | 'target' | 'rel'>

export const Link = React.forwardRef<HTMLAnchorElement, LinkProps>(
  (
    {
      href,
      target,
      rel,
      children,
      styles,
      prefetch = false,
      btnStyle,
      onClick,
      onPointerDown,
      ...props
    },
    ref,
  ) => {
    const computedRel = React.useMemo(() => {
      if (target === '_blank') {
        const tokens = new Set(['noopener', 'noreferrer'])
        if (prefetch) tokens.add('prefetch')
        if (rel) {
          rel.split(/\s+/).forEach((t) => { if (t) tokens.add(t) })
        }
        return Array.from(tokens).join(' ')
      }
      return rel
    }, [target, rel, prefetch])

    return (
      <UI
        as="a"
        ref={ref}
        href={href}
        target={target}
        rel={computedRel}
        styles={styles}
        data-btn={btnStyle}
        onClick={onClick}
        onPointerDown={onPointerDown}
        {...props}
      >
        {children}
      </UI>
    )
  },
)

Link.displayName = 'Link'
export default Link
```

## CSS Variables

```scss
--link-color: var(--color-primary, #0066cc);
--link-hover-color: var(--color-primary-hover, #0052a3);
--link-visited-color: #551a8b;
--link-text-decoration: underline;
--link-hover-text-decoration: none;
--link-focus-outline: 2px solid currentColor;
--link-focus-outline-offset: 2px;

--link-subtle-color: var(--color-text, inherit);
--link-subtle-hover-color: var(--color-primary, #0066cc);
```

## SCSS Template

```scss
// link.scss
a {
  color: var(--link-color, #0066cc);
  text-decoration: var(--link-text-decoration, underline);
  text-underline-offset: 0.15em;
  text-decoration-thickness: 1px;
  transition: color 0.15s ease, text-decoration-thickness 0.15s ease;

  &:hover {
    color: var(--link-hover-color, #0052a3);
    text-decoration: var(--link-hover-text-decoration, none);
  }

  &:visited {
    color: var(--link-visited-color, #551a8b);
  }

  &:focus-visible {
    outline: var(--link-focus-outline, 2px solid currentColor);
    outline-offset: var(--link-focus-outline-offset, 2px);
    text-decoration-thickness: 2px;
  }

  &[data-btn] {
    // Button-style link inherits button styling — see button.scss
    text-decoration: none;
  }
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `Link` component.

**Link text — descriptive**
- Always use descriptive link text. "Read installation guide" not "Click here". "View pricing details" not "More" (WCAG 2.4.4 Link Purpose, AA).
- For icon-only links, pass `aria-label` describing what activating the link does. The icon glyph itself is not an accessible name.
- Avoid identical link text pointing at different URLs on the same page — assistive tech users get confused (WCAG 2.4.4).

**External-link security**
- When `target="_blank"`, the component automatically adds `rel="noopener noreferrer"`. This:
  - `noopener` prevents the new tab from accessing `window.opener` (security: blocks tabnabbing attacks).
  - `noreferrer` strips the `Referer` header (privacy).
- User-provided `rel` tokens are merged with the defaults — duplicates are deduplicated. So `rel="nofollow"` + `target="_blank"` produces `rel="nofollow noopener noreferrer"`.
- Consider also marking external links visually (icon, text indicator) so users know they're leaving the site. The component doesn't auto-render this — pair Link with an external-link Icon when needed.

**Keyboard interaction**
- Native `<a>` element provides full keyboard support: Tab navigates, Enter activates. No JavaScript needed.
- Don't intercept the click handler to prevent navigation unless you have a SPA router actively handling the route — and in that case, still let Cmd/Ctrl-click open in a new tab.

**Focus visible**
- `:focus-visible` adds a 2-px outline at `currentColor` with `2px` offset. The outline color inherits the link's color, which adapts to light/dark themes.
- Outline must meet 3:1 contrast against the surrounding page background (WCAG 1.4.11). The default at link color on a light page is typically well above 3:1; verify in dark themes.

**Color contrast**
- Link color (`--link-color`) on the page background must meet 4.5:1 (WCAG 1.4.3 Contrast Minimum, AA). The default `var(--color-primary)` should be palette-tuned for AA.
- Visited link color (`--link-visited-color`) must also meet 4.5:1. The default `#551a8b` (browser default purple) on white is ~7:1; on dark backgrounds, override.
- Underline (default `text-decoration: underline`) is the visual indicator that the text is a link, satisfying WCAG 1.4.1 Use of Color (color is not the only indicator).

**Skip link pattern**
- Common a11y pattern: a hidden Link at the top of the page that becomes visible on focus, jumping the user to `#main-content`. The vendored Link supports this via standard CSS — no special prop needed. Render the Link, hide it visually except on focus.

**Button-style links (`btnStyle`)**
- When using `btnStyle` to make a link look like a button, the underlying element is still `<a>` — keyboard activates with Enter (not Space). If the user expects button-like behavior (Space activation, no URL), use a real Button with `onClick` instead.

**WCAG 2.2 AA criteria addressed**
- 1.4.1 Use of Color (underline is the non-color indicator)
- 1.4.3 Contrast Minimum (link color on background)
- 1.4.11 Non-text Contrast (focus outline against background)
- 2.1.1 Keyboard (native anchor — Tab + Enter)
- 2.4.4 Link Purpose (in Context) (descriptive text or aria-label is required)
- 2.4.7 Focus Visible (`:focus-visible` outline)
- 4.1.2 Name, Role, Value (native anchor with descriptive text or aria-label)

## Usage Examples

```tsx
import Link from './link/link'
import './link/link.scss'

// Internal
<Link href="/about">About us</Link>

// External — automatic security defaults
<Link href="https://example.com" target="_blank">
  Visit example.com
</Link>

// External + user-provided rel (merged with security defaults)
<Link href="https://partner.com" target="_blank" rel="sponsored">
  Sponsored: partner site
</Link>

// Icon-only link (accessible name required)
<Link href="/settings" aria-label="Settings">
  <Icon name="info" aria-hidden size={20} />
</Link>

// Skip-link pattern (combined with CSS visually-hidden-until-focus)
<Link href="#main" className="skip-link">Skip to main content</Link>

// Button-style link (visually a button; semantically still an anchor)
<Link href="/signup" btnStyle="block">
  Get started
</Link>

// Analytics tracking — works for keyboard activation too
<Link
  href="/products"
  onClick={() => trackEvent('link_click', { href: '/products' })}
>
  Browse products
</Link>
```
