#!/usr/bin/env python3
"""ModWorkshop release helper.

Today the ModWorkshop API is GET-only (per their OpenAPI spec). This script
does a read-only sanity check: fetches the current latest file version on MW
for a mod and compares it to an expected version, emitting a markdown summary
suitable for a GitHub Release body or Actions job summary.

When MW enables write access + API keys, implement upload() below.

Usage:
  publish_modworkshop.py check <ModFolder> --expected-version X.Y.Z [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from modlib import PROJECT_ROOT, load_manifest

API_BASE = "https://api.modworkshop.net"


def fetch_latest_version(mod_id: int) -> str | None:
    url = f"{API_BASE}/mods/{mod_id}/files/latest/version"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8").strip()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    if not body:
        return None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return body.strip('"')
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        for key in ("version", "data"):
            if key in data and isinstance(data[key], str):
                return data[key]
    return None


def version_tuple(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            return tuple()
    return tuple(parts)


def check(mod_folder: Path, expected_version: str) -> str:
    manifest = load_manifest(mod_folder)
    lines = [f"## ModWorkshop upload checklist — {manifest.name} v{expected_version}", ""]

    if manifest.modworkshop_id is None:
        lines += [
            "- No `[updates] modworkshop=<id>` set in `mod.txt`, so no MW page is linked yet.",
            "- Publish the mod on ModWorkshop, then add the id to `mod.txt` in a follow-up PR.",
            "",
            "Attach the `.vmz` from this release to the ModWorkshop page when ready.",
        ]
        return "\n".join(lines)

    mw_id = manifest.modworkshop_id
    edit_url = f"https://modworkshop.net/mod/{mw_id}/edit"
    try:
        remote = fetch_latest_version(mw_id)
    except (urllib.error.URLError, TimeoutError) as e:
        remote = None
        lines.append(f"- WARNING: could not reach ModWorkshop API ({e}); skipping version check.")

    if remote is None:
        lines.append(f"- No prior file version found on ModWorkshop for mod id {mw_id}.")
    else:
        exp_t = version_tuple(expected_version)
        rem_t = version_tuple(remote)
        if exp_t and rem_t and rem_t >= exp_t:
            lines.append(
                f"- WARNING: ModWorkshop already has version `{remote}`, which is >= the release "
                f"version `{expected_version}`. Uploading may create a duplicate."
            )
        else:
            lines.append(f"- ModWorkshop currently shows `{remote}`; this release bumps to `{expected_version}`.")

    lines += [
        "",
        "Manual upload steps (API writes are not yet supported by ModWorkshop):",
        "",
        f"1. Open [{edit_url}]({edit_url}).",
        "2. Go to **Downloads & Updates** and upload the `.vmz` attached to this release.",
        "3. Mark the new file active and set its version name to match this tag.",
        "4. Verify the mod page shows the new version and downloads work.",
    ]
    return "\n".join(lines)


def upload(*_args, **_kwargs):  # pragma: no cover — future work
    """Upload a .vmz to ModWorkshop. Not implemented: MW API is currently GET-only.

    When write endpoints become available, implement using:
      POST /mods/{mod_id}/files/begin-pending  (or /mods/{mod_id}/files with multipart)
      PUT  /files/{id}                          (metadata: version, desc, name)
    Auth will require an API key; header format TBD by MW.
    """
    raise NotImplementedError("ModWorkshop write API not yet available")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    check_p = sub.add_parser("check", help="Read-only version check + markdown summary")
    check_p.add_argument("mod_folder")
    check_p.add_argument("--expected-version", required=True)
    check_p.add_argument("--out", help="Write markdown to this file (default: stdout)")

    args = parser.parse_args()

    if args.command == "check":
        mod_folder = Path(args.mod_folder)
        if not mod_folder.is_absolute():
            candidate = PROJECT_ROOT / mod_folder
            if candidate.is_dir():
                mod_folder = candidate
        if not mod_folder.is_dir():
            print(f"Error: mod folder {mod_folder} not found", file=sys.stderr)
            return 1
        markdown = check(mod_folder, args.expected_version)
        if args.out:
            Path(args.out).write_text(markdown + "\n", encoding="utf-8")
        else:
            print(markdown)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
