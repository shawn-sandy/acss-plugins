# Plan: `/setup` skill for acss-kit — first-run project bootstrap

## Context

The transcript at `tests/2026-04-26-214810-implement-the-following-plan.txt` captures a real `/kit-add button card` first-run inside `tests/sandbox/`. Before any component could be generated, the user had to manually:

1. Install `sass` as a dev dep (Vite needs it to compile `*.scss` imports)
2. Create `src/components/fpkit/`
3. Copy `assets/foundation/ui.tsx` verbatim
4. Hand-patch `ui.tsx` for React 19 + TS 6 (`React.ElementRef<C>` → custom `ElementInstance<C>`)

Today this prerequisite plumbing is wedged into Step A of `plugins/acss-kit/skills/components/SKILL.md` (lines 24–74), which runs at the start of *every* `/kit-add` invocation. There is no dedicated entry point users can run once after `/plugin install acss-kit` to prepare a project.

This plan adds a `/setup` slash command + `setup` skill that front-loads the one-time bootstrap so subsequent `/kit-add` and `/theme-create` calls become pure generation. `/kit-add`'s inline Step A is left untouched as a safety net (per user decision — lower-risk than slimming it).

## Decisions (locked in via AskUserQuestion + plan-interview)

| Question | Decision |
|---|---|
| Sass install execution | **Print command only** — detect PM, print the exact `<pm> add -D sass` command, stop. User runs it. (Mirrors current `components` SKILL Step A2.) |
| Package manager detection | Auto-detect via lockfile (`pnpm-lock.yaml`, `yarn.lock`, `bun.lock`/`bun.lockb`, `package-lock.json`) + `package.json#packageManager` field. |
| Scope | Components init **+ starter theme** (inline the `/theme-create` script pipeline; no cross-command call). |
| Modify `/kit-add` Step A? | No — keep as-is, `/setup` is purely additive. |
| React 19 ui.tsx patch | Detect React 19+ via simple regex on `dependencies.react` and **warn**; do not auto-patch (preserves "verbatim copy" contract from `components` SKILL.md A4). |
| Idempotency | Per-step skip; final summary tabulates `kept` vs `created`. No `--force` flag. |
| Sass variants | Accept `sass` \| `sass-embedded`; warn on `node-sass` but don't block. |
| Theme failure handling | Keep components init; print `validate_theme.py` errors; point user to `/theme-create` to retry. Bootstrap remains usable. |
| Output verbosity | One-line checkpoint per step + structured final summary. |
| Git tree check | None — keep friction low. |
| Generated artifacts | **Committed** (developer owns the code). Not added to `.gitignore`. |
| `marketplace.json` description | **Will be updated** — adding a top-level command is materially user-facing. |

## Files to create

### 1. `plugins/acss-kit/commands/setup.md`

Slash command, delegates to the new skill. Front-matter follows existing convention (`description`, `argument-hint`, `allowed-tools`):

```yaml
---
description: Bootstrap a React project for acss-kit — installs sass, copies ui.tsx, writes .acss-target.json, optionally seeds a starter theme
argument-hint: [--no-theme] [--target=<dir>]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---
```

Body: H1 `# /setup`, `## Usage`, `## Workflow` pointing to `${CLAUDE_PLUGIN_ROOT}/skills/setup/SKILL.md`, plus a `### Quick Reference` checklist (mirrors `kit-add.md` shape).

### 2. `plugins/acss-kit/skills/setup/SKILL.md`

The orchestration skill. Front-matter:

```yaml
---
name: setup
description: Use when the user runs /setup or asks to "set up", "bootstrap", "initialize", or "prepare" a project for acss-kit components and themes. One-time first-run init — detects package manager, prints the sass install command, writes .acss-target.json, copies ui.tsx, optionally seeds a starter theme. Cross-domain skill (touches both components and styles concerns) — deliberately not nested under either domain skill.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.4.0"
---
```

**Skill placement rationale (in skill body):** /setup spans both the `components` and `styles` domains, so it lives as its own skill rather than as a section of either. This is the only skill in the plugin that crosses domains; document this explicitly so future maintainers don't try to merge it.

