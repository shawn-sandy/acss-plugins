# Vanilla-JS patterns for static-HTML components

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` — same upstream the React skill targets. The vanilla-JS patterns below are the behavior-equivalent rewrites of the inlined React hooks. See `https://github.com/shawn-sandy/acss/blob/v6.5.0/packages/fpkit/src/hooks/use-disabled-state.tsx` for the upstream React hook these patterns mirror.

This reference catalogues the vanilla-JS recipes used by stateful components when generated via `/kit-add-html`. Each per-component `.js` file imports the shared `wireDisabled` helper from `./_stateful.js` and adds component-specific behavior.

---

## Pattern 1 — Disabled state (`wireDisabled`)

**Used by:** Button, IconButton, Checkbox

The helper lives at `<componentsHtmlDir>/_stateful.js` and is copied once per project. It mirrors the inlined `useDisabledState` React hook by:

- Reading `aria-disabled` directly off the element so the source of truth is the DOM (no shadow state).
- Short-circuiting `click` and `keydown` (Enter / Space) when `aria-disabled === "true"`.
- Toggling the `is-disabled` class so SCSS can target either selector.
- Providing `setDisabled(next)` for runtime updates and `destroy()` for teardown.

```js
// button.js — usage example
import { wireDisabled } from './_stateful.js';

export function init(root = document) {
  for (const el of root.querySelectorAll('.btn')) {
    wireDisabled(el, {
      onActivate: (event) => {
        // user-supplied click handler — runs only when not disabled
        console.log('button activated', event.currentTarget);
      },
    });
  }
}
```

The helper is intentionally minimal — it does not manage `data-btn`, focus styling, or color variants because those are pure CSS concerns.

---

## Pattern 2 — Dialog open/close

**Used by:** Dialog

The native `<dialog>` element does the heavy lifting:

- `dialog.showModal()` opens with focus trap, scrim, and Escape-to-close.
- Backdrop click is wired by comparing `event.target === dialog` (the dialog element receives the click when the user clicks on the scrim).

```js
// dialog.js — idempotent: each element is guarded by a sentinel attribute
// so calling init() twice does not stack listeners. (addEventListener only
// de-duplicates when the exact same function reference is passed; the
// arrow functions below are fresh closures on every call, so without the
// sentinel they would compound.)
const SENTINEL = 'data-acss-dialog-init';

export function init(root = document) {
  for (const dialog of root.querySelectorAll('dialog.dialog')) {
    if (dialog.getAttribute(SENTINEL) === 'true') continue;
    dialog.setAttribute(SENTINEL, 'true');

    // Open triggers — any [data-dialog-open] pointing at this dialog's id.
    const openTriggers = root.querySelectorAll(
      `[data-dialog-open="${dialog.id}"]`,
    );
    for (const trigger of openTriggers) {
      trigger.addEventListener('click', () => dialog.showModal());
    }

    // Close triggers inside the dialog.
    const closeTriggers = dialog.querySelectorAll('[data-dialog-close]');
    for (const trigger of closeTriggers) {
      trigger.addEventListener('click', () => dialog.close());
    }

    // Backdrop click closes — only when the click is on the <dialog> itself,
    // not on a descendant (which would otherwise dismiss the dialog while
    // the user is interacting with its body).
    dialog.addEventListener('click', (event) => {
      if (event.target === dialog) dialog.close();
    });
  }
}
```

The sentinel attribute (`data-acss-dialog-init`) makes `init()` safe to call after dynamic DOM insertions, HMR refreshes, or page transitions — re-runs short-circuit on already-wired elements. Every per-component `init()` in this plugin (button.js, card.js, alert.js, dialog.js) follows the same pattern.

---

## Pattern 3 — Popover wiring

**Used by:** Popover

The native HTML Popover API (`popover` attribute + `popovertarget` on the trigger) handles open/close, light-dismiss, and stacking. No JS is required for the basic case — the `popover.html` snippet ships fully working markup.

```js
// popover.js — only needed when the user wants programmatic control
export function init(root = document) {
  // Optional: emit a custom 'popover:open' event when the popover transitions
  // to the open state, so the user's analytics / state code can hook in
  // without touching the markup.
  for (const pop of root.querySelectorAll('[popover].popover')) {
    pop.addEventListener('toggle', (event) => {
      if (event.newState === 'open') {
        pop.dispatchEvent(
          new CustomEvent('popover:open', { bubbles: true }),
        );
      }
    });
  }
}
```

Browsers without the Popover API (Safari < 17, Firefox < 125) need a polyfill. The vanilla-JS skill does **not** ship one — the user can add `@oddbird/popover-polyfill` in their entrypoint if they need broader support. This is the same trade-off the React generator makes.

---

## Pattern 4 — Input validation announcement

**Used by:** Input, Field

The HTML output ships with a `<span class="field-error" id="<input-id>-error">` paired with `aria-describedby` on the input. The vanilla-JS module wires these together at runtime so the user can call `setError(input, message)` to update the message and the announcement.

```js
// input.js
export function init(root = document) {
  for (const input of root.querySelectorAll('.input')) {
    const errorId = input.getAttribute('aria-describedby');
    if (!errorId) continue;
    const errorEl = root.getElementById(errorId);
    if (!errorEl) continue;

    // Surface validation state via data-validation attribute on the input
    // so SCSS can paint the right border color. The role="status" on the
    // error span makes assistive tech announce updates non-interruptively.
    input.addEventListener('invalid', (event) => {
      event.preventDefault();
      input.setAttribute('data-validation', 'invalid');
      errorEl.textContent = input.validationMessage;
    });
    input.addEventListener('input', () => {
      if (input.validity.valid) {
        input.removeAttribute('data-validation');
        errorEl.textContent = '';
      }
    });
  }
}
```

The error span must have `role="status"` (or `aria-live="polite"`) — the HTML Template provides that. The JS only writes the message; assistive tech announces it.

---

## Idempotence

All `init` functions follow the same rule: calling `init()` more than once on the same DOM tree must not produce duplicate listeners or inconsistent state. Follow these guidelines:

- Re-reading attributes on every event (no shadow state).
- Using `event.currentTarget` rather than captured references.
- For one-off setup that *must* not repeat (custom events, observers), guard with a sentinel attribute: `if (el.dataset.acssInit === 'true') continue; el.dataset.acssInit = 'true';`.

This matches the React generator's idempotence guarantee — `<Button>` mounted twice is two independent components with independent handlers, and the static-HTML output preserves that semantic.
