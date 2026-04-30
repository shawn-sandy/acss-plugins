# Document the browser-preview workflow for kit-add components

## Context

We just used a 3-step workflow to render the `kit-add`-generated `Button` component in Chrome for visual verification:

1. Compile the generated SCSS → CSS
2. Write a standalone HTML preview file (compiled CSS inlined, demo markup using the `data-*` variant attributes) into `tests/sandbox/`
3. Serve `tests/sandbox/` over `python3 -m http.server` and open the preview URL (manually or via the `claude-in-chrome` MCP)

This is the only way to *visually* smoke-test a generated component today. `tests/setup.sh` deliberately omits a dev server (see `tests/README.md` line 131 — "previewing rendered components in a real browser was explicitly removed because the goal is to test the skill output, not to render a React app"), so contributors with no playbook for visual checks tend to either skip the visual verification entirely or reach for a heavier Vite/Storybook setup.

The intended outcome of this plan: capture the workflow as a task-oriented recipe so any contributor can reproduce it in under a minute, **without** contradicting the existing "no dev server in the sandbox" stance — the recipe is framed as a static-HTML preview (compiled CSS + plain markup), not a React dev server.

## Approach

Add **one new recipe** to `plugins/acss-kit/docs/recipes.md` and **one cross-reference line** in `tests/README.md`.

### File 1 — `plugins/acss-kit/docs/recipes.md` (add new section)

Append a `## Preview a generated component in a browser` section after the existing recipes. The section follows the file's existing shape (intro paragraph → Prerequisites → numbered steps → expected outcome). Concretely:

- **Intro** — one paragraph: this is an opt-in, static-HTML smoke check that exercises the *compiled CSS and `data-*` selectors*; it does not boot React. Use it to eyeball variant coverage after generating a new component, not to test event handlers.
- **Prerequisites:**
  - `tests/sandbox/` exists (run `tests/setup.sh` if not — link to `tests/README.md#demo-fixture`)
  - The target component has been generated via `/kit-add <name>` into the sandbox
  - Python 3 on `PATH` (no extra deps — uses `python3 -m http.server`)
- **Steps (numbered):**
  1. From `tests/sandbox/`, compile the SCSS:
     ```sh
     npx sass --no-source-map src/components/fpkit/<name>/<name>.scss > /tmp/<name>.css
     ```
     (The recipe does not need to dump CSS to a separate file — but stating the option lets contributors inspect the compiled output if `<name>-preview.html` shows nothing.)
  2. Write `tests/sandbox/<name>-preview.html` from the template below. Inline the compiled CSS in a `<style>` block; render one row per variant using the `data-color`, `data-style`, `data-btn`, and `aria-disabled` attributes the component would emit.
  3. Start a local HTTP server from `tests/sandbox/`:
     ```sh
     python3 -m http.server 7743 &
     ```
     (Background it so the same shell can stop it later with `kill %1` or by capturing the PID.)
  4. Open `http://localhost:7743/<name>-preview.html` — manually, or in a Claude Code session via the `claude-in-chrome` MCP (`navigate` + `computer screenshot`).
  5. Stop the server when done: `kill %1` (or the saved PID).
