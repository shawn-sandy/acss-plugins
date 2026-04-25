---
name: verify-plugins
description: Run structural validation across all plugins in the repo. Reports pass/fail per plugin without requiring a plugin name argument.
disable-model-invocation: false
---

# /verify-plugins

Usage: `/verify-plugins`

Scans every directory under `plugins/` and reports pass/fail for each. No argument needed — this is a repo-wide sweep, not a single-plugin check.

## What this skill does vs. /validate-plugin

`/validate-plugin <name>` does deep per-plugin validation (semver strings, command bodies, fpkit URL checks, Python syntax). Use it before publishing a specific plugin.

`/verify-plugins` is a fast structural sweep — catches missing manifests, forbidden `version` keys, and absent required files across all plugins at once. Run it after branching or merging to confirm nothing regressed.

## Checks (per plugin)

Run these in order for each `plugins/*/` directory.

### 1. Manifest exists and has required fields

```bash
jq -e '(.name | type == "string" and length > 0) and (.version | type == "string" and length > 0) and (.description | type == "string" and length > 0)' plugins/<plugin>/.Codex-plugin/plugin.json
```

- PASS if file exists and all three fields are non-null/non-empty strings.
- FAIL if file is missing or any field is absent or empty.

### 2. Marketplace entry has no `version` key

Read `.Codex-plugin/marketplace.json`. Run two checks in sequence.

First, verify the entry exists:

```bash
jq -e --arg p "<plugin>" '.plugins | map(.name) | index($p) != null' .Codex-plugin/marketplace.json
```

- FAIL if entry is absent: "marketplace.json has no entry for <plugin> — add one."
- If absent, skip the next check for this plugin.

Then, verify no `version` key:

```bash
jq -e '.plugins[] | select(.name == "<plugin>") | has("version") | not' .Codex-plugin/marketplace.json
```

- PASS if no `version` key present.
- FAIL with message: "marketplace.json entry for <plugin> carries a `version` key — remove it (plugin.json always wins)."

### 3. Required files present

Check that each of these paths exists:

- `plugins/<plugin>/README.md`
- `plugins/<plugin>/skills/<plugin>/SKILL.md`
- `plugins/<plugin>/commands/` directory containing at least one `.md` file

Report each missing path as a separate FAIL line.

### 4. Delegate deep checks (optional)

After the structural sweep, offer: "Run `/validate-plugin <name>` for a full pre-publish check on any plugin above."

Do not re-implement the logic from `validate-plugin` — keep this skill fast and structural only.

## Output format

```
plugins/acss-app-builder
  PASS  Manifest fields (name, version, description)
  PASS  Marketplace entry has no version key
  PASS  README.md present
  PASS  skills/acss-app-builder/SKILL.md present
  PASS  commands/ has .md files

plugins/acss-kit-builder
  PASS  Manifest fields (name, version, description)
  FAIL  Marketplace entry has a version key — remove it
  PASS  README.md present
  ...

Summary: 2 plugins checked, 1 failure total.
```

If all pass: "All plugins passed structural checks."
