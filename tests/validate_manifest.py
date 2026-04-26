#!/usr/bin/env python3
"""Validate marketplace.json + each plugin's plugin.json + required files.

Replicates the structural checks performed by the verify-plugins skill so
the harness can run standalone without a Claude session. Mirrors the
detector contract: JSON to stdout, "reasons" array, exit 0 on success
and 1 on logical failure.

Checks:
  - Repo-level marketplace.json: required fields, well-formed plugins
    array, and **no `version` key inside any plugin entry** (silent
    override hazard documented in CLAUDE.md).
  - Each referenced plugin: plugin.json present + required fields
    + semver-shaped version.
  - Each plugin directory contains: README.md, CHANGELOG.md, at least
    one commands/*.md, at least one SKILL.md anywhere under skills/.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"

REQUIRED_MARKETPLACE_FIELDS = {"name", "description", "owner", "plugins"}
REQUIRED_PLUGIN_ENTRY_FIELDS = {"name", "source", "description"}
REQUIRED_PLUGIN_MANIFEST_FIELDS = {"name", "description", "version", "author"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][\w.-]+)?$")


def fail(reasons: list[str]) -> int:
    print(json.dumps({"ok": False, "reasons": reasons}, indent=2))
    return 1


def ok(detail: dict) -> int:
    print(json.dumps({"ok": True, "reasons": [], **detail}, indent=2))
    return 0


def check_plugin_dir(name: str, source: str) -> list[str]:
    failures: list[str] = []
    plugin_dir = (REPO_ROOT / source).resolve()
    if not plugin_dir.is_dir():
        failures.append(f"{name}: source path not found: {source}")
        return failures

    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if not manifest_path.exists():
        failures.append(f"{name}: missing .claude-plugin/plugin.json")
    else:
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as e:
            failures.append(f"{name}: plugin.json is invalid JSON: {e}")
            manifest = None
        if manifest is not None:
            missing = REQUIRED_PLUGIN_MANIFEST_FIELDS - manifest.keys()
            if missing:
                failures.append(
                    f"{name}: plugin.json missing required fields: {sorted(missing)}",
                )
            version = manifest.get("version")
            if version and not SEMVER_RE.match(version):
                failures.append(
                    f"{name}: plugin.json version {version!r} is not semver",
                )

    for required in ("README.md", "CHANGELOG.md"):
        if not (plugin_dir / required).exists():
            failures.append(f"{name}: missing {required}")

    commands_dir = plugin_dir / "commands"
    if commands_dir.is_dir():
        if not list(commands_dir.glob("*.md")):
            failures.append(f"{name}: commands/ directory has no .md files")
    else:
        failures.append(f"{name}: missing commands/ directory")

    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        if not list(skills_dir.rglob("SKILL.md")):
            failures.append(f"{name}: no SKILL.md anywhere under skills/")
    else:
        failures.append(f"{name}: missing skills/ directory")

    return failures


def main() -> int:
    if not MARKETPLACE_PATH.exists():
        return fail([f"marketplace.json not found at {MARKETPLACE_PATH}"])

    try:
        marketplace = json.loads(MARKETPLACE_PATH.read_text())
    except json.JSONDecodeError as e:
        return fail([f"marketplace.json is invalid JSON: {e}"])

    failures: list[str] = []

    missing = REQUIRED_MARKETPLACE_FIELDS - marketplace.keys()
    if missing:
        failures.append(
            f"marketplace.json missing required fields: {sorted(missing)}",
        )

    plugins = marketplace.get("plugins", [])
    if not isinstance(plugins, list) or not plugins:
        failures.append("marketplace.json plugins must be a non-empty array")
        return fail(failures)

    for entry in plugins:
        name = entry.get("name", "<unnamed>")
        entry_missing = REQUIRED_PLUGIN_ENTRY_FIELDS - entry.keys()
        if entry_missing:
            failures.append(
                f"{name}: marketplace entry missing required fields: {sorted(entry_missing)}",
            )
        if "version" in entry:
            failures.append(
                f"{name}: marketplace entry has a `version` key. Remove it — "
                "plugin.json is the authoritative source and the marketplace "
                "version is silently overridden (see CLAUDE.md).",
            )
        if "source" in entry:
            failures.extend(check_plugin_dir(name, entry["source"]))

    if failures:
        return fail(failures)
    return ok({"plugins": [p.get("name") for p in plugins]})


if __name__ == "__main__":
    sys.exit(main())
