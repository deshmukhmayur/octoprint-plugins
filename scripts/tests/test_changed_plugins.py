import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from changed_plugins import plugins_to_test  # noqa: E402

PLUGINS = ["alpha", "beta"]


def test_change_inside_a_plugin_selects_only_that_plugin():
    assert plugins_to_test(["plugins/alpha/octoprint_alpha/__init__.py"], PLUGINS) == ["alpha"]


def test_shared_file_change_selects_every_plugin():
    assert plugins_to_test(["plugins/alpha/x.py", "pyproject.toml"], PLUGINS) == PLUGINS
    assert plugins_to_test([".github/workflows/ci.yml"], PLUGINS) == PLUGINS


def test_docs_only_changes_select_nothing():
    assert plugins_to_test(["README.md", "docs/adr/0001-x.md"], PLUGINS) == []


def test_plugin_markdown_still_counts_for_that_plugin():
    # A plugin's README is packaged, so a change to it should still be built and tested.
    assert plugins_to_test(["plugins/beta/README.md"], PLUGINS) == ["beta"]


def test_deleted_plugin_is_ignored():
    assert plugins_to_test(["plugins/gone/pyproject.toml"], PLUGINS) == []
