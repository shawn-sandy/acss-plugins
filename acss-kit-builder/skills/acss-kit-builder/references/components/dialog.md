# Component: Dialog

## Overview

A modal dialog using the native HTML `<dialog>` element. The native element provides focus trapping automatically via `showModal()` — no npm packages needed. Supports a header/body/footer structure, dismissable via Escape key (built-in), backdrop click, and a close button.

## Generation Contract

```
export_name: Dialog (+ DialogHeader, DialogBody, DialogFooter)
file: dialog.tsx
scss: dialog.scss
imports: UI from '../ui', Button from '../button/button'
dependencies: [button]
```

Note: Unlike the fpkit source, the generated Dialog does NOT depend on `icon-button`. The close button is rendered using a text "×" character or a simple Button variant. This simplifies the dependency tree.

## Why Native `<dialog>`?

- `showModal()` automatically traps focus within the dialog (no `focus-trap` package)
- Focus returns to the trigger element on `close()`
- Escape key fires `cancel` event automatically
- Native `::backdrop` pseudo-element for the overlay
- `aria-modal` behavior built in

## Props Interface

```tsx
export type DialogProps = {
  /** Ref to the dialog element — required for showModal()/close() */
  dialogRef: React.RefObject<HTMLDialogElement>
  /** Whether to open on mount */
  openOnMount?: boolean
  /** Callback when dialog is closed */
  onClose?: () => void
  /** Dialog title for aria-labelledby */
  title?: string
  /** Dialog description for aria-describedby */
  description?: string
  /** Whether to show a close button in the header */
  showCloseButton?: boolean
  /** Dialog content */
  children?: React.ReactNode
  /** Footer action buttons */
  footer?: React.ReactNode
  /** CSS class name */
  classes?: string
  /** Inline styles */
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'dialog'>, 'open'>

export type DialogHeaderProps = {
  children?: React.ReactNode
  onClose?: () => void
  showCloseButton?: boolean
  classes?: string
}

export type DialogBodyProps = {
  children?: React.ReactNode
  classes?: string
}

export type DialogFooterProps = {
  children?: React.ReactNode
  classes?: string
}
```

## Key Pattern: showModal / close

```tsx
// Parent component usage
const dialogRef = useRef<HTMLDialogElement>(null)

// Open
const openDialog = () => dialogRef.current?.showModal()

// Close
const closeDialog = () => dialogRef.current?.close()

// Pass ref to Dialog
<Dialog dialogRef={dialogRef} onClose={closeDialog} title="Confirm Action">
  <p>Are you sure?</p>
  <Dialog.Footer>
    <Button type="button" onClick={closeDialog} variant="outline">Cancel</Button>
    <Button type="button" color="primary" onClick={handleConfirm}>Confirm</Button>
  </Dialog.Footer>
</Dialog>
```

## Key Pattern: Backdrop Click Close

```tsx
const handleBackdropClick = (e: React.MouseEvent<HTMLDialogElement>) => {
  // e.target is the dialog itself (not inner content) when backdrop is clicked
  if (e.currentTarget === e.target) {
    e.currentTarget.close()
    onClose?.()
  }
}
```

## Full Implementation Reference

