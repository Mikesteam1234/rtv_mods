#!/usr/bin/env python3
"""Validate an RTV mod folder against the publishing guide's sanity checks.

Exits non-zero on errors. Warnings are printed but do not fail the run.
See .claude/knowledge_base/guides/publishing.md for the canonical list.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from modlib import PROJECT_ROOT, load_manifest

SEMVER_RE = re.compile(r"^\d+(\.\d+)*$")


def validate(mod_folder: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    mod_txt = mod_folder / "mod.txt"
    if not mod_txt.is_file():
        errors.append(f"{mod_folder.name}: mod.txt missing at folder root")
        return errors, warnings

    try:
        manifest = load_manifest(mod_folder)
    except (ValueError, FileNotFoundError) as e:
        errors.append(str(e))
        return errors, warnings

    if not SEMVER_RE.match(manifest.version):
        errors.append(
            f"{mod_folder.name}: version {manifest.version!r} is not dot-separated integers "
            "(pre-release tags like 1.0.0-beta are not supported by the mod loader)"
        )

    for file in mod_folder.rglob("*"):
        if not file.is_file():
            continue
        rel = file.relative_to(mod_folder)
        if "\\" in str(rel):
            errors.append(f"{mod_folder.name}: path contains backslash: {rel}")

    for gd_file in mod_folder.rglob("*.gd"):
        try:
            text = gd_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("print(") or stripped.startswith("prints("):
                rel = gd_file.relative_to(mod_folder)
                warnings.append(f"{mod_folder.name}: {rel}:{lineno} contains debug print")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mod_folder", help="Mod folder name (relative to repo root) or path")
    args = parser.parse_args()

    mod_folder = Path(args.mod_folder)
    if not mod_folder.is_absolute():
        candidate = PROJECT_ROOT / mod_folder
        if candidate.is_dir():
            mod_folder = candidate
    if not mod_folder.is_dir():
        print(f"Error: mod folder {mod_folder} not found", file=sys.stderr)
        return 1

    errors, warnings = validate(mod_folder)
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"{mod_folder.name}: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
