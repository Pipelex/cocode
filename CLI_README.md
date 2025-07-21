# CoCode CLI Reference

🚀 **CoCode** - Repository Analysis and SWE Automation Tool

## Quick Examples

Here are some common CoCode command examples to get you started:

```bash
# Basic repository analysis
cocode repox --output-filename cocode_test.txt

# Analyze external project
cocode repox ../pipelex-cookbook/ --output-filename pipelex-cookbook.txt

# Extract examples with specific Python rule
cocode repox ../pipelex-cookbook/ --output-filename "pipelex-cookbook-examples.txt" \
    --path-pattern "examples" --python-rule integral --include-pattern "*.py"

# Extract Python imports from tools directory
cocode repox ../pipelex/ --output-filename "pipelex-tools-imports.txt" \
    --path-pattern "tools" --python-rule imports --output-style import_list \
    --include-pattern "*.py"

# Analyze test interfaces
cocode repox ../pipelex/ --output-filename "pipelex-tests.txt" \
    --path-pattern "tests" --python-rule interface --include-pattern "*.py"

# Extract cursor rules
cocode repox ../pipelex/ --output-filename "pipelex-cursor-rules.txt" \
    --path-pattern ".cursor/rules" --include-pattern "*.mdc"

# Extract documentation
cocode repox ../pipelex/ --output-filename "pipelex-docs.txt" \
    --path-pattern "docs" --include-pattern "*.md"

# Tree structure only
cocode repox ../pipelex/ --output-filename "pipelex-docs-tree.txt" \
    --path-pattern "docs" --include-pattern "*.md" --output-style tree

# Flat documentation with exclusions
cocode repox ../pipelex/ --output-filename "pipelex-docs.txt" \
    --path-pattern "docs" --include-pattern "*.md" \
    --ignore-pattern "contributing.md" --ignore-pattern "CODE_OF_CONDUCT.md" \
    --ignore-pattern "changelog.md" --ignore-pattern "license.md" \
    --output-style flat

# SWE analysis: Extract fundamentals
cocode swe-from-repo extract_fundamentals ../pipelex/ \
    --path-pattern "docs" --include-pattern "*.md" \
    --output-filename "fundamentals.json"

# SWE analysis: Extract onboarding documentation
cocode swe-from-repo extract_onboarding_documentation ../pipelex/ \
    --path-pattern "docs" --include-pattern "*.md" \
    --output-filename "docs-structured.json"

# SWE analysis: Comprehensive documentation extraction
cocode swe-from-repo extract_onboarding_documentation ../pipelex/ \
    --include-pattern "*.md" --include-pattern "*.mdc" \
    --include-pattern "Makefile" --include-pattern "mkdocs.yml" \
    --include-pattern "pyproject.toml" --include-pattern ".env.example" \
    --output-filename "docs-structured.json"

# SWE analysis: Extract features recap from file
cocode swe-from-file extract_features_recap ./results/pipelex-docs.txt \
    --output-filename "pipelex-features-recap.md"

# SWE analysis: Generate changelog from git diff
cocode swe-from-repo-diff write_changelog v0.2.4 ../pipelex-cookbook/ \
    --output-filename "changelog.md"
```

## Overview

CoCode provides powerful tools for repository analysis and Software Engineering automation through a command-line interface. It can convert repository structures to text files and perform AI-powered analysis using configurable pipelines.

## Installation & Setup

```bash
# Validate your setup
cocode validate
```

## Commands

### `repox` - Repository Analysis

Convert repository structure and contents to text files for analysis.

**Basic Usage:**
```bash
# Analyze current directory
cocode repox

# Specify output file
cocode repox --output-filename my-repo.txt

# Analyze external repository
cocode repox ../my-project/ --output-filename project-analysis.txt
```

**Advanced Filtering:**
```bash
# Filter by file patterns
cocode repox --include-pattern "*.py" --python-rule interface

# Extract Python imports from specific directory
cocode repox ../pipelex/ \
    --output-filename "pipelex-tools-imports.txt" \
    --path-pattern "tools" \
    --python-rule imports \
    --output-style import_list \
    --include-pattern "*.py"

# Analyze documentation with filtering
cocode repox ../project/ \
    --output-filename "docs.txt" \
    --path-pattern "docs" \
    --include-pattern "*.md" \
    --ignore-pattern "contributing.md" \
    --ignore-pattern "changelog.md" \
    --output-style flat
```

**Options:**
- `--output-dir, -o`: Output directory (use 'stdout' for console)
- `--output-filename, -n`: Output filename
- `--ignore-pattern, -i`: Patterns to ignore (gitignore format)
- `--include-pattern, -r`: Patterns files must match (glob)
- `--path-pattern, -pp`: Regex pattern for path filtering
- `--python-rule, -p`: Python processing rule
- `--output-style, -s`: Output format

