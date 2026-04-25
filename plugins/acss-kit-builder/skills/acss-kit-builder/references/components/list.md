# Component: List

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). Vendored List preserves the upstream compound API (`List` + `List.ListItem`) and the `role="list"` override pattern that restores list semantics for VoiceOver/Safari when CSS `list-style: none` would otherwise strip them. Supports `ul`, `ol`, and `dl` variants (with `dt` / `dd` items for definition lists).

## Overview

A semantic list wrapper supporting unordered (`ul`), ordered (`ol`), and definition (`dl`) lists. The `ListItem` sub-component renders `<li>`, `<dt>`, or `<dd>` based on its `type` prop. Both List and ListItem use `forwardRef` for programmatic focus and DOM access. The compound API (`List.ListItem`) keeps the parent-child relationship explicit at the call site.

## Generation Contract

```
export_name: List (compound: List.ListItem)
file: list.tsx
scss: list.scss
imports: UI from '../ui'
dependencies: []
```

## Props Interface

```tsx
export type ListType = 'ul' | 'ol' | 'dl'

export type ListProps = {
  /** List variant: ul | ol | dl (default: ul) */
  type?: ListType
  /** Visual variant — drives data-variant for SCSS targeting */
  variant?: 'inline' | 'numbered' | 'none' | string
  /**
   * Explicit role override.
   * Pass `role="list"` when applying `variant="none"` (or any unstyled variant)
   * to restore list semantics for VoiceOver/Safari, which strip them when
   * `list-style: none` is applied via CSS.
   */
  role?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'ul'>, 'type'>

export type ListItemType = 'li' | 'dt' | 'dd'

export type ListItemProps = {
  /** li (default), dt, or dd — match the parent list type */
  type?: ListItemType
  id?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'li'>, 'type'>
```

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

export type ListType = 'ul' | 'ol' | 'dl'

