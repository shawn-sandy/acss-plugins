---
format_version: 1
name: dialog
display_name: Dialog
description: Modal dialog using native HTML <dialog> element. Native focus trapping via showModal(). Compound component with Header, Body, Footer.
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/dialogs/dialog.tsx
fpkit_version: main
component_type: interactive
a11y:
  wcag: ['2.1.1', '2.1.2', '4.1.2', '3.2.2']
  accessible_name: title prop maps to aria-labelledby on <dialog> element
  described_by: description prop maps to aria-describedby on <dialog> element
props:
  - name: dialogRef
    type: "React.RefObject<HTMLDialogElement>"
    required: true
    maps_to: prop
    description: Ref to the <dialog> element. Required for showModal()/close() control.
  - name: openOnMount
    type: boolean
    required: false
    maps_to: prop
    description: If true, dialog opens on mount (non-modal; use for inline non-modal dialogs)
  - name: onClose
    type: "() => void"
    required: false
    maps_to: prop
    description: Callback when dialog closes. Wire to dialogRef.current?.close().
  - name: title
    type: string
    required: false
    maps_to: aria
    aria_attr: aria-labelledby
    description: Dialog heading text. Rendered as h2 inside DialogHeader; wired to aria-labelledby.
  - name: description
    type: string
    required: false
    maps_to: aria
    aria_attr: aria-describedby
    description: Supplementary description rendered below title; wired to aria-describedby.
  - name: showCloseButton
    type: boolean
    required: false
    maps_to: prop
    description: Show close button in header (default true)
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Dialog body content
  - name: footer
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Footer slot for action buttons
  - name: classes
    type: string
    required: false
    maps_to: class
    description: CSS class names on root <dialog>
  - name: styles
    type: React.CSSProperties
    required: false
    maps_to: css-var
    description: Inline styles on root <dialog>
events:
  - name: onClose
    type: "React.SyntheticEvent"
framework_notes:
  react:
    strategy: Native <dialog> via UI base with React.forwardRef. showModal()/close() driven by consumer-held dialogRef. Compound assembly with Header/Body/Footer sub-components.
    dependencies: [ui.tsx, button.tsx]
    caveats: Dialog depends on Button for the close button and footer actions. Button must be generated first. titleId is generated client-side for aria-labelledby linking.
  html:
    strategy: Native <dialog> with showModal()/close() inline JS. No focus-trap package. Backdrop click via event target check.
    dependencies: []
    caveats: Use showModal() (not show()) to ensure focus is trapped. Escape key fires cancel event automatically.
  astro:
    strategy: Dialog.astro wrapping native <dialog>. Client script handles open/close. Sub-components as sibling .astro files.
    dependencies: [dialog.scss]
    caveats: Open/close control must be client-side via script block.
css_vars:
  - name: --dialog-bg
    default: "var(--color-surface, #fff)"
    description: Dialog background
  - name: --dialog-color
    default: "var(--color-text, inherit)"
    description: Dialog text color
  - name: --dialog-radius
    default: 0.5rem
    description: Border radius
  - name: --dialog-width
    default: 32rem
    description: Dialog width
  - name: --dialog-max-width
    default: 90vw
    description: Maximum width
  - name: --dialog-max-height
    default: 85vh
    description: Maximum height
  - name: --dialog-shadow
    default: "0 20px 25px rgba(0, 0, 0, 0.15)"
    description: Box shadow
  - name: --dialog-backdrop-bg
    default: "rgba(0, 0, 0, 0.5)"
    description: Backdrop overlay color
  - name: --dialog-title-fs
    default: 1.25rem
    description: Title font size
  - name: --dialog-title-fw
    default: "600"
    description: Title font weight
  - name: --dialog-body-padding
    default: 1.5rem
    description: Body section padding
  - name: --dialog-footer-padding
    default: 1rem 1.5rem
    description: Footer section padding
  - name: --dialog-footer-bg
    default: "var(--color-surface-subtle, #f9f9f9)"
    description: Footer background
theme_dependencies: []
---

## SCSS

```scss
// dialog.scss
.dialog {
  background: var(--dialog-bg, var(--color-surface, #fff));
  color: var(--dialog-color, var(--color-text, inherit));
  padding: var(--dialog-padding, 0);
  border-radius: var(--dialog-radius, 0.5rem);
  border: var(--dialog-border, none);
  width: var(--dialog-width, 32rem);
  max-width: var(--dialog-max-width, 90vw);
  max-height: var(--dialog-max-height, 85vh);
  box-shadow: var(--dialog-shadow, 0 20px 25px rgba(0, 0, 0, 0.15));
  overflow: hidden;
  display: flex;
  flex-direction: column;

  &::backdrop {
    background: var(--dialog-backdrop-bg, rgba(0, 0, 0, 0.5));
  }
}

.dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: var(--dialog-header-padding, 1.5rem);
  border-bottom: var(--dialog-header-border-bottom, 1px solid var(--color-border, #e0e0e0));
  flex-shrink: 0;
}

.dialog-header-content { flex: 1; }

.dialog-title {
  font-size: var(--dialog-title-fs, 1.25rem);
  font-weight: var(--dialog-title-fw, 600);
  margin: 0;
}

.dialog-description {
  margin-block-start: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-text-subtle, #555);
}

.dialog-close {
  font-size: 1.25rem;
  line-height: 1;
  color: var(--dialog-close-color, var(--color-text-subtle, #555));
  padding: 0.25rem;
  width: var(--dialog-close-size, 2rem);
  height: var(--dialog-close-size, 2rem);
  flex-shrink: 0;
}

.dialog-body {
  padding: var(--dialog-body-padding, 1.5rem);
  overflow-y: var(--dialog-body-overflow, auto);
  flex: 1;
}

.dialog-footer {
  display: flex;
  justify-content: var(--dialog-footer-justify, flex-end);
  gap: var(--dialog-footer-gap, 0.75rem);
  padding: var(--dialog-footer-padding, 1rem 1.5rem);
  background: var(--dialog-footer-bg, var(--color-surface-subtle, #f9f9f9));
  border-top: var(--dialog-footer-border-top, 1px solid var(--color-border, #e0e0e0));
  flex-shrink: 0;
}
```

## Usage

```tsx
import { useRef } from 'react'
import Dialog from './dialog/dialog'
import Button from './button/button'
import './dialog/dialog.scss'

function App() {
  const dialogRef = useRef<HTMLDialogElement>(null)

  return (
    <>
      <Button type="button" onClick={() => dialogRef.current?.showModal()}>
        Open Dialog
      </Button>
      <Dialog
        dialogRef={dialogRef}
        title="Confirm Action"
        description="This action cannot be undone."
        onClose={() => dialogRef.current?.close()}
        footer={
          <>
            <Button type="button" variant="outline" onClick={() => dialogRef.current?.close()}>
              Cancel
            </Button>
            <Button type="button" color="primary" onClick={() => {}}>
              Confirm
            </Button>
          </>
        }
      >
        <p>Are you sure you want to proceed?</p>
      </Dialog>
    </>
  )
}
```
