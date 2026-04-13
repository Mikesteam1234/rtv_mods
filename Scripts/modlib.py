"""Shared helpers for RTV mod tooling: mod.txt parsing, mod folder discovery."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

_NON_MOD_DIRS = {"Scripts", "Decomp", ".claude", ".github", ".git", ".vscode"}


@dataclass
class ModManifest:
    folder: Path
    name: str
    id: str
    version: str
    modworkshop_id: int | None
    raw: dict[str, dict[str, str]]

    @property
    def folder_name(self) -> str:
        return self.folder.name


def parse_mod_txt(path: Path) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current: str | None = None
    section_re = re.compile(r"^\[([^\]]+)\]\s*$")
    kv_re = re.compile(r'^([A-Za-z_][\w-]*)\s*=\s*"?(.*?)"?\s*$')

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue
        m = section_re.match(stripped)
        if m:
            current = m.group(1).strip()
            sections.setdefault(current, {})
            continue
        if current is None:
            continue
        m = kv_re.match(stripped)
        if m:
            sections[current][m.group(1)] = m.group(2)
    return sections


def load_manifest(folder: Path) -> ModManifest:
    mod_txt = folder / "mod.txt"
    if not mod_txt.is_file():
        raise FileNotFoundError(f"{folder} has no mod.txt")
    raw = parse_mod_txt(mod_txt)
    mod = raw.get("mod", {})
    for field in ("name", "id", "version"):
        if not mod.get(field):
            raise ValueError(f"{mod_txt}: missing required [mod] field '{field}'")
    mw_raw = raw.get("updates", {}).get("modworkshop")
    mw_id: int | None = None
    if mw_raw:
        try:
            mw_id = int(mw_raw)
        except ValueError:
            raise ValueError(f"{mod_txt}: [updates] modworkshop must be an integer, got {mw_raw!r}")
    return ModManifest(
        folder=folder,
        name=mod["name"],
        id=mod["id"],
        version=mod["version"],
        modworkshop_id=mw_id,
        raw=raw,
    )


def discover_mod_folders(root: Path = PROJECT_ROOT) -> list[Path]:
    """Return mod folder paths (anything at the repo root containing a mod.txt)."""
    folders: list[Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in _NON_MOD_DIRS:
            continue
        if (child / "mod.txt").is_file():
            folders.append(child)
    return folders


def find_mod_by_id(mod_id: str, root: Path = PROJECT_ROOT) -> ModManifest:
    for folder in discover_mod_folders(root):
        manifest = load_manifest(folder)
        if manifest.id == mod_id:
            return manifest
    raise LookupError(f"No mod with id={mod_id!r} found under {root}")


def rewrite_version_in_mod_txt(text: str, new_version: str) -> str:
    """Replace the `version=` line inside the [mod] section. Preserves quoting style."""
    lines = text.splitlines(keepends=True)
    in_mod = False
    section_re = re.compile(r"^\s*\[([^\]]+)\]\s*$")
    version_re = re.compile(r'^(\s*version\s*=\s*)("?)([^"\r\n]*)("?)(\s*)$')
    for i, line in enumerate(lines):
        m = section_re.match(line)
        if m:
            in_mod = m.group(1).strip() == "mod"
            continue
        if in_mod:
            vm = version_re.match(line)
            if vm:
                prefix, q1, _old, q2, trailing = vm.groups()
                lines[i] = f"{prefix}{q1}{new_version}{q2}{trailing}"
                if not lines[i].endswith("\n"):
                    lines[i] += "\n"
                return "".join(lines)
    raise ValueError("No [mod] version= line found in mod.txt")