### `swe-from-repo` - SWE Analysis from Repository

Perform Software Engineering analysis on repositories using AI pipelines.

```bash
# Extract fundamentals from documentation
cocode swe-from-repo extract_fundamentals ../pipelex/ \
    --path-pattern "docs" \
    --include-pattern "*.md" \
    --output-filename "fundamentals.json"

# Extract comprehensive documentation structure
cocode swe-from-repo extract_onboarding_documentation ../pipelex/ \
    --include-pattern "*.md" \
    --include-pattern "*.mdc" \
    --include-pattern "Makefile" \
    --include-pattern "mkdocs.yml" \
    --include-pattern "pyproject.toml" \
    --include-pattern ".env.example" \
    --output-filename "docs-structured.json"

# Dry run to test pipeline
cocode swe-from-repo extract_fundamentals . --dry
```

### `swe-from-file` - SWE Analysis from File

Process SWE analysis from existing text files.

```bash
# Extract features recap from documentation
cocode swe-from-file extract_features_recap ./results/docs.txt \
    --output-filename "features-recap.md"
```

### `swe-from-repo-diff` - SWE Analysis from Git Diff

Analyze git diffs using AI pipelines.

```bash
# Generate changelog from git diff
cocode swe-from-repo-diff write_changelog v0.2.4 ../project/ \
    --output-filename "changelog.md"

# With ignore patterns
cocode swe-from-repo-diff write_changelog v1.0.0 . \
    --ignore-patterns "*.log" \
    --ignore-patterns "temp/" \
    --output-filename "CHANGELOG.md"
```

### `swe-doc-update` - Documentation Update Suggestions

This command generates documentation update suggestions based on the differences detected in the git repository.

**Usage**:
```bash
cocode swe-doc-update
```

**Examples**:
```bash
cocode swe-doc-update --help
```

### `validate` - Configuration Validation

Validate setup and pipelines.

```bash
cocode validate
```

### `help` - Show Help

Display comprehensive help and examples.

```bash
cocode help
```

## Python Processing Rules

- **`interface`**: Extract class/function signatures, docstrings, and public APIs
- **`imports`**: Extract only import statements and public symbols  
- **`integral`**: Include complete Python code (default)

## Output Styles

- **`repo_map`**: Tree structure + file contents (default)
- **`flat`**: File contents only, no tree structure
- **`import_list`**: Formatted import statements (for imports rule)
- **`tree`**: Directory structure only

## Common Patterns

### Code Analysis
```bash
# Analyze test files
cocode repox --path-pattern "tests" --include-pattern "*.py"

# Focus on specific modules
cocode repox --path-pattern "src/core" --python-rule interface

# Extract all Python interfaces
cocode repox --include-pattern "*.py" --python-rule interface
```

### Documentation Analysis
```bash
# Extract documentation
cocode repox --path-pattern "docs" --include-pattern "*.md"

# Analyze README files
cocode repox --include-pattern "README*" --include-pattern "*.md"

# Get project structure only
cocode repox --output-style tree
```

### Configuration Files
```bash
# Analyze configuration
cocode repox --include-pattern "*.toml" --include-pattern "*.yaml" --include-pattern "*.json"

# Extract cursor rules
cocode repox --path-pattern ".cursor/rules" --include-pattern "*.mdc"
```

## Configuration

- Output directory defaults to config value (typically `./results/`)
- Use `--output-dir stdout` to print to console instead of file
- Use `cocode validate` to check configuration and pipelines
- Configuration files are loaded from `pipelex_libraries/` directory

## Getting Started

1. **Validate Setup**: Run `cocode validate` to ensure everything is configured correctly
2. **Basic Analysis**: Try `cocode repox` to analyze your current directory
3. **Explore Pipelines**: Use `cocode swe-from-repo --dry` to test SWE pipelines
4. **Get Help**: Use `cocode help` for detailed examples and `<command> --help` for specific options

## Examples by Use Case

### Repository Documentation
```bash
# Generate comprehensive repo analysis
cocode repox --output-filename "full-analysis.txt"

# Documentation-focused analysis
cocode repox --path-pattern "docs" --include-pattern "*.md" \
    --output-filename "documentation.txt" --output-style flat
```

### Code Review Preparation
```bash
# Extract interfaces for review
cocode repox --include-pattern "*.py" --python-rule interface \
    --output-filename "interfaces.txt"

# Get import dependencies
cocode repox --python-rule imports --output-style import_list \
    --output-filename "dependencies.txt"
```

### Project Onboarding
```bash
# Extract project fundamentals
cocode swe-from-repo extract_fundamentals . \
    --include-pattern "*.md" --output-filename "project-overview.json"

# Generate feature summary
cocode swe-from-file extract_features_recap ./results/documentation.txt \
    --output-filename "features-summary.md"
```

For more information on specific commands, use `cocode <command> --help`. 