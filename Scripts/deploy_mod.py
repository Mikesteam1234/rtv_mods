#!/usr/bin/env python3
"""Local dev convenience: build a mod's .vmz and rsync it to $RTV_PATH/mods/.

For CI packaging, call build_mod.py directly.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from build_mod import build
from modlib import PROJECT_ROOT

SCRIPT_DIR = Path(__file__).parent.resolve()
ENV_FILE = SCRIPT_DIR / ".env"


def load_env(path: Path) -> dict:
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def main() -> int:
    if not ENV_FILE.exists():
        print(f"Error: {ENV_FILE} not found. Copy Scripts/.env.example to Scripts/.env and fill in your values.", file=sys.stderr)
        return 1

    env = load_env(ENV_FILE)
    rtv_path = env.get("RTV_PATH")
    if not rtv_path:
        print(f"Error: RTV_PATH is not set in {ENV_FILE}", file=sys.stderr)
        return 1
    mod_dest_path = Path(rtv_path) / "mods"

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <mod-folder-name>", file=sys.stderr)
        return 1

    mod_name = sys.argv[1].rstrip("/")
    mod_dir = PROJECT_ROOT / mod_name
    if not mod_dir.is_dir():
        print(f"Error: Folder '{mod_dir}' does not exist.", file=sys.stderr)
        return 1

    print(f"Zipping {mod_name}...")
    zip_path = build(mod_dir, Path(tempfile.gettempdir()), version_override=None)
    print(f"Created {zip_path}")

    print(f"Deploying to {mod_dest_path}...")
    subprocess.run(["rsync", "-av", str(zip_path), mod_dest_path], check=True)
    print("Deploy complete.")

    zip_path.unlink()
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
