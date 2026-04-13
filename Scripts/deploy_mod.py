#!/usr/bin/env python3

import os
import sys
import subprocess
import zipfile
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
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


def main():
    if not ENV_FILE.exists():
        print(f"Error: {ENV_FILE} not found. Copy Scripts/.env.example to Scripts/.env and fill in your values.", file=sys.stderr)
        sys.exit(1)

    env = load_env(ENV_FILE)
    rtv_path = env.get("RTV_PATH")
    if not rtv_path:
        print(f"Error: RTV_PATH is not set in {ENV_FILE}", file=sys.stderr)
        sys.exit(1)
    mod_dest_path = Path(rtv_path) / "mods"

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <mod-folder-name>", file=sys.stderr)
        sys.exit(1)

    mod_name = sys.argv[1].rstrip("/")
    mod_dir = PROJECT_ROOT / mod_name

    if not mod_dir.is_dir():
        print(f"Error: Folder '{mod_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    zip_path = Path(tempfile.gettempdir()) / f"{mod_name}.vmz"

    print(f"Zipping {mod_name}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in mod_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(mod_dir))
    print(f"Created {zip_path}")

    print(f"Deploying to {mod_dest_path}...")
    subprocess.run(["rsync", "-av", str(zip_path), mod_dest_path], check=True)
    print("Deploy complete.")

    print(f"Cleaning up {zip_path}...")
    zip_path.unlink()
    print("Done.")


if __name__ == "__main__":
    main()
