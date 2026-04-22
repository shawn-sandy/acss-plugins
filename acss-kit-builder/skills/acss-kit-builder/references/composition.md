# Composition Reference

## Generation Decision Tree

When generating a component, ask these questions in order:

```
1. Is it in catalog.md (simple component)?
   YES → Read its catalog entry, generate single tsx + scss file
   NO  → Read its dedicated reference doc in references/components/

2. Does it have dependencies in its Generation Contract?
   NO  → Generate directly (bottom of tree)
   YES → Resolve each dependency first (bottom-up)

3. Does a dependency file already exist in the target dir?
   YES → Skip generation, import from existing file
   NO  → Generate it from its own reference doc

4. Is it a compound component (Card, Nav)?
   YES → All sub-components (Title, Content, Footer) go in ONE file
   NO  → Standard single-component file

5. Does it need useDisabledState?
   YES → Inline the condensed 50-line version from accessibility.md
   NO  → No hook needed
```

---

## Component Categories

### Simple — No Dependencies

These components import only `UI from '../ui'`. Generate as a single tsx + scss file.

| Component | File | Notes |
|---|---|---|
| Badge | `badge.tsx` + `badge.scss` | `<sup><span>` nested structure |
| Tag | `tag.tsx` + `tag.scss` | Dismissible variant |
| Heading | `heading.tsx` + `heading.scss` | Polymorphic h1-h6 |
| Text | `text.tsx` + `text.scss` | Inline/block text |
| Progress | `progress.tsx` + `progress.scss` | Native `<progress>` |
| Details | `details.tsx` + `details.scss` | Native `<details><summary>` |

### Interactive — useDisabledState Required

These components inline the condensed `useDisabledState` hook.

| Component | File | Hook |
|---|---|---|
| Button | `button.tsx` + `button.scss` | `useDisabledState` |
| Link | `link.tsx` + `link.scss` | Visited state only (no hook needed) |
| IconButton | `icon-button.tsx` + `icon-button.scss` | `useDisabledState` |

### Icon — Inline SVG

```tsx
// icon.tsx — no SCSS needed, uses inline SVG
// Generated with a curated set of SVGs based on what components need
```

Icon depends on nothing. All other components that need icons depend on Icon.

### Compound — Multiple Sub-Components in One File

These components are generated as a single `.tsx` file containing the root + all sub-components:

| Component | Sub-Components |
|---|---|
| Card | `Card`, `Card.Title`, `Card.Content`, `Card.Footer` |
| Nav | `Nav`, `Nav.List`, `Nav.Item` |

**Why one file?** Deleting a single component shouldn't break others. Sub-components are only useful when the parent is present.

### Complex — Multiple Dependencies

| Component | Dependencies |
|---|---|
| Alert | `icon.tsx` |
| Dialog | `button.tsx`, `icon-button.tsx`, `icon.tsx` |
| Form | `input.tsx` (or inline — see form.md) |

---

## Inline Types Pattern

**Every generated component file contains its own type definitions.** No cross-file type imports.

```tsx
// button.tsx
export type ButtonProps = {
  type: 'button' | 'submit' | 'reset'
  children?: React.ReactNode
  disabled?: boolean
  isDisabled?: boolean        // Legacy compat prop
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'text' | 'pill' | 'icon' | 'outline'
  color?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning'
  block?: boolean
  classes?: string
  styles?: React.CSSProperties
  'data-btn'?: string
  onClick?: React.MouseEventHandler<HTMLButtonElement>
  onKeyDown?: React.KeyboardEventHandler<HTMLButtonElement>
  onPointerDown?: React.PointerEventHandler<HTMLButtonElement>
} & Omit<React.ComponentPropsWithoutRef<'button'>, 'disabled'>
```

The `& Omit<React.ComponentPropsWithoutRef<'button'>, 'disabled'>` pattern:
- Adds all native `<button>` HTML props
- Omits native `disabled` (replaced by our `disabled?: boolean` with different handling)

---

## Compound Component Creation Pattern

```tsx
// card.tsx — all three sub-components + root in one file

import UI from '../ui'
import React from 'react'

// --- Types (inline) ---
export type CardProps = {
  as?: React.ElementType
  children?: React.ReactNode
  interactive?: boolean
  styles?: React.CSSProperties
  classes?: string
} & Omit<React.ComponentPropsWithoutRef<'div'>, 'onClick'>
  & { onClick?: () => void }

type CardTitleProps = {
  as?: React.ElementType
  children?: React.ReactNode
  className?: string
  id?: string
} & React.ComponentPropsWithoutRef<'h3'>

type CardContentProps = {
  as?: React.ElementType
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'article'>

type CardFooterProps = {
  as?: React.ElementType
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'div'>

// --- Sub-components ---
const CardTitle = ({ as = 'h3', children, className, ...props }: CardTitleProps) => (
  <UI as={as} classes={`card-title${className ? ' ' + className : ''}`} {...props}>
    {children}
  </UI>
)
CardTitle.displayName = 'Card.Title'

const CardContent = ({ as = 'article', children, ...props }: CardContentProps) => (
  <UI as={as} classes="card-content" {...props}>{children}</UI>
)
CardContent.displayName = 'Card.Content'

const CardFooter = ({ as = 'div', children, ...props }: CardFooterProps) => (
  <UI as={as} classes="card-footer" {...props}>{children}</UI>
)
CardFooter.displayName = 'Card.Footer'

// --- Root component ---
const CardRoot = ({ as = 'div', children, interactive, onClick, classes, styles, ...props }: CardProps) => {
  const interactiveProps = interactive ? {
    role: 'button' as const,
    tabIndex: 0,
    onClick,
    onKeyDown: (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick?.() }
    },
  } : { onClick }

  return (
    <UI
      as={as}
      classes={`card${classes ? ' ' + classes : ''}`}
      styles={styles}
      data-card={interactive ? 'interactive' : true}
      {...interactiveProps}
      {...props}
    >
      {children}
    </UI>
  )
}

// --- Compound component assembly ---
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
Card.displayName = 'Card'

export default Card
```

---

## Local Import Paths

All imports in generated files are local. Never `@fpkit/acss`.

```tsx
// Foundation — always this path regardless of component
import UI from '../ui'

// Component depends on another generated component
import Button from '../button/button'
import Icon from '../icon/icon'
import IconButton from '../icon-button/icon-button'
```

Path convention: `../component-name/component-name` (kebab-case directory, kebab-case file).

---

## CSS Class Naming

Generated components use simple lowercase class names matching the component name:

```scss
// Not BEM, not complex — just the component name
.btn { }
.card { }
.card-title { }
.card-content { }
.card-footer { }
.alert { }
.nav { }
.badge { }
```

State classes:
```scss
.is-disabled { opacity: 0.6; cursor: not-allowed; }
.is-active { }
.is-open { }
.is-visible { }
```
