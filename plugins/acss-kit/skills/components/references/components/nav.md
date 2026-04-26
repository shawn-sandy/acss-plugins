# Component: Nav

## Overview

A semantic navigation landmark with the compound pattern: `Nav`, `Nav.List`, `Nav.Item`. All sub-components are in a single generated file. Supports horizontal (default) and vertical layouts.

## Generation Contract

```
export_name: Nav (compound: Nav.List, Nav.Item)
file: nav.tsx
scss: nav.scss
imports: UI from '../ui'
dependencies: []
```

All sub-components go in the same `nav.tsx` file. No separate files.

## Props Interface

```tsx
export type NavProps = {
  children?: React.ReactNode
  classes?: string
  styles?: React.CSSProperties
  /** Label required when multiple <nav> elements exist on the page (WCAG 2.4.8) */
  'aria-label'?: string
} & Omit<React.ComponentPropsWithoutRef<'nav'>, 'className'>

type NavListProps = {
  children?: React.ReactNode
  /** Vertical (block) layout instead of horizontal (default) */
  isBlock?: boolean
  /** Accessible label for the list */
  'aria-label'?: string
} & Omit<React.ComponentPropsWithoutRef<'ul'>, 'className'>

type NavItemProps = {
  children?: React.ReactNode
  classes?: string
  styles?: React.CSSProperties
  id?: string
} & Omit<React.ComponentPropsWithoutRef<'li'>, 'className'>
```

## Key Pattern: Compound Component Assembly

```tsx
import UI from '../ui'
import React from 'react'

// NavList — uses <ul> element
const NavList = React.forwardRef<HTMLUListElement, NavListProps>(
  ({ isBlock, children, ...props }, ref) => (
    <UI
      as="ul"
      classes={`nav-list${isBlock ? ' nav-list--block' : ''}`}
      data-list={isBlock ? 'unstyled block' : 'unstyled'}
      ref={ref}
      {...props}
    >
      {children}
    </UI>
  )
)
NavList.displayName = 'Nav.List'

// NavItem — uses <li> element
const NavItem = React.forwardRef<HTMLLIElement, NavItemProps>(
  ({ id, styles, classes, children, ...props }, ref) => (
    <UI
      as="li"
      id={id}
      classes={`nav-item${classes ? ' ' + classes : ''}`}
      styles={styles}
      ref={ref}
      {...props}
    >
      {children}
    </UI>
  )
)
NavItem.displayName = 'Nav.Item'

// Nav root — uses <nav> element
const NavRoot = React.forwardRef<HTMLElement, NavProps>(
  ({ children, ...props }, ref) => (
    <UI as="nav" classes="nav" ref={ref} {...props}>
      {children}
    </UI>
  )
)
NavRoot.displayName = 'Nav'

// Compound assembly
type NavComponent = typeof NavRoot & {
  List: typeof NavList
  Item: typeof NavItem
}

export const Nav = Object.assign(NavRoot, {
  List: NavList,
  Item: NavItem,
}) as NavComponent

export default Nav
```

## CSS Variables

```scss
--nav-display: flex;
--nav-direction: row;
--nav-align: center;
--nav-justify: space-between;
--nav-bg: transparent;
--nav-padding-inline: 1rem;
--nav-padding-block: 0.5rem;
--nav-gap: 1rem;
--nav-fs: 0.9rem;
--nav-flex-wrap: wrap;

// Nav list
--nav-list-display: flex;
--nav-list-direction: row;
--nav-list-gap: 0.5rem;
--nav-list-padding: 0;
--nav-list-margin: 0;
--nav-list-list-style: none;

// Nav list — vertical
--nav-list-block-direction: column;
--nav-list-block-align: flex-start;
--nav-list-block-gap: 0.25rem;
--nav-list-block-width: 100%;

// Nav item
--nav-item-display: block;

// Link styling inside nav items
--nav-link-color: var(--color-text, currentColor);
--nav-link-hover-color: var(--color-primary, #0066cc);
--nav-link-padding-inline: 0.5rem;
--nav-link-padding-block: 0.375rem;
--nav-link-text-decoration: none;
--nav-link-radius: 0.25rem;
--nav-link-fw: 400;
--nav-link-current-color: var(--color-primary, #0066cc);
--nav-link-current-fw: 600;
--nav-link-focus-outline: 2px solid var(--color-primary, #0066cc);
```

## SCSS Pattern

