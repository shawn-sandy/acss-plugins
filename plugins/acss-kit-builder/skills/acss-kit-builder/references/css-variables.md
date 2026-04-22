# CSS Variables Reference

## Naming Convention

All CSS custom properties follow a consistent hierarchical pattern:

```
--{component}-{element?}-{variant?}-{property}
```

| Segment | Required | Examples |
|---------|----------|----------|
| component | Yes | `btn`, `alert`, `card`, `nav` |
| element | No | `header`, `footer`, `title`, `icon` |
| variant | No | `primary`, `error`, `success`, `warning` |
| property | Yes | `bg`, `color`, `padding`, `border`, `radius` |

### Examples

```scss
--btn-bg                      // Component base property
--btn-primary-bg              // Variant-specific property
--btn-hover-bg                // State-specific property
--btn-focus-outline           // State + property
--btn-focus-outline-offset    // State + property with modifier
--card-header-padding         // Element-specific property
--card-header-bg              // Element + property
--alert-error-bg              // Component + variant + property
--alert-icon-color            // Component + element + property
```

---

## Approved Abbreviations

### Use Abbreviations For

| Abbreviation | Full | Rationale |
|---|---|---|
| `bg` | background-color | Universal convention |
| `fs` | font-size | Well-established in typography |
| `fw` | font-weight | Common in design systems |
| `radius` | border-radius | Short enough already |
| `gap` | gap | Already one word |

### Use Full Words For

| Property | Don't Use | Use |
|---|---|---|
| padding | `px`, `py`, `p` | `padding`, `padding-inline`, `padding-block` |
| margin | `mx`, `my`, `m` | `margin`, `margin-inline`, `margin-block` |
| color | `cl`, `c` | `color` |
| border | `bdr`, `br` | `border` |
| display | `dsp`, `d` | `display` |
| width | `w` | `width` |
| height | `h` | `height` |

### Logical Properties

Use logical CSS properties for better RTL support:

```scss
// Correct
--btn-padding-inline: 1.5rem;   // Left + right padding
--btn-padding-block: 0.5rem;    // Top + bottom padding
--card-margin-block-end: 1rem;  // Bottom margin

// Avoid
--btn-padding-left: 1.5rem;     // Physical property
--btn-padding-top: 0.5rem;      // Physical property
```

---

## Fallback Strategy

Every CSS variable reference MUST include a hardcoded fallback value. Generated components must work standalone without any global design token file.

### Pattern

```scss
// Simple fallback
font-size: var(--btn-fs, 0.9375rem);           // 15px
border-radius: var(--btn-radius, 0.375rem);    // 6px

// Fallback to another variable with further fallback
background: var(--btn-primary-bg, var(--color-primary, #0066cc));
color: var(--btn-primary-color, var(--color-text-inverse, #ffffff));

// Calc with fallback
padding-inline: var(--btn-padding-inline, calc(var(--btn-fs, 0.9375rem) * 1.5));
```

### Why

Generated components are installed independently. Without a global `--color-primary` token file, the component would have no background color. The fallback ensures correct rendering immediately after generation, while still being overridable via CSS cascade.

A developer can later add a global tokens file to replace all defaults:

```css
/* tokens.css — optional, added after initial generation */
:root {
  --color-primary: #7c3aed;
  --color-text-inverse: #ffffff;
}
```

---

## Component Variable Sets

### Button

```scss
// Size tokens
--btn-size-xs: 0.6875rem;    // 11px
--btn-size-sm: 0.8125rem;    // 13px
--btn-size-md: 0.9375rem;    // 15px
--btn-size-lg: 1.125rem;     // 18px
--btn-size-xl: 1.25rem;      // 20px

// Base
--btn-display: inline-flex;
--btn-fs: var(--btn-size-md, 0.9375rem);
--btn-fw: 500;
--btn-radius: 0.375rem;
--btn-gap: 0.5rem;
--btn-padding-block: calc(var(--btn-fs, 0.9375rem) * 0.5);
--btn-padding-inline: calc(var(--btn-fs, 0.9375rem) * 1.5);
--btn-bg: transparent;
--btn-color: currentColor;
--btn-border: 1px solid currentColor;
--btn-cursor: pointer;

// Primary color variant
--btn-primary-bg: var(--color-primary, #0066cc);
--btn-primary-color: var(--color-text-inverse, #fff);
--btn-primary-border: none;

// States
--btn-hover-bg: var(--color-primary-dark, #0052a3);
--btn-hover-transform: translateY(-1px);
--btn-focus-outline: 2px solid currentColor;
--btn-focus-outline-offset: 2px;
--btn-disabled-opacity: 0.6;
--btn-disabled-cursor: not-allowed;

// Transition
--btn-transition: all 0.2s ease-in-out;
```

