# Component: UI (Foundation)

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). The vendored `UI` component is the polymorphic React primitive that every other component imports as `import UI from '../ui'`. **Intentional preservation**: this is the one file copied verbatim from fpkit at first `/kit-add` run — the polymorphic-component pattern with ref-forwarding has subtle TypeScript shape requirements (the `as unknown as UIComponent` double-cast in particular) that benefit from being a single canonical implementation rather than a re-derived one.

## Overview

`UI` is a polymorphic React component that renders as any HTML element via the `as` prop. Every kit-builder component (Button, Card, Dialog, Input, etc.) imports `UI` and forwards its props plus polymorphism, which is why `UI` ships once at first `/kit-add` and isn't regenerated. The `as` prop is type-safe — the component infers the correct ref type and prop set from the rendered element.

## Generation Contract

```
export_name: UI (default export)
file: ui.tsx
scss: (none — UI carries no styles; just markup)
imports: React (only)
dependencies: []
copy_method: verbatim from assets/foundation/ui.tsx (one-time, on first /kit-add)
```

`UI` is the only file copied verbatim from `assets/` rather than authored from a markdown spec. Every other component is generated from its embedded-markdown reference doc.

## Props Interface

```tsx
type AsProp<C extends React.ElementType> = { as?: C }
type PolymorphicRef<C extends React.ElementType> = React.Ref<React.ElementRef<C>>

type UIProps<C extends React.ElementType> = React.PropsWithChildren<
  AsProp<C> & {
    /** @deprecated Reserved for future use. Currently has no effect. */
    renderStyles?: boolean
    styles?: React.CSSProperties
    defaultStyles?: React.CSSProperties
    classes?: string
    className?: string
    id?: string
    children?: React.ReactNode
  }
> &
  Omit<
    React.ComponentPropsWithoutRef<C>,
    keyof (AsProp<C> & {
      renderStyles?: boolean
      styles?: React.CSSProperties
      defaultStyles?: React.CSSProperties
      classes?: string
      className?: string
      id?: string
      children?: React.ReactNode
    })
  > & {
    ref?: PolymorphicRef<C> | React.ForwardedRef<React.ElementRef<C>>
  }
```

## Key Pattern: The polymorphic forwardRef double-cast

The `UI` component returns from `React.forwardRef<...>` but is typed as a polymorphic `UIComponent`. Because `forwardRef` returns `ForwardRefExoticComponent`, which is structurally incompatible with the polymorphic call signature, the implementation requires a `as unknown as UIComponent` double-cast. This is the standard pattern used by Radix UI and similar polymorphic libraries — don't try to "fix" the cast, it's load-bearing.

```tsx
const UI: UIComponent = React.forwardRef(
  // implementation
) as unknown as UIComponent
```

## TSX Template

```tsx
import React from 'react'

type PolymorphicRef<C extends React.ElementType> = React.Ref<
  React.ElementRef<C>
>

type AsProp<C extends React.ElementType> = {
  as?: C
}

type PropsToOmit<C extends React.ElementType, P> = keyof (AsProp<C> & P)

type PolymorphicComponentProp<
  C extends React.ElementType,
  Props extends object = Record<string, never>,
> = React.PropsWithChildren<Props & AsProp<C>> &
  Omit<React.ComponentPropsWithoutRef<C>, PropsToOmit<C, Props>>

type PolymorphicComponentPropWithRef<
  C extends React.ElementType,
  Props extends object = Record<string, never>,
> = PolymorphicComponentProp<C, Props> & {
  ref?: PolymorphicRef<C> | React.ForwardedRef<React.ElementRef<C>>
}

type UIProps<C extends React.ElementType> = PolymorphicComponentPropWithRef<
  C,
  {
    /** @deprecated Reserved for future use. Currently has no effect. */
    renderStyles?: boolean
    styles?: React.CSSProperties
    defaultStyles?: React.CSSProperties
    classes?: string
    className?: string
    id?: string
    children?: React.ReactNode
  }
>

type UIComponent = (<C extends React.ElementType = 'div'>(
  props: UIProps<C>,
) => React.ReactElement | null) & { displayName?: string }

// `as unknown as UIComponent` is required: React.forwardRef returns
// ForwardRefExoticComponent which is structurally incompatible with the
// polymorphic UIComponent call signature at the type level. This double-cast
// is the standard pattern for polymorphic forwardRef components (used by
// Radix UI and similar libraries).
// eslint-disable-next-line react/display-name -- displayName is set on the next line; ESLint can't see post-definition assignment
const UI: UIComponent = React.forwardRef(
  <C extends React.ElementType>(
    {
      as,
      styles,
      style,
      classes,
      className,
      children,
      defaultStyles,
      ...props
    }: UIProps<C>,
    ref?: PolymorphicRef<C>,
  ) => {
    const Component = as ?? 'div'

    const styleObj: React.CSSProperties = {
      ...defaultStyles,
      ...styles,
      ...style,
    }

    // Support both 'classes' (custom) and 'className' (React standard).
    // 'classes' takes precedence if both are provided.
    const classNameValue = classes ?? className

    return (
      <Component
        {...props}
        ref={ref}
        style={styleObj}
        className={classNameValue}
      >
        {children}
      </Component>
    )
  },
) as unknown as UIComponent

export default UI
UI.displayName = 'UI'
```

