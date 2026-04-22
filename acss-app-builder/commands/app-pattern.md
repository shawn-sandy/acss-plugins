---
description: Insert a common UI pattern (data-table, empty-state, skeleton, hero, pricing, toast)
argument-hint: <pattern> [--into=<file>] [--force]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

Insert a reusable UI pattern into a target file or as a standalone component.

**Patterns:** `data-table`, `empty-state`, `loading-skeleton`, `hero`, `pricing-grid`, `notification-toast`.

Follow the `/app-pattern` section of `.claude/plugins/acss-app-builder/skills/acss-app-builder/SKILL.md`.

**Modes:**

- **Standalone** (no `--into`) — writes `src/patterns/<Name>.tsx`.
- **Inline** (`--into=<file>`) — replaces the first `{/* @acss-app-builder:insert */}` marker in the target file with the pattern's JSX body and merges imports. Refuses if the marker is absent.

**Quick steps:**

1. Shared preflight.
2. Read `assets/patterns/<pattern>.tsx`.
3. Substitute imports based on `scripts/detect_component_source.py` output.
4. Write the file or perform the inline insert.
5. If the pattern ships a `.scss`, write it alongside or ensure it's imported.
