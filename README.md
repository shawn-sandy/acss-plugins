# agentic-acss-plugins

A Claude Code plugin marketplace for building accessible React applications with the [fpkit/acss](https://github.com/shawn-sandy/acss) design system.

## Plugins in this marketplace

| Plugin | Purpose |
|---|---|
| [`acss-kit`](./plugins/acss-kit) | Generate accessible React components and CSS themes for fpkit/acss projects. Run `/setup` to bootstrap a project (sass check, `ui.tsx` copy, starter theme), then `/kit-add` for components and `/theme-create` or `/style-tune` for theme and component-style work. Skills: **setup** (project bootstrap), **components** (markdown-as-source TSX/SCSS generation), **styles** (OKLCH theme generation and component SCSS tuning with WCAG 2.2 AA validation), plus the **style-tune** and **component-form** pilots. |
| [`acss-utilities`](./plugins/acss-utilities) | Tailwind-style atomic CSS utility classes (`.bg-primary`, `.mt-4`, `.sm-hide`) for fpkit/acss projects. Hyphen-prefix responsive variants — no CSS escaping needed. Pairs with `acss-kit` via a token-bridge so utility colors resolve against the same OKLCH roles. Run `/utility-add` to drop the bundle into your project; `/utility-list`, `/utility-tune`, and `/utility-bridge` round out the workflow. |

The two plugins are decoupled — install one, both, or use `acss-utilities` standalone with a hand-written theme.

## Install

```shell
/plugin marketplace add shawn-sandy/agentic-acss-plugins
/plugin install acss-kit@shawn-sandy-agentic-acss-plugins
/plugin install acss-utilities@shawn-sandy-agentic-acss-plugins
```

## Migration

If you previously installed `acss-kit-builder`, `acss-theme-builder`, `acss-app-builder`, or `acss-component-specs` — these have been consolidated into the single `acss-kit` plugin (or, in the case of `acss-app-builder` and `acss-component-specs`, removed entirely). Uninstall the old plugins and install `acss-kit` instead. See [`plugins/acss-kit/CHANGELOG.md`](./plugins/acss-kit/CHANGELOG.md) for the full migration notes.

Existing `.acss-target.json` files at project roots remain compatible — the schema is unchanged.

If you installed `acss-utilities` 0.1.0, the 0.2.0 release switched responsive variants from the escaped-colon form (`.sm\:hide`) to a plain hyphen (`.sm-hide`) — see [`plugins/acss-utilities/CHANGELOG.md`](./plugins/acss-utilities/CHANGELOG.md) and the `scripts/migrate_classnames.py` dry-run helper.

## Testing locally

`tests/run.sh` from the repo root is the default automated check — structural validation in ~30 seconds, no browser. One-time setup: `npm --prefix tests ci && pip3 install --user tinycss2`.

```sh
tests/run.sh
```

For render-sensitive changes, `tests/e2e.sh` runs the deeper opt-in check (~30s after first install) — extracts components from reference docs, type-checks them with `tsc --noEmit`, compiles SCSS, validates theme contrast, and runs jsdom + axe-core a11y on rendered output.

For end-to-end slash-command verification, `tests/setup.sh` writes a minimal verification fixture at `tests/sandbox/` (gitignored) — `package.json` + `tsconfig.json`, no Vite, no app shell:

```sh
tests/setup.sh
cd tests/sandbox && claude
```

See [`tests/README.md`](./tests/README.md) for the full workflow, the `--reset` flag, escape hatches, and troubleshooting.

## Relationship to the main fpkit repo

Plugin development references the live fpkit source at [`shawn-sandy/acss`](https://github.com/shawn-sandy/acss). Contributors should keep both repos available side-by-side — see [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the workflow.

SKILL.md files and reference docs in the plugin link to specific fpkit source files via full GitHub URLs, so plugin authors can click through without a local clone.

## License

MIT
