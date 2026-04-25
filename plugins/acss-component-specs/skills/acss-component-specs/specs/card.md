---
format_version: 1
name: card
display_name: Card
description: Flexible content container. Compound component with Title, Content, and Footer sub-parts. Supports interactive (clickable) variant.
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/cards/card.tsx
fpkit_version: main
component_type: layout
a11y:
  wcag: ['2.1.1', '2.4.3', '4.1.2']
  accessible_name: aria-labelledby pointing to Card.Title id, or aria-label for interactive cards
  described_by: Card.Title id via aria-labelledby on root element
props:
  - name: as
    type: React.ElementType
    required: false
    maps_to: element
    default: div
    description: Polymorphic root element. Use article or section for semantic document structure.
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Card body — compose with Card.Title, Card.Content, Card.Footer
  - name: interactive
    type: boolean
    required: false
    maps_to: data-attr
    data_attr: data-card
    data_value: interactive
    description: Enables whole-card click and keyboard navigation. Adds role=button, tabIndex=0.
  - name: onClick
    type: "() => void"
    required: false
    maps_to: prop
    description: Click handler. Required when interactive=true.
  - name: classes
    type: string
    required: false
    maps_to: class
    description: CSS class names (takes precedence over className)
  - name: styles
    type: React.CSSProperties
    required: false
    maps_to: css-var
    description: Inline styles override
events:
  - name: onClick
    type: "React.MouseEventHandler<HTMLElement>"
  - name: onKeyDown
    type: "React.KeyboardEventHandler<HTMLElement>"
framework_notes:
  react:
    strategy: Compound component via static property attachment (Card.Title, Card.Content, Card.Footer). All in one card.tsx. Interactive variant adds role=button and keyboard handler.
    dependencies: [ui.tsx]
    caveats: Use React.forwardRef on CardRoot for ref passthrough. Compound assembly via Object.assign pattern.
  html:
    strategy: article or section element with nested semantic children. aria-labelledby on root.
    dependencies: []
    caveats: Include data-card=interactive for the interactive variant; add tabindex=0 and role=button manually.
  astro:
    strategy: Separate Card.astro, CardTitle.astro, CardContent.astro, CardFooter.astro files. SCSS sidecar card.scss.
    dependencies: [card.scss]
    caveats: No static property attachment in Astro; import sub-components separately.
css_vars:
  - name: --card-bg
    default: "var(--color-surface, #fff)"
    description: Card background (semantic token)
  - name: --card-color
    default: "var(--color-text, inherit)"
    description: Card text color (semantic token)
  - name: --card-radius
    default: 0.5rem
    description: Border radius
  - name: --card-border
    default: "1px solid var(--color-border, #e0e0e0)"
    description: Card border (semantic token)
  - name: --card-shadow
    default: "0 1px 3px rgba(0, 0, 0, 0.1)"
    description: Box shadow
  - name: --card-focus-outline
    default: "2px solid var(--color-primary, #0066cc)"
    description: Focus outline for interactive variant
theme_dependencies: []
---

## SCSS

```scss
// card.scss
.card {
  display: var(--card-display, flex);
  flex-direction: var(--card-direction, column);
  background: var(--card-bg, var(--color-surface, #fff));
  color: var(--card-color, var(--color-text, inherit));
  padding: var(--card-padding, 0);
  border-radius: var(--card-radius, 0.5rem);
  border: var(--card-border, 1px solid var(--color-border, #e0e0e0));
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
      outline: var(--card-focus-outline, 2px solid var(--color-primary, #0066cc));
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
  background: var(--card-footer-bg, var(--color-surface-subtle, #f9f9f9));
  border-top: var(--card-footer-border-top, 1px solid var(--color-border, #e0e0e0));
}
```

## Usage

```tsx
import Card from './card/card'
import './card/card.scss'

// Basic card
<Card>
  <Card.Title>Product Name</Card.Title>
  <Card.Content><p>Description here.</p></Card.Content>
  <Card.Footer><Button type="button" color="primary">Buy Now</Button></Card.Footer>
</Card>

// Semantic with accessible title linking
<Card as="article" aria-labelledby="product-1">
  <Card.Title id="product-1">Featured Widget</Card.Title>
  <Card.Content><p>Best widget available.</p></Card.Content>
</Card>

// Interactive card (entire card is clickable)
<Card
  interactive
  aria-label="View article: 5 Tips"
  onClick={() => navigate('/articles/1')}
>
  <Card.Title>5 Tips for Better Code</Card.Title>
  <Card.Content><p>Learn how to write cleaner code.</p></Card.Content>
</Card>

// Custom heading level
<Card as="section">
  <Card.Title as="h2">Section Title</Card.Title>
  <Card.Content>Content here.</Card.Content>
</Card>
```
