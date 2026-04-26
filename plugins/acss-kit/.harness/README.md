# acss-kit Storybook Harness

Optional, opt-in deep check for live render and runtime accessibility audits of the components defined in `plugins/acss-kit/skills/components/references/components/*.md`.

**This is not the default test gate.** For everyday PR validation, run `tests/run.sh` from the repo root — that catches the majority of contract regressions in ~30 seconds without a browser. This harness adds runtime DOM verification for changes that affect rendering.

## When to use

- Before merging a change that touches a component's TSX Template, especially focus-management or compound-component patterns.
- After modifying `assets/foundation/ui.tsx` (or its markdown equivalent) where the polymorphic base could affect every consumer.
- When investigating a runtime regression that the static harness cannot reproduce.

## How to run

From the repo root:

```sh
tests/storybook.sh
```

The script:

1. Runs `npm --prefix plugins/acss-kit/.harness ci` if `node_modules/` is missing.
2. Generates `<component>.stories.tsx` files into `src/generated/` from the `## Usage Examples` blocks of each reference doc.
3. Builds Storybook (`storybook build`).
4. Runs `@storybook/test-runner` with `axe-playwright` for accessibility checks.

First run also requires `npx playwright install` to download the Playwright browser bundle (~300 MB). Subsequent runs reuse the cached bundle.

## What this catches

- Live render errors — a component throws on mount.
- Runtime DOM accessibility violations from `axe-playwright` against every story.

## What this does not catch

- Theme contrast regressions (no Storybook story for CSS-only files) — see `validate_theme.py`.
- SCSS contract violations that render but break the rules — see `tests/validate_components.py`.
- Manifest / structure drift — see `tests/validate_manifest.py`.

Run `tests/run.sh` first; this harness is supplementary.

## Contents

This directory ships only the configuration scaffolding. Generated stories and dependencies are produced on demand and gitignored:

- `package.json` — Storybook + Vite + axe-playwright dependencies.
- `vite.config.ts` — Vite + React plugin config.
- `.storybook/main.ts` — Storybook entry pointing at `src/generated/`.
- `.storybook/preview.ts` — runtime preview config for the a11y addon.
- `src/generated/` (gitignored) — auto-generated stories from `## Usage Examples` blocks.
