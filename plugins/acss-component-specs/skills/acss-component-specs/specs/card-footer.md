---
format_version: 1
name: card-footer
display_name: Card.Footer
description: Footer sub-component for Card. Horizontal flex row for action buttons and metadata.
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/cards/card.tsx
fpkit_version: main
component_type: layout
parent: card
maps_to_parent: compound-part
a11y:
  layout_only: true
props:
  - name: as
    type: React.ElementType
    required: false
    maps_to: element
    default: div
    description: Root element for footer area
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Footer content — typically action buttons
events: []
framework_notes:
  react:
    strategy: Emitted inside card.tsx as CardFooter sub-component.
    dependencies: [ui.tsx]
    caveats: Attached as Card.Footer via Object.assign.
  html:
    strategy: div.card-footer element inside the card root.
    dependencies: []
    caveats: ""
  astro:
    strategy: Separate CardFooter.astro file.
    dependencies: [card.scss]
    caveats: ""
css_vars:
  - name: --card-footer-padding
    default: 1rem 1.5rem
    description: Footer padding
  - name: --card-footer-bg
    default: "var(--color-surface-subtle, #f9f9f9)"
    description: Footer background (semantic token)
  - name: --card-footer-border-top
    default: "1px solid var(--color-border, #e0e0e0)"
    description: Footer top border separator
  - name: --card-footer-gap
    default: 0.75rem
    description: Gap between footer children
  - name: --card-footer-display
    default: flex
    description: Footer display
  - name: --card-footer-align
    default: center
    description: Footer align-items
theme_dependencies: []
---

## Notes

Card.Footer is emitted inside `card.tsx` (React) or as `CardFooter.astro` (Astro). It is not a standalone file in React output.
