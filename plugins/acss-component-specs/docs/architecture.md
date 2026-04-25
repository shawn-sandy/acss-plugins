# acss-component-specs — Architecture (Contributor Guide)

This page is for maintainers editing the plugin: adding new renderers, modifying scripts, updating specs, or extending cross-plugin coordination.

## Plugin layout

```
plugins/acss-component-specs/
  .claude-plugin/
    plugin.json                     # Authoritative version source
  assets/
    foundation/
      ui.tsx                        # Polymorphic UI base for React renderer; copied into user projects
      ui-html.css                   # CSS baseline for HTML renderer
    fpkit-cache/
      .gitkeep                      # Cache populated at runtime by fetch_fpkit_source.py; gitignored
  commands/
    spec-add.md                     # /spec-add command definition
    spec-render.md                  # /spec-render command definition
    spec-diff.md                    # /spec-diff command definition
    spec-promote.md                 # /spec-promote command definition
    spec-validate.md                # /spec-validate command definition
    spec-list.md                    # /spec-list command definition
  scripts/
    fetch_fpkit_source.py
    parse_spec.py
    validate_spec.py
    plan_render.py
    check_kitbuilder_parity.py
    verify_contract_subset.py
  skills/
    acss-component-specs/
      SKILL.md                      # Full runbook for all six commands
      specs/                        # Bundled reference specs
        button.md
        card.md + card-title.md + card-content.md + card-footer.md
        dialog.md
        alert.md
        stack.md
        nav.md + nav-link.md
      references/
        spec-format.md              # Authoritative schema
        authoring-guide.md          # 10-step contributor walkthrough
        compound-components.md      # Sub-spec pattern across all 3 renderers
        state-and-events.md         # Stateful component patterns
        frameworks/
          react.md                  # React+SCSS renderer rulebook
          html.md                   # HTML+CSS renderer rulebook, native element catalog
          astro.md                  # Astro+SCSS renderer rulebook
```

## Command → SKILL delegation

Each command file in `commands/` is thin: it declares the signature, tools, and a one-line body that ends with "Follow SKILL.md § /<command>". The logic lives entirely in the corresponding section of `SKILL.md`. Do not duplicate the workflow inside the command file.

## scripts/ contract

All Python scripts must satisfy four rules (from the repo-level `CLAUDE.md`):

1. **Python 3 stdlib only** — no third-party packages (`pip install` is not available in plugin context).
2. **Output JSON to stdout** — one JSON object, complete and valid.
3. **Exit 0 on success, 1 on failure**.
4. **Include a `"reasons"` array** in JSON output for human-readable error messages.

### Script reference

| Script | Input | JSON output shape | Notes |
|--------|-------|-------------------|-------|
| `parse_spec.py` | `<spec-file>` | `{ ok, data: { frontmatter, sections, theme_dependencies }, reasons }` | Hand-rolled minimal YAML parser; rejects anchors/aliases; auto-derives `theme_dependencies` from `var(--color-*, …)` patterns |
| `validate_spec.py` | `[spec-file ...] [--stale]` | `{ ok, data: { validated, errors: { path: [msg] }, stale: [...] }, reasons }` | Imports `parse_spec` via `sys.path.insert`; `--stale` scans project files for `// generated from <spec>.md@<ver>` stamps |
| `plan_render.py` | `<spec-file> [--target=react\|html\|astro\|all]` | `{ ok, data: { component, targets, dependency_order, manifest, staging_base, is_compound_part }, reasons }` | Hard-codes `DEPENDENCY_GRAPH` and `COMPOUND_PARTS` set; compound parts return empty manifests |
| `check_kitbuilder_parity.py` | `<component> [<component2> …]` | `{ ok, data: { results: { <comp>: { ok, reasons } } }, reasons }` | Compares `.acss-staging/react/<c>/<c>.scss` against kit-builder `## SCSS Pattern` block; "no kit-builder counterpart" is a pass |
| `verify_contract_subset.py` | (none) | `{ ok, data: { ref_files_checked, contract_fields_seen, missing }, reasons }` | Walks kit-builder `references/components/*.md`; confirms every Generation Contract field maps to a spec frontmatter field |
| `fetch_fpkit_source.py` | `<component> [--refresh]` | `{ ok, data: { component, sha, cache_path, source_url, fetched, [bytes] }, reasons }` | Only script with filesystem side effects (writes cache); uses `urllib.request` (stdlib); 7-day TTL; SHA-resolve failure falls back to `'main'` as version label |

