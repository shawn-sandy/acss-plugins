# Token bridge

`utilities.css` references **fpkit-style token names** that don't all exist in acss-kit's role catalogue. The bridge translates between the two namespaces in both light and dark modes.

## The naming gap

| Used by utilities (fpkit-style) | Defined by acss-kit | Status |
|---|---|---|
| `--color-primary` | `--color-primary` | ✓ same name — no alias needed |
| `--color-success` | `--color-success` | ✓ |
| `--color-warning` | `--color-warning` | ✓ |
| `--color-info` | `--color-info` | ✓ |
| `--color-text` | `--color-text` | ✓ |
| `--color-text-muted` | `--color-text-muted` | ✓ |
| `--color-surface` | `--color-surface` | ✓ |
| `--color-error` | `--color-danger` | ✗ — bridge required |
| `--color-error-bg` | *(not defined)* | ✗ — bridge synthesizes via `color-mix` |
| `--color-success-bg` | *(not defined)* | ✗ — bridge synthesizes |
| `--color-warning-bg` | *(not defined)* | ✗ — bridge synthesizes |
| `--color-info-bg` | *(not defined)* | ✗ — bridge synthesizes |
| `--color-primary-light` | *(not defined)* | ✗ — bridge synthesizes |
| `--color-secondary` | *(not defined)* | ✗ — bridge falls back to `--color-primary` |
| `--color-surface-secondary` | `--color-surface-raised` | ✗ — bridge aliases |

## Bridge contract

1. Every alias defined in `:root` **must** also be defined in `[data-theme="dark"]`. The validator (`validate_utilities.py`) enforces parity. Without the dark block, every color utility resolves to its light-mode value when the page is in dark mode.
2. Every alias **must** have a hex fallback embedded in its `var()` chain or `color-mix` arguments. So if acss-kit isn't installed, the bridge still resolves to a sensible color.
3. Mix ratios are tuned for each mode: `12%` mix on `var(--color-{role}) → var(--color-background)` produces a subtle "subtle" background in light mode; `18%` produces a slightly stronger one in dark mode (background luminance is lower so the chip needs more saturation).

## Synthesized values via `color-mix`

The bridge uses CSS-native `color-mix(in oklch, …)` to synthesize `-bg` and `-light` variants:

```css
:root {
  --color-error-bg: color-mix(in oklch, var(--color-danger, #dc2626) 12%, var(--color-background, #ffffff));
}
```

Browser support for `color-mix(in oklch, …)`: Chrome 111+, Firefox 113+, Safari 16.2+ (≥ early 2023). For older browsers the embedded hex fallback resolves only the base role — `--color-error-bg` would fall back to `transparent` (the value declared in `.bg-error-subtle`'s `var()` fallback).

## Regenerating the bridge

`/utility-bridge` reads the user's active theme and rewrites the bridge to match. The defaults shipped at `assets/token-bridge.css` are appropriate for any acss-kit theme that follows the canonical role catalogue. Custom themes (extra roles, renamed roles) will need a re-run.

## Standalone use (without acss-kit)

If acss-kit is not installed, the bridge's hex fallbacks resolve to fpkit-default-ish values (`#dc2626` for error, `#16a34a` for success, etc.). Users who want their own color identity can either:

1. Author their own theme CSS that defines `--color-danger`, `--color-success`, … under `:root` and `[data-theme="dark"]`. The bridge composes on top.
2. Write a custom `token-bridge.css` that hard-codes their colors directly (skip the `var()` chain). Run `/utility-add --no-bridge` to skip the default bridge.

## Validator checks

`validate_utilities.py` recognizes `token-bridge*.css` by filename and runs the parity check:

```bash
python3 scripts/validate_utilities.py assets/token-bridge.css
```

Failures look like:

```json
{
  "ok": false,
  "filesScanned": 1,
  "reasons": [
    "token-bridge.css: bridge dark-mode parity gap — declared in :root but missing in [data-theme=\"dark\"]: --color-error-bg, --color-primary-light"
  ]
}
```

Fix by adding the missing aliases to the `[data-theme="dark"]` block, then re-run.