export type ListProps = {
  type?: ListType
  variant?: 'inline' | 'numbered' | 'none' | string
  role?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'ul'>, 'type'>

export type ListItemType = 'li' | 'dt' | 'dd'

export type ListItemProps = {
  type?: ListItemType
  id?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'li'>, 'type'>

const ListItem = React.forwardRef<HTMLLIElement | HTMLElement, ListItemProps>(
  ({ type = 'li', id, styles, children, classes, ...props }, ref) => (
    <UI
      id={id}
      as={type}
      className={classes}
      style={styles}
      ref={ref}
      {...props}
    >
      {children}
    </UI>
  ),
)
ListItem.displayName = 'ListItem'

const ListRoot = React.forwardRef<
  HTMLUListElement | HTMLOListElement | HTMLDListElement,
  ListProps
>(({ children, classes, type = 'ul', variant, styles, role, ...props }, ref) => (
  <UI
    as={type}
    data-variant={variant}
    className={classes}
    style={styles}
    role={role}
    ref={ref}
    {...props}
  >
    {children}
  </UI>
))
ListRoot.displayName = 'List'

type ListComponent = typeof ListRoot & {
  ListItem: typeof ListItem
}

export const List = Object.assign(ListRoot, { ListItem }) as ListComponent

export default List
```

## CSS Variables

```scss
--list-padding-inline-start: 1.25rem;
--list-gap: 0.5rem;
--list-item-padding-block: 0.25rem;
--list-marker-color: var(--color-primary, #0066cc);
--list-inline-gap: 1rem;

// Definition list
--dl-term-fw: 600;
--dl-term-margin-block-start: 0.5rem;
--dl-desc-margin-inline-start: 0;
--dl-desc-margin-block-end: 0.5rem;
```

## SCSS Template

```scss
// list.scss
ul, ol {
  padding-inline-start: var(--list-padding-inline-start, 1.25rem);
  display: flex;
  flex-direction: column;
  gap: var(--list-gap, 0.5rem);
  margin: 0;

  > li {
    padding-block: var(--list-item-padding-block, 0.25rem);

    &::marker {
      color: var(--list-marker-color, #0066cc);
    }
  }

  &[data-variant="inline"] {
    flex-direction: row;
    flex-wrap: wrap;
    gap: var(--list-inline-gap, 1rem);
    list-style: none;
    padding-inline-start: 0;
  }

  &[data-variant="none"] {
    list-style: none;
    padding-inline-start: 0;
  }
}

dl {
  margin: 0;

  > dt {
    font-weight: var(--dl-term-fw, 600);
    margin-block-start: var(--dl-term-margin-block-start, 0.5rem);
  }

  > dd {
    margin-inline-start: var(--dl-desc-margin-inline-start, 0);
    margin-block-end: var(--dl-desc-margin-block-end, 0.5rem);
  }
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `List` component.

**Native semantics — preserved**
- Renders native `<ul>`, `<ol>`, or `<dl>` elements. Screen readers announce "list of N items" / "ordered list of N items" / "definition list" automatically. Definition list items announce "term" / "definition" appropriately.
- Don't add `role="listbox"` / `role="menu"` for plain content lists — those roles trigger keyboard interaction expectations that you'd then need to implement (arrow-key navigation, single selection, etc.). Use them only for actual interactive widgets.

**The `list-style: none` Safari/VoiceOver gotcha**
- Safari + VoiceOver strip the implicit `role="list"` from `<ul>` / `<ol>` when CSS `list-style: none` is applied. The list still renders, but VoiceOver no longer announces "list" or item counts.
- The vendored `variant="none"` and `variant="inline"` apply `list-style: none`, so they trigger this Safari behavior.
- **Fix**: pass `role="list"` explicitly when using these variants:
  ```tsx
  <List variant="none" role="list">
    <List.ListItem>Nav link</List.ListItem>
  </List>
  ```
- This is a real bug in Safari that will not be fixed; the workaround is permanent. Document it in code review for any unstyled list.

**Definition list pattern (`dl`)**
- `<dl>` pairs `<dt>` (term) with `<dd>` (description). Multiple `<dd>` per `<dt>` is allowed (multiple definitions for the same term).
- Don't pair `<dt>` and `<dd>` with non-list semantics — VoiceOver and NVDA rely on the `<dl>` parent for the "definition list" announcement.
- Pass `type="dt"` and `type="dd"` on `List.ListItem` when `List type="dl"`.

**Keyboard navigation**
- Plain content lists have no keyboard interaction. Tab moves through any interactive descendants (links, buttons) using their native order.
- For lists of links, the focus order follows DOM order. Sort lists meaningfully — alphabetical, by date, by importance — so keyboard users get a useful traversal.

**Color contrast — markers**
- `::marker` color (`--list-marker-color`) is the bullet/number color. Custom markers must meet 3:1 against the page background (WCAG 1.4.11 Non-text Contrast) since the marker is purely visual.
- The default `var(--color-primary)` is typically well above 3:1; verify in dark themes.

**Inline lists for navigation**
- The `variant="inline"` pattern is common for nav menus. Always pair with `role="list"` (Safari fix) and a parent landmark (`<nav aria-label="Primary">`) so the list is reachable via assistive-tech navigation.
- Inline lists must keep adequate spacing (`--list-inline-gap`) to satisfy WCAG 2.5.8 Target Size when the list items are interactive.

**WCAG 2.2 AA criteria addressed**
- 1.3.1 Info and Relationships (native list semantics)
- 1.4.11 Non-text Contrast (marker color when used as the only indicator)
- 2.1.1 Keyboard (interactive descendants follow native focus order)
- 2.5.8 Target Size Minimum (inline-list spacing for interactive items)
- 4.1.2 Name, Role, Value (native list elements; explicit `role="list"` on unstyled variants for VoiceOver)

## Usage Examples

```tsx
import List from './list/list'
import './list/list.scss'

// Basic unordered list
<List>
  <List.ListItem>Apples</List.ListItem>
  <List.ListItem>Bananas</List.ListItem>
  <List.ListItem>Cherries</List.ListItem>
</List>

// Ordered list with custom marker color
<List
  type="ol"
  styles={{ '--list-marker-color': '#0066cc' } as React.CSSProperties}
>
  <List.ListItem>Step one</List.ListItem>
  <List.ListItem>Step two</List.ListItem>
</List>

// Unstyled list with role restoration (Safari/VoiceOver fix)
<List variant="none" role="list">
  <List.ListItem><a href="/about">About</a></List.ListItem>
  <List.ListItem><a href="/contact">Contact</a></List.ListItem>
</List>

// Inline list — navigation menu
<nav aria-label="Primary">
  <List variant="inline" role="list">
    <List.ListItem><a href="/home">Home</a></List.ListItem>
    <List.ListItem><a href="/products">Products</a></List.ListItem>
    <List.ListItem><a href="/contact">Contact</a></List.ListItem>
  </List>
</nav>

// Definition list (glossary)
<List type="dl">
  <List.ListItem type="dt">React</List.ListItem>
  <List.ListItem type="dd">A JavaScript library for building user interfaces.</List.ListItem>
  <List.ListItem type="dt">TypeScript</List.ListItem>
  <List.ListItem type="dd">JavaScript with syntactic types.</List.ListItem>
</List>
```
