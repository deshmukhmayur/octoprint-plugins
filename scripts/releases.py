"""Release helpers for CI, built on knope.toml.

A plugin is *release-enabled* when its knope.toml package lists `versioned_files`. Plugins listed
with only a `changelog` collect change files but are never released.

Usage:
    python scripts/releases.py pending
        JSON list of release-enabled plugins whose current version has no
        `<identifier>/v<version>` tag yet, i.e. what `knope release` is about to release.
    python scripts/releases.py check-changesets <base-ref>
        Fail if a release-enabled plugin changed since <base-ref> without a change file
        in .changeset/ naming it.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def release_enabled_plugins(repo_root: Path = REPO_ROOT) -> list[str]:
    packages = _load_toml(repo_root / "knope.toml").get("packages", {})
    return sorted(name for name, cfg in packages.items() if cfg.get("versioned_files"))


def pending_releases(tags: set[str], repo_root: Path = REPO_ROOT) -> list[dict]:
    pending = []
    for plugin in release_enabled_plugins(repo_root):
        pyproject = _load_toml(repo_root / "plugins" / plugin / "pyproject.toml")
        version = pyproject["project"]["version"]
        tag = f"{plugin}/v{version}"
        if tag not in tags:
            pending.append({"plugin": plugin, "version": version, "tag": tag})
    return pending


def changeset_packages(text: str) -> set[str]:
    """Package names in a change file's frontmatter (`<package>: <change type>` lines)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return set()
    names = set()
    for line in lines[1:]:
        if line.strip() == "---":
            break
        name, sep, _ = line.partition(":")
        if sep:
            names.add(name.strip().strip("\"'"))
    return names


def missing_changesets(
    changed_files: list[str], changeset_texts: list[str], enabled: list[str]
) -> list[str]:
    """Release-enabled plugins with user-facing changes but no change file naming them."""
    changed = set()
    for path in changed_files:
        parts = path.split("/")
        if len(parts) > 2 and parts[0] == "plugins" and parts[1] in enabled:
            if parts[2] != "tests":
                changed.add(parts[1])
    documented = set().union(*(changeset_packages(t) for t in changeset_texts))
    return sorted(changed - documented)


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=True
    ).stdout


def main(argv: list[str]) -> int:
    if argv[:1] == ["pending"]:
        tags = set(_git("tag", "--list").split())
        print(json.dumps(pending_releases(tags)))
        return 0

    if len(argv) == 2 and argv[0] == "check-changesets":
        changed = _git("diff", "--name-only", f"{argv[1]}...HEAD").split()
        added = _git(
            "diff", "--name-only", "--diff-filter=AM", f"{argv[1]}...HEAD", "--", ".changeset/"
        ).split()
        texts = [(REPO_ROOT / p).read_text(encoding="utf-8") for p in added if p.endswith(".md")]
        missing = missing_changesets(changed, texts, release_enabled_plugins())
        if missing:
            print(
                f"Missing change file for: {', '.join(missing)}. Run `knope document-change`, "
                "or add the `no-changeset` label if users won't notice this change.",
                file=sys.stderr,
            )
            return 1
        print("Change files OK.")
        return 0

    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
