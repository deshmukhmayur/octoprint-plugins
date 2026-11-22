# Releasing a plugin

Each plugin is released on its own, by pushing a release tag `<identifier>-v<version>`.

1. Bump `version` in `plugins/<identifier>/pyproject.toml`.
2. Add a `## <version>` section to `plugins/<identifier>/CHANGELOG.md`. It becomes the GitHub release notes.
3. Commit, push to `main`, then tag and push:
   ```sh
   git tag <identifier>-v<version>
   git push origin <identifier>-v<version>
   ```

The **Release** workflow then:

1. Checks the tag's version matches `pyproject.toml`, and builds the sdist, wheel and Plugin Manager zip.
2. Publishes to PyPI with Trusted Publishing (GitHub environment `pypi`).
3. Creates a GitHub release with that changelog section and the built files.
4. Updates `https://deshmukhmayur.github.io/octoprint-plugins/<identifier>/latest.zip` on the `gh-pages` branch.

If a later step fails after PyPI accepted the upload, re-run only the failed jobs. PyPI never accepts the same version twice.

## One-time setup

### Per repository (once)

1. **GitHub environment**: in repo *Settings → Environments*, create an environment named `pypi`. Optionally add yourself as a required reviewer, so every PyPI upload needs a click.
2. **GitHub Pages**: after the first release has created the `gh-pages` branch, go to *Settings → Pages* and set the source to *Deploy from a branch*, `gh-pages`, `/ (root)`.

### Per plugin (before its first release)

1. **PyPI pending publisher**: on https://pypi.org/manage/account/publishing/, add a pending publisher with:
   - PyPI project name: the plugin's package name, e.g. `OctoPrint-FilamentTracker`
   - Owner: `deshmukhmayur`, Repository: `octoprint-plugins`
   - Workflow: `release.yml`, Environment: `pypi`
   The first successful release creates the PyPI project. After that, the publisher stays attached.
2. **Plugin Registry** (after the first release): open a PR to https://github.com/OctoPrint/plugins.octoprint.org adding `_plugins/<identifier>.md`, following https://plugins.octoprint.org/help/registering/. Use:
   - `archive`: `https://deshmukhmayur.github.io/octoprint-plugins/<identifier>/latest.zip`
   - `homepage`: `https://github.com/deshmukhmayur/octoprint-plugins/tree/main/plugins/<identifier>`
   - `source`: `https://github.com/deshmukhmayur/octoprint-plugins`
   - `license`: `MIT`
