---
name: test-component
description: Render a quick visual preview of an acss-kit component in the default browser. Use when the user says "test component", "test the button", "show me the alert", "preview <component>", or any phrasing that asks to see what a component looks like. Produces a self-contained HTML file with all variants from the component's Usage Examples.
disable-model-invocation: false
---

# test-component

Goal: render a one-page visual preview of an `acss-kit` component fast — no dev server, no build step, no React. The component's SCSS works as plain CSS in any modern browser (CSS nesting is native in Chrome 112+, Firefox 117+, Safari 16.4+), so we copy it verbatim into a `<style>` tag and render the variants as static HTML.

Usage examples (any of these should trigger):
- "test component button"
- "test the alert"
- "show me what the card looks like"
- "preview dialog"

## Steps

1. **Resolve the component name.**
   - Lower-case it. Strip filler words ("the", "a", "component").
   - Verify `plugins/acss-kit/skills/components/references/components/<name>.md` exists.
   - If the name is ambiguous or missing, list `plugins/acss-kit/skills/components/references/components/*.md` and ask the user to pick.

2. **Read the reference doc.**
   Read the whole file. You need three sections:
   - `## CSS Variables` — first fenced ``` ```scss ``` block. These are `:root` tokens.
   - `## SCSS Template` — first fenced ``` ```scss ``` block. The component styles. Use as-is (CSS nesting is native).
   - `## Usage Examples` — JSX snippets you'll convert to plain HTML.

3. **Convert Usage Examples JSX to HTML.**
   Each component's reference doc tells you how the JSX maps to DOM. The general rule for `acss-kit`:
   - The React component renders a single semantic element with a class and data attributes.
   - Look at the SCSS Template's root selector (e.g. `.btn`, `.alert`, `.card`) — that's the className.
   - Props that map to `data-*` attributes (`color="primary"` → `data-color="primary"`, `size="lg"` → `data-btn="lg"`, `variant="outline"` → `data-style="outline"`) are documented in the Props Interface.
   - For Button specifically: combine `size` + `block` + raw `data-btn` into a single space-separated `data-btn` token (see Key Pattern: data-btn Merging in `button.md`).
   - For compound components (Card.Title, Card.Content, Table.Row, etc.) check the SCSS for the nested selectors and use the matching tag/class.
   - Replace `disabled` prop with `aria-disabled="true"` and add the `is-disabled` class — never use the native `disabled` attribute.
   - Drop event handlers (`onClick`, etc.) — this is a static preview.

   Aim for one `<section>` per variant family (color, size, style, state) with a small heading. Cover every distinct example that appears in Usage Examples.

