# AGENTS.md

## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default triage labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Repository

Monorepo of independently released OctoPrint plugins: each `plugins/<identifier>/` is its own package with its own version and changelog. Read `docs/adr/` before changing packaging, update checks or the release workflow.

- **New plugin**: `uv run scripts/new_plugin.py <identifier>`; edit `templates/plugin/` to change what every new plugin starts with.
- **Release**: see `docs/releasing.md`.
