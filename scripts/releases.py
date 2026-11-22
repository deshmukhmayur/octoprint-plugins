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
    python scripts/releases.py preview
        After `knope preview-release` has modified the working tree, print a Markdown summary
        of the versions and changelog entries it produced, compared with HEAD.
    python scripts/releases.py release-pr <base-ref>
        JSON {"title", "body"} for the release PR, comparing the working tree with <base-ref>.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

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


PREVIEW_MARKER = "<!-- release-preview -->"


def _changelog_section(changelog: str, version: str) -> str:
    """The body of the `## <version>` section, without its heading."""
    lines, body, inside = changelog.splitlines(), [], False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].split(" ")[0] == version
            continue
        if inside:
            body.append(line)
    return "\n".join(body).strip()


def release_preview(repo_root: Path, read_head: Callable[[str], str | None]) -> list[dict]:
    """Compare each knope package in the working tree with HEAD (via ``read_head(path)``).

    Returns one entry per package whose version or changelog changed.
    """
    packages = _load_toml(repo_root / "knope.toml").get("packages", {})
    entries = []
    for plugin, cfg in sorted(packages.items()):
        pyproject = f"plugins/{plugin}/pyproject.toml"
        changelog = cfg.get("changelog", f"plugins/{plugin}/CHANGELOG.md")
        after = tomllib.loads((repo_root / pyproject).read_text(encoding="utf-8"))
        before = tomllib.loads(read_head(pyproject) or "[project]\nversion = ''")
        new_version = after["project"]["version"]
        old_version = before["project"]["version"]
        new_log = (repo_root / changelog).read_text(encoding="utf-8")
        if new_version == old_version and new_log == (read_head(changelog) or ""):
            continue
        entries.append(
            {
                "plugin": plugin,
                "from": old_version,
                "to": new_version,
                "enabled": bool(cfg.get("versioned_files")),
                "notes": _changelog_section(new_log, new_version),
            }
        )
    return entries


PR_PREVIEW_INTRO = (
    "Based on the change files in this PR and any already pending on `main`. "
    "After this PR is merged, merging the release PR will publish:"
)


def preview_markdown(entries: list[dict]) -> str:
    """The sticky release preview comment on a pull request."""
    lines = [PREVIEW_MARKER, "### Release preview", ""]
    if not entries:
        lines.append("No pending change files. Merging this PR won't release anything.")
    else:
        lines += _summary(entries, PR_PREVIEW_INTRO)
    return "\n".join(lines) + "\n"


def release_pr(entries: list[dict]) -> dict:
    """Title and body of the release PR. The title keeps ``chore: prepare release`` because
    prepare-release.yml skips commits whose message contains it."""
    published = [f"{e['plugin']} {e['to']}" for e in entries if e["enabled"]]
    if len(published) > 3:
        title = f"chore: prepare release of {len(published)} plugins"
    elif published:
        title = f"chore: prepare release of {', '.join(published)}"
    else:
        skipped = ", ".join(e["plugin"] for e in entries)
        title = f"chore: prepare release (changelog only: {skipped})"
    body = _summary(entries, "Merging this PR will publish:") + [
        "",
        "---",
        "",
        "_This PR is rebuilt from the change files in `.changeset/` on every push to `main`, "
        "so edits to it are overwritten. See [docs/releasing.md](https://github.com/deshmukhmayur/octoprint-plugins/blob/main/docs/releasing.md)._",
    ]
    return {"title": title, "body": "\n".join(body) + "\n"}


def _summary(entries: list[dict], intro: str) -> list[str]:
    published = [e for e in entries if e["enabled"]]
    skipped = [e for e in entries if not e["enabled"]]
    lines = [intro, ""]
    if published:
        lines += ["| Plugin | Version |", "|---|---|"]
        lines += [f"| `{e['plugin']}` | {e['from']} → **{e['to']}** |" for e in published]
        lines += _changelog_details(published)
    else:
        lines.append("_Nothing._")

    if skipped:
        names = ", ".join(f"`{e['plugin']}`" for e in skipped)
        lines += [
            "",
            f"> [!WARNING]\n> {names}: has change files but isn't release-enabled, so it "
            "won't be published. Its change files will only become changelog entries.",
            "",
            "**Changelog only (not published):**",
            "",
            "| Plugin | Version |",
            "|---|---|",
        ]
        lines += [f"| `{e['plugin']}` | {e['to']} (unchanged) |" for e in skipped]
        lines += _changelog_details(skipped)
    return lines


def _changelog_details(entries: list[dict]) -> list[str]:
    lines = []
    for e in entries:
        lines += [
            "",
            f"<details><summary><code>{e['plugin']}</code> {e['to']} changelog</summary>",
            "",
            e["notes"] or "_No notes._",
            "",
            "</details>",
        ]
    return lines


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

    if argv[:1] in (["preview"], ["release-pr"]) and len(argv) <= 2:
        base = argv[1] if len(argv) == 2 else "HEAD"

        def read_base(path: str) -> str | None:
            try:
                return _git("show", f"{base}:{path}")
            except subprocess.CalledProcessError:
                return None

        entries = release_preview(REPO_ROOT, read_base)
        if argv[0] == "preview":
            print(preview_markdown(entries), end="")
        else:
            print(json.dumps(release_pr(entries)))
        return 0

    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
