# Button size scale redistribution

## Context

The current button scale renders all sizes too large at the bottom and not differentiated
enough at the top. The default (`md = 0.9375rem` ≈ 15px) feels heavy in the sandbox
preview, and `xl = 1.25rem` ≈ 20px isn't visibly bigger enough than `lg = 1.125rem`
(only 2px difference) to read as a true "extra-large" emphasis.

The first attempt at this plan only mutated the default mapping and the `xl` token.
That would have collided `--btn-size-md` with `--btn-size-sm` at the same value
(0.8125rem) — collapsing the scale's contract that every size step is visually distinct.
This revision **redistributes the entire 5-step scale** so each `data-btn` step still
renders at a distinguishable size while moving the default down and the top end up.

## Proposed scale

| Token | Before | After | Δ | Notes |
|---|---|---|---|---|
| `--btn-size-xs` | 0.6875rem (11px) | **0.625rem** (10px) | −1px | bottom of scale, still legible for icon-buttons |
| `--btn-size-sm` | 0.8125rem (13px) | **0.6875rem** (11px) | −2px | takes over the old `xs` value |
| `--btn-size-md` | 0.9375rem (15px) | **0.8125rem** (13px) | −2px | new default; takes the old `sm` value |
| `--btn-size-lg` | 1.125rem (18px) | 1.125rem (18px) | — | unchanged; sits midway between new md and xl, preserves a deliberate non-uniform top curve |
| `--btn-size-xl` | 1.25rem (20px) | **1.5rem** (24px) | +4px | clearer emphasis above `lg` |

Step gaps after the change: 10 → 11 → 13 → 18 → 24 (Δ 1 / 2 / 5 / 6) — every step
distinct, gentle progression at the bottom, more pronounced jumps at the top.

## Visual preview (before vs. after)

