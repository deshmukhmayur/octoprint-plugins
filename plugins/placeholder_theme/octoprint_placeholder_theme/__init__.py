"""Placeholder Theme OctoPrint plugin."""

import octoprint.plugin

PLUGIN_IDENTIFIER = "placeholder_theme"
PACKAGE_NAME = "OctoPrint-PlaceholderTheme"


class PlaceholderThemePlugin(octoprint.plugin.AssetPlugin):
    def get_assets(self):
        return {"css": ["css/placeholder_theme.css"]}

    def get_update_information(self):
        # Updates come from PyPI. See docs/adr/0002-pypi-for-releases-and-updates.md.
        return {
            PLUGIN_IDENTIFIER: {
                "displayName": __plugin_name__,
                "displayVersion": self._plugin_version,
                "type": "pypi_release",
                "package": PACKAGE_NAME,
                "pip": PACKAGE_NAME + "=={target_version}",
            }
        }


__plugin_name__ = "Placeholder Theme"
__plugin_pythoncompat__ = ">=3.9,<4"
__plugin_implementation__ = PlaceholderThemePlugin()
__plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": (
        __plugin_implementation__.get_update_information
    ),
}