- **HTML template** — a fenced `html` block based on the `button-preview.html` we just wrote. Keep it generic by naming the variant rows after the `data-*` axes (`Default / Colors / Style variants / Sizes / Disabled`) and noting that components without a given axis simply omit that row.
- **Honest-scope note** — one sentence at the end: this preview only covers what CSS can render. Behavior (focus management, `useDisabledState` short-circuiting, keyboard activation) is verified by `tests/e2e.sh`'s axe-core run, not here.
- **Gitignore note** — one sentence: `*-preview.html` files are scratch artifacts; either delete them or add a `tests/sandbox/*-preview.html` entry to the gitignore (mention but don't prescribe).

### File 2 — `tests/README.md` (one-line cross-reference)

Inside the existing `## Demo fixture: tests/setup.sh` section (around the "Running the recipe" subsection at ~line 156), add a single bullet:

> **Optional:** to visually verify a generated component's CSS variants in a browser, see [Preview a generated component in a browser](../plugins/acss-kit/docs/recipes.md#preview-a-generated-component-in-a-browser). This is a static-HTML preview, not a revival of the removed dev server.

The framing ("static-HTML preview, not a revival of the removed dev server") preserves the existing stance on line 131 while pointing readers at the escape hatch.

## Files to modify

- `plugins/acss-kit/docs/recipes.md` — add new `## Preview a generated component in a browser` section (≈ 60 lines including the HTML template fence)
- `tests/README.md` — add one cross-reference bullet inside `## Demo fixture: tests/setup.sh`

## Files NOT to modify

- `plugins/acss-kit/docs/visual-guide.md` line 128's screenshot TODO — out of scope for this plan; can be addressed separately
- `plugins/acss-kit/docs/README.md` — the recipes file is already linked from the index, so no link update needed
- `tests/setup.sh` — explicitly do not bake the preview HTML or HTTP server into the bootstrap; this stays opt-in
- `tests/sandbox/.gitignore` (or root `.gitignore`) — mention the gitignore option in the recipe but don't prescribe a code change as part of this plan; the sandbox is itself gitignored under `.claude/worktrees/`, so committed `*-preview.html` would only matter if a contributor runs `tests/setup.sh` outside a worktree

## Existing patterns reused

- **Recipe shape** — the file's existing recipes (`First run`, `Generate a single leaf component`, `Generate a component with dependencies`) all use the same intro + Prerequisites + numbered steps shape. Mirror it exactly.
- **Cross-reference style** — `tests/README.md` already cross-links between sections (e.g. `Quick local test: --plugin-dir` → `Demo fixture: tests/setup.sh`). The new bullet matches that style.
- **HTML preview template** — the `button-preview.html` we just generated at `tests/sandbox/button-preview.html` (in the worktree) is the canonical template. Generalize the `<h2>` row labels to match each component's variant axes.

## Verification

End-to-end test of the plan after implementation:

1. From `/Users/shawnsandy/devbox/acss-plugins/.claude/worktrees/test-plugin/`, render the new recipes section and confirm the markdown is well-formed:
   ```sh
   grep -n "Preview a generated component in a browser" plugins/acss-kit/docs/recipes.md
   grep -n "Preview a generated component in a browser" tests/README.md
   ```
2. Walk through the recipe verbatim with a *different* component (not `button` — try `badge` or `card`) to confirm the steps generalize:
   - `bash tests/setup.sh --reset` to wipe and rebuild the sandbox
   - `/kit-add badge` (in a Claude session inside `tests/sandbox/`)
   - Follow steps 1–5 of the new recipe, swapping `<name>` for `badge`
   - Confirm the preview renders and the `data-*` rows show variant changes
3. Run the existing test suite to confirm the doc-only changes do not break the structural validation:
   ```sh
   bash tests/run.sh
   ```
   Expected: all 9 steps green (no doc-aware checks exist, but this confirms no accidental file moves).
4. Confirm the hyperlinks resolve when rendered on GitHub:
   - `tests/README.md` → `plugins/acss-kit/docs/recipes.md#preview-a-generated-component-in-a-browser` (relative path, anchor matches the heading slug)

## Out of scope (next steps)

- Promoting `button-preview.html` to a reusable Python or Node script that auto-generates the HTML from a component's reference doc — would let contributors run `python3 scripts/preview.py button` instead of hand-writing the HTML. Worth considering once the recipe sees use.
- Linking the recipe from `plugins/acss-kit/docs/visual-guide.md` line 128's screenshot TODO. Separate concern (visual-guide is about the broader theme/style story, not per-component previews).
- Adding a `*-preview.html` entry to `tests/sandbox/.gitignore`. The sandbox lives under `.claude/worktrees/` (already gitignored) for most contributors; only contributors who run `tests/setup.sh` from the repo root would need this.
