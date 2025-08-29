# Changelog

## [v0.0.14] - 2025-08-29

### Fixed

- Fixed `StrEnum` import error in `cocode/cli.py` and `cocode/repox/process_python.py` to use `pipelex.types.StrEnum` instead of `enum.StrEnum`.

## [v0.0.13] - 2025-08-27

### Changed
- Bump `pipelex` to `v0.8.1`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)

## [v0.0.12] - 2025-08-21

### Changed
- Bump `pipelex` to `v0.7.0`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)

## [v0.0.11] - 2025-08-02

### Added
 - Added comprehensive changelog generation pipeline (`write_changelog_v2`) with three-stage processing: draft generation, polishing, and markdown formatting
 - Added `DraftChangelog` concept definition for intermediate changelog processing
 - Added AI-powered `draft_changelog_from_git_diff` pipe that analyzes code diffs using LLM to extract changes, improvements, and features
 - Added `polish_changelog` pipe that removes redundancy, groups related changes, and applies markdown formatting

## [v0.0.10] - 2025-08-02

### Changed
 - Default output file extension changed from .txt to .md for SWE diff analysis
 - Pipelex dependency constraint relaxed from exact version 0.6.9 to minimum version >=0.6.9
 - Jinja2 template formatting improved with consistent indentation for changelog sections

## [v0.0.9] - 2025-07-26

- Updated pipelex dependency from version 0.6.8 to 0.6.9

### Added
- README example for new CLI command `swe-ai-instruction-update` for updating AI instruction files
- New PipeCode enum values for extraction and documentation operations: EXTRACT_FUNDAMENTALS, EXTRACT_ENVIRONMENT_BUILD, EXTRACT_CODING_STANDARDS, EXTRACT_TEST_STRATEGY, EXTRACT_COLLABORATION, DOC_PROOFREAD, DOC_UPDATE, AI_INSTRUCTION_UPDATE

### Changed
- Simplified pipeline input handling to use input_memory instead of working_memory pattern
- Updated pipeline type definitions from CodeDiff to swe_diff.GitDiff for better naming consistency
- Switched default LLM model from gpt-4o to claude-4-sonnet for software engineering tasks
- Polished code related to cursor rules file detection with support for .cursor/rules directory pattern, using failable_load_text_from_path for better error handling

### Fixed
- Corrected typo in documentation update prompt template ('inclide' to 'include')
- Removed redundant doc_dir parameter from AI instruction update command
- Cleaned up unused to_stdout parameter from doc proofread command

## [v0.0.8] - 2025-07-25

### Added
- `NoDifferencesFound` exception class for handling cases where no differences are found in git diff.

### Changed
- Modified `swe_diff.toml` to reflect changes in pipeline steps and inputs/outputs.
- Refactored CLI commands to use `PipeRunMode` instead of `dry_run`.

### Removed
- Moved utility code from `swe_cmd.py` to `swe_utils.py`.

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
