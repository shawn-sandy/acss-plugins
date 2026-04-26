---
name: release-plugin
description: Bump a plugin's version in plugin.json and update marketplace.json description if needed. Run before committing a publishable change.
disable-model-invocation: false
---

# /release-plugin

Usage: `/release-plugin <plugin-name> <new-version>`

Example: `/release-plugin acss-kit 0.3.1`

## Steps

1. **Confirm the plugin exists** — parse the first argument as `<plugin-name>`, verify it is `acss-kit`, and confirm `plugins/acss-kit/.claude-plugin/plugin.json` exists. If not, list available plugins from `.claude-plugin/marketplace.json` and stop.

2. **Read current version** from `plugins/<plugin>/.claude-plugin/plugin.json`.

3. **Validate the new version** — must be a valid semver string (`MAJOR.MINOR.PATCH`). Refuse if not.

4. **Bump `plugin.json`** — update the `"version"` field in `plugins/<plugin>/.claude-plugin/plugin.json`.

5. **Check marketplace.json** — read `.claude-plugin/marketplace.json`. If the matching plugin entry contains a `"version"` key, **remove it** and warn the user ("marketplace.json should not have a version field — the plugin.json always wins").

6. **Ask the user** if the marketplace.json `description` for this plugin needs updating to reflect the change. If yes, update it.

7. **Print a pre-commit summary**:
   - Plugin bumped: `<plugin>` `<old>` → `<new>`
   - Files modified: list them
   - Reminder: "Run the pre-submit checklist in AGENTS.md before committing."

Do not commit. Do not push. Leave that to the user.
