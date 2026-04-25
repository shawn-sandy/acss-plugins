---
format_version: 1
name: card-content
display_name: Card.Content
description: Content body sub-component for Card. Default element is article. Flex-grows to fill available space.
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
    default: article
    description: Semantic content element. Use div if nesting inside an article root.
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Card body content — arbitrary markup
events: []
framework_notes:
  react:
    strategy: Emitted inside card.tsx as CardContent sub-component.
    dependencies: [ui.tsx]
    caveats: Attached as Card.Content via Object.assign.
  html:
    strategy: div.card-content element inside the card root.
    dependencies: []
    caveats: ""
  astro:
    strategy: Separate CardContent.astro file.
    dependencies: [card.scss]
    caveats: ""
css_vars:
  - name: --card-content-padding
    default: 1.5rem
    description: Content area padding
  - name: --card-content-flex
    default: "1"
    description: Flex-grow value (fills available vertical space)
theme_dependencies: []
---

## Notes

Card.Content is emitted inside `card.tsx` (React) or as `CardContent.astro` (Astro). It is not a standalone file in React output.