### Card

```scss
--card-bg: var(--color-surface, #fff);
--card-color: var(--color-text, inherit);
--card-padding: 1rem;
--card-radius: 0.5rem;
--card-border: 1px solid var(--color-border, #e0e0e0);
--card-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

--card-title-fs: 1.25rem;
--card-title-fw: 600;
--card-title-margin-block-end: 0.5rem;

--card-content-padding: 1.5rem;
--card-content-gap: 1rem;

--card-footer-padding: 1rem 1.5rem;
--card-footer-bg: var(--color-surface-subtle, #f9f9f9);
--card-footer-border-top: 1px solid var(--color-border, #e0e0e0);
--card-footer-gap: 0.75rem;
```

### Alert

```scss
--alert-display: flex;
--alert-gap: 0.75rem;
--alert-padding: 1rem;
--alert-margin-block-end: 1rem;
--alert-radius: 0.375rem;
--alert-border: 1px solid;
--alert-bg: var(--color-surface, #f0f0f0);
--alert-color: inherit;
--alert-fs: 0.9375rem;

--alert-icon-size: 1rem;
--alert-icon-color: currentColor;

--alert-title-fs: 1rem;
--alert-title-fw: 600;
--alert-title-margin-block-end: 0.25rem;

// Severity variants
--alert-info-bg: #d1ecf1;
--alert-info-border: #bee5eb;
--alert-info-color: #0c5460;

--alert-success-bg: #d4edda;
--alert-success-border: #c3e6cb;
--alert-success-color: #155724;

--alert-warning-bg: #fff3cd;
--alert-warning-border: #ffeeba;
--alert-warning-color: #856404;

--alert-error-bg: #f8d7da;
--alert-error-border: #f5c6cb;
--alert-error-color: #721c24;
```

### Dialog

```scss
--dialog-bg: var(--color-surface, #fff);
--dialog-color: var(--color-text, inherit);
--dialog-padding: 0;
--dialog-radius: 0.5rem;
--dialog-width: 32rem;
--dialog-max-width: 90vw;
--dialog-max-height: 85vh;
--dialog-shadow: 0 20px 25px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.04);
--dialog-border: none;

--dialog-header-padding: 1.5rem;
--dialog-header-border-bottom: 1px solid var(--color-border, #e0e0e0);

--dialog-body-padding: 1.5rem;
--dialog-body-max-height: 60vh;
--dialog-body-overflow: auto;

--dialog-footer-padding: 1rem 1.5rem;
--dialog-footer-bg: var(--color-surface-subtle, #f9f9f9);
--dialog-footer-border-top: 1px solid var(--color-border, #e0e0e0);
--dialog-footer-gap: 0.75rem;

// Backdrop (::backdrop pseudo-element)
--dialog-backdrop-bg: rgba(0, 0, 0, 0.5);
```

### Nav

```scss
--nav-display: flex;
--nav-direction: row;
--nav-align: center;
--nav-justify: space-between;
--nav-bg: transparent;
--nav-height: auto;
--nav-padding-inline: 1rem;
--nav-padding-block: 0.5rem;
--nav-gap: 1rem;
--nav-fs: 0.9rem;

--nav-link-color: var(--color-text, currentColor);
--nav-link-hover-color: var(--color-primary, #0066cc);
--nav-link-active-color: var(--color-primary, #0066cc);
--nav-link-text-decoration: none;
--nav-link-padding-inline: 0.5rem;
--nav-link-padding-block: 0.25rem;
```

### Form/Input

```scss
--input-display: block;
--input-width: 100%;
--input-bg: var(--color-surface, #fff);
--input-color: var(--color-text, inherit);
--input-border: 1px solid var(--color-border, #d0d0d0);
--input-border-radius: 0.375rem;
--input-padding-inline: 0.75rem;
--input-padding-block: 0.5rem;
--input-fs: 1rem;
--input-line-height: 1.5;
--input-outline: 2px solid var(--color-primary, #0066cc);
--input-outline-offset: 0;
--input-focus-border: var(--color-primary, #0066cc);
--input-disabled-bg: var(--color-surface-subtle, #f5f5f5);
--input-disabled-opacity: 0.7;
--input-placeholder-color: var(--color-text-subtle, #757575);
```

---

## rem Units Reference

All sizes MUST use rem. Never use px in generated SCSS.

| px | rem |
|----|-----|
| 10px | 0.625rem |
| 12px | 0.75rem |
| 13px | 0.8125rem |
| 14px | 0.875rem |
| 15px | 0.9375rem |
| 16px | 1rem |
| 18px | 1.125rem |
| 20px | 1.25rem |
| 24px | 1.5rem |
| 32px | 2rem |

Formula: `px ÷ 16 = rem`
