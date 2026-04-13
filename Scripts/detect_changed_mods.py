#!/usr/bin/env python3
"""Emit the set of mod folders touched between two git refs as JSON.

Usage: detect_changed_mods.py [--base REF] [--head REF]

Defaults: base=origin/dev, head=HEAD. Output is a JSON array of folder names
suitable for consumption as a GitHub Actions matrix via fromJSON().
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from modlib import PROJECT_ROOT, discover_mod_folders


def git_changed_files(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/dev")
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args()

    mod_folder_names = {f.name for f in discover_mod_folders()}
    try:
        changed = git_changed_files(args.base, args.head)
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e.stderr}", file=sys.stderr)
        return 1

    touched = set()
    for path in changed:
        first = path.split("/", 1)[0]
        if first in mod_folder_names:
            touched.add(first)

    print(json.dumps(sorted(touched)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
