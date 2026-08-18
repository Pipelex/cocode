# Changelog

## [v0.10.0] - 2026-08-18

### Changed
- **Dependencies:** Bumped `pipelex` (with the `anthropic`, `google`, `google-genai` and `bedrock` extras) from `0.45.0` to `0.46.1`.
- **Config (breaking):** Migrated the vendored `.pipelex/` configuration to the reshaped `pipelex` 0.46 root. The old `[pipelex.*]` and `[cogt.*]` tables are gone, replaced by tables named after the runtime layer they configure and stripped of the redundant `_config` suffix: `[interpreter.*]` for the method machinery (`pipeline_execution`, `scan`, `builder`), `[inference.*]` for the model-calling seam (`model_deck`, `llm`, `llm.instructor`), and `[runtime.*]` for process-scoped infrastructure (`storage`, `log`, `reporting`). Every value cocode had chosen is carried over unchanged. Anyone with their own `.pipelex/` directory — global or per-project — should run `pipelex migrate` after upgrading; a stale file no longer hard-crashes the boot, but it does warn until the command is run.
- **Config (breaking):** Removed `prompting_target` from every vendored inference backend file under `.pipelex/inference/backends/`. `pipelex` 0.46 deleted the field and its `PromptingTarget` enum, and the strict boot loader now rejects the key — fatally so in `portkey.toml`, where it appeared both in `[defaults]` and on individual Gemini model entries.
- **Prompting:** Prompt shape changes for every cocode pipeline as a consequence of the upgrade. `pipelex` 0.46 makes the templating style an authoring decision on the pipe rather than something inferred from the model, and ships XML tags (`<tag>...</tag>`) as the new global default in place of back-ticks. Cocode's pipes declare no `templating_style`, so they all pick up that default. No pipeline output format changed, but the prompts sent to the models are not byte-identical to those of 0.9.1.

## [v0.9.1] - 2026-08-15

### Changed
- **Dependencies:** Bumped `pipelex` (with the `anthropic`, `google`, `google-genai` and `bedrock` extras) from `0.42.0` to `0.45.0`.

### Fixed
- **Pipelines:** The `write_changelog_enhanced` sequence in `swe_diff/changelog_enhanced.mthds` referenced `format_changelog_as_markdown` without its domain, but that pipe is declared in the `changelog` domain. `pipelex` 0.45.0 resolves an unqualified pipe reference strictly inside the referencing pipe's own domain, so this became a hard startup failure for every `cocode` command. The reference is now written out as `changelog.format_changelog_as_markdown`.

## [v0.9.0] - 2026-08-01

### Changed
- **Swept onto `pipelex` 0.42.0** (`pipelex[...]==0.39.0` → `==0.42.0`, crossing three release cycles). Despite 0.41.0 being the largest breaking core release of the year, the blast radius here is small — cocode drives pipelex through its public run surface rather than its internals, so only two addresses moved: `pipelex.hub` was deleted with no shim (split into `pipelex.runtime_hub` / `pipelex.interpreter_hub` by owning layer, and `get_required_concept` is interpreter-layer), and `PipeRunMode` moved from `pipelex.pipe_run.pipe_run_mode` to `pipelex.system.pipe_run_mode`. Nothing in the parser move, the Pipe-machinery move, the `pipelex.providers` vendor rename, or the `Concept`-becomes-pure-data change reaches this repo. From 0.42.0, the only change that reaches us is strict PipeFunc name collisions — see the fix below.
- **Pipelines:** Custom PipeFunc functions are now registered solely through the `@pipe_func()` decorator; the redundant manual `func_registry.register_function(...)` calls in `doc_proofread/file_utils.py` and `pipelines/text_utils.py` are gone. `split_text_by_identifiers` gains the decorator it was missing, so it no longer depends on the class-registry scan importing its module as a side effect.
- **CI:** Added Python 3.14 to the lint and test matrices, so every version advertised in the package classifiers is now actually tested.
- **CI:** Bumped `actions/setup-python` from `v4` to `v6` in the lint and test workflows. `v4` targets the Node 16 runtime, which the runners only still execute via a forced fallback; `v6` is the first major on Node 24. Note that `v5` would not have helped — it targets the equally deprecated Node 20.
- **Core:** Import `StrEnum` from the stdlib `enum` module instead of the `pipelex.types` re-export, which upstream deleted along with its own 3.10 support.
- **Tooling:** Point mypy at local paths (`files`) rather than module names (`packages`), so an editable `pipelex` checkout on the import path no longer drags that repo's test suite into our type check.

### Fixed
- **Pipelines:** Every `cocode` command crashed at startup on `pipelex` 0.42.0 with `FuncRegistryError: Function name 'read_file_content' is already registered by a different function`. `file_utils.py` registered `read_file_content` twice — once when imported as a package module by `swe_cmd.py`, once when pipelex's folder scan re-imported the same file by path under a mangled module name — and 0.42.0 turned that silent overwrite into a hard error. Dropping the manual registration leaves the decorator-driven scan as the single registration path.