4. **Generate the HTML file.**
   Write to `tests/.tmp/preview-<name>.html` (create `tests/.tmp/` if missing). Template:

   ````html
   <!doctype html>
   <html lang="en">
   <head>
     <meta charset="utf-8">
     <title>Preview: <PascalCaseName></title>
     <style>
       /* ---- Page chrome (not part of the component) ---- */
       *, *::before, *::after { box-sizing: border-box; }
       body {
         margin: 0;
         padding: 2rem;
         font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
         background: #fafafa;
         color: #1a1a1a;
         line-height: 1.5;
       }
       h1 { margin: 0 0 0.5rem; font-size: 1.5rem; }
       h2 { margin: 2rem 0 0.75rem; font-size: 1rem; color: #555; font-weight: 600; }
       .meta { color: #666; font-size: 0.875rem; margin-bottom: 2rem; }
       .row { display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center; }
       .swatch { display: inline-block; padding: 1rem; background: #fff; border: 1px solid #e5e5e5; border-radius: 0.5rem; }

       /* ---- Component CSS Variables (verbatim from <name>.md) ---- */
       :root {
         /* paste the CSS Variables block here, indented */
       }

       /* ---- Component SCSS Template (verbatim, used as native CSS) ---- */
       /* paste the SCSS Template block here */
     </style>
   </head>
   <body>
     <h1>Preview: <PascalCaseName></h1>
     <p class="meta">Source: <code>plugins/acss-kit/skills/components/references/components/<name>.md</code></p>

     <h2>Default</h2>
     <div class="row swatch">
       <!-- one minimal example -->
     </div>

     <h2>Variant family 1 (e.g. Color)</h2>
     <div class="row swatch">
       <!-- one element per variant -->
     </div>

     <!-- repeat per variant family -->
   </body>
   </html>
   ````

   Notes:
   - Paste the CSS Variables block contents inside `:root { ... }`. Strip any SCSS-only syntax (there shouldn't be any in CSS Variables blocks — they're plain custom-property declarations).
   - Paste the SCSS Template verbatim into the `<style>` tag. Modern CSS handles `&:hover`, `&[data-attr]`, and nested selectors natively. Do NOT compile.
   - If the SCSS uses `@use`, `@mixin`, `@include`, `@if`, or `$variables` (rare in this repo — components are kept var()-driven), call that out and skip those lines with an HTML comment explaining what was dropped. The user can decide whether to address it.

5. **Serve it on a lightweight HTTP server, then open it.**
   Python 3 is already a project dependency, so `python3 -m http.server` gives us a zero-install static server. Default port: `8765`.

   First, check whether a server is already up on that port (re-runs of this skill should reuse it, not spawn duplicates):
   ```sh
   curl -fsS -o /dev/null http://localhost:8765/ 2>/dev/null
   ```
   - Exit 0 → server already running, skip the spawn step.
   - Non-zero → start the server. Use the **Bash tool with `run_in_background: true`** so it keeps running after this turn:
     ```sh
     python3 -m http.server 8765 --directory tests/.tmp --bind 127.0.0.1
     ```
     Then poll the port up to ~5 times with a short sleep until `curl` returns 0, so the open step doesn't race the server's startup.
   - If port `8765` is taken by something that *isn't* our server (curl returns HTML you don't recognize, or the server's directory listing doesn't show `preview-*.html`), bump to `8766`, `8767`, etc. Don't kill whatever's already on `8765`.

   Then open the URL, swallowing errors so headless environments don't fail:
   ```sh
   xdg-open  http://localhost:8765/preview-<name>.html 2>/dev/null \
     || open http://localhost:8765/preview-<name>.html 2>/dev/null \
     || true
   ```
   **Always** print both URLs so the user has a manual fallback:
   ```
   Preview: http://localhost:8765/preview-<name>.html
   Fallback (no server): file:///<abs-path>/tests/.tmp/preview-<name>.html
   ```

   If `python3` isn't on PATH (extremely unlikely in this repo — every script under `plugins/acss-kit/scripts/` requires it), skip the server step entirely and use only the `file://` URL.

   Mention to the user that the server is running in the background and can be stopped with `pkill -f "http.server 8765"` (or whatever port was used) when they're done.

6. **Don't over-engineer.**
   - No screenshot generation, no Puppeteer, no React, no Vite, no theme assembly, no `npx serve` / `live-server` / any node-side dep. Stick with `python3 -m http.server` — already on PATH.
   - Don't write tests, don't validate accessibility, don't run the full `tests/` harness — there's a separate `/review-component` skill for that.
   - If the user asks for something the static preview can't show (e.g. "test the click handler", "test focus trap"), say so explicitly and recommend `tests/e2e.sh` instead.

## Edge cases

- **Compound components** (`Card`, `Table`, `List`): the SCSS has nested selectors like `.card .card-title`. Replicate the DOM structure with the matching tags/classes.
- **Components requiring JS** (`Dialog` uses native `<dialog>` with `showModal()`, `Popover` uses `popover` attribute): render the open state directly via the `open` attribute / `popover` attribute so the visual state shows without scripting.
- **Form controls** (`Input`, `Checkbox`, `Field`): always pair with a `<label>` so the preview shows the accessible-name story.
- **Icon components**: if the SCSS doesn't define the glyph, render placeholder SVGs (a 16×16 square with the variant name as text) — note this in a comment.

## What success looks like

User says "test the button". In under 5 seconds you produce `tests/.tmp/preview-button.html`, start (or reuse) `python3 -m http.server 8765 --directory tests/.tmp` in the background, attempt to open `http://localhost:8765/preview-button.html`, and print both that URL and the `file://` fallback. The page shows: default button, every color variant in a row, every size variant in a row, every style variant (outline/pill/text/icon) in a row, a disabled example, and a block-width example — all styled by the component's actual CSS.
