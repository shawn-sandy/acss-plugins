---
name: setup
description: Use when the user runs /setup or asks to "set up", "bootstrap", "initialize", or "prepare" a project for acss-kit components and themes. One-time first-run init — detects package manager, prints the sass install command, writes .acss-target.json, copies ui.tsx, optionally seeds a starter theme. Cross-domain skill (touches both components and styles concerns) — deliberately not nested under either domain skill.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.5.0"
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
- The project's main CSS/SCSS entry imports `light.css` and `dark.css`, and `stack.cssEntryFile` records the choice in `.acss-target.json` (skipped with `--no-theme`)

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

Then confirm TypeScript is configured: check that `<projectRoot>/tsconfig.json` exists. If not, halt with:

```
TypeScript not configured. /setup requires a React + TypeScript project.
Add tsconfig.json and re-run /setup.
```

Checkpoint: `Detected React + TypeScript project at <projectRoot>`.

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

**If `--target=<dir>` was passed:**
Set `componentsDir` to the specified value. Always write `.acss-target.json` at `projectRoot` so subsequent `/kit-add` calls use the same directory:
```json
{ "componentsDir": "<dir>" }
```
Add `.acss-target.json` to `created[]`.

**Otherwise:**
Read `.acss-target.json` at `projectRoot`:

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

Let `themeDir = <projectRoot>/src/styles/theme/`. Check `light.css` and `dark.css` in `themeDir` independently:

- If `<themeDir>/light.css` exists, add it to `kept[]`.
- If `<themeDir>/dark.css` exists, add it to `kept[]`.

Determine generation mode from what is missing:

| light.css | dark.css | Action |
|-----------|----------|--------|
| present   | present  | skip — both already kept |
| present   | missing  | `--mode=dark` |
| missing   | present  | `--mode=light` |
| missing   | missing  | `--mode=both` |

**If generation is needed:**
1. Ask the developer for a seed hex color:
   ```
   Enter a seed hex color for your theme (default: #4f46e5):
   ```
2. Validate the input is a 3- or 6-digit hex color (e.g. `#4f46e5` or `#fff`). If invalid, use `#4f46e5` and note the substitution.
3. Run:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate_palette.py <hex> --mode=<mode>
   ```
   Capture JSON stdout. If exit code is non-zero, print the error output, skip to Step 8 (keep component init intact; record theme as not generated).
4. Run:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tokens_to_css.py --stdin --out-dir=<projectRoot>/src/styles/theme/
   ```
   piping the palette JSON to stdin.
5. Run:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_theme.py <projectRoot>/src/styles/theme/
   ```
   **On validation failure:** Print the contrast errors. Add the generated files to `created[]` with a `(contrast warning)` flag. Print:
   ```
   Theme validation failed — fix the seed color and re-run /theme-create.
   ```
   Do not roll back `ui.tsx` or `.acss-target.json`. Continue to Step 8.

   **On validation success:** Add the generated files to `created[]`.

Checkpoint: `Wrote <generated files>` or `Theme files already present, skipped`.

---

## Step 7.5 — Wire theme imports into the project's CSS/SCSS entry

Skip this step entirely if `--no-theme` was passed, or if neither `light.css` nor `dark.css` ended up present (e.g. theme generation failed in Step 7). The goal is to make the generated theme actually take effect by adding `@import` lines to the project's main CSS/SCSS file.

### 7.5a — Detect candidate entry files

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_css_entry.py <projectRoot>`.

Parse the JSON. The script returns `candidates[]` ordered by priority, each with a relative `path` and an `imports` map keyed by `light.css`, `dark.css`, `token-bridge.css`, `utilities.css`. A non-null value is the 1-based line number where that basename appears in an import-bearing line (`import`, `require(`, `@import`, `@use`, `@forward`).

### 7.5b — Choose a target file

Branch on the output:

- **`source: "detected"` and exactly one candidate** — use that path. No prompt.
- **`source: "detected"` and multiple candidates** — call `AskUserQuestion`:
  - Question: `Which file should the acss-kit theme imports be added to?`
  - One option per candidate; label is the relative path; description notes which tracked imports already exist (e.g. `already imports light.css, dark.css` or `no theme imports yet`).
  - The user's free-text "Other" answer is treated as a path relative to `projectRoot`. If the file does not exist, create it.
- **`source: "none"`** — call `AskUserQuestion` with a single question:
  - Question: `No CSS/SCSS entry file was detected. Where should the theme imports go?`
  - Options: `src/styles/index.scss (Recommended)`, `src/styles/index.css`, `src/index.css`. Free-text "Other" is honoured.
  - If the chosen file does not exist, create the parent directory and write an empty file. Add the file path to `created[]`.

Resolve the chosen path to `<projectRoot>/<chosen>`. Re-read its `imports` map (re-run `detect_css_entry.py` or read the file fresh) so the next sub-step can skip lines that are already wired.

### 7.5c — Append the import block (idempotent)

Compute the relative path from the chosen entry file's directory to `<projectRoot>/src/styles/theme/`. Build the desired import block:

```scss
/* acss-kit theme — managed by /setup */
@import "<rel>/theme/light.css";
@import "<rel>/theme/dark.css";
/* token-bridge.css + utilities.css load here once /utility-* runs */
```

For a pure `.css` entry file, use `@import url("<rel>/theme/light.css");` instead so it parses under plain CSS.

Skip any line whose basename appears non-null in the `imports` map from 7.5b. If both `light.css` and `dark.css` are already imported, do not write anything — print `Theme imports already present in <chosen>, skipped` and continue to 7.5d.

When at least one line is new, append the block (only the lines that aren't already present) at the **top** of the file, after any leading `@charset` directive, leading block comment, or existing `@use` lines (Sass requires `@use` to precede `@import`). Read the file, splice the block into the correct location, and write the result back.

Add the chosen file to `created[]` if it was newly written, otherwise to `kept[]` with a `(theme imports appended)` flag.

### 7.5d — Persist the choice

Read `<projectRoot>/.acss-target.json`. Set `stack.cssEntryFile` to the chosen relative path. If `stack` is absent, create it with just this key (other detectors will populate the rest later). Preserve every other field. Write the file back.

This makes `verify_integration.py` accept the SCSS entry as a valid place for theme imports — see `plugins/acss-kit/scripts/verify_integration.py`.

Checkpoint: `Wired theme imports into <chosen>` or `Theme imports already present in <chosen>, skipped`.

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
  - src/styles/index.scss   (theme imports wired in)

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
