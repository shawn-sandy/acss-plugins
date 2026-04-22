# Component: Card

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

## SCSS Pattern

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
