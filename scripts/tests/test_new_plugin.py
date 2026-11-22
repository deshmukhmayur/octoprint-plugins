import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from new_plugin import REPO_ROOT, PluginExistsError, create_plugin  # noqa: E402
from releases import release_enabled_plugins  # noqa: E402


@pytest.fixture
def repo(tmp_path):
    shutil.copytree(REPO_ROOT / "templates", tmp_path / "templates")
    shutil.copyfile(REPO_ROOT / "LICENSE", tmp_path / "LICENSE")
    shutil.copyfile(REPO_ROOT / "knope.toml", tmp_path / "knope.toml")
    (tmp_path / "plugins").mkdir()
    return tmp_path


def test_renders_template_with_names_derived_from_identifier(repo):
    target = create_plugin("filament_tracker", repo_root=repo)

    pyproject = (target / "pyproject.toml").read_text()
    assert 'name = "OctoPrint-FilamentTracker"' in pyproject
    assert 'version = "0.0.0"' in pyproject  # first release is a `major` change file → 0.1.0
    assert 'filament_tracker = "octoprint_filament_tracker"' in pyproject

    init = (target / "octoprint_filament_tracker" / "__init__.py").read_text()
    assert "class FilamentTrackerPlugin(" in init
    assert '__plugin_name__ = "Filament Tracker"' in init
    assert (target / "octoprint_filament_tracker/static/css/filament_tracker.css").is_file()
    assert (target / "LICENSE").read_text() == (repo / "LICENSE").read_text()


def test_no_template_tokens_left_behind(repo):
    target = create_plugin("x", display_name="X Plugin", description="Does X.", repo_root=repo)
    for path in target.rglob("*"):
        assert "__identifier__" not in str(path)
        if path.is_file():
            text = path.read_text()
            for token in (
                "__identifier__",
                "__display_name__",
                "__package_name__",
                "__class_name__",
                "__description__",
            ):
                assert token not in text, f"{token} in {path}"


@pytest.mark.parametrize("bad", ["Theme", "my-theme", "1theme", "theme_", "my__theme", ""])
def test_rejects_invalid_identifiers(repo, bad):
    with pytest.raises(ValueError):
        create_plugin(bad, repo_root=repo)


def test_refuses_to_overwrite_existing_plugin(repo):
    create_plugin("theme", repo_root=repo)
    with pytest.raises(PluginExistsError):
        create_plugin("theme", repo_root=repo)


def test_new_plugin_is_listed_in_knope_but_not_release_enabled(repo):
    create_plugin("filament_tracker", repo_root=repo)
    knope = (repo / "knope.toml").read_text()
    assert "[packages.filament_tracker]" in knope
    assert 'changelog = "plugins/filament_tracker/CHANGELOG.md"' in knope
    assert "filament_tracker" not in release_enabled_plugins(repo)
