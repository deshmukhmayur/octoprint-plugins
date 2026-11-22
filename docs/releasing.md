# Releasing plugins

Versions and changelogs are managed by [knope](https://knope.tech) from **change files** in `.changeset/`, much like Changesets in the JavaScript world. You never edit versions or tag by hand.

## Day to day

1. In every PR that changes a release-enabled plugin in a way users will notice, add a change file:
   ```sh
   knope document-change
   ```
   It asks which plugin(s) changed, the change type (`major`, `minor` or `patch`) and a summary, then writes `.changeset/<summary>.md`. You can also write one by hand:
   ```md
   ---
   placeholder_theme: minor
   ---

   # Add dark dashboard

   Optional longer description, copied into the changelog.
   ```
   CI fails a PR that changes a release-enabled plugin (outside its `tests/`) with no change file naming it. For changes users won't notice, add the `no-changeset` label to the PR instead.
2. Merge PRs to `main` as usual. After each push to `main`, **Prepare release** builds or updates the **release PR** ("chore: prepare release", from the `release` branch). That PR bumps each affected plugin's version in `pyproject.toml` and `uv.lock`, adds its `CHANGELOG.md` section, and deletes the used change files.
3. When you want to release, merge the release PR. **Release** then, for each plugin whose new version has no tag yet:
   1. Creates the tag `<identifier>/v<version>` and a GitHub release with that changelog section (knope).
   2. Publishes the package to PyPI with Trusted Publishing (GitHub environment `pypi`), and attaches the sdist and wheel to the GitHub release.
   3. Updates `https://deshmukhmayur.github.io/octoprint-plugins/<identifier>/latest.zip` on the `gh-pages` branch.

The `release` branch is rebuilt from scratch on every run, so don't commit to it by hand.

On `0.x` versions, knope follows the usual pre-1.0 convention: `major` bumps the minor version (0.1.0 → 0.2.0), and `minor` and `patch` both bump the patch version (0.1.0 → 0.1.1).

If a job fails after PyPI accepted an upload, re-run only the failed jobs. PyPI never accepts the same version twice.

### Installing knope locally

See https://knope.tech for install options, or download a binary from https://github.com/knope-dev/knope/releases. You only need it for `knope document-change`; writing change files by hand works just as well.

## Release-enabled plugins

Every plugin has an entry in `knope.toml`, which `scripts/new_plugin.py` adds. A plugin is **release-enabled** once its entry lists `versioned_files`:

```toml
[packages.filament_tracker]
versioned_files = ["plugins/filament_tracker/pyproject.toml"]
changelog = "plugins/filament_tracker/CHANGELOG.md"
```

Without `versioned_files`, a plugin is never released. Its change files still become changelog entries, but nothing is tagged or published. knope releases any release-enabled plugin whose current version has no tag, so a newly enabled plugin goes out at its starting version (`0.1.0`) the next time a release PR is merged.

## One-time setup

### Per repository (done once)

1. **GitHub environment**: in repo *Settings → Environments*, create an environment named `pypi`. Optionally add yourself as a required reviewer, so every PyPI upload needs a click.
2. **Let Actions open PRs**: in *Settings → Actions → General → Workflow permissions*, tick *Allow GitHub Actions to create and approve pull requests*. Prepare release needs this to open the release PR.
3. **GitHub Pages**: after the first release has created the `gh-pages` branch, go to *Settings → Pages* and set the source to *Deploy from a branch*, `gh-pages`, `/ (root)`.

The release PR is opened with the built-in Actions token, so GitHub doesn't run CI on it. That's fine: it only changes versions, changelogs and `uv.lock`. If you later make CI checks required on `main`, you'll need a personal access token or GitHub App for Prepare release.

### Per plugin (before its first release)

1. **PyPI pending publisher**: on https://pypi.org/manage/account/publishing/, add a pending publisher with:
   - PyPI project name: the plugin's package name, e.g. `OctoPrint-FilamentTracker`
   - Owner: `deshmukhmayur`, Repository: `octoprint-plugins`
   - Workflow: `release.yml`, Environment: `pypi`
   The first successful release creates the PyPI project.
2. **Release-enable it** in `knope.toml` (see above), in a PR with a change file for it.
3. **Plugin Registry** (after the first release): open a PR to https://github.com/OctoPrint/plugins.octoprint.org adding `_plugins/<identifier>.md`, following https://plugins.octoprint.org/help/registering/. Use:
   - `archive`: `https://deshmukhmayur.github.io/octoprint-plugins/<identifier>/latest.zip`
   - `homepage`: `https://github.com/deshmukhmayur/octoprint-plugins/tree/main/plugins/<identifier>`
   - `source`: `https://github.com/deshmukhmayur/octoprint-plugins`
   - `license`: `MIT`
