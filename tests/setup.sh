#!/usr/bin/env bash
# Scaffold a disposable Vite + React + TypeScript sandbox at tests/sandbox/
# for smoke-testing the acss-plugins marketplace locally.
#
# Usage:
#   tests/setup.sh           # first-time setup (errors if sandbox exists)
#   tests/setup.sh --reset   # wipe and recreate the sandbox

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SANDBOX="$REPO_ROOT/tests/sandbox"
RESET=0

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
  echo "Run this script from inside the acss-plugins repo." >&2
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

mkdir -p "$REPO_ROOT/tests"

echo "Scaffolding Vite + React + TypeScript at $SANDBOX..."
# create-vite mishandles absolute paths in some versions (it treats them as relative
# to cwd, producing a nested duplicate). Workaround: cd to the parent and pass a
# bare directory name. NPM_CONFIG_YES skips the "Ok to proceed?" exec prompt.
cd "$REPO_ROOT/tests"
NPM_CONFIG_YES=true npm create vite@latest sandbox -- --template react-ts

cd "$SANDBOX"

echo "Installing dependencies..."
npm install --silent

echo "Adding sass (required by every acss plugin that writes SCSS)..."
npm install --silent --save-dev sass

# --- Recipe (written before commit so it's part of the bootstrap) --------
# Generated first, ahead of the bootstrap commit, so RECIPE.md is included in
# the initial commit. If we wrote it after, the sandbox would have an untracked
# file from the start — defeating the "clean anchor" the bootstrap commit is
# meant to provide for plugin dirty-tree guards.

cat > "$SANDBOX/RECIPE.md" <<EOF
# Local plugin testing recipe

This sandbox is a disposable Vite + React + TypeScript project. From here:

\`\`\`
claude
\`\`\`

Inside the Claude Code session, paste these commands (the path is quoted so it works even if your repo lives under a directory with spaces):

\`\`\`
/plugin marketplace add "$REPO_ROOT"
/plugin install acss-app-builder@acss-plugins
/plugin install acss-kit-builder@acss-plugins
/plugin install acss-theme-builder@acss-plugins
/plugin install acss-component-specs@acss-plugins
\`\`\`

Then exercise the plugins. Suggested smoke flow:

\`\`\`
/app-init
/app-page dashboard
/theme-create "#4f46e5"
/kit-add badge
\`\`\`

Verify file changes appear under \`src/\`: \`app/\`, \`pages/\`, \`styles/theme/\`, plus your kit components directory (default: \`src/components/fpkit/\`, configurable on first \`/kit-add\` run via \`.acss-target.json\`).

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
#     might add later; running pre-commit or commit-msg hooks against vite
#     scaffolding output is not meaningful
# The .invalid TLD is reserved by RFC 2606 to signal a non-real address.
# Subsequent commits the contributor makes inside tests/sandbox/ use their
# normal git config — the overrides only affect this one invocation.
git -c user.name="acss-plugins sandbox" \
    -c user.email="sandbox@acss-plugins.invalid" \
    -c commit.gpgsign=false \
    commit --no-verify -q -m "initial sandbox"

echo ""
echo "================================================================"
cat "$SANDBOX/RECIPE.md"
echo "================================================================"
echo ""
echo "Sandbox ready. cd tests/sandbox && claude"
