"""Print, as a JSON list, the plugins CI should test for a set of changed files.

Usage:
    git diff --name-only <base> <head> | python scripts/changed_plugins.py

A change inside plugins/<id>/ selects that plugin. A change to shared files (root config,
scripts, templates, workflows) selects every plugin. Docs-only changes select none.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IGNORED_PREFIXES = ("docs/",)
IGNORED_SUFFIXES = (".md",)


def all_plugins(repo_root: Path = REPO_ROOT) -> list[str]:
    plugins_dir = repo_root / "plugins"
    return sorted(p.name for p in plugins_dir.iterdir() if (p / "pyproject.toml").is_file())


def plugins_to_test(changed_files: list[str], plugins: list[str]) -> list[str]:
    selected: set[str] = set()
    for path in changed_files:
        parts = path.split("/")
        if parts[0] == "plugins" and len(parts) > 2:
            if parts[1] in plugins:
                selected.add(parts[1])
        elif path.startswith(IGNORED_PREFIXES) or path.endswith(IGNORED_SUFFIXES):
            continue
        else:
            return sorted(plugins)
    return sorted(selected)


def main() -> int:
    changed = [line.strip() for line in sys.stdin if line.strip()]
    print(json.dumps(plugins_to_test(changed, all_plugins())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
