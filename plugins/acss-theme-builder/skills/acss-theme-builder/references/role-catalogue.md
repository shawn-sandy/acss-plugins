# Semantic Role Catalogue

Canonical set of CSS custom properties used by acss-theme-builder. All generated theme files must define every required role. Optional roles may be omitted.

## Required roles

### Backgrounds

| Role | Light value | Dark value | Notes |
|---|---|---|---|
| `--color-background` | `#ffffff` (seed) | `#0b1220` (seed) | Page/app background |
| `--color-surface` | `#f9fafb` | `#121a2b` | Card, modal, panel |
| `--color-surface-raised` | `#ffffff` | `#1a2440` | Elevated surface (dropdown, tooltip) |

### Text

| Role | Light value | Dark value | Notes |
|---|---|---|---|
| `--color-text` | `#111827` | `#f3f4f6` | Body copy |
| `--color-text-muted` | `#4b5563` | `#cbd5e1` | Secondary text, captions |
| `--color-text-inverse` | `#ffffff` | `#0b1220` | Text on `--color-primary` background |

### Borders

| Role | Light value | Dark value | Notes |
|---|---|---|---|
| `--color-border` | `#e5e7eb` | `#263145` | Default border |
| `--color-border-strong` | `#d1d5db` | `#374357` | Emphasized border |

### Brand + semantic

| Role | Notes |
|---|---|
| `--color-primary` | Primary action color (buttons, links) |
| `--color-primary-hover` | Darker (light) / lighter (dark) hover state |
| `--color-success` | Positive state |
| `--color-warning` | Caution state |
| `--color-danger` | Destructive / error state |
| `--color-info` | Informational state; may equal `--color-primary` |

### Focus

| Role | Notes |
|---|---|
| `--color-focus-ring` | Keyboard focus outline; usually equals `--color-primary` |

## Optional roles

| Role | Notes |
|---|---|
| `--color-surface-subtle` | Very light tint (referenced by kit-builder input/card components) |
| `--color-text-subtle` | Even lighter muted text (referenced by kit-builder helper text) |
| `--color-brand-accent` | Secondary accent; used by brand-*.css files only |

## WCAG AA contrast targets

These pairs are validated by `scripts/validate_theme.py`. Minimum ratios follow WCAG 2.1 AA for normal text (4.5:1) and UI components / large text (3.0:1).

| Foreground | Background | Min ratio | Reason |
|---|---|---|---|
| `--color-text` | `--color-background` | 4.5:1 | Normal body text |
| `--color-text-muted` | `--color-background` | 4.5:1 | Secondary text still requires AA |
| `--color-text` | `--color-surface` | 4.5:1 | Text inside cards and panels |
| `--color-text-inverse` | `--color-primary` | 4.5:1 | Button label on primary bg |
| `--color-primary` | `--color-background` | 3.0:1 | UI component / large text |
| `--color-success` | `--color-background` | 3.0:1 | State badge / icon |
| `--color-warning` | `--color-background` | 3.0:1 | State badge / icon |
| `--color-danger` | `--color-background` | 3.0:1 | State badge / icon |
| `--color-info` | `--color-background` | 3.0:1 | State badge / icon |
| `--color-focus-ring` | `--color-background` | 3.0:1 | Focus indicator visibility |
