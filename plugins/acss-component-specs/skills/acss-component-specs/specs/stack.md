---
format_version: 1
name: stack
display_name: Stack
description: Layout primitive for stacking children with consistent spacing. Horizontal or vertical axis via data attribute. No semantic meaning — purely spatial.
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/stack/stack.tsx
fpkit_version: main
component_type: layout
a11y:
  layout_only: true
props:
  - name: direction
    type: "'row' | 'column'"
    required: false
    maps_to: data-attr-token
    data_attr: data-stack
    description: Flex direction. row = horizontal stack, column = vertical stack (default).
  - name: gap
    type: string
    required: false
    maps_to: css-var
    description: Gap between children (CSS value, e.g. '1rem', '0.5rem'). Overrides --stack-gap.
  - name: align
    type: "'start' | 'center' | 'end' | 'stretch' | 'baseline'"
    required: false
    maps_to: data-attr
    data_attr: data-align
    description: align-items value
  - name: justify
    type: "'start' | 'center' | 'end' | 'between' | 'around' | 'evenly'"
    required: false
    maps_to: data-attr
    data_attr: data-justify
    description: justify-content value. between = space-between, around = space-around.
  - name: wrap
    type: boolean
    required: false
    maps_to: data-attr
    data_attr: data-stack
    data_value: wrap
    description: Enable flex-wrap for responsive stacking
  - name: as
    type: React.ElementType
    required: false
    maps_to: element
    default: div
    description: Root element
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Stack children
  - name: classes
    type: string
    required: false
    maps_to: class
    description: CSS class names
  - name: styles
    type: React.CSSProperties
    required: false
    maps_to: css-var
    description: Inline styles (includes gap override)
events: []
framework_notes:
  react:
    strategy: Simple flex container wrapping UI base. No state, no hooks.
    dependencies: [ui.tsx]
    caveats: ""
  html:
    strategy: div with class=stack and data attributes.
    dependencies: []
    caveats: ""
  astro:
    strategy: Stack.astro wrapper. SCSS sidecar.
    dependencies: [stack.scss]
    caveats: ""
css_vars:
  - name: --stack-gap
    default: 1rem
    description: Default gap between children
  - name: --stack-display
    default: flex
    description: Display (always flex)
  - name: --stack-direction
    default: column
    description: Default flex-direction
  - name: --stack-align
    default: stretch
    description: Default align-items
theme_dependencies: []
---

## SCSS

```scss
// stack.scss
.stack {
  display: var(--stack-display, flex);
  flex-direction: var(--stack-direction, column);
  gap: var(--stack-gap, 1rem);
  align-items: var(--stack-align, stretch);

  // Direction variants
  &[data-stack="row"] { flex-direction: row; }
  &[data-stack~="wrap"] { flex-wrap: wrap; }

  // Align variants
  &[data-align="start"] { align-items: flex-start; }
  &[data-align="center"] { align-items: center; }
  &[data-align="end"] { align-items: flex-end; }
  &[data-align="baseline"] { align-items: baseline; }

  // Justify variants
  &[data-justify="start"] { justify-content: flex-start; }
  &[data-justify="center"] { justify-content: center; }
  &[data-justify="end"] { justify-content: flex-end; }
  &[data-justify="between"] { justify-content: space-between; }
  &[data-justify="around"] { justify-content: space-around; }
  &[data-justify="evenly"] { justify-content: space-evenly; }
}
```

## Usage

```tsx
import Stack from './stack/stack'
import './stack/stack.scss'

// Vertical stack (default)
<Stack>
  <Button type="button">First</Button>
  <Button type="button">Second</Button>
  <Button type="button">Third</Button>
</Stack>

// Horizontal row
<Stack direction="row" align="center" justify="between">
  <span>Left</span>
  <span>Right</span>
</Stack>

// Custom gap
<Stack gap="0.5rem">
  <Alert severity="info">First</Alert>
  <Alert severity="success">Second</Alert>
</Stack>
```
