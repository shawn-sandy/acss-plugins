# Component: Field

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). Field is the small label+control wrapper from `components/form/fields.tsx`. The vendored version preserves the upstream `labelFor` requirement (compile-time accessible-name guarantee for the wrapped control) and the `data-style="fields"` SCSS hook.

## Overview

A minimal wrapper that pairs a `<label>` with a single form control (Input, Select, Textarea, etc.) and ensures the label is associated via `htmlFor`. Field doesn't render error or helper text — those concerns live in the control itself (Input handles `errorMessage` / `hintText` and generates the `aria-describedby` ids). Use Field for the layout + label association; layer the control inside.

## Generation Contract

```
export_name: Field
file: field.tsx
scss: field.scss
imports: UI from '../ui'
dependencies: []
```

## Props Interface

```tsx
export type FieldProps = {
  /** Label content — accepts text or a React node */
  label: React.ReactNode
  /**
   * REQUIRED — must match the `id` of the wrapped control.
   * The type makes the value required; runtime can't enforce that the wrapped control
   * actually has a matching `id`, so authoring discipline matters here.
   */
  labelFor: string
  /** The form control rendered inside (Input, Select, Textarea, etc.) */
  children: React.ReactNode
  /** Optional id on the wrapper div */
  id?: string
  classes?: string
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'label'>, 'htmlFor'>
```

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

export type FieldProps = {
  label: React.ReactNode
  labelFor: string
  children: React.ReactNode
  id?: string
  classes?: string
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'label'>, 'htmlFor'>

export const Field = ({
  label,
  labelFor,
  id,
  styles,
  classes,
  children,
  ...props
}: FieldProps) => (
  <UI
    as="div"
    id={id}
    styles={styles}
    classes={classes}
    data-style="fields"
    {...props}
  >
    <label htmlFor={labelFor}>{label}</label>
    {children}
  </UI>
)

Field.displayName = 'Field'
export default Field
```

## CSS Variables

```scss
--field-display: flex;
--field-direction: column;
--field-gap: 0.375rem;
--field-margin-block-end: 1rem;

--field-label-fs: 0.875rem;
--field-label-fw: 500;
--field-label-color: var(--color-text, inherit);
--field-label-margin-block-end: 0.25rem;
```

## SCSS Template

```scss
// field.scss
[data-style="fields"] {
  display: var(--field-display, flex);
  flex-direction: var(--field-direction, column);
  gap: var(--field-gap, 0.375rem);
  margin-block-end: var(--field-margin-block-end, 1rem);

  > label {
    font-size: var(--field-label-fs, 0.875rem);
    font-weight: var(--field-label-fw, 500);
    color: var(--field-label-color, inherit);
    margin-block-end: var(--field-label-margin-block-end, 0.25rem);
    display: block;
  }
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `Field` component.

**Label association (required)**
- `labelFor` is required by the type; pass the `id` of the wrapped control. The `<label htmlFor={labelFor}>` association lets users click the label to focus the control and lets screen readers announce the label when the control is focused (WCAG 1.3.1 Info and Relationships, WCAG 4.1.2 Name, Role, Value).
- The compile-time `labelFor: string` requirement makes "missing label" impossible at the Field level. The remaining authoring discipline is making sure the wrapped control's `id` matches.

**Visible label policy**
- Always pass a visible `label` — Field does not support visually-hidden labels. If you need a visually-hidden label (rare; consider whether the design is excluding sighted users with cognitive needs), use the bare control with an `aria-label` or `aria-labelledby` instead of Field.

**Layout & required indicators**
- Field doesn't render `*` or "required" text. The wrapped Input handles `aria-required` and visual required indicators if needed. This split keeps Field's responsibility narrow.

**Error & helper text**
- Field doesn't render error or hint text. Input/Textarea/Select render their own error / hint paragraphs and link them via `aria-describedby`. Don't manually add `<p class="error">` siblings inside Field — the control will not pick them up in `aria-describedby`.

**WCAG 2.2 AA criteria addressed**
- 1.3.1 Info and Relationships (programmatic label-control association)
- 3.3.2 Labels or Instructions (visible label is required)
- 4.1.2 Name, Role, Value (control gets its accessible name from the `<label>`)

## Usage Examples

```tsx
import Field from './field/field'
import Input from './input/input'
import './field/field.scss'

// Field + Input
<Field labelFor="email" label="Email address">
  <Input id="email" type="email" required />
</Field>

// Field + Select
<Field labelFor="country" label="Country">
  <select id="country" name="country">
    <option value="">Select a country</option>
    <option value="us">United States</option>
  </select>
</Field>

// Custom label content
<Field labelFor="card" label={<>Card number <small>(no spaces)</small></>}>
  <Input id="card" inputMode="numeric" pattern="\d*" required />
</Field>
```