Buttons drawn at true pixel sizes with the same padding ratios as the SCSS template
(`block = font × 0.5`, `inline = font × 1.5`), primary color fill (`#0066cc`), 6px
corner radius. Each row shows xs / sm / md (default) / lg / xl from left to right.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" width="640" height="360" role="img" aria-label="Button scale before/after comparison">
  <style>
    .lbl { font: 600 13px system-ui, sans-serif; fill: #6b7280; }
    .axis { font: 500 11px system-ui, sans-serif; fill: #9ca3af; }
    .btn-text { font-family: system-ui, sans-serif; font-weight: 500; fill: #ffffff; text-anchor: middle; dominant-baseline: central; }
    .btn { fill: #0066cc; }
    .btn-default { fill: #0052a3; }
    .divider { stroke: #e5e7eb; stroke-width: 1; }
    .delta { font: 500 10px system-ui, sans-serif; fill: #9ca3af; text-anchor: middle; }
    .delta-down { fill: #b91c1c; }
    .delta-up { fill: #047857; }
  </style>

  <!-- ============= BEFORE ============= -->
  <text x="20" y="24" class="lbl">BEFORE</text>
  <text x="20" y="42" class="axis">xs 11 / sm 13 / md 15 / lg 18 / xl 20  (px)</text>

  <!-- xs 11px → 47×22 -->
  <rect class="btn" x="20" y="80" width="47" height="22" rx="6" />
  <text class="btn-text" x="43" y="91" font-size="11">XS</text>
  <text x="43" y="118" class="axis" text-anchor="middle">xs</text>

  <!-- sm 13px → 55×26 -->
  <rect class="btn" x="85" y="78" width="55" height="26" rx="6" />
  <text class="btn-text" x="112" y="91" font-size="13">SM</text>
  <text x="112" y="118" class="axis" text-anchor="middle">sm</text>

  <!-- md 15px (default) → 63×30 -->
  <rect class="btn-default" x="160" y="76" width="63" height="30" rx="6" />
  <text class="btn-text" x="191" y="91" font-size="15">MD</text>
  <text x="191" y="118" class="axis" text-anchor="middle">md (default)</text>

  <!-- lg 18px → 76×36 -->
  <rect class="btn" x="245" y="73" width="76" height="36" rx="6" />
  <text class="btn-text" x="283" y="91" font-size="18">LG</text>
  <text x="283" y="118" class="axis" text-anchor="middle">lg</text>

  <!-- xl 20px → 84×40 -->
  <rect class="btn" x="345" y="71" width="84" height="40" rx="6" />
  <text class="btn-text" x="387" y="91" font-size="20">XL</text>
  <text x="387" y="118" class="axis" text-anchor="middle">xl</text>

  <line class="divider" x1="20" y1="160" x2="620" y2="160" />

  <!-- ============= AFTER ============= -->
  <text x="20" y="190" class="lbl">AFTER</text>
  <text x="20" y="208" class="axis">xs 10 / sm 11 / md 13 / lg 18 / xl 24  (px)</text>

  <!-- xs 10px → 43×20 -->
  <rect class="btn" x="20" y="246" width="43" height="20" rx="6" />
  <text class="btn-text" x="41" y="256" font-size="10">XS</text>
  <text x="41" y="284" class="axis" text-anchor="middle">xs</text>
  <text x="41" y="298" class="delta delta-down">−1px</text>

  <!-- sm 11px → 47×22 -->
  <rect class="btn" x="85" y="245" width="47" height="22" rx="6" />
  <text class="btn-text" x="108" y="256" font-size="11">SM</text>
  <text x="108" y="284" class="axis" text-anchor="middle">sm</text>
  <text x="108" y="298" class="delta delta-down">−2px</text>

  <!-- md 13px (default) → 55×26 -->
  <rect class="btn-default" x="160" y="243" width="55" height="26" rx="6" />
  <text class="btn-text" x="187" y="256" font-size="13">MD</text>
  <text x="187" y="284" class="axis" text-anchor="middle">md (default)</text>
  <text x="187" y="298" class="delta delta-down">−2px</text>

  <!-- lg 18px (unchanged) → 76×36 -->
  <rect class="btn" x="245" y="239" width="76" height="36" rx="6" />
  <text class="btn-text" x="283" y="257" font-size="18">LG</text>
  <text x="283" y="284" class="axis" text-anchor="middle">lg</text>
  <text x="283" y="298" class="delta">0</text>

  <!-- xl 24px → 100×48 -->
  <rect class="btn" x="345" y="235" width="100" height="48" rx="6" />
  <text class="btn-text" x="395" y="259" font-size="24">XL</text>
  <text x="395" y="298" class="axis" text-anchor="middle">xl</text>
  <text x="395" y="312" class="delta delta-up">+4px</text>

  <!-- Side notes -->
  <text x="475" y="96" class="axis">old md/xl gap: 5px</text>
  <text x="475" y="265" class="axis">new md/xl gap: 11px</text>
</svg>

The darker rectangle in each row is the *default* (`md`) — easy to see how the default
shrinks while xl picks up emphasis. Lg is the visual anchor that doesn't move, which
keeps the upper portion of the scale calibrated against an existing reference.

## Objective

- Redistribute all five button size tokens (`xs/sm/md/lg/xl`) per the table above so
  every step remains visually distinct.
- Keep `--btn-fs` chained to `--btn-size-md` (md *is* the default — semantic name stays
  honest); just update its fallback to match the new value.
- Update every `var(... , <fallback>)` in the same file to remain coherent with the
  declared defaults, per existing file convention.
- Run `tests/run.sh` to confirm the structural gate stays green.
- Launch the Vite sandbox and load it in Chrome via the browser MCP for visual review.

## Steps

1. **Edit the source-of-truth reference doc**
   `plugins/acss-kit/skills/components/references/components/button.md`:

   *Size tokens (lines 181–185):*
   - L181: `--btn-size-xs: 0.6875rem;` → `--btn-size-xs: 0.625rem;`
   - L182: `--btn-size-sm: 0.8125rem;` → `--btn-size-sm: 0.6875rem;`
   - L183: `--btn-size-md: 0.9375rem;   // default` → `--btn-size-md: 0.8125rem;   // default`
   - L184: `--btn-size-lg: 1.125rem;` (no change)
   - L185: `--btn-size-xl: 1.25rem;` → `--btn-size-xl: 1.5rem;`

   *Default + padding fallbacks (lines 192, 195, 196):*
   - L192: `--btn-fs: var(--btn-size-md, 0.9375rem);`
     → `--btn-fs: var(--btn-size-md, 0.8125rem);`
   - L195: `calc(var(--btn-fs, 0.9375rem) * 0.5)`
     → `calc(var(--btn-fs, 0.8125rem) * 0.5)`
   - L196: `calc(var(--btn-fs, 0.9375rem) * 1.5)`
     → `calc(var(--btn-fs, 0.8125rem) * 1.5)`

   *SCSS template fallbacks (lines 237, 240, 241):*
   - L237: `font-size: var(--btn-fs, 0.9375rem);` → `var(--btn-fs, 0.8125rem);`
   - L240: `padding-block: var(--btn-padding-block, 0.46875rem);`
     → `padding-block: var(--btn-padding-block, 0.40625rem);`  *(= 0.8125 × 0.5)*
   - L241: `padding-inline: var(--btn-padding-inline, 1.40625rem);`
     → `padding-inline: var(--btn-padding-inline, 1.21875rem);`  *(= 0.8125 × 1.5)*

   *Size-variant selector fallbacks (lines 273–276):*
   - L273: `&[data-btn~="xs"] { font-size: var(--btn-size-xs, 0.6875rem); }`
     → `... 0.625rem); }`
   - L274: `&[data-btn~="sm"] { font-size: var(--btn-size-sm, 0.8125rem); }`
     → `... 0.6875rem); }`
   - L275: `&[data-btn~="lg"] { font-size: var(--btn-size-lg, 1.125rem); }` (no change)
   - L276: `&[data-btn~="xl"] { font-size: var(--btn-size-xl, 1.25rem); }`
     → `... 1.5rem); }`

   *Why all the fallback math:* the file's existing convention keeps every
   `var(... , <fallback>)` coherent with the declared default. `tests/run.sh` doesn't
   math-check fallbacks, so a slip would survive validation but surface in any
   context where the custom property is undefined.

2. **Mirror the change into the sandbox preview**
   `tests/sandbox/src/components/fpkit/button.scss` — apply the same line-by-line edits
   from step 1 (this file is a hand-maintained twin of the reference doc; `tests/run.sh`
   does *not* re-extract into the sandbox).

3. **Add a full-scale preview row to the sandbox app**
   `tests/sandbox/src/App.tsx` — extend the existing kit-add smoke section (lines
   122–127) to render all five sizes so the redistribution is visible end-to-end:
   ```tsx
   <Card.Footer>
     <Button type="button" size="xs">XS</Button>
     <Button type="button" size="sm">SM</Button>
     <Button type="button">MD (default)</Button>
     <Button type="button" size="lg">LG</Button>
     <Button type="button" size="xl">XL</Button>
   </Card.Footer>
   ```
   Reuses the already-imported `Button` from `./components/fpkit/button` (App.tsx:6) —
   no new imports needed. The `size` prop already wires through to `data-btn`
   (button.md:35, merge logic at button.md:110–113).

4. **Run the structural test gate**
   ```bash
   tests/run.sh
   ```
   Expectations: extracts the updated `button.md` into `tests/.tmp/extracted/button/`,
   syntax-checks the SCSS, runs the manifest/WCAG validators. Should pass — only token
   values changed, structure is untouched.

5. **Start the Vite sandbox**
   ```bash
   npm --prefix tests/sandbox run dev
   ```
   Run in background; capture the printed local URL (default `http://localhost:5173`).

6. **Open in Chrome via the browser MCP**
   - `ToolSearch select:mcp__claude-in-chrome__tabs_context_mcp` then call it.
   - `ToolSearch select:mcp__claude-in-chrome__tabs_create_mcp` then create a new tab
     pointing at the dev URL.
   - `ToolSearch select:mcp__claude-in-chrome__read_page` (or `get_page_text`) to
     confirm the buttons rendered, then hand control to the user for visual review.
   - Do not commit until the user confirms the preview looks right.

## Critical files

- `plugins/acss-kit/skills/components/references/components/button.md` — source of truth.
- `tests/sandbox/src/components/fpkit/button.scss` — preview-only mirror, must be kept in sync.
- `tests/sandbox/src/App.tsx` — extend kit-add smoke section with full size row.
- `tests/run.sh` — validation gate.
- `tests/sandbox/package.json` — `npm run dev` script (already wired).

## Reused existing pieces (no new code)

- The `Button` component is already imported in `tests/sandbox/src/App.tsx:6`.
- The `size` prop already wires through to `data-btn` — every existing size variant
  selector (`xs/sm/lg/xl`) and the default `.btn` rule pick up the new values
  automatically because they all reference `--btn-size-*` tokens via `var()`.
- `--btn-size-lg` stays at `1.125rem` (existing value), so no change to the lg path.

## Verification

- **Structural gate:** `tests/run.sh` exits 0 with the "extract + syntax-check" and
  manifest sections green.
- **Visual preview:** in Chrome at `http://localhost:5173`, the kit-add smoke section
  shows the 5-button row XS / SM / MD / LG / XL with strictly increasing sizes (no two
  buttons looking identical), default reads ≈13px, XL reads ≈24px.
- **Spot-check the extracted artifact:** open `tests/.tmp/extracted/button/button.scss`
  after `tests/run.sh` runs and confirm the new font-size and fallback values landed.
- **Stop criterion:** user confirms the preview looks right before any commit.

## Out of scope

- No commit of the change (user requested preview-before-commit).
- No bump of `plugin.json` version — that belongs to a separate `/release-plugin` step
  once the visual is approved.
- No changes to `acss-utilities` — utilities don't override button tokens.
- No edit to `--btn-fs`'s chain target (still `--btn-size-md`); only the value of `md`
  and the cascade of fallbacks change.

## Unresolved questions

None — full-scale redistribution has been derived from the user's directive
("modify the other tokens so we don't lose scale") and the existing token contract.
