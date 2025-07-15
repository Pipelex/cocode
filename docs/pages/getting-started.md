---
title: Getting Started
---

# Getting Started

## Requirements

- Python ≥ 3.10
- pip

## Installation

```bash
pip install cocode
```

## Setup

Create a `.env` file with your API key:

```bash
OPENAI_API_KEY=sk-your-key-here

# Optional
ANTHROPIC_API_KEY=sk-ant-your-key-here
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

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
cocode repox --ignore-pattern "test_*"

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