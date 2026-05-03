---
description: Safely re-copy unmodified acss-kit components after a plugin upgrade — overwrites clean files, skips user-modified ones based on .acss-kit/manifest.json sha256 drift detection
argument-hint: [<component> ...] [--check] [--force]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /kit-update

Re-copy every component, foundation, and theme file recorded in `.acss-kit/manifest.json` whose on-disk sha256 still matches the recorded hash. Files you've edited (drift detected) are skipped by default and listed in the summary so your changes are preserved.

Pair with `/kit-sync` (which writes the manifest in the first place).

## Usage

```
/kit-update                      # update every tracked file that's still clean
/kit-update button alert         # restrict to specific components
/kit-update --check              # report drift only — no writes
/kit-update --force              # overwrite modified files too (writes <file>.bak first)
```

## Workflow

When this command is invoked, follow the **Safe-update workflow** in the `kit-sync` skill at `${CLAUDE_PLUGIN_ROOT}/skills/kit-sync/SKILL.md`.

### Quick reference

1. **Read manifest** — `manifest_read.py`. If missing, halt with a "run /kit-sync first" message.
2. **Compute drift** — `diff_status.py` returns `clean[]`, `modified[]`, `missing[]` based on normalized sha256 comparison.
3. **Filter** — if positional component args were passed, intersect each list with the requested set.
4. **Report** — show counts + list of modified files (your changes preserved) and missing files (will recreate). `--check` stops here.
5. **Regenerate** — for `clean` and `missing`: re-run the same generation logic `/kit-sync` uses, hash, write, update manifest entry.
6. **Skip or force** — `modified` files are skipped by default. `--force` writes `<file>.bak` then overwrites and updates the hash.
7. **Rewrite manifest** — `manifest_write.py` with merged payload. Untouched (skipped) entries keep their previous sha — no churn.
8. **Summary** — updated / skipped / recreated counts.

### Drift detection

A file is "clean" when its current normalized sha256 (LF endings, trailing-whitespace stripped, single trailing newline) matches the value recorded by `/kit-sync` in the manifest. Otherwise it's "modified".

### Full workflow

See `${CLAUDE_PLUGIN_ROOT}/skills/kit-sync/SKILL.md` for the complete step-by-step workflow including the manifest schema and the regeneration logic per `kind`.
