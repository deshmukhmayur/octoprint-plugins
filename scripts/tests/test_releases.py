import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from releases import (  # noqa: E402
    PREVIEW_MARKER,
    changeset_packages,
    missing_changesets,
    pending_releases,
    preview_markdown,
    release_enabled_plugins,
    release_pr,
    release_preview,
)


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "knope.toml").write_text(
        "[packages.ready]\n"
        'versioned_files = ["plugins/ready/pyproject.toml"]\n'
        'changelog = "plugins/ready/CHANGELOG.md"\n'
        "\n"
        "[packages.wip]\n"
        'changelog = "plugins/wip/CHANGELOG.md"\n'
    )
    for name, version in [("ready", "1.2.0"), ("wip", "0.1.0")]:
        (tmp_path / "plugins" / name).mkdir(parents=True)
        (tmp_path / "plugins" / name / "pyproject.toml").write_text(
            f'[project]\nname = "{name}"\nversion = "{version}"\n'
        )
    return tmp_path


def test_only_plugins_with_versioned_files_are_release_enabled(repo):
    assert release_enabled_plugins(repo) == ["ready"]


def test_pending_release_when_current_version_is_untagged(repo):
    assert pending_releases({"ready/v1.1.0"}, repo) == [
        {"plugin": "ready", "version": "1.2.0", "tag": "ready/v1.2.0"}
    ]


def test_nothing_pending_when_current_version_is_tagged(repo):
    assert pending_releases({"ready/v1.2.0"}, repo) == []


def test_changeset_frontmatter_names_packages():
    text = '---\nalpha: minor\n"beta": patch\n---\n\n# Summary: with a colon\n'
    assert changeset_packages(text) == {"alpha", "beta"}


def test_text_without_frontmatter_names_nothing():
    assert changeset_packages("# Just a heading\nalpha: minor\n") == set()


def test_changed_enabled_plugin_needs_a_changeset():
    files = ["plugins/ready/octoprint_ready/__init__.py", "plugins/wip/x.py"]
    assert missing_changesets(files, [], ["ready"]) == ["ready"]
    assert missing_changesets(files, ["---\nready: patch\n---\n# Fix\n"], ["ready"]) == []


def test_test_only_changes_need_no_changeset():
    assert missing_changesets(["plugins/ready/tests/test_x.py"], [], ["ready"]) == []


def _bump(repo, plugin, version, changelog):
    path = repo / "plugins" / plugin
    text = (path / "pyproject.toml").read_text()
    head = {
        f"plugins/{plugin}/pyproject.toml": text,
        f"plugins/{plugin}/CHANGELOG.md": "# Changelog\n",
    }
    (path / "pyproject.toml").write_text(f'[project]\nname = "{plugin}"\nversion = "{version}"\n')
    (path / "CHANGELOG.md").write_text(changelog)
    return head


def test_preview_lists_bumped_release_enabled_plugin_with_notes(repo):
    head = _bump(
        repo,
        "ready",
        "2.0.0",
        "# Changelog\n\n## 2.0.0 (2026-11-22)\n\n### Breaking Changes\n\n- Big change\n\n"
        "## 1.2.0\n\n- Old\n",
    )
    (repo / "plugins/wip/CHANGELOG.md").write_text("# Changelog\n")
    head["plugins/wip/pyproject.toml"] = (repo / "plugins/wip/pyproject.toml").read_text()
    head["plugins/wip/CHANGELOG.md"] = "# Changelog\n"

    entries = release_preview(repo, head.get)
    assert entries == [
        {
            "plugin": "ready",
            "from": "1.2.0",
            "to": "2.0.0",
            "enabled": True,
            "notes": "### Breaking Changes\n\n- Big change",
        }
    ]
    md = preview_markdown(entries)
    assert md.startswith(PREVIEW_MARKER)
    assert "| `ready` | 1.2.0 → **2.0.0** |" in md
    assert "- Big change" in md and "- Old" not in md


def test_preview_warns_when_plugin_is_not_release_enabled(repo):
    head = {
        "plugins/wip/pyproject.toml": (repo / "plugins/wip/pyproject.toml").read_text(),
        "plugins/wip/CHANGELOG.md": "# Changelog\n",
        "plugins/ready/pyproject.toml": (repo / "plugins/ready/pyproject.toml").read_text(),
    }
    (repo / "plugins/wip/CHANGELOG.md").write_text("# Changelog\n\n## 0.1.0\n\n- Thing\n")
    (repo / "plugins/ready").joinpath("CHANGELOG.md").write_text("")
    head["plugins/ready/CHANGELOG.md"] = ""

    md = preview_markdown(release_preview(repo, head.get))
    assert "_Nothing._" in md
    assert "`wip`: has change files but isn't release-enabled" in md
    assert "| `wip` | 0.1.0 (unchanged) |" in md
    assert "<code>wip</code> 0.1.0 changelog" in md and "- Thing" in md


def test_preview_with_no_changes():
    assert "won't release anything" in preview_markdown([])


def _entry(plugin, to, enabled=True, notes="- Change"):
    return {"plugin": plugin, "from": "0.0.0", "to": to, "enabled": enabled, "notes": notes}


def test_release_pr_title_names_published_plugins_and_versions():
    pr = release_pr(
        [_entry("alpha", "0.1.0"), _entry("beta", "1.2.0"), _entry("wip", "0.0.0", False)]
    )
    assert pr["title"] == "chore: prepare release of alpha 0.1.0, beta 1.2.0"
    assert "Merging this PR will publish:" in pr["body"]
    assert "| `alpha` | 0.0.0 → **0.1.0** |" in pr["body"]
    assert "`wip`: has change files but isn't release-enabled" in pr["body"]


def test_release_pr_title_counts_many_plugins():
    pr = release_pr([_entry(name, "1.0.0") for name in "abcd"])
    assert pr["title"] == "chore: prepare release of 4 plugins"


def test_release_pr_title_says_when_nothing_is_published():
    pr = release_pr([_entry("wip", "0.0.0", False)])
    assert pr["title"] == "chore: prepare release (changelog only: wip)"
    assert "_Nothing._" in pr["body"]