Sections (follows existing skill heading pattern):

- `## Purpose`
- `## Prerequisites` — React + TypeScript project
- `## Idempotency contract` — every step checks for its artifact and skips if present. Track `kept[]` and `created[]` for the final summary.
- `## Step 1 — Verify React project` — call `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py`. If `projectRoot: null`, refuse with the script's `reasons[0]`. Print one-line checkpoint: `Detected React project at <path>`.
- `## Step 2 — Detect React version` — read `package.json` `dependencies.react` with a simple regex (`/^[~^>=]*(\d+)/`). If first major ≥ 19, print warning that `ui.tsx` may need the `ElementInstance<C>` adaptation seen in the first-run transcript. Continue regardless. Checkpoint: `React 19+ detected — see warning above` or `React 18 detected`.
- `## Step 3 — Detect package manager` — call new `detect_package_manager.py` (see file 3). Checkpoint: `Detected pnpm (pnpm-lock.yaml)`.
- `## Step 4 — Print sass install command (does not execute)` — read `package.json` `devDependencies`. If `sass` or `sass-embedded` is present, skip and add to `kept[]`. If `node-sass` only, print warning that Vite prefers `sass`/`sass-embedded` and proceed without erroring. Otherwise, print:

  ```text
  sass not found in devDependencies.
  Run: <detected-pm> add -D sass
  Then re-run: /setup
  ```

  Stop the skill (do not proceed to Step 5). Same UX as today's `components` SKILL Step A2 — no install side effect from the skill.
- `## Step 5 — Determine target directory` — same logic as `components` SKILL Step A3. Honors `--target=<dir>` flag. If `.acss-target.json` exists, reuse and add to `kept[]`; else prompt with default `src/components/fpkit/` and write file → add to `created[]`. Checkpoint: `Wrote .acss-target.json` or `Reusing existing .acss-target.json (componentsDir=<dir>)`.
- `## Step 6 — Copy ui.tsx foundation` — if `<target>/ui.tsx` exists, skip → `kept[]`. Else `cp ${CLAUDE_PLUGIN_ROOT}/assets/foundation/ui.tsx <target>/ui.tsx` (verbatim, per A4 contract) → `created[]`. Checkpoint: `Copied ui.tsx` or `ui.tsx already present, skipped`.
- `## Step 7 — Seed starter theme` — unless `--no-theme` passed:
  1. If `src/styles/theme/light.css` already exists, skip → `kept[]`.
  2. Otherwise prompt for seed hex (default `#4f46e5`).
  3. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate_palette.py <hex> --mode=both` → capture JSON.
  4. Pipe into `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tokens_to_css.py` to write `src/styles/theme/{light,dark}.css`.
  5. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_theme.py src/styles/theme/`.
  6. **On failure**: print the contrast errors. Add `light.css` / `dark.css` to `created[]` with a warning flag. Print: `Theme validation failed — fix the seed color and re-run /theme-create`. Do **not** roll back ui.tsx or `.acss-target.json`. Continue to Step 8.
  7. On success: checkpoint `Wrote light.css and dark.css (top contrast: <ratio>)`.
- `## Step 8 — Print summary + next steps` — structured table:

  ```text
  Setup complete.

  Created:
    - src/components/fpkit/ui.tsx
    - .acss-target.json
    - src/styles/theme/light.css
    - src/styles/theme/dark.css

  Kept (already present):
    - sass in devDependencies

  Next steps:
    - Commit these files (developer owns the code)
    - /kit-add button card    # generate your first components
  ```

  If sass install was needed (Step 4 stopped early), summary instead says: `Setup paused at Step 4. Run: <pm> add -D sass, then re-run /setup.`

### 3. `plugins/acss-kit/scripts/detect_package_manager.py`

New Python 3 stdlib script. Follows the **detector contract** (`.claude/rules/python-scripts.md`): JSON to stdout, exit 0/1, `reasons` array.

