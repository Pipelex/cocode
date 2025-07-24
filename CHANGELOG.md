# Changelog

## [v0.0.7] - 2025-07-24

### Added
- New pipeline for proofreading documentation: `cocode swe-doc-proofread . --doc-dir docs`

### Changed
- Updated dependencies to `pipelex` version `v0.6.6`. See full `Pipelex` changelog [here](https://github.com/Pipelex/pipelex/blob/main/CHANGELOG.md).
- Updated LLM configurations in `cocode_deck.toml` and `vertexai.toml` files.

## [v0.0.6] - 2025-07-18

### Added
- New pipeline for updating documentation based on `git diff` analysis.
- New pipeline for updating AI instruction files based on `git diff` analysis.

### Changed
- Updated dependencies to `pipelex` version `0.6.3`.
- Modified the `Makefile` to include new commands for installing the latest dependencies and initializing libraries.

## [v0.0.5] - 2025-07-15

- Added the `pipelex_libraries` folder to the project
- Added `/pipelex_libraries` to `.gitignore`
- Moved `data/github/example_labels.json` to `tests/data/github/example_labels.json`

## [v0.0.4] - 2025-07-15

- Added GHA for publishing to PyPI, changelog check, doc deployment, and more

## [v0.0.3] - 2025-07-15

### Added
- New GitHub integration module (based on PyGithub) for cocode with commands for authentication, branch checking, repository info, and label syncing
- New issue templates for bug reports, feature requests, and general issues in GitHub
- New documentation pages including Getting Started, Commands, Examples, and Contributing

### Changed
- Updated Makefile to include new documentation commands for serving, checking, and deploying documentation with mkdocs
- Enhanced CLI with new command group for GitHub-related operations

## [v0.0.2] - 2025-07-11

### Added
- Added `CLA.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md`.

### Changed
- Fresh new look for the CLI: better helpers, sub commands, and more

### Fixed
- Fixed the dry run of `pipelex`
- Removed implementation of the `system` as in `pipelex`.

## [v0.0.1] - 2025-07-09

- Initial release
