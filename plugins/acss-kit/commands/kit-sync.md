---
description: Bulk-install every acss-kit component, foundation, and starter theme into a project, tracked by .acss-kit/manifest.json for safe future updates
argument-hint: [--target=<dir>] [--styles-dir=<dir>] [--seed=<hex>] [--skip-styles] [--dry-run]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /kit-sync

Vendor every shipped acss-kit component, the `ui.tsx` foundation, and a starter OKLCH theme into your project in a single command. Records every file's normalized sha256 in `.acss-kit/manifest.json` so `/kit-update` can later re-copy unmodified files without clobbering your edits.

## Usage

```
/kit-sync
/kit-sync --seed="#4f46e5"
/kit-sync --skip-styles
/kit-sync --target=src/ui/fpkit --styles-dir=src/styles
/kit-sync --dry-run
```

## Workflow

When this command is invoked, follow the **Bulk install workflow** in the `kit-sync` skill at `${CLAUDE_PLUGIN_ROOT}/skills/kit-sync/SKILL.md`.

### Quick reference

1. **Preflight** — `detect_target.py` for project root, `detect_stack.py` for sass, `manifest_read.py` to detect re-sync.
2. **Enumerate** — every component in `references/components/catalog.md` (excluding `Form` and `UI (foundation)`).
3. **Resolve** — walk Generation Contract `dependencies:` recursively, dedupe.
4. **Plan** — show the full file tree (foundation + components + styles + manifest) and wait for confirmation. `--dry-run` stops here.
5. **Generate components** — bottom-up, hash before write, build manifest payload.
6. **Foundation** — copy `assets/foundation/ui.tsx` → `<target>/ui.tsx`.
7. **Styles** — `generate_palette.py` → `tokens_to_css.py` → write `light.css` + `dark.css` + `acss-kit.theme.json`. Skipped under `--skip-styles`.
8. **Write manifest** — pipe payload to `manifest_write.py`.
9. **Verify integration** — `verify_integration.py`; surface missing-import reasons.
10. **Summary** — created / skipped / next steps.

### Re-sync behavior

If `.acss-kit/manifest.json` already exists, every file is routed through the `/kit-update` drift check before writing — modified files are skipped (preserving user edits), clean files are overwritten.

### Hash normalization

sha256s are computed on **normalized** content (LF endings, trailing-whitespace stripped, single trailing newline) so a Prettier run doesn't trigger drift.

### Full workflow

See `${CLAUDE_PLUGIN_ROOT}/skills/kit-sync/SKILL.md` for the complete step-by-step workflow including the manifest schema, drift classification, and re-sync semantics.
