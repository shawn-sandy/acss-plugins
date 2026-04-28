---
description: Copy the prebuilt utilities.css bundle (and token-bridge.css) into a target React project
argument-hint: [--target=<dir>] [--families=<comma-list>] [--no-bridge]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Copy the bundled `utilities.css` and `token-bridge.css` into the user's React project.

Follow the `/utility-add` section of `${CLAUDE_PLUGIN_ROOT}/skills/utilities/SKILL.md`.

**Arguments:**

- `--target=<dir>` — override the auto-detected drop directory (default: `src/styles/`).
- `--families=<comma-list>` — emit only the listed family partials concatenated into a single file. Otherwise the full bundle is copied verbatim. Example: `--families=color-bg,color-text,spacing,display`.
- `--no-bridge` — skip copying `token-bridge.css`. Use when the project ships its own theme without acss-kit.

**Quick steps:**

1. Run `scripts/detect_utility_target.py`. Use the result to pick the drop directory unless `--target` overrides.
2. If `--families=` is present, concatenate the requested partials from `assets/utilities/<family>.css` plus the bundle header. Otherwise copy `assets/utilities.css` verbatim to `<target>/utilities.css`.
3. Unless `--no-bridge`, copy `assets/token-bridge.css` to `<target>/token-bridge.css`.
4. Print the recommended import order:
   ```ts
   import "./styles/token-bridge.css";   // first — defines the aliases
   import "./styles/utilities.css";       // then — utility classes consume them
   ```
5. Print a summary: files written, total size, families included.
