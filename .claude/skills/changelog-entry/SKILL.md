---
name: changelog-entry
description: Generate a Keep-a-Changelog entry for acss-kit from git log since last tag. Groups commits by conventional type and appends to plugins/acss-kit/CHANGELOG.md under the Unreleased section.
disable-model-invocation: true
---

Run these commands to gather context:

```bash
git log $(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD --oneline
```

Then read `plugins/acss-kit/CHANGELOG.md` to see the existing format.

Group the commits by conventional commit type:
- `feat` → **Added**
- `fix` → **Fixed**
- `docs` → **Changed**
- `refactor` → **Changed**
- `chore`, `build`, `ci` → omit unless user-facing

Format as a Keep-a-Changelog block using today's date:

```
## [Unreleased]

### Added
- …

### Fixed
- …

### Changed
- …
```

Show the proposed entry to the user. Wait for explicit approval before writing. Insert it above the previous latest version entry in `plugins/acss-kit/CHANGELOG.md`.
