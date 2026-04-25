# acss-plugins

Claude Code plugins for building applications with [@fpkit/acss](https://github.com/shawn-sandy/acss) React components.

## Plugins in this marketplace

| Plugin | Purpose |
|---|---|
| [`acss-app-builder`](./plugins/acss-app-builder) | Scaffold apps with the fpkit design system — layouts, pages, themes, forms, patterns. Works with the `@fpkit/acss` npm package OR generated source. |
| [`acss-kit-builder`](./plugins/acss-kit-builder) | Generate fpkit-style React components directly into your project — no `@fpkit/acss` npm install required. |
| [`acss-theme-builder`](./plugins/acss-theme-builder) | Generate and update CSS themes — create from seed colors, scaffold brand presets, update roles in place, extract from images or Figma. |
| [`fpkit-developer`](./plugins/fpkit-developer) | **Deprecated** — superseded by `acss-app-builder`. Kept for one release cycle. |

See [GUIDE.md](./GUIDE.md) for the full end-user guide — install, choose a plugin, run commands, troubleshoot.

## Install

```shell
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-app-builder@shawn-sandy-acss-plugins
/plugin install acss-kit-builder@shawn-sandy-acss-plugins
```

## Testing locally

Contributors can smoke-test plugin changes against a disposable sandbox without leaking artifacts into the repo:

```sh
tests/setup.sh
cd tests/sandbox && claude
```

The sandbox is gitignored. See [`tests/README.md`](./tests/README.md) for the full workflow, the `--reset` flag, and troubleshooting.

## Relationship to the main fpkit repo

Plugin development references the live fpkit source at [`shawn-sandy/acss`](https://github.com/shawn-sandy/acss). Contributors should keep both repos available side-by-side — see [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the workflow.

SKILL.md files and reference docs in each plugin link to specific fpkit source files via full GitHub URLs, so plugin authors can click through without a local clone.

## License

MIT
