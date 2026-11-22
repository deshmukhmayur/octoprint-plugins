# OctoPrint Plugins

A collection of [OctoPrint](https://octoprint.org) plugins I developed for my 3D Printer Setup. Each plugin lives in `plugins/<identifier>/` and is versioned, released and installed on its own.

| Plugin | Status |
|---|---|
| [`placeholder_theme`](plugins/placeholder_theme) | Placeholder for a future UI theme, not published |

## Development

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv sync --all-packages                           # OctoPrint + every plugin (editable) + dev tools
uv run octoprint serve --basedir .octoprint      # run OctoPrint locally with all plugins loaded
uv run pytest                                    # all tests
uv run ruff check . && uv run ruff format .      # lint + format
```

`--basedir .octoprint` keeps the dev instance's config and data inside the repo (gitignored), separate from any real OctoPrint install.

### Adding a plugin

```sh
uv run scripts/new_plugin.py filament_tracker --name "Filament Tracker" --description "Tracks filament usage."
uv sync --all-packages
```

This creates `plugins/filament_tracker/` from [`templates/plugin/`](templates/plugin). Choose the identifier carefully: it can't change once the plugin is published.

### Releasing

See [docs/releasing.md](docs/releasing.md).

## Layout

```
plugins/<identifier>/   one independent package per plugin
templates/plugin/       what every new plugin starts as
scripts/                repo tooling (plugin scaffolding, CI helpers)
docs/adr/               architecture decisions
GLOSSARY.md             project vocabulary
```

## License

MIT, see [LICENSE](LICENSE).
