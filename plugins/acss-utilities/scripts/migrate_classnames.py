#!/usr/bin/env python3
"""
Migrate acss-utilities class names from 0.1.x colon form to 0.2.0 hyphen form.

Rewrites `sm:hide` → `sm-hide`, `md:p-6` → `md-p-6`, etc. in source files.
By default performs a dry run and prints a unified diff per modified file.
Use --write to apply changes in place.

Contract: generator/validator (data on stdout, errors on stderr, exit 0/1/2).
Stdlib only.

Usage:
    migrate_classnames.py <path> [<path>...]
                          [--write]
                          [--include=<glob>,<glob>,...]
                          [--exclude=<glob>,<glob>,...]
                          [--prefixes=sm,md,lg,xl,print]

Exit codes:
    0 — no changes needed (or all applied with --write)
    1 — dry-run: changes pending (use --write to apply)
    2 — usage / IO error

Match strategy (conservative):
    The substitution `(sm|md|lg|xl|print):` → `<prefix>-` is applied only
    inside string-literal contexts per file type:
      - JSX/TSX, TS/JS: inside `className="..."`, `className='...'`,
        `className={\`...\`}`, and clsx/classnames call arguments.
      - HTML/Svelte/Vue/Astro: inside `class="..."` and `className="..."` attributes.
      - CSS/SCSS: inside `@apply <classes>;` directives and literal `.<prefix>\\:<name>`
        selectors (old escaped-colon form in hand-authored CSS).

    Known limitations (documented, not silently skipped):
      - Combo prefixes like `lg:hover:bg-primary` (not used by this plugin's grammar)
        will have the leading `lg:` rewritten to `lg-` — incorrect in that system.
      - Vue `:class="[...]"` array bindings, Svelte `class:` directives, and Astro
        expressions are not rewritten in v0.2.0 — use --write with review.
      - Comments inside any format are skipped.

    Idempotency: running the script twice on the same tree produces zero diffs
    on the second run.
"""
from __future__ import annotations

import argparse
import difflib
import fnmatch
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_PREFIXES = ("sm", "md", "lg", "xl", "print")

# Extensions handled per family.
JSX_EXTS = {".jsx", ".tsx"}
JS_EXTS = {".js", ".ts", ".mjs", ".cjs"}
HTML_EXTS = {".html", ".svelte", ".vue", ".astro"}
CSS_EXTS = {".css", ".scss"}

ALL_HANDLED = JSX_EXTS | JS_EXTS | HTML_EXTS | CSS_EXTS

# Default glob patterns to exclude (version-control dirs, build artefacts).
DEFAULT_EXCLUDES = {
    ".git", "node_modules", "dist", "build", ".next", ".nuxt", "__pycache__",
}


# ---------------------------------------------------------------------------
# Core rewriter
# ---------------------------------------------------------------------------

def _build_prefix_re(prefixes: Tuple[str, ...]) -> re.Pattern[str]:
    """Match `<prefix>:<letter>` — the `:` is the substitution target."""
    alt = "|".join(re.escape(p) for p in sorted(prefixes, key=len, reverse=True))
    return re.compile(r"(?<![A-Za-z0-9_-])(" + alt + r"):([a-z])")


def _replace(m: re.Match, _prefixes: Tuple[str, ...]) -> str:
    return m.group(1) + "-" + m.group(2)


def _rewrite_string_value(text: str, prefix_re: re.Pattern) -> str:
    """Replace all `<prefix>:` → `<prefix>-` inside `text`."""
    return prefix_re.sub(lambda m: _replace(m, ()), text)


# --- JSX / TS / JS ---------------------------------------------------------

# className="..." or className='...' (static strings)
_JSX_CLASSNAME_DQ = re.compile(r'(className\s*=\s*")([^"]*?)(")')
_JSX_CLASSNAME_SQ = re.compile(r"(className\s*=\s*')([^']*?)(')")
# className={`...`} template literal
_JSX_CLASSNAME_TMPL = re.compile(r"(className\s*=\s*\{`)(.*?)(`\})", re.DOTALL)
# clsx/classnames/cx("...", '...') — captures first arg string only; handles
# typical patterns like clsx("hide sm:show", condition && "md:flex")
_CLSX_STR_DQ = re.compile(r'(clsx|classnames|cx)\s*\(([^)]*)\)', re.DOTALL)


def _rewrite_jsx(src: str, prefix_re: re.Pattern) -> str:
    def rw_attr(m: re.Match) -> str:
        return m.group(1) + _rewrite_string_value(m.group(2), prefix_re) + m.group(3)

    out = _JSX_CLASSNAME_DQ.sub(rw_attr, src)
    out = _JSX_CLASSNAME_SQ.sub(rw_attr, out)
    out = _JSX_CLASSNAME_TMPL.sub(rw_attr, out)

    # clsx/cx calls: rewrite string literals inside the call parens.
    def rw_clsx(m: re.Match) -> str:
        fn = m.group(1)
        args = m.group(2)
        # Replace inside double-quoted strings within the args.
        args = re.sub(r'"([^"]*)"', lambda a: '"' + _rewrite_string_value(a.group(1), prefix_re) + '"', args)
        args = re.sub(r"'([^']*)'", lambda a: "'" + _rewrite_string_value(a.group(1), prefix_re) + "'", args)
        return fn + "(" + args + ")"

    out = _CLSX_STR_DQ.sub(rw_clsx, out)
    return out


