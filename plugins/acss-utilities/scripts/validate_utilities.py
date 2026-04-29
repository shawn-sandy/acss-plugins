#!/usr/bin/env python3
"""
Validate utility CSS files for the acss-utilities plugin.

Two modes (auto-detected by filename):

  Mode A — utility CSS files (`utilities.css` or `utilities/<family>.css`)
    - Selectors must be `.kebab-case`, with optional escaped breakpoint
      prefix (e.g. `.sm\\:hide`) and optional pseudo-class (e.g. `:focus`).
    - Every `var(--x)` must include a fallback (`var(--x, …)`).
    - No duplicate selectors at the same nesting level.
    - Every responsive variant present at one breakpoint must be present
      at every other breakpoint declared in the file.
    - Bundle file (`utilities.css`) must not exceed the size budget.
      Resolution order: `--max-kb` flag (explicit) → `bundleSizeBudgetKb`
      from a `utilities.tokens.json` co-located with the bundle or under
      the validation target → fallback 80.

  Mode B — `token-bridge.css`
    - Every `--alias-name: …;` declaration in `:root` must also appear in
      `[data-theme="dark"]`. Dark-mode parity is mandatory; without it,
      utility colors silently fall back to light values when the page is
      in dark mode.

Output contract: detector style — JSON to stdout with a `reasons` array.
Exit 0 on success, 1 on logical failure, 2 on usage / IO errors.

Stdlib + tinycss2 (already a test dependency for `validate_components.py`).

Usage:
    python3 validate_utilities.py <file-or-dir> [--max-kb N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

try:
    import tinycss2
except ImportError:
    print(json.dumps({
        "ok": False,
        "reasons": ["tinycss2 not installed: run `pip3 install --user tinycss2`"],
    }))
    sys.exit(2)


# Allowed breakpoint-or-media prefix names. Includes `print` and the four
# responsive breakpoints; if a token file adds new ones, extend this list
# from the same source.
DEFAULT_PREFIXES = ("sm", "md", "lg", "xl", "print")

# A utility selector: `.<prefix>\:<name>` or `.<name>`, with optional
# pseudo-class (e.g. `:focus`, `:focus-within`).
SELECTOR_RE = re.compile(
    r"^\."
    r"(?:(?P<prefix>[a-z][a-z0-9-]*)\\:)?"        # optional escaped prefix
    r"(?P<name>[a-z][a-z0-9-]*)"
    r"(?P<pseudo>(?::[a-z-]+)*)$"
)

# Bare var() with no fallback — same regex as validate_components.py but
# wider (any custom property prefix). Utility CSS may reference roles
# from any `--*` namespace.
VAR_NO_FALLBACK_RE = re.compile(r"var\(\s*--[A-Za-z0-9_-]+\s*\)")

# Inside `[data-theme="dark"]`, this matches every declared property name.
DECL_NAME_RE = re.compile(r"(?P<name>--[a-z0-9-]+)\s*:", re.IGNORECASE)


def _selectors_from_prelude(prelude) -> List[str]:
    """Extract comma-separated selectors from a tinycss2 prelude."""
    text = tinycss2.serialize(prelude).strip()
    return [s.strip() for s in text.split(",") if s.strip()]


def _validate_selector(sel: str, prefixes: Tuple[str, ...]) -> List[str]:
    failures: List[str] = []
    m = SELECTOR_RE.match(sel)
    if not m:
        failures.append(f"selector not in canonical form: {sel}")
        return failures
    prefix = m.group("prefix")
    if prefix and prefix not in prefixes:
        failures.append(
            f"selector {sel}: unknown breakpoint prefix '{prefix}' "
            f"(allowed: {', '.join(prefixes)})"
        )
    return failures


def validate_utility_file(path: Path, prefixes: Tuple[str, ...]) -> List[str]:
    failures: List[str] = []
    text = path.read_text(encoding="utf-8")
    rules = tinycss2.parse_stylesheet(text, skip_whitespace=True, skip_comments=True)

    # Walk: (context, selector) → count, plus per-prefix variant set. The
    # context key is the empty string at top-level or the serialized media
    # condition (e.g. "(width >= 30rem)") inside an @media — that way the
    # same selector can legitimately appear under multiple media queries
    # without tripping the duplicate check.
    seen_selectors: Dict[Tuple[str, str], int] = defaultdict(int)
    base_classes: Set[str] = set()
    per_bp_classes: Dict[str, Set[str]] = defaultdict(set)

    def visit_qualified(rule, current_ctx: str):
        body = tinycss2.serialize(rule.content) if rule.content else ""
        for m in VAR_NO_FALLBACK_RE.finditer(body):
            failures.append(f"{path.name}: var() without fallback: {m.group(0)}")
        for sel in _selectors_from_prelude(rule.prelude):
            failures.extend(_validate_selector(sel, prefixes))
            seen_selectors[(current_ctx, sel)] += 1
            sm = SELECTOR_RE.match(sel)
            if not sm:
                continue
            prefix = sm.group("prefix") or ""
            name = sm.group("name")
            # Pseudo-classes don't participate in parity checks.
            if sm.group("pseudo"):
                continue
            if not prefix:
                base_classes.add(name)
            else:
                per_bp_classes[prefix].add(name)

    for rule in rules:
        if rule.type == "error":
            failures.append(f"{path.name}: parser error at line {rule.source_line}: {rule.message}")
            continue
        if rule.type == "qualified-rule":
            visit_qualified(rule, "")
        elif rule.type == "at-rule" and rule.lower_at_keyword == "media":
            media_ctx = "@media " + tinycss2.serialize(rule.prelude).strip()
            inner_text = tinycss2.serialize(rule.content) if rule.content else ""
            inner = tinycss2.parse_stylesheet(inner_text, skip_whitespace=True, skip_comments=True)
            for inner_rule in inner:
                if inner_rule.type == "qualified-rule":
                    visit_qualified(inner_rule, media_ctx)

    # Duplicate selectors within the same context.
    for (ctx, sel), count in seen_selectors.items():
        if count > 1:
            ctx_label = ctx or "top-level"
            failures.append(f"{path.name}: duplicate selector {sel} in {ctx_label} ({count}×)")

    # Responsive parity: every base class that appears prefixed at one bp
    # should appear at every other declared bp (`print` is exempt — fpkit
    # only ships `.print\:hide`).
    declared_bps = sorted(b for b in per_bp_classes if b != "print")
    if declared_bps:
        for bp in declared_bps:
            for cls in per_bp_classes[bp]:
                # If a class has a base form, no parity issue.
                if cls in base_classes:
                    continue
                # Otherwise, every other declared bp should also have it.
                missing = [other for other in declared_bps if cls not in per_bp_classes[other]]
                if missing:
                    failures.append(
                        f"{path.name}: responsive parity gap — '.{bp}\\:{cls}' "
                        f"is declared but missing at: {', '.join(missing)}"
                    )

    return failures


def validate_bridge_file(path: Path) -> List[str]:
    failures: List[str] = []
    text = path.read_text(encoding="utf-8")
    rules = tinycss2.parse_stylesheet(text, skip_whitespace=True, skip_comments=True)

    root_decls: Set[str] = set()
    dark_decls: Set[str] = set()

    for rule in rules:
        if rule.type == "error":
            failures.append(f"{path.name}: parser error at line {rule.source_line}: {rule.message}")
            continue
        if rule.type != "qualified-rule":
            continue
        sel = tinycss2.serialize(rule.prelude).strip()
        body = tinycss2.serialize(rule.content) if rule.content else ""
        names = {m.group("name") for m in DECL_NAME_RE.finditer(body)}
        # Tolerate `:root, :where(...)` and similar compound selectors.
        if sel == ":root" or sel.startswith(":root"):
            root_decls.update(names)
        elif "[data-theme=\"dark\"]" in sel or "[data-theme='dark']" in sel:
            dark_decls.update(names)
        # Accept any `var()` references, including ones without fallback,
        # because the bridge's job is to *define* fallbacks for utilities.

    if not root_decls:
        failures.append(f"{path.name}: bridge file has no :root declarations")
    if not dark_decls and root_decls:
        failures.append(f"{path.name}: bridge file has no [data-theme=\"dark\"] block")
    missing_in_dark = sorted(root_decls - dark_decls)
    if missing_in_dark:
        failures.append(
            f"{path.name}: bridge dark-mode parity gap — declared in :root "
            f"but missing in [data-theme=\"dark\"]: {', '.join(missing_in_dark)}"
        )
    return failures


def is_bridge_path(path: Path) -> bool:
    return "token-bridge" in path.name


def is_utility_path(path: Path) -> bool:
    return path.name == "utilities.css" or path.parent.name == "utilities"


def collect_files(target: Path) -> List[Path]:
    """Return the CSS files this validator knows how to handle.

    For a single file: only return it if its filename matches a utility
    bundle/partial or a token-bridge — otherwise the validator's two
    modes don't apply and the caller would get confusing failures (e.g.
    selector-grammar errors against an unrelated stylesheet). The empty
    list signals "no recognised files" and `main()` raises a usage error.

    For a directory: walk the tree and collect every matching file.
    """
    if target.is_file():
        if is_bridge_path(target) or is_utility_path(target):
            return [target]
        return []
    files: List[Path] = []
    for p in target.rglob("*.css"):
        if is_bridge_path(p) or is_utility_path(p):
            files.append(p)
    return files


def find_budget_kb(target: Path, bundle: Path | None) -> int | None:
    """Locate `utilities.tokens.json#bundleSizeBudgetKb` near the bundle or
    target. Returns the integer budget if found, else None."""
    candidates: List[Path] = []
    if bundle is not None:
        candidates.append(bundle.parent / "utilities.tokens.json")
        candidates.append(bundle.parent.parent / "utilities.tokens.json")
    if target.is_dir():
        candidates.append(target / "utilities.tokens.json")
    for tokens_path in candidates:
        if tokens_path.is_file():
            try:
                data = json.loads(tokens_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            kb = data.get("bundleSizeBudgetKb")
            if isinstance(kb, int) and kb > 0:
                return kb
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    parser.add_argument("target", help="File or directory to validate")
    parser.add_argument("--max-kb", type=int, default=None,
                        help="Bundle size budget for utilities.css. "
                             "Defaults to bundleSizeBudgetKb from a co-located "
                             "utilities.tokens.json, or 80 if neither is set.")
    parser.add_argument("--prefixes", default=",".join(DEFAULT_PREFIXES),
                        help="Allowed breakpoint prefixes, comma-separated")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(json.dumps({"ok": False, "reasons": [f"not found: {target}"]}))
        return 2

    prefixes = tuple(p.strip() for p in args.prefixes.split(",") if p.strip())
    files = collect_files(target)

    if not files:
        if target.is_file():
            # Unrecognised filename — the validator's two modes (utility CSS,
            # token-bridge CSS) are auto-detected by name, so a mismatch is
            # a usage error rather than a contract violation.
            reason = (
                f"unrecognised filename: {target.name}. "
                f"This validator only handles `utilities.css`, "
                f"`utilities/<family>.css`, or `token-bridge*.css`."
            )
            print(json.dumps({"ok": False, "reasons": [reason]}))
            return 2
        print(json.dumps({
            "ok": False,
            "reasons": [f"no utility CSS files found under {target}"],
        }))
        return 1

    failures: List[str] = []
    bundle_files: List[Path] = []

    for f in sorted(files):
        if is_bridge_path(f):
            failures.extend(validate_bridge_file(f))
        else:
            failures.extend(validate_utility_file(f, prefixes))
            if f.name == "utilities.css":
                bundle_files.append(f)

    # Bundle-size budget — applies only to the concatenated bundle.
    for f in bundle_files:
        if args.max_kb is not None:
            budget_kb = args.max_kb
        else:
            budget_kb = find_budget_kb(target, f) or 80
        size = f.stat().st_size
        if size > budget_kb * 1024:
            failures.append(
                f"{f.name}: bundle size {size} bytes exceeds budget "
                f"{budget_kb} KB ({budget_kb * 1024} bytes)"
            )

    payload = {
        "ok": len(failures) == 0,
        "filesScanned": len(files),
        "reasons": failures,
    }
    print(json.dumps(payload, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
