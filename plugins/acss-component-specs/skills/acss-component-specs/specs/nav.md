---
format_version: 1
name: nav
display_name: Nav
description: Navigation landmark with Nav.Link sub-component. Uses native <nav> element. aria-current="page" marks active link.
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/navs/nav.tsx
fpkit_version: main
component_type: layout
a11y:
  wcag: ['2.4.1', '2.4.4', '4.1.2']
  accessible_name: aria-label on nav element (e.g. aria-label="Main navigation")
props:
  - name: as
    type: React.ElementType
    required: false
    maps_to: element
    default: nav
    description: Root element. Default nav provides landmark role automatically.
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Nav.Link items
  - name: direction
    type: "'horizontal' | 'vertical'"
    required: false
    maps_to: data-attr-token
    data_attr: data-nav
    description: Layout direction. horizontal = row, vertical = column.
  - name: classes
    type: string
    required: false
    maps_to: class
    description: CSS class names
  - name: styles
    type: React.CSSProperties
    required: false
    maps_to: css-var
    description: Inline styles override
events: []
framework_notes:
  react:
    strategy: Compound component via Object.assign (Nav + Nav.Link). Native <nav> provides landmark. No state in root.
    dependencies: [ui.tsx]
    caveats: Attach Nav.Link as static property. Both in same nav.tsx file.
  html:
    strategy: Native <nav> with <a> children. aria-current="page" on active link.
    dependencies: []
    caveats: ""
  astro:
    strategy: Nav.astro + NavLink.astro. SCSS sidecar.
    dependencies: [nav.scss]
    caveats: ""
css_vars:
  - name: --nav-display
    default: flex
    description: Nav display
  - name: --nav-direction
    default: row
    description: Default flex direction (horizontal nav)
  - name: --nav-gap
    default: 0.25rem
    description: Gap between nav links
  - name: --nav-padding
    default: "0.5rem"
    description: Nav container padding
  - name: --nav-link-color
    default: "var(--color-text, currentColor)"
    description: Link text color
  - name: --nav-link-hover-color
    default: "var(--color-primary, #0066cc)"
    description: Link hover color
  - name: --nav-link-active-color
    default: "var(--color-primary, #0066cc)"
    description: Active link color (aria-current=page)
theme_dependencies: []
---

## SCSS

```scss
// nav.scss
.nav {
  display: var(--nav-display, flex);
  flex-direction: var(--nav-direction, row);
  gap: var(--nav-gap, 0.25rem);
  padding: var(--nav-padding, 0.5rem);
  list-style: none;
  margin: 0;

  &[data-nav="vertical"] {
    flex-direction: column;
  }
}

.nav-link {
  display: var(--nav-link-display, inline-flex);
  align-items: center;
  padding-block: var(--nav-link-padding-block, 0.5rem);
  padding-inline: var(--nav-link-padding-inline, 0.75rem);
  color: var(--nav-link-color, var(--color-text, currentColor));
  text-decoration: none;
  border-radius: var(--nav-link-radius, 0.25rem);
  font-weight: var(--nav-link-fw, 400);
  transition: var(--nav-link-transition, color 0.15s ease, background 0.15s ease);

  &:hover {
    color: var(--nav-link-hover-color, var(--color-primary, #0066cc));
    background: var(--nav-link-hover-bg, var(--color-surface-subtle, rgba(0, 0, 0, 0.04)));
  }

  &:focus-visible {
    outline: var(--nav-link-focus-outline, 2px solid currentColor);
    outline-offset: var(--nav-link-focus-outline-offset, 2px);
  }

  &[aria-current="page"],
  &[data-nav="active"] {
    color: var(--nav-link-active-color, var(--color-primary, #0066cc));
    font-weight: var(--nav-link-active-fw, 600);
    background: var(--nav-link-active-bg, transparent);
  }
}
```

## Usage

```tsx
import Nav from './nav/nav'
import './nav/nav.scss'

<Nav aria-label="Main navigation">
  <Nav.Link href="/">Home</Nav.Link>
  <Nav.Link href="/about">About</Nav.Link>
  <Nav.Link href="/work" active>Work</Nav.Link>
  <Nav.Link href="/contact">Contact</Nav.Link>
</Nav>

// Vertical nav
<Nav direction="vertical" aria-label="Sidebar navigation">
  <Nav.Link href="/dashboard">Dashboard</Nav.Link>
  <Nav.Link href="/settings">Settings</Nav.Link>
</Nav>
```
