---
format_version: 1
name: alert
display_name: Alert
description: Contextual message component with severity levels. Supports auto-dismiss. Uses role=alert for live region announcement.
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/alerts/alert.tsx
fpkit_version: main
component_type: interactive
a11y:
  wcag: ['1.3.3', '1.4.1', '4.1.3']
  accessible_name: children text content; do not rely on color alone (WCAG 1.4.1)
props:
  - name: severity
    type: "'info' | 'success' | 'warning' | 'error'"
    required: false
    maps_to: data-attr-token
    data_attr: data-severity
    description: Alert severity level mapped to data-severity (drives color via CSS)
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Alert message content
  - name: dismissable
    type: boolean
    required: false
    maps_to: prop
    description: Show dismiss button (X) in the alert
  - name: onDismiss
    type: "() => void"
    required: false
    maps_to: prop
    description: Callback when alert is dismissed
  - name: autoDismiss
    type: boolean
    required: false
    maps_to: prop
    description: Auto-dismiss after autoDismissMs (default 5000ms)
  - name: autoDismissMs
    type: number
    required: false
    maps_to: prop
    description: Auto-dismiss timeout in milliseconds
  - name: as
    type: React.ElementType
    required: false
    maps_to: element
    default: div
    description: Root element
  - name: classes
    type: string
    required: false
    maps_to: class
    description: CSS class names
  - name: styles
    type: React.CSSProperties
    required: false
    maps_to: css-var
    description: Inline styles override
events:
  - name: onDismiss
    type: "() => void"
framework_notes:
  react:
    strategy: Div with role=alert for live region. useEffect drives auto-dismiss timer. Severity via data-severity.
    dependencies: [ui.tsx]
    caveats: role=alert causes immediate announcement on render. Use aria-live=polite for non-urgent messages.
  html:
    strategy: div with role=alert and data-severity. Inline JS for auto-dismiss via data-auto-dismiss attribute.
    dependencies: []
    caveats: Add role=alert to trigger live region announcement. Color alone must not convey severity (WCAG 1.4.1).
  astro:
    strategy: Alert.astro with role=alert. Client script handles auto-dismiss.
    dependencies: [alert.scss]
    caveats: ""
css_vars:
  - name: --alert-padding
    default: 1rem 1.25rem
    description: Alert padding
  - name: --alert-radius
    default: 0.375rem
    description: Border radius
  - name: --alert-border-width
    default: 1px
    description: Border width
  - name: --alert-info-bg
    default: "var(--color-info-surface, #e8f4fd)"
    description: Info severity background
  - name: --alert-info-color
    default: "var(--color-info-text, #0c5a8a)"
    description: Info severity text
  - name: --alert-info-border
    default: "var(--color-info-border, #90caf9)"
    description: Info severity border
  - name: --alert-success-bg
    default: "var(--color-success-surface, #e8f5e9)"
    description: Success severity background
  - name: --alert-success-color
    default: "var(--color-success-text, #1b5e20)"
    description: Success severity text
  - name: --alert-warning-bg
    default: "var(--color-warning-surface, #fff8e1)"
    description: Warning severity background
  - name: --alert-warning-color
    default: "var(--color-warning-text, #7c4d00)"
    description: Warning severity text
  - name: --alert-error-bg
    default: "var(--color-error-surface, #fce4ec)"
    description: Error severity background
  - name: --alert-error-color
    default: "var(--color-error-text, #880e2f)"
    description: Error severity text
theme_dependencies: []
---

## SCSS

```scss
// alert.scss
.alert {
  display: var(--alert-display, flex);
  align-items: var(--alert-align, flex-start);
  gap: var(--alert-gap, 0.75rem);
  padding: var(--alert-padding, 1rem 1.25rem);
  border-radius: var(--alert-radius, 0.375rem);
  border-width: var(--alert-border-width, 1px);
  border-style: solid;
  border-color: transparent;

  // Severity variants (data-severity exact match)
  &[data-severity="info"] {
    background: var(--alert-info-bg, var(--color-info-surface, #e8f4fd));
    color: var(--alert-info-color, var(--color-info-text, #0c5a8a));
    border-color: var(--alert-info-border, var(--color-info-border, #90caf9));
  }

  &[data-severity="success"] {
    background: var(--alert-success-bg, var(--color-success-surface, #e8f5e9));
    color: var(--alert-success-color, var(--color-success-text, #1b5e20));
    border-color: var(--alert-success-border, var(--color-success-border, #a5d6a7));
  }

  &[data-severity="warning"] {
    background: var(--alert-warning-bg, var(--color-warning-surface, #fff8e1));
    color: var(--alert-warning-color, var(--color-warning-text, #7c4d00));
    border-color: var(--alert-warning-border, var(--color-warning-border, #ffe082));
  }

  &[data-severity="error"] {
    background: var(--alert-error-bg, var(--color-error-surface, #fce4ec));
    color: var(--alert-error-color, var(--color-error-text, #880e2f));
    border-color: var(--alert-error-border, var(--color-error-border, #f48fb1));
  }
}

.alert-content { flex: 1; }

.alert-dismiss {
  flex-shrink: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.125rem;
  line-height: 1;
  opacity: 0.7;

  &:hover { opacity: 1; }
  &:focus-visible {
    outline: var(--alert-focus-outline, 2px solid currentColor);
    outline-offset: var(--alert-focus-outline-offset, 2px);
  }
}
```

## Usage

```tsx
import Alert from './alert/alert'
import './alert/alert.scss'

// Basic
<Alert severity="info">Your account has been updated.</Alert>

// Dismissable
<Alert severity="warning" dismissable onDismiss={() => setVisible(false)}>
  Your session will expire in 5 minutes.
</Alert>

// Auto-dismiss (3 seconds)
<Alert severity="success" autoDismiss autoDismissMs={3000} onDismiss={() => setVisible(false)}>
  Saved successfully.
</Alert>

// Error
<Alert severity="error">Unable to process request. Please try again.</Alert>
```
