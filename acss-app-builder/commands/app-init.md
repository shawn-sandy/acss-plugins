---
description: Bootstrap a Vite+React+TS project for the acss design system (folders, base theme, entry-file imports)
argument-hint: [--with=theme,layout] [--force]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Bootstrap the current project for the `@fpkit/acss` design system.

Follow the `/app-init` workflow in the plugin's master SKILL.md:
`.claude/plugins/acss-app-builder/skills/acss-app-builder/SKILL.md`

**Quick checklist:**

1. Verify Vite+React via `scripts/detect_vite_project.py`.
2. Verify `sass` in devDependencies; halt with install hint if missing.
3. Create `src/app/`, `src/pages/`, `src/styles/theme/` (refuse non-empty without `--force`).
4. Copy `assets/themes/base.css` to `src/styles/theme/base.css`.
5. Ensure `.acss-target.json` exists at project root (ask for components dir on first run, default `src/components/fpkit`).
6. Append sentinel-bounded `import './styles/theme/base.css'` to the entry file after the last existing import.
7. If `--with=theme` or `--with=layout` is passed, delegate to `/app-theme light` and `/app-layout sidebar` inline.
8. Print a summary with next-step hints.

**This command is exempt from the shared preflight's theme-base check** (it creates that file).

**Safety:** refuse on dirty git tree and on any existing non-empty target file unless `--force`.
