---
name: setup
description: Use when the user runs /setup or asks to "set up", "bootstrap", "initialize", or "prepare" a project for acss-kit components and themes. One-time first-run init — detects package manager, prints the sass install command, writes .acss-target.json, copies ui.tsx, optionally seeds a starter theme. Cross-domain skill (touches both components and styles concerns) — deliberately not nested under either domain skill.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.4.0"
---

# SKILL: setup

Bootstrap a React project for acss-kit. Run once after `/plugin install acss-kit` to front-load the one-time setup so subsequent `/kit-add` and `/theme-create` calls are pure generation.

**Skill placement rationale:** `/setup` spans both the `components` and `styles` domains — it initializes `ui.tsx` (component foundation) and seeds a starter theme (styles). It lives as its own skill rather than as a section of either domain skill. This is the only cross-domain skill in the plugin; future maintainers should not merge it into `components/SKILL.md` or `styles/SKILL.md`.

## Purpose

Front-load the one-time project configuration that would otherwise run piecemeal at the start of each `/kit-add` invocation. After `/setup` succeeds:

- `sass` is confirmed in `devDependencies` (or the user has the exact install command to run)
- `.acss-target.json` exists at the project root
- `<componentsDir>/ui.tsx` is present
- `src/styles/theme/light.css` and `dark.css` exist (unless `--no-theme` was passed)

## Prerequisites

- React + TypeScript project

## Idempotency contract

Every step checks for its artifact before acting. If the artifact already exists, the step is skipped and added to `kept[]`. If the artifact is created, it is added to `created[]`. The final summary tabulates both lists. There is no `--force` flag — re-running `/setup` is safe.

## Flags

- `--no-theme` — skip Step 7 (theme generation). Only initializes the component foundation.
- `--target=<dir>` — override the default target directory (default: `src/components/fpkit/`).

---

## Step 1 — Verify React project

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`.

Parse the JSON output. If `projectRoot` is `null`, halt with the script's `reasons[0]` message. Do not proceed.

Checkpoint: `Detected React project at <projectRoot>`.

---

## Step 2 — Detect React version

Read `package.json` at the detected `projectRoot`. Extract `dependencies.react`.

Apply the regex `/^[~^>=]*(\d+)/` to the version string. If the first captured group is `19` or higher, print:

```
Warning: React 19+ detected. ui.tsx is copied verbatim from the plugin asset.
It may need the ElementInstance<C> adaptation for React 19 + TS compatibility.
See the acss-kit first-run transcript for the patch pattern.
```

Continue regardless — the warning is advisory only.

Checkpoint: `React 19+ detected — see warning above` or `React <major> detected`.

---

## Step 3 — Detect package manager

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_package_manager.py <projectRoot>`.

Parse the JSON output. Capture `manager`, `lockfile`, and `installCommand` for use in Steps 4 and 8.

Checkpoint: `Detected <manager> (<lockfile if present, else "packageManager field">)`.

---

## Step 4 — Print sass install command (does not execute)

Read `package.json` `devDependencies` at `projectRoot`. Check for `sass` or `sass-embedded`.

**If `sass` or `sass-embedded` is present:** Skip. Add `sass` (or `sass-embedded`) to `kept[]`. Continue to Step 5.

**If `node-sass` only:** Print:
```
Warning: node-sass found in devDependencies.
Vite prefers sass or sass-embedded. Consider replacing it:
  <installCommand> sass
```
Continue to Step 5 — do not halt.

**If neither is present:** Print:
```
sass not found in devDependencies.
Run: <installCommand> sass
Then re-run: /setup
```
Halt. Record `paused=true` for the Step 8 summary. Do not proceed to Step 5.

---

## Step 5 — Determine target directory

Honor the `--target=<dir>` flag if provided; use that value as `componentsDir`.

Otherwise, read `.acss-target.json` at `projectRoot`:

- **If it exists:** Use the `componentsDir` value. Add `.acss-target.json` to `kept[]`. Skip the prompt.
- **If it does not exist:** Ask:
  ```
  Where should components be generated? (default: src/components/fpkit/)
  ```
  Write `.acss-target.json` at `projectRoot`:
  ```json
  { "componentsDir": "src/components/fpkit" }
  ```
  Add `.acss-target.json` to `created[]`.

Checkpoint: `Wrote .acss-target.json (componentsDir=<dir>)` or `Reusing existing .acss-target.json (componentsDir=<dir>)`.

---

## Step 6 — Copy ui.tsx foundation

Check if `<projectRoot>/<componentsDir>/ui.tsx` exists.

**If it exists:** Skip. Add `<componentsDir>/ui.tsx` to `kept[]`.

**If it does not exist:**
1. Create the directory `<projectRoot>/<componentsDir>/` if it does not exist.
2. Read `${CLAUDE_PLUGIN_ROOT}/assets/foundation/ui.tsx` and write it verbatim to `<projectRoot>/<componentsDir>/ui.tsx`. Do not edit or adapt the content.
3. Add `<componentsDir>/ui.tsx` to `created[]`.

Checkpoint: `Copied ui.tsx to <componentsDir>/` or `ui.tsx already present, skipped`.

---

## Step 7 — Seed starter theme (skip if --no-theme)

If `--no-theme` was passed, skip this step entirely.

Check if `<projectRoot>/src/styles/theme/light.css` exists.

**If it exists:** Add `src/styles/theme/light.css` and `src/styles/theme/dark.css` to `kept[]`. Skip.

**If it does not exist:**
1. Ask the developer for a seed hex color:
   ```
   Enter a seed hex color for your theme (default: #4f46e5):
   ```
2. Validate the input is a 3- or 6-digit hex color (e.g. `#4f46e5` or `#fff`). If invalid, use `#4f46e5` and note the substitution.
3. Run:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate_palette.py <hex> --mode=both
   ```
   Capture JSON stdout. If exit code is non-zero, print the error output, skip to Step 8 (keep component init intact; record theme as not generated).
4. Run:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tokens_to_css.py --stdin --out-dir=src/styles/theme/
   ```
   piping the palette JSON to stdin. This writes `src/styles/theme/light.css` and `dark.css`.
5. Run:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_theme.py src/styles/theme/
   ```
   **On validation failure:** Print the contrast errors. Add `light.css` and `dark.css` to `created[]` with a `(contrast warning)` flag. Print:
   ```
   Theme validation failed — fix the seed color and re-run /theme-create.
   ```
   Do not roll back `ui.tsx` or `.acss-target.json`. Continue to Step 8.

   **On validation success:** Add `src/styles/theme/light.css` and `src/styles/theme/dark.css` to `created[]`.

Checkpoint: `Wrote light.css and dark.css` or `Theme files already present, skipped`.

---

## Step 8 — Print summary

If `paused=true` (Step 4 halted), print:
```
Setup paused at Step 4.
Run: <installCommand> sass
Then re-run: /setup
```

Otherwise, print a structured summary:

```
Setup complete.

Created:
  - <componentsDir>/ui.tsx
  - .acss-target.json
  - src/styles/theme/light.css
  - src/styles/theme/dark.css

Kept (already present):
  - sass in devDependencies

Next steps:
  - Commit these files (developer owns the code)
  - /kit-add button card    # generate your first components
```

If theme validation failed, append to next steps:
```
  - Fix the seed color and re-run /theme-create
```

Omit any section (`Created` or `Kept`) that is empty.
