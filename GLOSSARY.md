# OctoPrint Plugins

A collection of independently released OctoPrint plugins by deshmukhmayur, kept in one repository.

## Plugins

**Plugin**:
One installable OctoPrint extension, living in its own folder under `plugins/` and released on its own schedule.
_Avoid_: Package (when you mean the plugin as a whole), extension, addon

**Plugin identifier**:
The permanent snake_case id OctoPrint uses to recognise a plugin (e.g. `placeholder_theme`). It never changes after the plugin is first published.
_Avoid_: Plugin key, slug, plugin id (as a loose synonym for the display name)

**Package name**:
The name a plugin is published under on PyPI, always `OctoPrint-<CamelCaseIdentifier>`.
_Avoid_: Distribution name, project name

**Display name**:
The human-readable name OctoPrint shows for a plugin (e.g. "Placeholder Theme").
_Avoid_: Title, plugin name (ambiguous)

**Placeholder plugin**:
A stand-in plugin that exists only to exercise the repository's tooling and is never published.

## Distribution

**Release**:
One published version of one plugin, triggered by a release tag.

**Release tag**:
A git tag of the form `<plugin identifier>-v<version>` that marks and triggers a release.
_Avoid_: Version tag

**Archive URL**:
The stable link the Plugin Registry uses for a plugin's first install; always serves the latest release.
_Avoid_: Download link, install URL

**Plugin Registry**:
OctoPrint's official plugin listing at plugins.octoprint.org, from which users discover and first install plugins.
_Avoid_: Plugin repository (ambiguous with this git repository)

**Update check**:
OctoPrint's periodic comparison of an installed plugin's version against its latest release on PyPI.