```tsx
import UI from '../ui'
import React from 'react'
import Button from '../button/button'

// --- Types (inline) ---
// [DialogProps, DialogHeaderProps, DialogBodyProps, DialogFooterProps as above]

// --- Sub-components ---
const DialogHeader = ({ children, onClose, showCloseButton = true, classes }: DialogHeaderProps) => (
  <UI as="div" classes={`dialog-header${classes ? ' ' + classes : ''}`}>
    <UI as="div" classes="dialog-header-content">{children}</UI>
    {showCloseButton && (
      <Button
        type="button"
        variant="icon"
        aria-label="Close dialog"
        onClick={onClose}
        classes="dialog-close"
      >
        ×
      </Button>
    )}
  </UI>
)
DialogHeader.displayName = 'Dialog.Header'

const DialogBody = ({ children, classes }: DialogBodyProps) => (
  <UI as="div" classes={`dialog-body${classes ? ' ' + classes : ''}`}>
    {children}
  </UI>
)
DialogBody.displayName = 'Dialog.Body'

const DialogFooter = ({ children, classes }: DialogFooterProps) => (
  <UI as="div" classes={`dialog-footer${classes ? ' ' + classes : ''}`}>
    {children}
  </UI>
)
DialogFooter.displayName = 'Dialog.Footer'

// --- Root component ---
const DialogRoot = React.forwardRef<HTMLDialogElement, DialogProps>(({
  dialogRef,
  openOnMount,
  onClose,
  title,
  description,
  showCloseButton = true,
  children,
  footer,
  classes,
  styles,
  ...props
}: DialogProps, _ref) => {
  const titleId = title ? `dialog-title-${Math.random().toString(36).slice(2, 7)}` : undefined

  const handleClose = () => {
    dialogRef.current?.close()
    onClose?.()
  }

  const handleBackdropClick = (e: React.MouseEvent<HTMLDialogElement>) => {
    if (e.currentTarget === e.target) handleClose()
  }

  return (
    <UI
      as="dialog"
      ref={dialogRef}
      open={openOnMount}
      classes={`dialog${classes ? ' ' + classes : ''}`}
      styles={styles}
      aria-labelledby={titleId}
      onClick={handleBackdropClick}
      {...props}
    >
      {title && (
        <DialogHeader onClose={handleClose} showCloseButton={showCloseButton}>
          <UI as="h2" id={titleId} classes="dialog-title">{title}</UI>
          {description && <UI as="p" classes="dialog-description">{description}</UI>}
        </DialogHeader>
      )}
      <DialogBody>{children}</DialogBody>
      {footer && <DialogFooter>{footer}</DialogFooter>}
    </UI>
  )
})
DialogRoot.displayName = 'Dialog'

// --- Compound assembly ---
type DialogComponent = typeof DialogRoot & {
  Header: typeof DialogHeader
  Body: typeof DialogBody
  Footer: typeof DialogFooter
}

export const Dialog = Object.assign(DialogRoot, {
  Header: DialogHeader,
  Body: DialogBody,
  Footer: DialogFooter,
}) as DialogComponent

export default Dialog
```

## CSS Variables

```scss
--dialog-bg: var(--color-surface, #fff);
--dialog-color: var(--color-text, inherit);
--dialog-padding: 0;
--dialog-radius: 0.5rem;
--dialog-width: 32rem;
--dialog-max-width: 90vw;
--dialog-max-height: 85vh;
--dialog-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
--dialog-border: none;

--dialog-header-padding: 1.5rem;
--dialog-header-border-bottom: 1px solid var(--color-border, #e0e0e0);

--dialog-title-fs: 1.25rem;
--dialog-title-fw: 600;
--dialog-title-color: var(--color-text, inherit);

--dialog-body-padding: 1.5rem;
--dialog-body-overflow: auto;

--dialog-footer-padding: 1rem 1.5rem;
--dialog-footer-bg: var(--color-surface-subtle, #f9f9f9);
--dialog-footer-border-top: 1px solid var(--color-border, #e0e0e0);
--dialog-footer-gap: 0.75rem;
--dialog-footer-justify: flex-end;

--dialog-close-size: 2rem;
--dialog-close-color: var(--color-text-subtle, #555);

--dialog-backdrop-bg: rgba(0, 0, 0, 0.5);
```

## SCSS Pattern

```scss
// dialog.scss
.dialog {
  background: var(--dialog-bg, #fff);
  color: var(--dialog-color, inherit);
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
  border-bottom: var(--dialog-header-border-bottom, 1px solid #e0e0e0);
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
  color: var(--dialog-close-color, #555);
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
  background: var(--dialog-footer-bg, #f9f9f9);
  border-top: var(--dialog-footer-border-top, 1px solid #e0e0e0);
  flex-shrink: 0;
}
```

## Usage Examples

```tsx
import { useRef } from 'react'
import Dialog from './dialog/dialog'
import Button from './button/button'
import './dialog/dialog.scss'
import './button/button.scss'

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
        onClose={() => console.log('closed')}
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

## Dependencies

When generating Dialog, Claude must first ensure these exist in the target directory:

1. `ui.tsx` — foundation (auto-created on first run)
2. `button/button.tsx` + `button/button.scss` — for close button and footer actions

Check if `button.tsx` exists before generating. If it exists, import from it. If not, generate it first.

Dependency order:
1. `ui.tsx` (foundation)
2. `button/button.tsx` + `button/button.scss`
3. `dialog/dialog.tsx` + `dialog/dialog.scss`