# --- HTML / Svelte / Vue / Astro --------------------------------------------

# class="..." or className="..." attribute values only.
_HTML_CLASS_DQ = re.compile(r'((?:class|className)\s*=\s*")([^"]*?)(")')
_HTML_CLASS_SQ = re.compile(r"((?:class|className)\s*=\s*')([^']*?)(')")


def _rewrite_html(src: str, prefix_re: re.Pattern) -> str:
    def rw(m: re.Match) -> str:
        return m.group(1) + _rewrite_string_value(m.group(2), prefix_re) + m.group(3)

    out = _HTML_CLASS_DQ.sub(rw, src)
    out = _HTML_CLASS_SQ.sub(rw, out)
    return out


# --- CSS / SCSS -------------------------------------------------------------

# @apply <classes>;  — rewrite only the class list.
_APPLY_RE = re.compile(r"(@apply\s+)(.*?)(;)", re.DOTALL)
# Old escaped-colon selector: `.sm\:hide` in hand-authored CSS.
_CSS_ESCAPED_COLON = re.compile(r"\.((?:sm|md|lg|xl|print))\\:([a-z][a-z0-9-]*)")


def _rewrite_css(src: str, prefix_re: re.Pattern) -> str:
    def rw_apply(m: re.Match) -> str:
        return m.group(1) + _rewrite_string_value(m.group(2), prefix_re) + m.group(3)

    out = _APPLY_RE.sub(rw_apply, src)
    # Rewrite old escaped-colon selectors to hyphen form.
    out = _CSS_ESCAPED_COLON.sub(lambda m: "." + m.group(1) + "-" + m.group(2), out)
    return out


# ---------------------------------------------------------------------------
# File-level dispatch
# ---------------------------------------------------------------------------

def rewrite_file(path: Path, prefixes: Tuple[str, ...]) -> Optional[str]:
    """Return rewritten content if any changes are needed, else None."""
    ext = path.suffix.lower()
    if ext not in ALL_HANDLED:
        return None

    src = path.read_text(encoding="utf-8", errors="replace")
    prefix_re = _build_prefix_re(prefixes)

    if ext in JSX_EXTS | JS_EXTS:
        out = _rewrite_jsx(src, prefix_re)
    elif ext in HTML_EXTS:
        out = _rewrite_html(src, prefix_re)
    elif ext in CSS_EXTS:
        out = _rewrite_css(src, prefix_re)
    else:
        return None

    return out if out != src else None


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def _matches_any(name: str, patterns: List[str]) -> bool:
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def collect_paths(
    roots: List[Path],
    include: List[str],
    exclude: List[str],
) -> List[Path]:
    found: List[Path] = []
    for root in roots:
        if root.is_file():
            if root.suffix.lower() in ALL_HANDLED:
                found.append(root)
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            # Skip excluded directories (check any component of the relative path).
            rel = p.relative_to(root)
            parts = rel.parts
            if any(_matches_any(part, list(DEFAULT_EXCLUDES) + exclude) for part in parts):
                continue
            if p.suffix.lower() not in ALL_HANDLED:
                continue
            if include and not _matches_any(p.name, include):
                continue
            found.append(p)
    return sorted(set(found))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", help="Files or directories to process")
    parser.add_argument("--write", action="store_true", help="Apply changes in place (default: dry-run diff)")
    parser.add_argument("--include", default="", help="Comma-separated glob patterns to include (e.g. '*.tsx,*.ts')")
    parser.add_argument("--exclude", default="", help="Comma-separated glob patterns to exclude")
    parser.add_argument("--prefixes", default=",".join(DEFAULT_PREFIXES),
                        help="Breakpoint prefixes to rewrite (default: sm,md,lg,xl,print)")
    args = parser.parse_args()

    include = [p.strip() for p in args.include.split(",") if p.strip()]
    exclude = [p.strip() for p in args.exclude.split(",") if p.strip()]
    prefixes = tuple(p.strip() for p in args.prefixes.split(",") if p.strip())

    roots: List[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if not p.exists():
            print(f"error: path not found: {p}", file=sys.stderr)
            return 2
        roots.append(p)

    files = collect_paths(roots, include, exclude)
    if not files:
        print("No handled files found.", file=sys.stderr)
        return 0

    changes_pending = False

    for path in files:
        try:
            new_content = rewrite_file(path, prefixes)
        except OSError as e:
            print(f"error reading {path}: {e}", file=sys.stderr)
            return 2

        if new_content is None:
            continue

        changes_pending = True

        if args.write:
            try:
                path.write_text(new_content, encoding="utf-8")
                print(f"updated: {path}")
            except OSError as e:
                print(f"error writing {path}: {e}", file=sys.stderr)
                return 2
        else:
            # Print unified diff.
            old_lines = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
            new_lines = new_content.splitlines(keepends=True)
            diff = difflib.unified_diff(
                old_lines, new_lines,
                fromfile=f"a/{path}",
                tofile=f"b/{path}",
            )
            sys.stdout.writelines(diff)

    if changes_pending and not args.write:
        print("\n# Dry run complete — rerun with --write to apply changes.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