- Walks parent dirs from `argv[1]` (or cwd) to find a project root containing `package.json`
- Inspects lockfiles in priority order: `pnpm-lock.yaml` → `yarn.lock` → `bun.lock` (Bun 1.2+ text format) → `bun.lockb` (legacy binary) → `package-lock.json`
- Falls back to `package.json#packageManager` field (parse `name@version` spec) if no lockfile
- Final fallback: `npm`

Output shape (success):

```json
{
  "manager": "pnpm",
  "lockfile": "pnpm-lock.yaml",
  "installCommand": "pnpm add -D",
  "projectRoot": "/abs/path",
  "reasons": []
}
```

Install command map:

| Manager | Install command |
|---|---|
| `npm` | `npm install -D` |
| `pnpm` | `pnpm add -D` |
| `yarn` | `yarn add -D` |
| `bun` | `bun add -d` |

On failure (no project root): `manager: null`, populated `reasons`, exit 1.

**Self-test (`if __name__ == "__main__"`)** — when invoked with `--self-test`, run against three in-memory fixtures (pnpm-lock present, package-lock present, no lockfile + packageManager field) and print pass/fail. This gives `tests/run.sh` a smoke check without external fixtures.

## Files to modify

| Path | Change |
|---|---|
| `plugins/acss-kit/.claude-plugin/plugin.json` | Bump `version` `0.3.1` → `0.4.0` via the explicit release step below — do **not** hand-edit. |
| `plugins/acss-kit/CHANGELOG.md` | Add `0.4.0` entry: "Added `/setup` command for first-run project bootstrap (PM detection, sass install instructions, ui.tsx copy, starter theme). New `detect_package_manager.py` detector script." |
| `plugins/acss-kit/README.md` | Document `/setup` in the commands section as the **recommended first command after install**. Note that generated artifacts (`src/components/fpkit/`, `src/styles/theme/`) are meant to be committed — developer owns the code. |
| `.claude/rules/python-scripts.md` | Add `detect_package_manager.py` to the script inventory under "Detectors". |
| `.claude-plugin/marketplace.json` | **Update** the `acss-kit` plugin entry `description` to mention the new `/setup` bootstrap. **Do not add a `version` field** (per CLAUDE.md). |
| `tests/run.sh` | Add a smoke step: `python3 plugins/acss-kit/scripts/detect_package_manager.py --self-test` (exit 0 expected). |

## Release step

After all files above are written, run `/release-plugin acss-kit` (interactive). It bumps `plugin.json#version` to `0.4.0`, scaffolds the CHANGELOG entry consistent with prior releases, and runs `tests/run.sh` as a final gate. Do **not** hand-edit `plugin.json` — the release skill keeps version semantics consistent.

## Existing functions / utilities to reuse (no duplication)

- `plugins/acss-kit/scripts/detect_target.py` — already detects React project root and reads/writes `.acss-target.json`. Use unchanged for Steps 1, 5.
- `plugins/acss-kit/assets/foundation/ui.tsx` — verbatim source for Step 6.
- `plugins/acss-kit/skills/styles/SKILL.md` `/theme-create` section — Step 7 delegates here rather than reimplementing palette math. Pipeline: `generate_palette.py` → `tokens_to_css.py` → `validate_theme.py`.
- `plugins/acss-kit/skills/components/SKILL.md` Step A — left as-is; serves as a fallback if a user runs `/kit-add` without `/setup` first.

## Verification

Run from the repo root:

1. **Structural validator** — `tests/run.sh` must pass. Specifically Step 5 (`tests/validate_manifest.py`) confirms:
   - `commands/setup.md` exists
   - `skills/setup/SKILL.md` exists
   - `plugin.json` version `0.4.0` matches semver
