#!/usr/bin/env python3
"""Package an RTV mod folder as a .vmz archive.

Usage: build_mod.py <ModFolder> [--version X.Y.Z] [--out DIR]

If --version is provided, rewrites the `version=` line in the archived
mod.txt (the working tree is not modified). Output filename is always
`<ModFolder>.vmz` — the game's mod loader keys off the folder/archive
name, so versioning lives in the tag and Release title, not the filename.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path

from modlib import PROJECT_ROOT, load_manifest, rewrite_version_in_mod_txt


def build(mod_folder: Path, out_dir: Path, version_override: str | None) -> Path:
    manifest = load_manifest(mod_folder)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{mod_folder.name}.vmz"

    rewritten_mod_txt: str | None = None
    if version_override and version_override != manifest.version:
        original = (mod_folder / "mod.txt").read_text(encoding="utf-8")
        rewritten_mod_txt = rewrite_version_in_mod_txt(original, version_override)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(mod_folder.rglob("*")):
            if not file.is_file():
                continue
            arcname = file.relative_to(mod_folder).as_posix()
            if rewritten_mod_txt is not None and arcname == "mod.txt":
                zf.writestr(arcname, rewritten_mod_txt)
            else:
                zf.write(file, arcname)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mod_folder", help="Mod folder name (relative to repo root) or path")
    parser.add_argument("--version", help="Override version in packaged mod.txt")
    parser.add_argument(
        "--out",
        default=str(Path(tempfile.gettempdir())),
        help="Output directory (default: system temp)",
    )
    args = parser.parse_args()

    mod_folder = Path(args.mod_folder)
    if not mod_folder.is_absolute():
        candidate = PROJECT_ROOT / mod_folder
        if candidate.is_dir():
            mod_folder = candidate
    if not mod_folder.is_dir():
        print(f"Error: mod folder {mod_folder} not found", file=sys.stderr)
        return 1

    out_path = build(mod_folder, Path(args.out), args.version)
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