```scss
// nav.scss
.nav {
  display: var(--nav-display, flex);
  flex-direction: var(--nav-direction, row);
  align-items: var(--nav-align, center);
  justify-content: var(--nav-justify, space-between);
  background: var(--nav-bg, transparent);
  padding-inline: var(--nav-padding-inline, 1rem);
  padding-block: var(--nav-padding-block, 0.5rem);
  gap: var(--nav-gap, 1rem);
  font-size: var(--nav-fs, 0.9rem);
  flex-wrap: var(--nav-flex-wrap, wrap);
}

.nav-list {
  display: var(--nav-list-display, flex);
  flex-direction: var(--nav-list-direction, row);
  gap: var(--nav-list-gap, 0.5rem);
  list-style: none;
  padding: 0;
  margin: 0;

  &.nav-list--block,
  &[data-list~="block"] {
    flex-direction: var(--nav-list-block-direction, column);
    align-items: var(--nav-list-block-align, flex-start);
    gap: var(--nav-list-block-gap, 0.25rem);
    width: var(--nav-list-block-width, 100%);
  }
}

.nav-item {
  display: var(--nav-item-display, block);

  // Style links inside nav items
  a {
    color: var(--nav-link-color, currentColor);
    text-decoration: var(--nav-link-text-decoration, none);
    padding-inline: var(--nav-link-padding-inline, 0.5rem);
    padding-block: var(--nav-link-padding-block, 0.375rem);
    border-radius: var(--nav-link-radius, 0.25rem);
    font-weight: var(--nav-link-fw, 400);
    display: block;
    transition: color 0.15s ease, background 0.15s ease;

    &:hover {
      color: var(--nav-link-hover-color, #0066cc);
    }

    &:focus-visible {
      outline: var(--nav-link-focus-outline, 2px solid #0066cc);
      outline-offset: 2px;
    }

    &[aria-current="page"] {
      color: var(--nav-link-current-color, #0066cc);
      font-weight: var(--nav-link-current-fw, 600);
    }
  }
}
```

## Usage Examples

```tsx
import Nav from './nav/nav'
import './nav/nav.scss'

// Basic horizontal nav
<Nav aria-label="Main navigation">
  <Nav.List>
    <Nav.Item><a href="/" aria-current="page">Home</a></Nav.Item>
    <Nav.Item><a href="/about">About</a></Nav.Item>
    <Nav.Item><a href="/contact">Contact</a></Nav.Item>
  </Nav.List>
</Nav>

// Multiple nav regions (aria-label required — WCAG 2.4.8)
<Nav aria-label="Main navigation">
  <Nav.List>
    <Nav.Item><a href="/">Home</a></Nav.Item>
    <Nav.Item><a href="/products">Products</a></Nav.Item>
  </Nav.List>
</Nav>

<Nav aria-label="Footer navigation">
  <Nav.List>
    <Nav.Item><a href="/privacy">Privacy</a></Nav.Item>
    <Nav.Item><a href="/terms">Terms</a></Nav.Item>
  </Nav.List>
</Nav>

// Vertical sidebar navigation
<Nav aria-label="Sidebar navigation">
  <Nav.List isBlock>
    <Nav.Item><a href="/dashboard">Dashboard</a></Nav.Item>
    <Nav.Item><a href="/settings">Settings</a></Nav.Item>
    <Nav.Item><a href="/profile">Profile</a></Nav.Item>
  </Nav.List>
</Nav>

// Nav with logo and menu
<Nav aria-label="Site navigation">
  <a href="/" aria-label="Go to homepage">
    <img src="/logo.svg" alt="Company Logo" />
  </a>
  <Nav.List>
    <Nav.Item><a href="/products">Products</a></Nav.Item>
    <Nav.Item><a href="/pricing">Pricing</a></Nav.Item>
  </Nav.List>
  <Nav.List aria-label="User actions">
    <Nav.Item><a href="/login">Sign in</a></Nav.Item>
  </Nav.List>
</Nav>
```

## Accessibility Notes

- `<nav>` is a landmark element — screen reader users can jump directly to it
- `aria-label` is required when multiple `<nav>` elements exist on the page (WCAG 2.4.8)
- `aria-current="page"` on the active link announces "current page" to screen readers
- List structure (`<ul>` + `<li>`) allows screen readers to announce "list of N items"
- Focus indicators on links meet WCAG 2.4.7 requirements
