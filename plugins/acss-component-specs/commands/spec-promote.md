---
description: Move staged render output into project component directories
argument-hint: <component> [--target=react|html|astro|all]
allowed-tools: Bash, Read, Write, Edit
---

Moves files from `.acss-staging/<framework>/` into project paths driven by `.acss-target.json`.

1. Read `.acss-target.json` `componentsDir` for the destination root.
2. Move (not copy) each staging file to its final path.
3. If a destination file already exists, overwrite it and note the overwrite.
4. After promotion, staging directory for the component is empty — confirm cleanup.
5. Report which files were promoted and their final paths.

Promotion is explicit and never automatic. Always run `/spec-diff` first.

Follow SKILL.md § /spec-promote.
