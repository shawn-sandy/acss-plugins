---
name: release-check
description: Audit release paperwork for a plugin before opening a PR — confirms version bump, CHANGELOG, and README are all touched when they should be.
argument-hint: <plugin-name>
disable-model-invocation: false
---

# /release-check

Usage: `/release-check <plugin-name>`

Example: `/release-check acss-kit`

This skill audits whether the release paperwork is complete on the current branch. It does **not** perform the version bump — use `/release-plugin <name> <version>` for that. Run this after `/release-plugin` and before opening a PR.

## Steps

### 1. Confirm plugin exists

Verify `$ARGUMENTS` matches a directory under `plugins/`. If not, list available plugins and stop.

### 2. Diff main...HEAD for the plugin

```bash
git diff main...HEAD --name-only -- plugins/<plugin>/
```

Collect the list of changed files scoped to `plugins/<plugin>/`.

### 3. Check version bump

- Attempt to read `plugins/<plugin>/.claude-plugin/plugin.json` from `main` via `git show main:plugins/<plugin>/.claude-plugin/plugin.json`.
- If the command exits non-zero (file does not exist on `main`): PASS with note "New plugin — initial version establishes the baseline." Skip the version-diff check.
- Otherwise read the same file from `HEAD` and compare `version` fields.
- PASS if the `version` field differs between `main` and `HEAD`.
- FAIL if version is unchanged: "plugin.json version not bumped — run `/release-plugin <name> <new-version>` first."

### 4. Check CHANGELOG touched

- PASS if `plugins/<plugin>/CHANGELOG.md` appears in the diff from step 2.
- FAIL if absent: "CHANGELOG.md not updated — add an entry for this release."

### 5. Check README updated when commands or SKILL changed

If any of these paths are in the diff:

- `plugins/<plugin>/commands/*.md`
- `plugins/<plugin>/skills/**/SKILL.md`

Then `plugins/<plugin>/README.md` must also be in the diff.

- PASS if README is touched or none of the trigger paths changed.
- FAIL if trigger paths changed but README did not: "commands/ or SKILL.md changed — update README.md to reflect new behavior."

### 6. Check marketplace.json description (informational)

The root marketplace.json lives at `.claude-plugin/marketplace.json` — not inside the plugin directory — so it never appears in the scoped diff from step 2. Run a separate unscoped diff:

```bash
git diff main...HEAD --name-only
```

If `.claude-plugin/marketplace.json` appears in this diff, note it as touched. If not touched, remind: "Consider updating `.claude-plugin/marketplace.json` description if this change is user-facing."

## Output

Print a checklist:

```
Release checklist for acss-kit (main...HEAD)

  [PASS] plugin.json version bumped (0.2.1 → 0.3.0)
  [FAIL] CHANGELOG.md not updated
  [PASS] README.md updated alongside command changes
  [INFO] marketplace.json not touched — update description if change is user-facing

1 item needs attention before opening a PR.
```

If all required checks pass: "Release paperwork complete. Ready to open a PR."

Do not commit, push, or open the PR — leave that to the user or `/ship`.
