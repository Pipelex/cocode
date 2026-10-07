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

Cocode runs its AI workflows on your own provider keys, through the Pipelex configuration of the directory it runs in. The current version only works when run from the cocode repository, whose `.pipelex/` directory enables the OpenAI backend alone, and every model its workflows use by default is an OpenAI model. The `pip` package does not include that directory: to run cocode elsewhere, first run `pipelex init`, which writes a configuration to `~/.pipelex/` and asks which backends to enable. Then create a `.env` file with your OpenAI key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

Pipelex reads `.env` over your environment, so leave a variable out of `.env` rather than setting it to an empty value, which would hide the one you exported.

To use another provider, such as Azure OpenAI, Anthropic, Amazon Bedrock, Google or Mistral, enable its backend in `.pipelex/inference/backends.toml` and set the variables `.env.example` lists for it. The active routing profile, `all_enabled_backends`, sends each model to the first enabled backend that serves it, OpenAI first, so routing needs no change. Every enabled backend needs its key, so to run on Azure OpenAI instead of OpenAI, disable the `openai` backend too. A provider that does not serve OpenAI models also needs the default models repointed at models it serves, in `.pipelex/inference/deck/x_custom_llm_deck.toml`. See [Configure AI Providers](https://docs.pipelex.com/latest/get-started/configure-ai-providers/) in the Pipelex documentation.

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