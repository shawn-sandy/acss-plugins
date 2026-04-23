# Changelog

All notable changes to the `acss-app-builder` plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the plugin adheres to [Semantic Versioning](https://semver.org/).

## [0.1.2] - 2026-04-22

### Added

- `CHANGELOG.md` (this file).
- `scripts/README.md` — index of the four Python helpers. Documents the split between detection scripts (JSON on stdout) and validator scripts (plain text + exit-code semantics), including correct field names on each output path.
- `## Installation` section in README with marketplace + manual install instructions.

### Fixed

- Typo in the `/plugin uninstall` migration snippet — now uses the correct marketplace name `shawn-sandy-acss-plugins`. Corrected in two places: `README.md` (line 17) and `commands/app-compose.md` (line 14). Copy-pasting either snippet will now actually uninstall the deprecated plugin instead of silently no-opping.

## [0.1.1]

Extracted from `shawn-sandy/acss` into the `acss-plugins` marketplace. Supersedes the deprecated `fpkit-developer` plugin. See `git log -- plugins/acss-app-builder` for the full development history of the seven `/app-*` commands, reference docs, and assets.
