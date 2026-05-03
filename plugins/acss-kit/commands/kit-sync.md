---
description: Bulk-install every acss-kit component, foundation, and starter theme into a project, tracked by .acss-kit/manifest.json for safe future updates
argument-hint: [--target=<dir>] [--styles-dir=<dir>] [--seed=<hex>] [--skip-styles] [--dry-run]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /kit-sync

Vendor every component listed in `references/components/catalog.md`, the `ui.tsx` foundation, and a starter OKLCH theme into your project in a single command. Records every file's normalized sha256 in `.acss-kit/manifest.json` so `/kit-update` can later re-copy unmodified files without clobbering your edits.

`Form` is **not** vendored by `/kit-sync` — it lives behind the `component-form` skill and is generated on-demand from a natural-language prompt. Run `/setup` plus a form-shaped prompt (e.g. "create a signup form with email and password") to bootstrap it.

## Usage

```text
/kit-sync
/kit-sync --seed="#4f46e5"
/kit-sync --skip-styles
/kit-sync --target=src/ui/fpkit --styles-dir=src/styles
/kit-sync --dry-run
```

## Workflow

When this command is invoked, follow the **Bulk install workflow** in the `kit-sync` skill at `${CLAUDE_PLUGIN_ROOT}/skills/kit-sync/SKILL.md`.

### Quick reference

1. Preflight
2. Enumerate
3. Resolve dep tree
4. Plan
5. Generate components
6. Foundation
7. Styles
8. Write manifest
9. Verify integration
10. Summary

See [`SKILL.md`](../skills/kit-sync/SKILL.md) for the full step-by-step workflow, flag semantics (`--dry-run`, `--skip-styles`, `--seed`, `--target`, `--styles-dir`), re-sync drift handling, manifest schema, and hash normalization rules.
