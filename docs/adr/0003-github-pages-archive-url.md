# GitHub Pages `latest.zip` as each plugin's Archive URL

The Plugin Registry's Archive URL must be an `http(s)` (or `git+`) link that always points at the latest release, and the Plugin Manager won't install a bare PyPI package name. PyPI has no versionless "latest" file link, and GitHub's `/archive/main.zip` doesn't work because plugins aren't at the repository root. So the release workflow publishes a zip of the released plugin to `https://deshmukhmayur.github.io/octoprint-plugins/<identifier>/latest.zip` on the `gh-pages` branch, overwriting only that plugin's folder.

## Considered Options

- A rolling `<identifier>-latest` GitHub release per plugin: clutters the releases page.
- A `git+https://…#subdirectory=…` link: needs git on the printer's host and has no clean "latest release" pointer.
- Updating the registry entry to a versioned PyPI file on every release: manual, and the registry lags.
- Deploying Pages from Actions instead of a branch: each deploy replaces the whole site, so every release would have to rebuild every plugin's zip.
