#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
ENV_FILE = SCRIPT_DIR / ".env"

DEFAULT_RECOVER_PATH = "/mnt/c/Dev/RTV/Decomp"


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

    dcmp_path = env.get("DCMP_PATH")
    if not dcmp_path:
        print(f"Error: DCMP_PATH is not set in {ENV_FILE}", file=sys.stderr)
        sys.exit(1)

    recover_path = env.get("RECOVER_PATH", DEFAULT_RECOVER_PATH)

    pck_file = Path(rtv_path) / "RTV.pck"
    if not pck_file.exists():
        print(f"Error: PCK file not found at {pck_file}", file=sys.stderr)
        sys.exit(1)

    dcmp_dir = Path(dcmp_path)
    dcmp_dir.mkdir(parents=True, exist_ok=True)

    recover_dir = Path(recover_path)
    recover_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting {pck_file} to {dcmp_dir}...")
    subprocess.run(
        ["godotpcktool", str(pck_file), "--action", "extract", "--output", str(dcmp_dir)],
        check=True,
    )
    print("Extraction complete.")

    print(f"Running full recovery from {dcmp_dir} to {recover_dir}...")
    subprocess.run(
        ["gdre_tools.x86_64", "--headless", f"--recover={dcmp_dir}", f"--output={recover_dir}"],
        check=True,
    )
    print(f"Recovery complete. Decompiled project is at {recover_dir}")


if __name__ == "__main__":
    main()
