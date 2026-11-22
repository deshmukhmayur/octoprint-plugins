# knope and change files for versions, changelogs and releases

Versions, changelogs and release tags are managed by knope from change files in `.changeset/`, collected into a release PR that's merged to release. We chose change files over commit-message tools like release-please because they record the size of each change per plugin explicitly, in the style of JavaScript's Changesets. The cost is knope's fixed monorepo tag format, `<identifier>/v<version>`. It can't be configured, and our earlier `<identifier>-v<version>` format was given up for it. Nothing outside the repo reads tags (see ADR-0002 and ADR-0003), so the format is cosmetic.

## Consequences

- A plugin is only released once its `knope.toml` entry lists `versioned_files`, because knope releases every listed package whose version is untagged. New plugins start without it.
- Tagging, publishing and Pages all run in the single `release.yml` workflow, because tags created with the built-in Actions token don't trigger other workflows.
