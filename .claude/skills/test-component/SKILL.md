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
   Lower-case the user's input and strip the words `the`, `a`, `component`. If the result is empty or names a component without a reference doc, list `plugins/acss-kit/skills/components/references/components/*.md` and ask the user to pick.

2. **Read the reference doc.**
   Read `plugins/acss-kit/skills/components/references/components/<name>.md` once. You need three sections from it. For each, locate the `##` heading first, then take the first fenced block **within that section's range** (i.e. before the next `##` heading) — never the first fence in the file:
   - `## CSS Variables` — first ` ```scss ` block in that section. These are `:root` tokens.
   - `## SCSS Template` — first ` ```scss ` block in that section. The component styles. Use as-is (CSS nesting is native).
   - `## Usage Examples` — JSX snippets in that section, to convert to plain HTML.

3. **Convert Usage Examples JSX to HTML.**
   The Props Interface in the same doc documents which props map to which `data-*` attributes — read it and follow it. General rules:
   - **Tag:** derive the HTML element from the TSX Template's `UI as="..."` value, or from the root JSX tag in Usage Examples — never from the SCSS selector. A class like `.btn` doesn't tell you whether the element is `<button>`, `<a>`, or `<input>`.
   - **Class:** the SCSS Template's root selector gives the className (e.g. `.btn` → `class="btn"`).
   - Compound components (`Card.Title`, `Table.Row`, etc.): use the nested SCSS selectors for the className, and the matching JSX/TSX for the tag.
   - `disabled` prop → `aria-disabled="true"` plus `is-disabled` class. Never the native `disabled` attribute.
   - Drop event handlers (`onClick`, etc.) — this is a static preview.

   Lay out one `<section>` per variant family (color, size, style, state) with a small heading. Cover every distinct example from Usage Examples.

4. **Generate the HTML file.**
   Run `mkdir -p tests/.tmp` and write `tests/.tmp/preview-<name>.html` using this template:

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
   Use `python3 -m http.server` on port `8765` — zero install, already a project dependency.

   If `curl` is available, probe the port to reuse an already-running server (an optimization, not required):
   ```sh
   curl -fsS -o /dev/null http://localhost:8765/ 2>/dev/null
   ```
   On non-zero exit (or if `curl` is missing — skip the probe), spawn a new server using the Bash tool with `run_in_background: true` so it survives the turn:
   ```sh
   python3 -m http.server 8765 --directory tests/.tmp --bind 127.0.0.1
   ```
   Then `sleep 0.3` to let it bind. If the port is already taken (python errors with `OSError: [Errno 98] Address already in use`, or curl shows content that doesn't list `preview-*.html`), bump to `8766`/`8767` and retry — don't kill the squatter. If `python3` isn't on PATH, skip the server entirely and use the `file://` URL.

   Open the URL, swallowing errors for headless environments:
   ```sh
   xdg-open  http://localhost:<port>/preview-<name>.html 2>/dev/null \
     || open http://localhost:<port>/preview-<name>.html 2>/dev/null \
     || true
   ```
   Always print both URLs so the user has a manual fallback, and tell them how to stop the server:
   ```
   Preview: http://localhost:<port>/preview-<name>.html
   Fallback: file:///<abs-path>/tests/.tmp/preview-<name>.html
   Stop server: pkill -f "http.server <port> --directory tests/.tmp"
   ```

6. **Stay in scope.**
   If the user asks for something a static preview can't show (click handlers, focus trap, real interaction), say so and recommend `tests/e2e.sh` instead. Don't extend this skill into a general test harness.

## Edge cases

- **Compound components** (`Card`, `Table`, `List`): the SCSS has nested selectors like `.card .card-title`. Replicate the DOM structure with the matching tags/classes.
- **Components requiring JS** (`Dialog` uses native `<dialog>` with `showModal()`, `Popover` uses `popover` attribute): render the open state directly via the `open` attribute / `popover` attribute so the visual state shows without scripting.
- **Form controls** (`Input`, `Checkbox`, `Field`): always pair with a `<label>` so the preview shows the accessible-name story.
- **Icon components**: if the SCSS doesn't define the glyph, render placeholder SVGs (a 16×16 square with the variant name as text) — note this in a comment.

## What success looks like

User says "test the button". In under 5 seconds you produce `tests/.tmp/preview-button.html`, start (or reuse) `python3 -m http.server 8765 --directory tests/.tmp` in the background, attempt to open `http://localhost:8765/preview-button.html`, and print both that URL and the `file://` fallback. The page shows: default button, every color variant in a row, every size variant in a row, every style variant (outline/pill/text/icon) in a row, a disabled example, and a block-width example — all styled by the component's actual CSS.
