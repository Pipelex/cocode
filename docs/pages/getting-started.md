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

Cocode runs its AI workflows on [Pipelex](https://github.com/Pipelex/pipelex), on your machine, with your own provider keys. It ships configured for OpenAI: the OpenAI backend is the one switched on in `.pipelex/inference/backends.toml`, and Pipelex's model deck resolves every tier Cocode uses to OpenAI's GPT-5.6 models. Create a `.env` file at the root of the cocode directory with your key, or put it in `~/.pipelex/.env` to use it in every project:

```bash
OPENAI_API_KEY=sk-your-key-here
```

### Another provider

A key alone is not enough for any other provider, including a local model through Ollama: its backend has to be switched on, and the deck's aliases pointed at the models it serves. Anthropic, for example:

1. Put `ANTHROPIC_API_KEY` in your `.env` file. `.env.example` lists the variable of every provider.
2. Switch the backends in `.pipelex/inference/backends_override.toml`, a personal file git ignores. Turn OpenAI off unless you keep its key, because a run refuses to start while an enabled backend's key is missing:

    ```toml
    [openai]
    enabled = false

    [anthropic]
    enabled = true
    ```

3. Point the aliases Cocode's workflows go through at that provider's models, in `.pipelex/inference/deck/x_custom_llm_deck.toml`:

    ```toml
    [llm.aliases]
    default-general = "claude-5-sonnet"
    default-premium-structured = "claude-5-opus"
    default-large-context-code = "claude-5-sonnet"
    ```

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