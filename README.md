# acss-plugins

A Claude Code plugin marketplace for building accessible React applications with the [fpkit/acss](https://github.com/shawn-sandy/acss) design system.

## Plugins in this marketplace

| Plugin | Purpose |
|---|---|
| [`acss-kit`](./plugins/acss-kit) | Generate accessible React components and CSS themes for fpkit/acss projects. Two skills: **components** (markdown-as-source TSX/SCSS generation via `/kit-add`) and **styles** (OKLCH theme generation via `/theme-create` and friends, with WCAG 2.2 AA validation). |

## Install

```shell
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-kit@shawn-sandy-acss-plugins
```

## Migration

If you previously installed `acss-kit-builder`, `acss-theme-builder`, `acss-app-builder`, or `acss-component-specs` — these have been consolidated into the single `acss-kit` plugin (or, in the case of `acss-app-builder` and `acss-component-specs`, removed entirely). Uninstall the old plugins and install `acss-kit` instead. See [`plugins/acss-kit/CHANGELOG.md`](./plugins/acss-kit/CHANGELOG.md) for the full migration notes.

Existing `.acss-target.json` files at project roots remain compatible — the schema is unchanged.

## Testing locally

Contributors can smoke-test plugin changes against a disposable sandbox without leaking artifacts into the repo:

```sh
tests/setup.sh
cd tests/sandbox && claude
```

The sandbox is gitignored. See [`tests/README.md`](./tests/README.md) for the full workflow, the `--reset` flag, and troubleshooting.

## Relationship to the main fpkit repo

Plugin development references the live fpkit source at [`shawn-sandy/acss`](https://github.com/shawn-sandy/acss). Contributors should keep both repos available side-by-side — see [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the workflow.

SKILL.md files and reference docs in the plugin link to specific fpkit source files via full GitHub URLs, so plugin authors can click through without a local clone.

## License

MIT
