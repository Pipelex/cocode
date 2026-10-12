---
title: Getting Started
---

# Getting Started

## Requirements

- Python ≥ 3.11
- pip

## Installation

```bash
pip install cocode
```

## Setup

Cocode runs its AI workflows on [Pipelex](https://github.com/Pipelex/pipelex), on your machine, with your own provider keys. It ships configured for OpenAI: its inference configuration switches on the OpenAI backend alone, and Pipelex's model deck resolves every tier Cocode uses to OpenAI's GPT-5.6 models. The package carries that configuration, so one key is all you need, whichever directory you run Cocode from. Set it in a `.env` file in that directory, or in `~/.pipelex/.env` to use it in every project:

```bash
OPENAI_API_KEY=sk-your-key-here
```

A directory with an inference configuration of its own, a `.pipelex/inference/backends.toml` such as `pipelex init` writes, runs on that configuration instead, as Pipelex always does. A clone of the Cocode repository is such a directory, with the same configuration the package carries.

### Another provider

A key alone is not enough for any other provider, including a local model through Ollama: its backend has to be switched on, and the model deck pointed at the models it serves. Anthropic, for example. In a clone of the Cocode repository, three personal files do it, and git ignores all of them, so the tracked configuration stays as it is:

1. Put `ANTHROPIC_API_KEY` in your `.env` file. `.env.example` lists the variable of every provider.
2. Switch the backends in `.pipelex/inference/backends_override.toml`. Turn OpenAI off unless you keep its key, because a run refuses to start while an enabled backend's key is missing:

    ```toml
    [openai]
    enabled = false

    [anthropic]
    enabled = true
    ```

3. Point the model deck at that provider's models in `.pipelex/inference/deck/x_custom_provider_deck.toml`, a deck file of your own that Pipelex reads after the tracked ones. The deck's tiers are its `default-*` aliases, which every preset goes through, except four that name a model directly, so this one file moves the whole deck:

    ```toml
    [llm.aliases]
    default-general = "claude-5-sonnet"
    default-premium = "claude-5-opus"
    default-premium-vision = "claude-5-opus"
    default-premium-structured = "claude-5-opus"
    default-large-context-code = "claude-5-sonnet"
    default-large-context-text = "claude-5-sonnet"
    default-small = "claude-5.5-haiku"
    default-small-structured = "claude-5.5-haiku"
    default-small-vision = "claude-5.5-haiku"
    default-small-creative = "claude-5.5-haiku"

    [llm.presets]
    retrieval-cheap = { model = "claude-5.5-haiku" }
    retrieval-premium = { model = "claude-5-sonnet" }
    engineering-code-cheap = { model = "claude-5-sonnet" }
    engineering-code-cheaper = { model = "claude-5.5-haiku" }
    ```

With a `pip install`, the configuration Cocode ships sits inside the package, so give the project you run Cocode in a configuration of its own. At its root, run `pipelex-agent init --config '{"backends": ["anthropic"]}'`: it writes a `.pipelex/` directory with Anthropic as its only backend, which does step 2 for you. Then do steps 1 and 3 in that project. Pipelex recognizes a project's root by a marker such as `.git` or `pyproject.toml`, so in a directory that has none, create an empty `.pipelex` directory before running the command.

The models each provider serves are listed in `.pipelex/inference/backends/`. Pipelex's [Configure AI Providers](https://docs.pipelex.com/latest/get-started/configure-ai-providers/) page covers every provider.

Cocode runs its workflows inside its own process, so the hosted Pipelex API and its Pipelex API key do not apply to it.

## Basic usage

### Analyze a repository

```bash
# Current directory
cocode repox

# Specific directory
cocode repox /path/to/project

# Save with custom name
cocode repox --output-filename my-analysis.txt
```

### Filter files

```bash
# Python files only
cocode repox --include-pattern "*.py"

# Exclude tests
cocode repox --exclude-pattern "test_*"

# Specific directory
cocode repox --path-pattern "src"
```

### Python processing modes

```bash
# Extract interfaces (signatures + docstrings)
cocode repox --python-rule interface --include-pattern "*.py"

# Extract imports only
cocode repox --python-rule imports --include-pattern "*.py"

# Full code (default)
cocode repox --python-rule integral --include-pattern "*.py"
```

### AI analysis

```bash
# Extract project overview
cocode swe-from-repo extract_fundamentals .

# Generate changelog from git diff
cocode swe-from-repo-diff write_changelog v1.0.0 .

# Extract features from text file
cocode swe-from-file extract_features_recap analysis.txt
```

## Output styles

- `repo_map` (default) - Tree structure with file contents
- `flat` - File contents only
- `tree` - Directory structure only
- `import_list` - Import statements (with imports rule)

```bash
cocode repox --output-style flat
```

## Next steps

- See [Commands](commands.md) for all available options
- Check [Examples](examples.md) for common workflows 