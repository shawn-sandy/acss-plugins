#!/usr/bin/env bash
# End-to-end skill-output verification.
#
# Exercises the same artifacts /kit-add and /theme-create produce, then
# asserts they pass type-check, SCSS compile, and a jsdom + axe-core a11y
# audit. Does not run a Claude Code session — slash commands are thin
# wrappers over Python scripts and a markdown extractor, both of which we
# call directly.
#
# Run AFTER tests/run.sh (which is the structural gate). This script is
# the deeper opt-in check that replaces the old tests/storybook.sh.
#
# Prerequisites:
#   - Node 20+ and npm
#   - python3
#   - tests/node_modules populated: npm --prefix tests ci

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TESTS_DIR="$REPO_ROOT/tests"
ACSS_KIT="$REPO_ROOT/plugins/acss-kit"
SCRIPTS="$ACSS_KIT/scripts"
REFS="$ACSS_KIT/skills/components/references/components"

# Components we exercise end-to-end. Limited to those with a fixture entry
# in tests/lib/render_components.mjs DEFAULT_PROPS — adding a new entry
# there extends coverage. Compound deps (Card.Title etc.) come along via
# resolve_deps.mjs.
SEED_COMPONENTS=("button" "link" "input")

red()    { printf '\033[31m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
section(){ printf '\n\033[1m== %s ==\033[0m\n' "$*"; }

# --- Preflight ----------------------------------------------------------

if ! command -v node >/dev/null 2>&1; then
  red "Error: 'node' not found on PATH."
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  red "Error: 'python3' not found on PATH."
  exit 1
fi
if [[ ! -d "$TESTS_DIR/node_modules" ]]; then
  red "tests/node_modules missing. Run: npm --prefix tests ci"
  exit 1
fi

# --- Temp fixture -------------------------------------------------------
# Per-invocation temp dir keeps tests/sandbox/ available for the developer
# without clobbering it. Cleanup on exit.

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

mkdir -p "$SANDBOX/src/components/fpkit"
mkdir -p "$SANDBOX/src/styles/theme"

# Symlink node_modules from tests/ so tsc/sass/react resolve without a
# second npm install. Faster than installing per-run.
ln -s "$TESTS_DIR/node_modules" "$SANDBOX/node_modules"

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

cat > "$SANDBOX/src/scss-modules.d.ts" <<'SCSS_DTS'
declare module '*.scss';
declare module '*.css';
SCSS_DTS

green "fixture: $SANDBOX"

# --- Step 1: axe self-test (negative-path check) -----------------------
# Run BEFORE generating real output, so a broken harness fails fast and
# loudly rather than producing a misleading green on real output.

section "1. axe self-test (verify the harness itself can detect violations)"
node "$TESTS_DIR/run_axe.mjs" --self-test

# --- Step 2: extract components ----------------------------------------

section "2. extract seed components and their dependencies"
RESOLVED=()
while IFS= read -r name; do
  RESOLVED+=("$name")
done < <(node "$TESTS_DIR/lib/resolve_deps.mjs" "$REPO_ROOT" "${SEED_COMPONENTS[@]}")

yellow "resolved order: ${RESOLVED[*]}"

# Copy ui.tsx foundation first.
cp "$ACSS_KIT/assets/foundation/ui.tsx" "$SANDBOX/src/components/fpkit/ui.tsx"

for name in "${RESOLVED[@]}"; do
  COMP_DIR="$SANDBOX/src/components/fpkit/$name"
  mkdir -p "$COMP_DIR"
  # Use the type-checkable extractor: TSX Template only, with Key Pattern
  # markers inlined. Mirrors what /kit-add does at runtime, unlike the
  # syntax-only lib/extract.mjs that tests/run.sh relies on.
  node --input-type=module -e "
    import { extractFull } from '$TESTS_DIR/lib/extract_full.mjs'
    import { writeFileSync } from 'node:fs'
    const { tsx, scss } = extractFull('$REFS/$name.md')
    writeFileSync('$COMP_DIR/$name.tsx', tsx)
    if (scss) writeFileSync('$COMP_DIR/$name.scss', scss)
  "
done
green "extracted ${#RESOLVED[@]} component(s)"

# --- Step 3: generate a theme via the Python pipeline ------------------

section "3. generate theme (light + dark) via /theme-create pipeline"
PALETTE_JSON="$(mktemp)"
trap 'rm -rf "$SANDBOX" "$PALETTE_JSON"' EXIT

python3 "$SCRIPTS/generate_palette.py" "#4f46e5" --mode=both > "$PALETTE_JSON"
python3 "$SCRIPTS/tokens_to_css.py" --stdin "--out-dir=$SANDBOX/src/styles/theme" < "$PALETTE_JSON"
ls "$SANDBOX/src/styles/theme/"

# --- Step 4: WCAG contrast on generated theme ---------------------------

section "4. validate generated theme contrast"
python3 "$SCRIPTS/validate_theme.py" "$SANDBOX/src/styles/theme"

# --- Step 5: type-check generated TSX -----------------------------------

section "5. tsc --noEmit against generated TSX"
(cd "$TESTS_DIR" && npx --no-install tsc --noEmit -p "$SANDBOX/tsconfig.json")

# --- Step 6: compile generated SCSS ------------------------------------

section "6. sass compile every generated SCSS file"
SCSS_FAIL=0
while IFS= read -r f; do
  if ! (cd "$TESTS_DIR" && npx --no-install sass --no-source-map --quiet "$f" >/dev/null); then
    red "  sass FAIL: $f"
    SCSS_FAIL=1
  else
    green "  ok: $f"
  fi
done < <(find "$SANDBOX/src/components/fpkit" -name '*.scss')
if [[ "$SCSS_FAIL" -ne 0 ]]; then
  red "sass compilation failures detected."
  exit 1
fi

# --- Step 7: render components and run axe -----------------------------

section "7. render components to HTML and run axe-core"
RENDERED_DIR="$SANDBOX/rendered"
RENDERED_LIST="$(mktemp)"
trap 'rm -rf "$SANDBOX" "$PALETTE_JSON" "$RENDERED_LIST"' EXIT

(cd "$TESTS_DIR" && node "$TESTS_DIR/lib/render_components.mjs" \
  "$SANDBOX/src/components/fpkit" "$RENDERED_DIR") > "$RENDERED_LIST"

# render_components.mjs prints status lines on stderr/stdout AND emits one
# rendered file path per line on stdout. Filter to just the path lines
# (those that end in .html and exist on disk).
HTML_FILES=()
while IFS= read -r line; do
  if [[ "$line" == *.html && -f "$line" ]]; then
    HTML_FILES+=("$line")
  fi
done < "$RENDERED_LIST"

if [[ "${#HTML_FILES[@]}" -eq 0 ]]; then
  red "render_components.mjs produced no HTML files."
  exit 1
fi

node "$TESTS_DIR/run_axe.mjs" --html "${HTML_FILES[@]}"

# --- Step 8: assert expected files exist -------------------------------

section "8. assert expected file tree"
EXPECTED=(
  "src/components/fpkit/ui.tsx"
  "src/components/fpkit/button/button.tsx"
  "src/components/fpkit/button/button.scss"
  "src/styles/theme/light.css"
  "src/styles/theme/dark.css"
)
MISSING=0
for rel in "${EXPECTED[@]}"; do
  if [[ ! -f "$SANDBOX/$rel" ]]; then
    red "  missing: $rel"
    MISSING=1
  fi
done
if [[ "$MISSING" -ne 0 ]]; then
  red "expected file tree incomplete."
  exit 1
fi
green "expected files present"

green ""
green "tests/e2e.sh: ALL PASSED"