### Removed
- **Python:** Dropped support for Python 3.10 (breaking). The minimum supported version is now Python 3.11, matching the version the type-checkers and linter already target.

## [v0.8.0] - 2026-07-06

### Added
- **Editor:** Added VS Code workspace settings (`.vscode/settings.json`) to auto-format code and organize imports on save via Ruff, and set the default Python interpreter.

### Changed
- **Dependencies:** Upgraded `pipelex` to `0.37.0` (enforces keyword-only arguments across the public API) and pinned `ruff` to `0.14.13`.
- **Core:** Migrated the SWE pipeline runner to the new MTHDS Protocol, replacing `PipelexRunner`/`execute_pipeline()` with `PipelexMTHDSProtocol`/`execute()` across `swe_cmd.py` and integration tests.
- **Pipelines:** Renamed `TestingStrategyDoc` to `TestStrategyDoc` and its `testing_strategy` field to `test_strategy` in the `swe_docs` pipeline schema.

### Fixed
- **Pipelines:** Corrected markdown list formatting in the `swe_diff/changelog.mthds` template by removing an errant leading space.

### Removed
- **Config:** Removed the experimental `[pipelex.feature_config]` section and its flags (`is_reporting_enabled`, `is_pipeline_tracking_enabled`) from `pipelex.toml` files.
- **Pipelines:** Removed `combined_output` definitions from the `ai_instruction_update.mthds` and `swe_docs.mthds` pipelines.

## [v0.7.1] - 2026-06-09

### Changed
 - Bump `pipelex` to `v0.32.1`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)
 - Adapt SWE commands to Pipelex's new cost-report rendering API: replace the removed `ReportingProtocol.generate_report()` with the one-arg `render_cost_report_for_output()` helper
 - Tighten the `pyright` configuration (set `venvPath`/`venv`, broaden the exclude list)

### Added
 - Ignore Pipelex runtime traces (`.pipelex/traces/`) in `.gitignore`

## [v0.7.0] - 2026-06-05

### Changed
 - Bump `pipelex` to `v0.31.0`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)
 - Bump `pyright` to `1.1.410`
 - Migrate pipeline definition files from the `.plx` extension to `.mthds`, aligning cocode with the MTHDS standard
 - Resync `.pipelex/inference/` configuration: added `fal`, `huggingface`, `portkey`, `scaleway`, and `pipelex_gateway` backends and restructured the model decks and routing profiles
 - `CLAUDE.md` is now a hand-maintained file scoped to a `## Commands` section (linting, testing, cleaning); dropped the auto-generated Pipelex `.mthds` authoring rules block

### Added
 - Release automation skill (`.claude/skills/release`) that bumps the version, finalizes the changelog, runs the quality gate, and opens the release PR
 - `make agent-check` and `make agent-test` Makefile targets for AI agents: a combined lint/typecheck gate and a test run that is silent on success and only prints output on failure

### Removed
 - Legacy AI-instruction files now consolidated into `CLAUDE.md`: `.cursor/rules/*`, `.github/copilot-instructions.md`, `.windsurfrules.md`, `AGENTS.md`, and `BLACKBOX_RULES.md`

## [v0.6.3] - 2025-11-18

- Bump `pipelex` to `v0.15.7` to fix `pipelex doctor`

## [v0.6.2] - 2025-11-18

- Bump `pipelex` to `v0.15.6`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)

## [v0.6.1] - 2025-11-13

### Added
 - Groq inference backend with configuration for Meta Llama 3.1/3.3/4, Llama Guard, OpenAI GPT-OSS, Groq compound models, Moonshot, and Qwen models via `.pipelex/inference/backends/groq.toml`

### Changed
 - Centralized exception handling by moving `PythonProcessingError`, `RepoxException`, and `NoDifferencesFound` to `cocode/exceptions.py`
 - Upgraded dependencies: `pipelex` to `0.15.4`, `pytest` to `9.0.1`
 - Improved test configuration with pre-flight initialization check

## [v0.6.0] - 2025-11-07

- Bump `pipelex` to `v0.15.3`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)