## CSS Variables / SCSS Template

`UI` has no SCSS file. It is a pass-through component — styling responsibility lives entirely with the consuming component (Button, Card, Dialog, etc.). The `styles` and `defaultStyles` props let consumers pass inline style objects; `classes` and `className` let consumers pass class strings.

## Accessibility

WCAG 2.2 AA notes for the foundational `UI` component.

**Native semantics, preserved**
- `UI` renders as whatever the `as` prop specifies (default: `<div>`). All native HTML semantics, ARIA defaults, keyboard behavior, and focusability come from the rendered element. `UI` itself adds no semantics.
- This is the right choice — wrapping in any layer of additional semantics or roles would compete with the native element's behavior. Component-level a11y patterns (focus management, keyboard handling, ARIA attributes) live in the component that *uses* `UI`, not in `UI` itself.

**Ref forwarding**
- `UI` forwards refs with the correct element type (`HTMLButtonElement` when `as="button"`, `HTMLAnchorElement` when `as="a"`, etc.). Component authors needing programmatic focus, scroll positioning, or DOM measurement can attach refs without type assertions.

**Class and style merging**
- Both `classes` and `className` are accepted; `classes` takes precedence if both are passed. Component authors deciding between them should pick `classes` for consistency with fpkit conventions.
- `styles` and `defaultStyles` are merged in order: `defaultStyles` first, then `styles`, then native `style`. Inline style overrides are explicit and predictable — important for theme overrides and one-off adjustments.

**No a11y opinions**
- `UI` is intentionally opinionless about a11y because it can't know what element it's rendering until call time. The only design choice that matters at the foundation level is *not stripping or wrapping* native semantics — and that's preserved.

**WCAG 2.2 AA criteria addressed (indirectly)**
- 4.1.2 Name, Role, Value — by rendering native elements unchanged, `UI` lets consuming components inherit native names, roles, and values without conflict. Every other WCAG criterion comes from the consuming component (Button, Input, Dialog, etc.) and the user authoring the props.

## Usage Examples

```tsx
import UI from '../ui'

// As a div (default)
<UI>Hello world</UI>

// As a button with native props
<UI as="button" type="button" onClick={() => {}}>
  Click me
</UI>

// As an anchor with type-safe href
<UI as="a" href="/about">About</UI>

// With ref forwarding (typed as HTMLButtonElement automatically)
const ref = useRef<HTMLButtonElement>(null)
<UI as="button" ref={ref}>Focusable</UI>

// Style + class merging
<UI
  as="div"
  defaultStyles={{ padding: '1rem' }}
  styles={{ background: 'var(--color-surface)' }}
  classes="card"
>
  Composable styling
</UI>
```

## Why this is the only verbatim-copied file

Every other kit-builder component is generated from its embedded-markdown reference doc. `UI` is the exception: it's copied verbatim from `assets/foundation/ui.tsx` at first `/kit-add` run because:

1. **The polymorphic forwardRef pattern is intricate.** The `as unknown as UIComponent` double-cast, the `PolymorphicComponentPropWithRef` constraint dance, and the `eslint-disable` for displayName are easy to "improve" in a way that subtly breaks type inference downstream. A single canonical implementation reduces the chance of bit-rot.
2. **Every other component depends on `UI`.** A breakage in `UI` cascades through every generated component. Centralizing the source of truth in one verbatim-copied file simplifies regression hunting.
3. **No project-specific customization is expected.** Unlike Button or Form, `UI` doesn't have variants, themes, or behavior options. The 171-line implementation is the entire surface — there's nothing to parameterize.

Future iterations of the markdown-as-source refactor may parameterize `UI` (e.g. drop the deprecated `renderStyles` prop, simplify the `classes` vs `className` merge), at which point a markdown spec with embedded TSX could replace `assets/foundation/ui.tsx`. Until then, this markdown reference doc serves as the canonical *documentation* of the foundation; `assets/foundation/ui.tsx` remains the canonical *source*.
