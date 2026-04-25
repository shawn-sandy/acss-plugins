---
description: Preview the diff between staged render output and existing project files
argument-hint: <component> [--target=react|html|astro]
allowed-tools: Bash, Read
---

Shows what `/spec-promote` would change before you commit to it.

1. Locate staging files in `.acss-staging/<framework>/`.
2. Compare each staging file against the corresponding file in the project (driven by `.acss-target.json` `componentsDir`).
3. If no project file exists yet, treat as a new-file diff (show full content).
4. If no target is specified, diff all frameworks present in staging.

Output a unified diff block per file. No files are written or moved.

Follow SKILL.md § /spec-diff.
