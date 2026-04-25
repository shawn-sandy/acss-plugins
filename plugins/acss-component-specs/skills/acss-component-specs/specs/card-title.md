---
format_version: 1
name: card-title
display_name: Card.Title
description: Title sub-component for Card. Polymorphic heading element. Provides the card's accessible name via aria-labelledby.
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
    default: h3
    description: Heading level — change for correct document outline (h2, h3, etc.)
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Title text content
  - name: id
    type: string
    required: false
    maps_to: prop
    description: Id for aria-labelledby linking from the Card root
  - name: className
    type: string
    required: false
    maps_to: class
    description: Additional CSS classes
events: []
framework_notes:
  react:
    strategy: Emitted inside card.tsx as CardTitle sub-component. Not a separate file.
    dependencies: [ui.tsx]
    caveats: CardTitle is attached as Card.Title via Object.assign.
  html:
    strategy: Native heading element inside the card article element.
    dependencies: []
    caveats: ""
  astro:
    strategy: Separate CardTitle.astro file alongside Card.astro.
    dependencies: [card.scss]
    caveats: ""
css_vars:
  - name: --card-title-fs
    default: 1.25rem
    description: Title font size
  - name: --card-title-fw
    default: "600"
    description: Title font weight
  - name: --card-title-color
    default: inherit
    description: Title text color
  - name: --card-title-padding
    default: 1.5rem 1.5rem 0
    description: Title padding (top/horizontal only — no bottom gap)
theme_dependencies: []
---

## Notes

Card.Title is emitted inside `card.tsx` (React) or as `CardTitle.astro` (Astro). It is not a standalone file in React output.

The `id` prop is used for accessibility linking: the Card root receives `aria-labelledby={titleId}` pointing to the Card.Title's `id`.
