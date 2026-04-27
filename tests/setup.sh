#!/usr/bin/env bash
# Scaffold a minimal verification fixture at tests/sandbox/.
#
# This is the manual demo / smoke-test path. For automated checks, run:
#
#     tests/run.sh   # ~30s structural validation (default gate)
#     tests/e2e.sh   # full skill-output verification (tsc + sass + jsdom+axe)
#
# The fixture is intentionally minimal — no Vite, no Storybook, no app shell.
# It is a `package.json` + `tsconfig.json` + ambient SCSS module declaration,
# just enough to host the files `/kit-add` and `/theme-create` write and to
# let `tsc --noEmit` and `sass` validate that output. There is no `npm run dev`
# in this fixture; previewing rendered components in a real browser was
# explicitly removed because the goal is to test the skill output, not to
# render a React app.
#
# Usage:
#   tests/setup.sh           # first-time setup (errors if sandbox exists)
#   tests/setup.sh --reset   # wipe and recreate the sandbox

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SANDBOX="$REPO_ROOT/tests/sandbox"
RESET=0

cat >&2 <<'BANNER'
[tests/setup.sh] This scaffolds the manual demo fixture.
                 For automated tests, run: tests/run.sh (default) or tests/e2e.sh

BANNER

if [[ $# -gt 1 ]]; then
  echo "Too many arguments: $*" >&2
  echo "Usage: tests/setup.sh [--reset]" >&2
  exit 1
fi

case "${1:-}" in
  --reset) RESET=1 ;;
  "")      ;;
  *)       echo "Unknown argument: $1" >&2
           echo "Usage: tests/setup.sh [--reset]" >&2
           exit 1 ;;
esac

# --- Preflight -----------------------------------------------------------

if ! command -v node >/dev/null 2>&1; then
  echo "Error: 'node' not found on PATH." >&2
  echo "Install Node 20+ from https://nodejs.org or via your version manager." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: 'npm' not found on PATH." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: 'git' not found on PATH." >&2
  echo "git is required for the bootstrap commit inside the sandbox." >&2
  exit 1
fi

if [[ ! -f "$REPO_ROOT/.claude-plugin/marketplace.json" ]]; then
  echo "Error: marketplace.json not found at $REPO_ROOT/.claude-plugin/" >&2
  echo "Run this script from inside the agentic-acss-plugins repo." >&2
  exit 1
fi

if [[ -d "$SANDBOX" && "$RESET" -eq 0 ]]; then
  echo "Sandbox already exists at: $SANDBOX"
  echo "Re-run with --reset to wipe and recreate it."
  exit 1
fi

# --- Scaffold ------------------------------------------------------------

if [[ -d "$SANDBOX" ]]; then
  echo "Removing existing sandbox..."
  rm -rf "$SANDBOX"
fi

mkdir -p "$SANDBOX/src"

echo "Writing minimal fixture at $SANDBOX..."

cat > "$SANDBOX/package.json" <<'PKG_JSON'
{
  "name": "acss-kit-sandbox",
  "version": "0.0.0",
  "private": true,
  "description": "Minimal fixture for manual smoke-testing of acss-kit slash commands. Not a real app.",
  "type": "module",
  "scripts": {
    "typecheck": "tsc --noEmit"
  },
  "devDependencies": {
    "typescript": "5.4.5",
    "sass": "1.77.8",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "@types/react": "18.3.3",
    "@types/react-dom": "18.3.0"
  }
}
PKG_JSON

cat > "$SANDBOX/tsconfig.json" <<'TS_CONFIG'
{
  "compilerOptions": {
    "target": "es2022",
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "noEmit": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "resolveJsonModule": true,
    "types": []
  },
  "include": ["src"]
}
TS_CONFIG

# Ambient declaration so component TSX with `import './foo.scss'` type-checks.
# Several reference docs (nav, card, img, link, table, ...) emit these imports.
cat > "$SANDBOX/src/scss-modules.d.ts" <<'SCSS_DTS'
declare module '*.scss';
declare module '*.css';
SCSS_DTS

# Placeholder so /kit-add has a stable directory tree to write into.
touch "$SANDBOX/src/.gitkeep"

cd "$SANDBOX"

echo "Installing fixture devDependencies (typescript, sass, react)..."
npm install --silent

# --- Recipe (written before commit so it's part of the bootstrap) --------
# Generated first, ahead of the bootstrap commit, so RECIPE.md is included in
# the initial commit. If we wrote it after, the sandbox would have an
# untracked file from the start — defeating the "clean anchor" the bootstrap
# commit provides for plugin dirty-tree guards.

cat > "$SANDBOX/RECIPE.md" <<EOF
# Local plugin testing recipe

This sandbox is a minimal verification fixture — a \`package.json\`, a
\`tsconfig.json\`, and an ambient SCSS module declaration. There is no app
shell, no Vite, no dev server. The goal is to host the files \`/kit-add\`
and \`/theme-create\` write and verify them with \`tsc --noEmit\` and \`sass\`.

From here:

\`\`\`
claude
\`\`\`

Inside the Claude Code session, paste these commands (the path is quoted so
it works even if your repo lives under a directory with spaces):

\`\`\`
/plugin marketplace add "$REPO_ROOT"
/plugin install acss-kit@agentic-acss-plugins
\`\`\`

Then exercise the plugin. Suggested smoke flow:

\`\`\`
/plugin list
/kit-list
/kit-add button card
/theme-create "#4f46e5" --mode=both
\`\`\`

Verify file changes appear under \`src/\`:
\`styles/theme/light.css\`, \`styles/theme/dark.css\`, plus your kit components
directory (default: \`src/components/fpkit/\`, configurable on first
\`/kit-add\` run via \`.acss-target.json\`).

Type-check the generated TSX from this directory:
\`\`\`
npm run typecheck
\`\`\`

Compile a generated SCSS file to confirm it parses:
\`\`\`
npx sass --no-source-map src/components/fpkit/button/button.scss
\`\`\`

Reset this sandbox with:
\`\`\`
"$REPO_ROOT/tests/setup.sh" --reset
\`\`\`
EOF

# --- Bootstrap commit ----------------------------------------------------
# Some plugin commands refuse to run on a dirty tree. Initializing a git repo
# with one commit (including RECIPE.md, written above) gives those guards a
# clean anchor for the developer's first run.

echo "Initializing git and committing the bootstrap state..."
git init -q
git add -A
# Per-invocation -c flags cover three failure modes contributors hit on real
# machines without polluting their global config:
#   - synthetic identity: works on fresh machines with no user.name/user.email
#   - commit.gpgsign=false: signing a synthetic identity would be misleading,
#     and contributors who enforce signing globally would otherwise hard-fail
#   - --no-verify: the bootstrap commit predates any project hooks the dev
#     might add later; running pre-commit or commit-msg hooks against fixture
#     scaffolding output is not meaningful
# The .invalid TLD is reserved by RFC 2606 to signal a non-real address.
# Subsequent commits the contributor makes inside tests/sandbox/ use their
# normal git config — the overrides only affect this one invocation.
git -c user.name="agentic-acss-plugins sandbox" \
    -c user.email="sandbox@agentic-acss-plugins.invalid" \
    -c commit.gpgsign=false \
    commit --no-verify -q -m "initial sandbox"

echo ""
echo "================================================================"
cat "$SANDBOX/RECIPE.md"
echo "================================================================"
echo ""
echo "Sandbox ready. cd tests/sandbox && claude"
