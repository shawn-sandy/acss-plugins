> **Legacy reference** — This bundled reference is superseded by `acss-component-specs/specs/card.md` when that plugin is installed. Prefer the spec-based workflow: `/spec-add card` then `/spec-render card`. The spec wins when both are present (kit-builder B0 bridge).

# Component: Card

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). Card uses the compound pattern (`Card`, `Card.Title`, `Card.Content`, `Card.Footer`) in a single `card.tsx` — same structure as upstream. Generated locally via `Object.assign(CardRoot, { Title, Content, Footer })`.

## Overview

A flexible container for grouping related content. Uses the compound component pattern: `Card`, `Card.Title`, `Card.Content`, `Card.Footer` — all in a single generated file. Supports an interactive (clickable) variant with keyboard support.

## Generation Contract

```
export_name: Card (compound: Card.Title, Card.Content, Card.Footer)
file: card.tsx
scss: card.scss
imports: UI from '../ui'
dependencies: []
```

All sub-components are generated in the same `card.tsx` file. No separate files.

## Props Interface

```tsx
export type CardProps = {
  /** HTML element to render as (default: div) */
  as?: React.ElementType
  /** Card content */
  children?: React.ReactNode
  /** Enable keyboard/mouse click for the whole card */
  interactive?: boolean
  /** Click handler (required when interactive=true) */
  onClick?: () => void
  /** CSS class names */
  classes?: string
  /** Inline styles */
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'div'>, 'onClick'>

type CardTitleProps = {
  /** HTML element to render as (default: h3) */
  as?: React.ElementType
  children?: React.ReactNode
  className?: string
  id?: string
} & React.ComponentPropsWithoutRef<'h3'>

type CardContentProps = {
  /** HTML element to render as (default: article) */
  as?: React.ElementType
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'article'>

type CardFooterProps = {
  /** HTML element to render as (default: div) */
  as?: React.ElementType
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'div'>
```

## Key Pattern: Interactive Cards

```tsx
// Non-interactive (default): semantic article or section
<Card as="article" aria-labelledby="title-1">
  <Card.Title id="title-1">Product</Card.Title>
  <Card.Content>Description</Card.Content>
</Card>

// Interactive: whole card is clickable + keyboard navigable
<Card
  interactive
  aria-label="View product details"
  onClick={() => navigate('/product/123')}
>
  <Card.Title>Product Name</Card.Title>
  <Card.Content>Click anywhere to view</Card.Content>
</Card>
```

The interactive card pattern:
- Adds `role="button"` and `tabIndex={0}`
- Responds to Enter/Space via `onKeyDown`
- Uses `data-card="interactive"` for SCSS targeting

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

// --- Sub-components ---
const CardTitle = ({
  as = 'h3',
  children,
  className,
  id,
  ...props
}: CardTitleProps) => (
  <UI as={as} classes={`card-title${className ? ' ' + className : ''}`} id={id} {...props}>
    {children}
  </UI>
)
CardTitle.displayName = 'Card.Title'

const CardContent = ({
  as = 'article',
  children,
  ...props
}: CardContentProps) => (
  <UI as={as} classes="card-content" {...props}>
    {children}
  </UI>
)
CardContent.displayName = 'Card.Content'

const CardFooter = ({
  as = 'div',
  children,
  ...props
}: CardFooterProps) => (
  <UI as={as} classes="card-footer" {...props}>
    {children}
  </UI>
)
CardFooter.displayName = 'Card.Footer'

// --- Root component ---
const CardRoot = ({
  as = 'div',
  children,
  interactive,
  onClick,
  classes,
  styles,
  ...props
}: CardProps) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (interactive && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault()
      onClick?.()
    }
  }

  return (
    <UI
      as={as}
      classes={`card${classes ? ' ' + classes : ''}`}
      styles={styles}
      data-card={interactive ? 'interactive' : undefined}
      role={interactive ? 'button' : undefined}
      tabIndex={interactive ? 0 : undefined}
      onClick={interactive ? onClick : undefined}
      onKeyDown={interactive ? handleKeyDown : undefined}
      {...props}
    >
      {children}
    </UI>
  )
}
CardRoot.displayName = 'Card'

