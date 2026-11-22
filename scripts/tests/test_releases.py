import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from releases import (  # noqa: E402
    changeset_packages,
    missing_changesets,
    pending_releases,
    release_enabled_plugins,
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
