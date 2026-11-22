import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import octoprint_placeholder_theme as plugin

PLUGIN_DIR = Path(__file__).resolve().parents[1]


def _pyproject():
    with open(PLUGIN_DIR / "pyproject.toml", "rb") as f:
        return tomllib.load(f)


def test_entry_point_uses_plugin_identifier():
    entry_points = _pyproject()["project"]["entry-points"]["octoprint.plugin"]
    assert entry_points == {plugin.PLUGIN_IDENTIFIER: "octoprint_placeholder_theme"}


def test_declared_assets_exist():
    static = Path(plugin.__file__).parent / "static"
    for files in plugin.__plugin_implementation__.get_assets().values():
        for name in files:
            assert (static / name).is_file(), name


def test_updates_come_from_pypi_package():
    impl = plugin.__plugin_implementation__
    impl._plugin_version = "0.1.0"
    check = impl.get_update_information()[plugin.PLUGIN_IDENTIFIER]
    assert check["type"] == "pypi_release"
    assert check["package"] == _pyproject()["project"]["name"] == plugin.PACKAGE_NAME
    assert check["pip"].format(target_version="1.2.3") == f"{plugin.PACKAGE_NAME}==1.2.3"
