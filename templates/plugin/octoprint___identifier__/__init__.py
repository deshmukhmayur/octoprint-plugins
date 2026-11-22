"""__display_name__ OctoPrint plugin."""

import octoprint.plugin

PLUGIN_IDENTIFIER = "__identifier__"
PACKAGE_NAME = "__package_name__"


class __class_name__Plugin(octoprint.plugin.AssetPlugin):
    def get_assets(self):
        return {"css": ["css/__identifier__.css"]}

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


__plugin_name__ = "__display_name__"
__plugin_pythoncompat__ = ">=3.9,<4"
__plugin_implementation__ = __class_name__Plugin()
__plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": (
        __plugin_implementation__.get_update_information
    ),
}