### Added
 - New Models: `claude-4.5-haiku` (Anthropic, Amazon Bedrock, Pipelex Inference), `claude-4.5-sonnet` (BlackBox AI), `gpt-5` and `o3` (Azure OpenAI), and image generation models on BlackBox AI: `flux-pro`, `flux-pro/v1.1`, `flux-pro/v1.1-ultra`, `fast-lightning-sdxl`, `nano-banana`
 - Project Configuration: New `.pipelex/pipelex.toml` file for customizing logging, directory scanning, prompt dumping, and cost reporting
 - Routing Profiles: `pipelex_first` profile now includes `fallback_order` for resilient routing; added backend-specific profiles (`all_openai`, `all_anthropic`, etc.)
 - Model Presets: New waterfall lists (`smart_llm_with_vision`, `smart_llm_for_structured`, `cheap_llm`) and skill-specific presets
 - Documentation: Configuration files now include headers with documentation and support links; backends configuration includes `display_name` for each provider

### Changed
 - Dependencies: Upgraded `pipelex` from v0.14.0 to v0.15.3
 - Model Deck Refactoring: Presets renamed and grouped by skill for clarity; obsolete generic presets replaced with specific waterfall lists
 - Default Aliases: `base-gpt` and `best-gpt` now point to `gpt-4o` instead of `gpt-5` for stability
 - Backend Organization: Inference backends in `backends.toml` sorted alphabetically
 - Internal Refactoring: Changelog generation pipeline moved from `swe_diff` to `changelog` domain; pipelines updated to use new model presets
 - Tooling: Makefile `validate` command now uses `cocode validate` entry point


### Removed
 - Makefile shorthand commands: `rl` (reinitlibraries) and `ri` (reinstall)

## [v0.5.0] - 2025-10-27

- Bump `pipelex` to `v0.14.0`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)

### Changed
 - Documentation Improvements: Overhauled `README.md` with a new "Get Your API Keys" section outlining three configuration methods (free `PIPELEX_API_KEY`, bring-your-own provider keys, or local AI models). Updated terminology from "AI-powered pipelines" to "AI-powered workflows".

### Removed
 - Removed unused `is_activity_tracking_enabled` option from `pipelex.toml` configuration files.
 - Removed `reportConstantRedescription` and `reportShadowedImports` linter rules from `pyproject.toml`.

## [v0.4.0] - 2025-10-21

### Added
 - **Multiplicity syntax:** Introduced bracket notation for defining input/output multiplicity in `.plx` files: `TypeName[]` for variable items, `TypeName[N]` for fixed count (e.g., `output = "Idea[]"` or `output = "Image[3]"`)
 - **`git` pipeline domain:** Created `git.plx` file to house `git.GitDiff` concept and related pipelines

### Changed
 - **Upgraded Pipelex:** Updated core dependency from `0.12.0` to `0.13.0` to support new multiplicity syntax
 - **API simplification:** Renamed `execute_pipeline` parameter `input_memory` to `inputs`, internal type `ImplicitMemory` to `PipelineInputs`, and model alias `llm_to_reason` to `llm_for_complex_reasoning`
 - **Pipeline organization:** Refactored monolithic `swe_diff.plx` into focused files (`git.plx`, `write_changelog_enhanced.plx`). Moved and renamed `swe_diff.GitDiff` to `git.GitDiff`
 - **Changelog generation:** The `changelog update` command now uses the `write_changelog_enhanced` pipeline
 - **Documentation:** Updated all docs (`README.md`, `AGENTS.md`, AI instruction files) to reflect new multiplicity syntax and naming conventions

### Fixed
 - **Execution context:** Added note to `README.md` clarifying that `cocode` must be run from the project's root directory

### Removed
 - **Legacy multiplicity parameters:** Removed `nb_output` and `multiple_output` parameters, replaced by bracket notation

## [v0.3.0] - 2025-10-15

### Highlights
- Bump `pipelex` to `v0.12.0`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)
- Major overhaul of Pipelex language syntax and inference configuration system

### Added
- `analyze` command for analyzing git diffs with custom prompts
- Migration guide for upgrading to v0.3.0
- Granular documentation guides: `write_pipelex.mdc`, `python_standards.mdc`, `run_pipelex.mdc`
- Inference backend configurations for `google`

### Changed
- **Breaking**: Overhauled Pipelex language syntax: `definition` → `description`, `llm` → `model`, `prompt_template` → `prompt`, `PipeOcr` → `PipeExtract`, `PipeJinja2` → `PipeCompose`
- **Breaking**: Revamped inference configuration to structured backend system in `.pipelex/inference/`
- **Breaking**: Renamed CLI flag `--ignore-pattern` → `--exclude-pattern`
- Renamed `pipelex_libraries` directory → `pipelines`
- Updated test markers: `ocr` → `extract`, `imgg` → `img_gen`
- Default routing profile changed to `pipelex_first`

### Removed
- Monolithic rule files (replaced with specific guides)
- Legacy `base_library` pipelines (functionality moved to core)
- `init` and `reinitbaselibrary` Makefile commands
- `base_templates.toml` (contents integrated into core)


## [v0.2.3] - 2025-09-22

### Changed

- Cleaned cli commands.

## [v0.2.2] - 2025-09-18

