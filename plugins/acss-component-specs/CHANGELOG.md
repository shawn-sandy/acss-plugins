# Changelog — acss-component-specs

## [0.1.0] — 2026-04-24

Initial release.

### Added

- Framework-agnostic spec format (YAML frontmatter + Markdown body)
- `format_version: 1` — **experimental; breaking changes possible until v1.0.0**
- 6 component specs: Button, Card (+ compound parts), Dialog, Alert, Stack, Nav (+ Nav.Link)
- 3 framework renderers: React+SCSS, HTML+CSS, Astro+SCSS
- Canonical 3-step render flow: `/spec-render` → `/spec-diff` → `/spec-promote`
- Python scripts (stdlib only): `parse_spec.py`, `validate_spec.py`, `plan_render.py`, `check_kitbuilder_parity.py`, `verify_contract_subset.py`, `fetch_fpkit_source.py`
- 6 slash commands: `/spec-add`, `/spec-render`, `/spec-diff`, `/spec-promote`, `/spec-validate`, `/spec-list`
- `maps_to` discriminator with 7 kinds: `data-attr`, `data-attr-token`, `aria`, `prop`, `class`, `element`, `css-var`
- `a11y` block with WCAG 2.2 SC validation; `layout_only: true` exemption for layout primitives
- Atomic render failure mode: all or nothing, no partial staging output
- Version stamps in generated files (`// generated from button.md@0.1.0`)
- `--stale` flag on `/spec-validate` to scan project files for outdated stamps
- Auto-gitignore `.acss-staging/` on first render
- Kit-builder bridge: specs take precedence over bundled kit-builder references when installed
- `framework` field extension to `.acss-target.json` for per-project render target defaults
- Legacy banners on kit-builder bundled component references pointing to new specs
- Pre-commit hook: editing `specs/*.md` triggers `check_kitbuilder_parity.py`
- `fetch_fpkit_source.py` caches fpkit source under `assets/fpkit-cache/<sha>/` (7-day TTL)

### Spec Format (format_version: 1)

The spec format is declared experimental. Any schema change bumps `format_version`. User-authored specs may require manual updates until spec migration tooling ships in v0.2.

### Known Limitations

- Web component HTML renderer (`<fpk-button>` with shadow DOM) deferred to v0.2
- Astro inline `<style>` block option deferred to v0.2
- Spec migration tooling (`/spec-migrate`) deferred to v0.2
- Second-wave components (Form, Badge, Tag, Heading, Text, Link, Icon) deferred to v0.2
- Bidirectional drift detection in `/spec-diff` deferred to v0.3
