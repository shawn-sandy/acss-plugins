# Framework Reference: React + SCSS

This document tells the renderer how to translate any acss-component-spec into a React + TypeScript component with a SCSS sidecar. Read it alongside the component spec.

---

## Render Outputs

For each component, produce two files in `.acss-staging/react/<component>/`:

- `<component>.tsx` — React component (TypeScript)
- `<component>.scss` — SCSS sidecar with CSS custom properties

Prepend stamp to both files: `// generated from <component>.md@<version>`.

---

## Prop Mapping by `maps_to` Kind

### `prop`
Pass directly to the underlying element.
```tsx
// maps_to: prop, name: type
type: 'button' | 'submit' | 'reset'
// → <button type={type} ...>
```

### `data-attr`
Merge into the space-separated `data-*` attribute string.
```tsx
// maps_to: data-attr, data_attr: data-btn, name: size
const dataBtnValue = [size, block ? 'block' : undefined, dataBtnProp]
  .filter(Boolean).join(' ') || undefined
// → <button data-btn={dataBtnValue} ...>
```

### `data-attr-token`
Set the `data-*` attribute directly to the prop value.
```tsx
// maps_to: data-attr-token, data_attr: data-color, name: color
// → <button data-color={color} ...>
```

### `aria`
Map to an ARIA attribute. For `disabled`/`isDisabled`, use `useDisabledState`.
```tsx
// maps_to: aria, aria_attr: aria-disabled, name: disabled
// → use useDisabledState(isDisabled, handlers, classes)
// → <button aria-disabled={disabledProps['aria-disabled']} ...>
```
Never use native `disabled` attribute — it removes elements from tab order (WCAG 2.1.1).

### `class`
The `classes` prop: use `classes` value as `className`. Takes precedence over `className`.
```tsx
// maps_to: class, name: classes
const classNameValue = classes ?? className
// → <Component className={classNameValue} ...>
```

### `element`
The `as` prop for polymorphic rendering — pass to `UI` base component.
```tsx
// maps_to: element, name: as
<UI as={as ?? 'button'} ...>
```

### `css-var`
The `styles` prop: pass as `style` prop (merged with defaultStyles if present).
```tsx
// maps_to: css-var, name: styles
<UI style={styles} ...>
```

---

## Component File Template

```tsx
// generated from <component>.md@<version>
import UI from '../ui'
import React from 'react'

export type <ComponentName>Props = {
  // ... props from spec, with JSDoc from prop.description
} & React.ComponentPropsWithoutRef<'<element>'>

export const <ComponentName> = ({
  // destructure all props
}: <ComponentName>Props) => {
  return (
    <UI as="<element>" ...>
      {children}
    </UI>
  )
}

export default <ComponentName>
<ComponentName>.displayName = '<ComponentName>'
```

---

## Disabled State Pattern (interactive components)

Inline `useDisabledState` in every interactive component file. Do not create a separate file.

```tsx
function useDisabledState<T extends HTMLElement = HTMLButtonElement>(
  disabled: boolean | undefined,
  handlers: {
    onClick?: (e: React.MouseEvent<T>) => void
    onKeyDown?: (e: React.KeyboardEvent<T>) => void
    onPointerDown?: (e: React.PointerEvent<T>) => void
  } = {},
  className?: string
) {
  const isDisabled = Boolean(disabled)
  const mergedClassName = [isDisabled ? 'is-disabled' : '', className]
    .filter(Boolean).join(' ')

  const wrap = <E,>(fn?: (e: E) => void) => fn
    ? (e: any) => { if (isDisabled) { e.preventDefault(); e.stopPropagation(); return } fn(e) }
    : undefined

  return {
    disabledProps: { 'aria-disabled': isDisabled, className: mergedClassName },
    handlers: {
      onClick: wrap(handlers.onClick),
      onKeyDown: wrap(handlers.onKeyDown),
      onPointerDown: wrap(handlers.onPointerDown),
    },
  }
}

const resolveDisabledState = (d?: boolean, id?: boolean) => d ?? id ?? false
```

---

## Compound Component Pattern

For compound specs (Card, Dialog, Nav), generate all sub-components in the same file. Attach sub-components as static properties on the root.

```tsx
// In card.tsx — all in one file
const CardTitle = (...) => ...
CardTitle.displayName = 'Card.Title'

const CardContent = (...) => ...
CardContent.displayName = 'Card.Content'

const CardFooter = (...) => ...
CardFooter.displayName = 'Card.Footer'

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

---

## SCSS File Template

```scss
// generated from <component>.md@<version>
// <ComponentName> component
// CSS variables with fallback defaults — override in :root or scoped selectors

.<component> {
  // All values in rem (not px)
  // Every var() has a hardcoded fallback
  // Global semantic tokens (--color-*) use double-fallback:
  //   var(--<component>-<prop>, var(--color-<token>, #hardcoded))
}
```

Data attribute selectors for variants:
```scss
// data-attr variants (data-btn~="sm" matches space-separated list)
.<component>[data-<name>~="<value>"] { ... }

// data-attr-token variants (exact match)
.<component>[data-color="primary"] {
  background: var(--<component>-primary-bg, var(--color-primary, #0066cc));
}
```

Focus visible (required for interactive components):
```scss
.<component>:focus-visible {
  outline: var(--<component>-focus-outline, 2px solid currentColor);
  outline-offset: var(--<component>-focus-outline-offset, 2px);
}
```

Disabled state (required for aria-disabled components):
```scss
.<component>[aria-disabled="true"],
.<component>.is-disabled {
  opacity: var(--<component>-disabled-opacity, 0.6);
  cursor: var(--<component>-disabled-cursor, not-allowed);
  pointer-events: none;
}
```

---

## Theme Degradation Warning

If `theme_dependencies` in the spec is non-empty and no `acss-theme-builder` output is detected in the project (no `:root { --color-primary: ... }` declaration found in project CSS), prepend a warning comment to the SCSS:

```scss
// WARNING: no acss-theme-builder theme detected.
// Relying on hardcoded fallback colors. Run /theme-generate to create a theme.
```

---

## UI Base Component

The React renderer requires `ui.tsx` at `<componentsDir>/ui.tsx`. Copy from:
`assets/foundation/ui.tsx`

Check if it exists in the target directory first. If not, prompt the user:
```
ui.tsx not found in <componentsDir>. Copy assets/foundation/ui.tsx? [Enter/Ctrl+C]
```

---

## Events Wiring

Events from the spec `events:` array are passed through to the underlying element with handler wrapping for disabled state (if the component is interactive):

```tsx
// Spec declares: events: [{name: onClick, type: React.MouseEventHandler}]
// Interactive component → wrap with useDisabledState
const { disabledProps, handlers } = useDisabledState(isActuallyDisabled, { onClick, onKeyDown })
```

---

## Types Convention

- Inline all types in the component file. Never import types from another generated file.
- Omit `disabled` from native element props when using aria-disabled: `Omit<React.ComponentPropsWithoutRef<'button'>, 'disabled'>`
- Use `React.ComponentPropsWithoutRef<'element'>` for pass-through props.
