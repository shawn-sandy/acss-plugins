---
description: Safely re-copy unmodified acss-kit components after a plugin upgrade — overwrites clean files, skips user-modified ones based on .acss-kit/manifest.json sha256 drift detection
argument-hint: [<component> ...] [--check] [--force]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /kit-update

Re-copy every component, foundation, and theme file recorded in `.acss-kit/manifest.json` whose on-disk sha256 still matches the recorded hash. Files you've edited (drift detected) are skipped by default and listed in the summary so your changes are preserved.

Pair with `/kit-sync` (which writes the manifest in the first place).

## Usage

```text
/kit-update                      # update every tracked file that's still clean
/kit-update button alert         # restrict to specific components
/kit-update --check              # report drift only — no writes
/kit-update --force              # overwrite modified files too (writes <file>.bak first)
```

## Workflow

When this command is invoked, follow the **Safe-update workflow** in the `kit-sync` skill at `${CLAUDE_PLUGIN_ROOT}/skills/kit-sync/SKILL.md`.

### Quick reference

1. Read manifest
2. Compute drift
3. Filter
4. Report
5. Regenerate
6. Skip or force
7. Rewrite manifest
8. Summary

See [`SKILL.md`](../skills/kit-sync/SKILL.md) for the full step-by-step workflow, script contracts (`manifest_read.py`, `diff_status.py`, `manifest_write.py`), drift classification rules, and `--check` / `--force` semantics.