### Highlights
- Bump `pipelex` to `v0.10.2`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)

### Added
- Comprehensive inference backend configuration system supporting Anthropic, Azure OpenAI, Bedrock, BlackboxAI, Mistral, Ollama, OpenAI, Perplexity, VertexAI, and XAI
- New model deck system with routing profiles for model-to-backend management
- Support for latest AI models: Claude 4 (sonnet, opus, 4.1-opus), GPT-5 (standard, mini, nano, chat), O3/O4, Grok-3, and Gemini 2.5
- Model aliases system with cost tracking and input/output type specifications

### Changed
- Migrated from LLM deck to model deck system with backend-specific configurations
- Restructured configuration from `cocode/pipelex_libraries` to `.pipelex` directory
- Updated model naming conventions and pipeline configurations

### Removed
- Legacy LLM integrations and individual provider files (anthropic.toml, openai.toml, etc.)
- Old configuration files: plugin_config.toml, preferred_platforms, ocr_handles, llm_external_handles

## [v0.2.1] - 2025-09-06

### Changed

- Bump `pipelex` to `v0.9.4`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)
- Support BlackboxAI endpoints for inference

## [v0.2.0] - 2025-09-06

### Added
- Command group structure with `app.add_typer()` for better CLI organization
- `cocode/common.py` module with shared utilities (`PipeCode` enum, `validate_repo_path()`, `get_output_dir()`)
- Alternative command names for flexibility (e.g., `repox repo` alongside `repox convert`)
- GitHub repository support for analyzing both local and remote repositories
- Smart caching system for GitHub repositories with local storage
- GitHub authentication support via Personal Access Tokens (PAT) and GitHub CLI
- Private repository access with proper authentication
- Shallow cloning for faster repository analysis
- Branch-specific repository analysis support
- Multiple GitHub URL format support (short format, HTTPS, SSH, branch-specific)
- Force refresh functionality for cached repositories
- Temporary directory mode for GitHub repository cloning
- Cache cleanup functionality for old repositories
- Comprehensive GitHub repository manager with `GitHubRepoManager` class
- Integration tests for GitHub functionality
- Unit tests for GitHub repository manager
- Enhanced CLI documentation with GitHub repository examples

### Changed
- **Major CLI restructuring**: Reorganized flat command structure into logical command groups for better organization and maintainability
  - `repox` → `repox convert` (repository processing commands)
  - `swe-*` commands → `swe *` subcommands (e.g., `swe-from-repo` → `swe from-repo`)
  - `validate` → `validation validate` (with additional `validation dry-run` and `validation check-config` options)
- **Improved CLI architecture**: Extracted command implementations from main CLI module into co-located packages (`cocode/repox/repox_cli.py`, `cocode/swe/swe_cli.py`, etc.) for better code organization
- **Updated documentation**: All examples and references updated to reflect new command structure
- Repository path validation now supports both local paths and GitHub URLs
- All SWE commands now support GitHub repository analysis in addition to local repositories
- CLI help text updated to reflect GitHub repository support
- Command descriptions enhanced with GitHub repository examples

### Removed
- Direct command implementations from main CLI module (moved to dedicated CLI modules)

### Deprecated
- Direct `cocode validate` command (still works but shows deprecation notice; use `cocode validation validate` instead)

### Security
- GitHub authentication support with secure token handling
- Private repository access with proper credential management

## [v0.1.3] - 2025-09-06

### Added

 - Better support for BlackboxAI IDE
 - VS Code extensions recommendations file with Pipelex, Ruff, and MyPy extensions
 - File association for .plx files in VS Code settings
 - Bump `pipelex` to `v0.9.3`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)


## [v0.1.2] - 2025-09-03

### Changed

- Deactivated pipeline tracking and activity tracking in `pipelex.toml`.
- Added IDE extension link to `README.md`.

## [v0.1.1] - 2025-09-02

### Added

- Added demo video to README.md

## [v0.1.0] - 2025-09-02

### Changed

- Bump `pipelex` to `v0.9.0`: See `Pipelex` changelog [here](https://docs.pipelex.com/changelog/)
- Switched from `TOML` to `PLX` for pipeline definitions.

## [v0.0.15] - 2025-08-29

### Changed

- Fixed `typing_extensions` import error in `cocode/pipelex_libraries/pipelines/swe_diff/swe_diff.py` to use `typing_extensions` instead of `typing`.

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
 - Added comprehensive changelog generation pipeline (`write_changelog_enhanced`) with three-stage processing: draft generation, polishing, and markdown formatting
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
- Simplified pipeline input handling to use inputs instead of working_memory pattern
- Updated pipeline type definitions from CodeDiff to git.GitDiff for better naming consistency
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
- Modified `swe_diff.plx` to reflect changes in pipeline steps and inputs/outputs.
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
