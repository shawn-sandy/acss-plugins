---
name: validate-plugin
description: Check a plugin's structure for completeness and correctness before publishing. Catches common issues like missing files, repo-relative fpkit links, or malformed JSON.
disable-model-invocation: false
---

# /validate-plugin

Usage: `/validate-plugin <plugin-name>`

Example: `/validate-plugin acss-kit-builder`

## Checks

Run each check in order. Report all failures at the end, not one at a time.

### 1. Manifest
- `<plugin>/.Codex-plugin/plugin.json` exists and is valid JSON
- Required fields present: `name`, `description`, `version`, `author`, `license`
- `version` is a valid semver string
- `claudeCodeMinVersion` is present (warn if missing, don't fail)

### 2. Marketplace entry
- `.Codex-plugin/marketplace.json` has an entry matching the plugin name
- The entry does **not** have a `"version"` field (this causes silent conflicts)
- `description` is non-empty

### 3. Required files
- `README.md` exists
- `commands/` directory exists and contains at least one `.md` file
- `skills/<plugin>/SKILL.md` exists

### 4. Command files
For each `commands/*.md`:
- Has valid YAML front-matter with `description` and `allowed-tools` fields
- Body references `SKILL.md` (not re-implements logic inline)
- Does not contain repo-relative paths to fpkit source (e.g., `../../acss/`)

### 5. SKILL.md references
- No repo-relative fpkit source links — all fpkit references must be full GitHub URLs (`https://github.com/shawn-sandy/acss/...`)
- Each command mentioned in the SKILL.md has a corresponding `commands/*.md` file

### 6. Python scripts (if present)
- Run `python3 -m py_compile <script>` on each `.py` file in `scripts/` or `<plugin>/scripts/`
- Report any syntax errors

### 7. Assets
- If `assets/` exists, verify no `.tmpl` files contain un-substituted `{{PLACEHOLDER}}` tokens that look like they were accidentally left from a copy-paste (i.e., tokens that don't follow the `{{ALL_CAPS}}` convention)

## Output

Print a summary table:
```
PASS  Manifest fields
PASS  Marketplace entry
FAIL  Command files — app-init.md missing allowed-tools front-matter
PASS  SKILL.md references
...
```

Exit with a count of failures. If zero failures: "Plugin <name> is ready to publish."
