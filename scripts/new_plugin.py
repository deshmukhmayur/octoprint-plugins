"""Create a new plugin under plugins/ from templates/plugin/.

Usage:
    uv run scripts/new_plugin.py <identifier> [--name "Display Name"] [--description "..."]

The identifier is the plugin's permanent id (snake_case, e.g. ``filament_tracker``).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = REPO_ROOT / "templates" / "plugin"
IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")


class PluginExistsError(Exception):
    pass


def _camel(identifier: str) -> str:
    return "".join(part.capitalize() for part in identifier.split("_"))


def create_plugin(
    identifier: str,
    display_name: str | None = None,
    description: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> Path:
    """Render the plugin template into ``<repo_root>/plugins/<identifier>`` and return that path."""
    if not IDENTIFIER_RE.match(identifier):
        raise ValueError(
            f"Invalid identifier {identifier!r}: use lowercase snake_case, starting with a letter."
        )

    target = repo_root / "plugins" / identifier
    if target.exists():
        raise PluginExistsError(f"{target} already exists.")

    display_name = display_name or " ".join(p.capitalize() for p in identifier.split("_"))
    tokens = {
        "__identifier__": identifier,
        "__display_name__": display_name,
        "__package_name__": f"OctoPrint-{_camel(identifier)}",
        "__class_name__": _camel(identifier),
        "__description__": description or f"{display_name} plugin for OctoPrint.",
    }

    def render(text: str) -> str:
        for token, value in tokens.items():
            text = text.replace(token, value)
        return text

    template_dir = repo_root / "templates" / "plugin"
    for src in sorted(template_dir.rglob("*")):
        if "__pycache__" in src.parts or not src.is_file():
            continue
        dest = target / render(str(src.relative_to(template_dir)))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(src.read_text(encoding="utf-8")), encoding="utf-8")

    # Each package ships its own copy of the repo license (license-files can't point outside it).
    shutil.copyfile(repo_root / "LICENSE", target / "LICENSE")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("identifier", help="permanent plugin identifier, snake_case")
    parser.add_argument("--name", help="display name (default: derived from identifier)")
    parser.add_argument("--description", help="one-line description")
    args = parser.parse_args(argv)

    try:
        target = create_plugin(args.identifier, args.name, args.description)
    except (ValueError, PluginExistsError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"Created {target.relative_to(REPO_ROOT)}")
    print("Next: run `uv sync --all-packages` to install it into the dev environment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
