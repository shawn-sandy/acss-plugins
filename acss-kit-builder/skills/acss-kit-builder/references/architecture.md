# Architecture Reference

## The UI Foundation Component

`ui.tsx` is the only file copied verbatim from fpkit into developer projects. It is **fully self-contained** — only `import React from "react"` and nothing else.

All generated components import from this local file:

```tsx
import UI from '../ui'  // Always local, never @fpkit/acss
```

### What UI Provides

UI is a polymorphic React component. It renders as any HTML element while forwarding all props (including all ARIA attributes) to the rendered element.

**Core behavior:**

```tsx
// Renders a <div> by default
<UI>Hello World</UI>

// Renders as any element via `as` prop
<UI as="button" onClick={handleClick}>Click me</UI>
<UI as="nav" aria-label="Main navigation">...</UI>
<UI as="dialog" ref={dialogRef}>...</UI>

// Supports both `classes` and `className` (classes takes precedence)
<UI as="section" classes="my-section" styles={{ padding: '1rem' }}>...</UI>

// Style merging: defaultStyles is the base, styles overrides it
<UI defaultStyles={{ color: 'blue' }} styles={{ color: 'red' }}>Red text</UI>
```

### Polymorphic Type System

All types are defined inline in `ui.tsx`. There are no imports from a `types/` directory. The type system chain:

```
PolymorphicRef<C>
  → AsProp<C>
    → PropsToOmit<C, P>
      → PolymorphicComponentProp<C, Props>
        → PolymorphicComponentPropWithRef<C, Props>
          → UIProps<C>
            → UIComponent
```

This chain ensures:
1. `as="button"` makes all `HTMLButtonElement` props available
2. The `ref` is typed to match the rendered element
3. Custom props (`styles`, `classes`) don't conflict with native props

### Key Implementation Detail

`classes` prop takes precedence over `className`:

```tsx
const classNameValue = classes ?? className;
```

Generated components use `classes` when setting CSS class names to match fpkit convention.

---

## Building on UI

Every generated component wraps UI. The pattern:

```tsx
import UI from '../ui'
import React from 'react'

export type BadgeProps = {
  children?: React.ReactNode
  variant?: 'rounded'
} & React.ComponentPropsWithoutRef<'sup'>

export const Badge = ({ children, variant, ...props }: BadgeProps) => {
  return (
    <UI
      as="sup"
      data-badge={variant}
      role="status"
      {...props}
    >
      <UI as="span">{children}</UI>
    </UI>
  )
}
```

### Props Spreading

Spread `...props` after explicit props so consumers can pass any native HTML attribute:
- `aria-label`, `aria-labelledby`, `aria-describedby`
- `id`, `className`, `style`
- Event handlers
- `data-*` attributes

### Ref Forwarding

When a component needs a ref (e.g., Dialog for focus management), use `React.forwardRef`:

```tsx
export const MyDialog = React.forwardRef<HTMLDialogElement, DialogProps>(
  ({ children, ...props }, ref) => {
    return (
      <UI as="dialog" ref={ref} {...props}>
        {children}
      </UI>
    )
  }
)
```

---

## Compound Component Pattern

For components with structured sub-parts (Card, Nav), use the compound component pattern:

```tsx
// Define sub-components
const CardTitle = ({ children, ...props }: CardTitleProps) => (
  <UI as="h3" classes="card-title" {...props}>{children}</UI>
)

const CardContent = ({ children, ...props }: CardContentProps) => (
  <UI as="article" classes="card-content" {...props}>{children}</UI>
)

// Define root component
const CardRoot = ({ children, ...props }: CardProps) => (
  <UI as="div" classes="card" data-card {...props}>{children}</UI>
)

// Attach sub-components
export const Card = Object.assign(CardRoot, {
  Title: CardTitle,
  Content: CardContent,
})
Card.displayName = 'Card'
```

Consumer usage:
```tsx
<Card>
  <Card.Title>Product Name</Card.Title>
  <Card.Content>Description...</Card.Content>
</Card>
```

---

## Data Attribute Variants

fpkit uses `data-*` attributes for variants instead of className modifiers:

```tsx
// Button with size and color variants
<Button
  type="button"
  data-btn="lg"         // Size: xs | sm | md | lg | xl | 2xl | block
  data-style="outline"  // Style: outline | pill | text | icon
  data-color="primary"  // Color: primary | secondary | danger | success | warning
>
  Click me
</Button>
```

**Why data attributes instead of className?**
- Avoids className collision with user-provided classes
- SCSS can use `[data-btn~="lg"]` for space-separated word matching
- Easier to compose multiple variants: `data-btn="sm block"`
- More semantic than BEM modifiers

**SCSS targeting:**

```scss
// Space-separated word matching (like classList contains)
.btn[data-btn~="sm"] { font-size: var(--btn-size-sm, 0.8125rem); }
.btn[data-btn~="block"] { width: 100%; display: block; }

// Style variant
.btn[data-style="outline"] { background: transparent; border: 1px solid currentColor; }

// Color variant
.btn[data-color="primary"] { background: var(--btn-primary-bg, #0066cc); }
```

---

## File Organization Pattern

Generated components go in their own subdirectory:

```
src/components/fpkit/
├── ui.tsx                    # Foundation (one-time copy)
├── button/
│   ├── button.tsx
│   └── button.scss
├── icon/
│   └── icon.tsx              # No SCSS (uses inline SVG)
├── card/
│   ├── card.tsx
│   └── card.scss
└── dialog/
    ├── dialog.tsx
    └── dialog.scss
```

Import paths are relative:

```tsx
// In dialog.tsx
import UI from '../ui'
import Button from '../button/button'
```
