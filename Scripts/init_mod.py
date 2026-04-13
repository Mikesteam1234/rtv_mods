#!/usr/bin/env python3

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

VALID_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def to_kebab(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    s = re.sub(r"[_\s]+", "-", s)
    return s.lower()


MOD_TXT = """[mod]
name="{name}"
id="{id}"
version="1.0.0"

[autoload]
{name}="res://mods/{name}/Main.gd"
"""

MAIN_GD = """extends Node

func _ready():
\t# overrideScript("res://mods/{name}/SomeOverride.gd")
\tget_tree().reload_current_scene()
\tqueue_free()

func overrideScript(overrideScriptPath: String):
\tvar script: Script = load(overrideScriptPath)
\tscript.reload()
\tvar parentScript = script.get_base_script()
\tscript.take_over_path(parentScript.resource_path)
\treturn script
"""


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <ModName>", file=sys.stderr)
        sys.exit(1)

    name = sys.argv[1].rstrip("/")
    if not VALID_NAME.match(name):
        print(
            f"Error: '{name}' is not a valid mod name. "
            "Use letters, digits, '_' or '-', starting with a letter.",
            file=sys.stderr,
        )
        sys.exit(1)

    mod_dir = PROJECT_ROOT / name
    if mod_dir.exists():
        print(f"Error: '{mod_dir}' already exists.", file=sys.stderr)
        sys.exit(1)

    mod_id = to_kebab(name)
    inner_dir = mod_dir / "mods" / name
    inner_dir.mkdir(parents=True)

    mod_txt_path = mod_dir / "mod.txt"
    main_gd_path = inner_dir / "Main.gd"

    mod_txt_path.write_text(MOD_TXT.format(name=name, id=mod_id))
    main_gd_path.write_text(MAIN_GD.format(name=name))

    print(f"Created {mod_txt_path}")
    print(f"Created {main_gd_path}")
    print(f"Next: Scripts/deploy_mod.py {name}")


if __name__ == "__main__":
    main()