## How compound parts are handled

`plan_render.py` maintains a `COMPOUND_PARTS` set (e.g., `{'card-title', 'card-content', 'card-footer', 'nav-link'}`). When a component name is in this set, `plan_render.py` returns an empty `manifest` — the sub-part's output is emitted *inside* the parent component file, not in a dedicated file.

The `is_compound_part` flag in the output tells the SKILL that the parent spec should be the render target. For Astro, compound parts are emitted as separate files (because Astro does not use `Object.assign` on components) — `plan_render.py` handles this per-target.

When adding a new compound parent, update `DEPENDENCY_GRAPH` and add the sub-part names to `COMPOUND_PARTS`.

## How the render pipeline slots together

```
/spec-render button --target=react
  → plan_render.py          (dependency order + file manifest)
  → SKILL.md §R3            (lazy-load references/frameworks/react.md + spec file)
  → SKILL.md §R4            (emit files to .acss-staging/react/, stamp each file)
  → SKILL.md §R5            (theme check: scan project for :root { --color-* })
  → SKILL.md §R6            (gitignore check: prompt to add .acss-staging/)
```

Each `references/frameworks/*.md` is loaded **lazily** — only the relevant renderer doc is read during a given render invocation. This keeps the LLM's context lean when rendering a single framework.

## Cross-plugin coordination

### With acss-kit-builder

- **Spec wins:** When kit-builder is installed, Step B0 of kit-builder's SKILL probes for the spec before using its bundled reference doc. No configuration required; the probe is passive.
- **`check_kitbuilder_parity.py`:** Pre-commit hook (fires when `specs/*.md` changes). Compares staged SCSS against kit-builder's bundled SCSS pattern. Keeps the two sources in sync during the transition window before kit-builder's bundled references are deprecated.
- **`verify_contract_subset.py`:** Used by `/release-check`. Confirms that every field in kit-builder's Generation Contract blocks has a corresponding spec frontmatter field. Ensures the interop shape stays intact.

### With acss-app-builder

- **`.acss-target.json.framework`:** Component-specs extends the shared config with an optional `framework` field. App-builder reads `componentsDir`; component-specs reads both `componentsDir` and `framework`. Both plugins commit to the same file — do not remove fields the other plugin writes.

### With acss-theme-builder

- **CSS cascade, no imports:** Every SCSS file uses `var(--component-prop, var(--color-token, #hardcoded))`. Theme values propagate via the natural CSS cascade when theme-builder output is present. The SKILL warns (step R5) if no `:root { --color-* }` block is found, but the component is functional either way.

## Adding a new renderer (framework)

1. Add a new `references/frameworks/<name>.md` following the structure of `react.md`, `html.md`, or `astro.md`. Include: file-output naming rules, per-`maps_to` kind mappings, asset copy prompts (e.g., `ui.tsx` equivalent), and state/event handling patterns.
2. Update `plan_render.py` to accept the new `--target=<name>` value and add the file manifest logic for the new framework.
3. Update the `SKILL.md` sections for `/spec-render` and `/spec-promote` to reference the new target.
4. Update all six command files if their argument-hint or description changes.
5. Bump `plugin.json` version.

## v0.2 roadmap (from CHANGELOG)

Known deferrals so contributors know what's in-flight and should not re-implement:

- Web component HTML renderer (`<fpk-button>` with shadow DOM) — deferred from v0.1.
- Astro inline `<style>` blocks option — deferred from v0.1.
- `/spec-migrate` tooling for `format_version` upgrades — deferred from v0.1.
- Second-wave components: Form, Badge, Tag, Heading, Text, Link, Icon — deferred from v0.1.
- Bidirectional drift detection in `/spec-diff` (currently staging → project only) — deferred to v0.3.

## format_version policy

`format_version: 1` is the current schema version. It is bumped **only** when the schema breaks backward compatibility (removing a required field, changing a field's type, renaming a `maps_to` kind). Do not bump it for additive changes (new optional fields). The bump requires a migration path for existing specs — document it in the CHANGELOG and consider shipping `/spec-migrate` tooling before bumping.