// --- Compound assembly ---
type CardComponent = typeof CardRoot & {
  Title: typeof CardTitle
  Content: typeof CardContent
  Footer: typeof CardFooter
}

export const Card = Object.assign(CardRoot, {
  Title: CardTitle,
  Content: CardContent,
  Footer: CardFooter,
}) as CardComponent

export default Card
```

## CSS Variables

```scss
--card-bg: var(--color-surface, #fff);
--card-color: var(--color-text, inherit);
--card-padding: 0;
--card-radius: 0.5rem;
--card-border: 1px solid var(--color-border, #e0e0e0);
--card-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
--card-display: flex;
--card-direction: column;

// Title
--card-title-fs: 1.25rem;
--card-title-fw: 600;
--card-title-color: var(--color-text, inherit);
--card-title-padding: 1.5rem 1.5rem 0;
--card-title-margin-block-end: 0;

// Content
--card-content-padding: 1.5rem;
--card-content-flex: 1;

// Footer
--card-footer-padding: 1rem 1.5rem;
--card-footer-bg: var(--color-surface-subtle, #f9f9f9);
--card-footer-border-top: 1px solid var(--color-border, #e0e0e0);
--card-footer-gap: 0.75rem;
--card-footer-display: flex;
--card-footer-align: center;

// Interactive variant
--card-interactive-cursor: pointer;
--card-interactive-hover-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
--card-interactive-hover-transform: translateY(-2px);
--card-focus-outline: 2px solid var(--color-primary, #0066cc);
--card-focus-outline-offset: 2px;
```

## SCSS Template

```scss
// card.scss
.card {
  display: var(--card-display, flex);
  flex-direction: var(--card-direction, column);
  background: var(--card-bg, #fff);
  color: var(--card-color, inherit);
  padding: var(--card-padding, 0);
  border-radius: var(--card-radius, 0.5rem);
  border: var(--card-border, 1px solid #e0e0e0);
  box-shadow: var(--card-shadow, 0 1px 3px rgba(0, 0, 0, 0.1));
  overflow: hidden;
  transition: all 0.2s ease-in-out;

  &[data-card="interactive"] {
    cursor: var(--card-interactive-cursor, pointer);
    &:hover {
      box-shadow: var(--card-interactive-hover-shadow, 0 4px 6px rgba(0, 0, 0, 0.1));
      transform: var(--card-interactive-hover-transform, translateY(-2px));
    }
    &:focus-visible {
      outline: var(--card-focus-outline, 2px solid #0066cc);
      outline-offset: var(--card-focus-outline-offset, 2px);
    }
  }
}

.card-title {
  font-size: var(--card-title-fs, 1.25rem);
  font-weight: var(--card-title-fw, 600);
  color: var(--card-title-color, inherit);
  padding: var(--card-title-padding, 1.5rem 1.5rem 0);
  margin: 0 0 var(--card-title-margin-block-end, 0);
}

.card-content {
  padding: var(--card-content-padding, 1.5rem);
  flex: var(--card-content-flex, 1);
}

.card-footer {
  display: var(--card-footer-display, flex);
  align-items: var(--card-footer-align, center);
  gap: var(--card-footer-gap, 0.75rem);
  padding: var(--card-footer-padding, 1rem 1.5rem);
  background: var(--card-footer-bg, #f9f9f9);
  border-top: var(--card-footer-border-top, 1px solid #e0e0e0);
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `Card` component.

**Non-interactive cards**
- Default rendering uses `<div>` (or whatever `as` prop specifies — typically `<article>` or `<section>`). No interactive semantics.
- For semantic association of the card with its title, use `as="article"` and link via `aria-labelledby`:
  ```tsx
  <Card as="article" aria-labelledby="title-1">
    <Card.Title id="title-1">Product</Card.Title>
    ...
  </Card>
  ```

**Interactive cards (whole-card click)**
- When `interactive` is true, the card receives `role="button"`, `tabIndex={0}`, and an `onKeyDown` handler that activates `onClick` on Enter/Space. The `e.preventDefault()` on Space prevents the page scroll that would otherwise fire.
- Always pass an `aria-label` describing what activating the card does (e.g. `aria-label="View article: 5 Tips for Better Code"`). The card's text content is not necessarily a complete accessible name, especially if the title and content are long.
- A native `<button>` would be more semantically correct, but it blocks nesting other interactive descendants (links, buttons inside the card). The `role="button"` + `tabIndex` pattern preserves the visual flexibility while supporting keyboard activation.
- If the card needs nested interactive elements (a "Like" button inside, for example), prefer a non-interactive card with a clearly placed link/button that handles the primary action — avoid the click-target ambiguity.

**Heading hierarchy**
- `Card.Title` defaults to `<h3>`. Pass `as="h2"`, `as="h4"`, etc. to maintain document outline within the surrounding section. Never skip levels (e.g. `<h2>` directly to `<h4>`) without an intervening structural reason.

**Focus management**
- Interactive cards show `:focus-visible` outline at `var(--card-focus-outline, 2px solid var(--color-primary, #0066cc))` with `var(--card-focus-outline-offset, 2px)`. The outline color uses the project's primary color so it inherits the active theme.
- Hover transform (`translateY(-2px)`) is purely visual; focus state is independent and remains visible regardless of pointer state.

**Color contrast**
- Card title at `--card-title-color` on `--card-bg` must meet 4.5:1 (WCAG 1.4.3 Contrast Minimum, AA).
- Footer at `--card-footer-bg` may differ from card body; ensure footer text still meets 4.5:1 against the footer background, not just the card body background.
- Border at `--card-border` must meet 3:1 against the page background (WCAG 1.4.11 Non-text Contrast) when the border is the sole indicator of the card boundary. With the default subtle shadow, the contrast requirement on the border alone relaxes — but in flat designs without shadow, the border carries the load.

**Target size**
- Interactive cards naturally meet WCAG 2.5.8 Target Size Minimum (44 px) since cards are typically much larger than 44 px in both dimensions.

**WCAG 2.2 AA criteria addressed**
- 1.4.3 Contrast Minimum (title on card background; text on footer background)
- 1.4.11 Non-text Contrast (card border when it is the sole boundary indicator)
- 2.1.1 Keyboard (interactive cards activate via Enter/Space)
- 2.4.7 Focus Visible (`:focus-visible` outline on interactive cards)
- 2.5.8 Target Size Minimum (interactive cards exceed 44 px)
- 4.1.2 Name, Role, Value (interactive: explicit role + accessible name via aria-label)

## Usage Examples

```tsx
import Card from './card/card'
import './card/card.scss'

// Basic card
<Card>
  <Card.Title>Product Name</Card.Title>
  <Card.Content>
    <p>Product description here...</p>
  </Card.Content>
  <Card.Footer>
    <button>Buy Now — $29.99</button>
  </Card.Footer>
</Card>

// Accessible card with linked title
<Card as="article" aria-labelledby="product-1">
  <Card.Title id="product-1">Featured Widget</Card.Title>
  <Card.Content>
    <p>Best widget on the market.</p>
  </Card.Content>
</Card>

// Interactive card (entire card is clickable)
<Card
  interactive
  aria-label="View article: 5 Tips for Better Code"
  onClick={() => navigate('/articles/1')}
>
  <Card.Title>5 Tips for Better Code</Card.Title>
  <Card.Content>
    <p>Learn how to write cleaner code...</p>
  </Card.Content>
</Card>

// Custom heading level for document outline
<Card as="section">
  <Card.Title as="h2">Section Title</Card.Title>
  <Card.Content>Content here...</Card.Content>
</Card>
```