2. **Front-matter hooks** — the PostToolUse hook in `.claude/settings.json` will validate command + SKILL.md front-matter on Write. Both new files must have required keys.
3. **End-to-end smoke test** in `tests/sandbox/`:
   ```bash
   tests/setup.sh                         # fresh sandbox
   cd tests/sandbox
   rm -rf src/components/fpkit src/styles .acss-target.json
   # invoke /setup with default target, default seed color
   npx tsc -b --noEmit                    # must pass
   npm run dev                            # Vite must boot without sass errors
   ```
   Confirm:
   - `package.json` has `sass` in `devDependencies` (correct PM was used)
   - `.acss-target.json` written at sandbox root
   - `src/components/fpkit/ui.tsx` is a byte-identical copy of the asset
   - `src/styles/theme/light.css` + `dark.css` exist and pass `validate_theme.py`
   - React 19 warning was printed (sandbox uses React 19 per the transcript)
4. **Idempotency** — re-run `/setup` in the prepared sandbox; it should detect each artifact and skip without overwriting.
5. **Follow-up** — `/kit-add button card` after `/setup` should now skip Step A's install/copy paths cleanly (Step A becomes verify-only).

## Next Steps (out of scope)

- Slim `components` SKILL.md Step A to "verify init artifacts present, else suggest `/setup`" — defer until `/setup` is proven in real use.
- Auto-patch `ui.tsx` for React 19 — better solved upstream by updating `assets/foundation/ui.tsx` itself so the verbatim copy stays correct on React 19+.
- Add `--theme-seed=<hex>` non-interactive flag to `/setup` for CI / scripted bootstrap.
- Detect Vite-specific config (e.g. confirm `vite.config.ts` is present and warn on Webpack/CRA projects).
- Add a `--yes` flag for fully non-interactive bootstrap (accepts all defaults).

---

## Interview Summary

Stress-tested via `/plan-interview` on 2026-04-26. All amendments below have been folded into the plan above.

### Key Decisions Confirmed

- Sass install is **print-only** (no skill-side execution) — revises the original "auto-install with confirmation" decision and aligns with current `components` SKILL Step A2.
- Per-step idempotency with `kept` vs `created` summary; no `--force` flag.
- Theme generation runs the `generate_palette.py` → `tokens_to_css.py` → `validate_theme.py` pipeline directly inside the setup skill (no cross-command call).
- React 19 detection uses a simple major-version regex on `dependencies.react`.
- `sass`/`sass-embedded` are accepted; `node-sass` triggers a warning but does not block.
- Theme failure keeps the components init intact; user is pointed to `/theme-create` to retry.
- One-line checkpoint per step + structured final summary.
- No git tree check.

### Open Risks & Concerns

- The new skill diverges from the one-skill-per-domain convention. Mitigation: explicit "skill placement rationale" in the SKILL.md description.
- Bun ships both `bun.lock` (text, 1.2+) and `bun.lockb` (binary). Detector must handle both.
- New Python script needs minimal test coverage — added via `--self-test` mode invoked from `tests/run.sh`.
- Implementer might hand-edit `plugin.json` and skip changelog scaffolding — mitigated by making `/release-plugin` an explicit step.

### Recommended Plan Amendments (applied)

1. Step 4 changed from "install sass" to "print install command and stop" — matches `components` Step A2.
2. Step 7 specifies failure handling (no rollback; print contrast errors; bootstrap remains usable).
3. Step 8 rewritten to tabulate `kept` vs `created` and surface "paused at Step 4" branch when sass is missing.
4. Skill placement rationale added to `setup` SKILL.md description.
5. `detect_package_manager.py` updated to detect `bun.lock` + `bun.lockb` + `package.json#packageManager`. Install-command map added.
6. `tests/run.sh` smoke step (`--self-test`) added to the "Files to modify" table.
7. `/release-plugin acss-kit` made an explicit step after file writes.
8. `marketplace.json` description update committed (not hedged); generated artifacts marked as committed (not gitignored) in the README update.

### Simplification Opportunities (acknowledged, not adopted)

- Could be a `## /setup` section in `components/SKILL.md` instead of a new skill. **Not adopted** — /setup is cross-domain (also seeds a theme); a dedicated skill is clearer. Documented in the SKILL.md rationale.
- Could inline PM detection as a Bash chain instead of a Python script. **Not adopted** — script is testable via `--self-test`, reusable by future commands, and follows the established detector contract.
