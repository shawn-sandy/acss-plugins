# Breakpoints

Responsive variants are generated for every family with `families.<f>.responsive: true` in [`utilities.tokens.json`](../../../assets/utilities.tokens.json). The breakpoint values match fpkit upstream (`@fpkit/acss@6.5.0`) verbatim.

## Default breakpoints

| Prefix | Min width | Pixel equivalent | Source |
|---|---|---|---|
| `sm` | `30rem` | 480 px | `_display.scss` (fpkit) |
| `md` | `48rem` | 768 px | `_display.scss` (fpkit) |
| `lg` | `62rem` | 992 px | `_display.scss` (fpkit) |
| `xl` | `80rem` | 1280 px | `_display.scss` (fpkit) |

The `print` prefix is special — it maps to `@media print` rather than a viewport width. fpkit only ships `.print:hide` upstream; this plugin matches that scope and does not add other `print:` variants.

## Media-query syntax

The generator emits modern range syntax matching fpkit:

```css
@media (width >= 30rem) {
  .sm\:hide { display: none !important; }
  .sm\:show { display: revert !important; }
  /* … every base class with `responsive: true` */
}
```

Not the legacy `@media (min-width: 30rem)` form. Browser support: Chrome 104+, Firefox 102+, Safari 16.4+ (≥ Apr 2023). All evergreen browsers ship it.

## JSX usage

In CSS the colon is escaped (`\:`) because `:` is a pseudo-class delimiter; in JSX `className` strings, write the colon literally:

```tsx
<div className="hide sm:show">
  Mobile-only header
</div>

<button className="bg-primary p-4 md:p-6 lg:p-8">
  Padded button
</button>
```

## Adding a custom breakpoint

`/utility-tune "add an xs breakpoint at 20rem"` will:

1. Edit `breakpoints.xs` in `utilities.tokens.json`.
2. Regenerate the bundle — every family with `responsive: true` will get `.xs:` variants.
3. Run `validate_utilities.py` with `--prefixes=sm,md,lg,xl,xs,print` so the new prefix is accepted.

Breakpoint **removal** is also supported but bundle size will drop and any project consuming `.<removed>:` classes will fall through to the base. Always communicate the removal to consumers.

## Responsive-parity check

The validator enforces that every responsive class declared at one breakpoint is declared at every other declared breakpoint. So if your tokens.json enables `responsive: true` for `flex`, every `.flex-*` class must appear at `sm:`, `md:`, `lg:`, *and* `xl:` — partial declarations fail the contract.

This guard prevents the silent pattern where a developer writes `.md:flex-row` in source, but the bundle only emits `.sm:flex-row` (so the class disappears at md+ and the row falls back to whatever the base value is). Generators that loop over breakpoints are the safe path; hand-authored CSS within a per-family partial must mirror across all breakpoints declared in the file.

`print` is exempt from the parity check (it's a single-purpose prefix, not part of the responsive family).
