# CoCode CLI Reference

🚀 **CoCode** - Repository Analysis and SWE Automation Tool

## Quick Examples

Here are some common CoCode command examples to get you started:

```bash
# Basic repository analysis
cocode repox convert --output-filename cocode_test.txt

# Analyze external project
cocode repox convert ../pipelex-cookbook/ --output-filename pipelex-cookbook.txt

# Extract examples with specific Python rule
cocode repox convert ../pipelex-cookbook/ --output-filename "pipelex-cookbook-examples.txt" \
    --path-pattern "examples" --python-rule integral --include-pattern "*.py"

# Extract Python imports from tools directory
cocode repox convert ../pipelex/ --output-filename "pipelex-tools-imports.txt" \
    --path-pattern "tools" --python-rule imports --output-style import_list \
    --include-pattern "*.py"

# Analyze test interfaces
cocode repox convert ../pipelex/ --output-filename "pipelex-tests.txt" \
    --path-pattern "tests" --python-rule interface --include-pattern "*.py"

# Extract cursor rules
cocode repox convert ../pipelex/ --output-filename "pipelex-cursor-rules.txt" \
    --path-pattern ".cursor/rules" --include-pattern "*.mdc"

# Extract documentation
cocode repox convert ../pipelex/ --output-filename "pipelex-docs.txt" \
    --path-pattern "docs" --include-pattern "*.md"

# Tree structure only
cocode repox convert ../pipelex/ --output-filename "pipelex-docs-tree.txt" \
    --path-pattern "docs" --include-pattern "*.md" --output-style tree

# Flat documentation with exclusions
cocode repox convert ../pipelex/ --output-filename "pipelex-docs.txt" \
    --path-pattern "docs" --include-pattern "*.md" \
    --ignore-pattern "contributing.md" --ignore-pattern "CODE_OF_CONDUCT.md" \
    --ignore-pattern "changelog.md" --ignore-pattern "license.md" \
    --output-style flat

# SWE analysis: Extract fundamentals from local repo
cocode swe from-repo extract_fundamentals ../pipelex/ \
    --path-pattern "docs" --include-pattern "*.md" \
    --output-filename "fundamentals.json"

# SWE analysis: Extract fundamentals from GitHub repo
cocode swe from-repo extract_fundamentals requests/requests \
    --path-pattern "docs" --include-pattern "*.md" \
    --output-filename "requests-fundamentals.json"

# SWE analysis: Extract onboarding documentation from local repo
cocode swe from-repo extract_onboarding_documentation ../pipelex/ \
    --path-pattern "docs" --include-pattern "*.md" \
    --output-filename "docs-structured.json"

# SWE analysis: Extract onboarding documentation from GitHub repo with full URL
cocode swe from-repo extract_onboarding_documentation https://github.com/psf/black \
    --path-pattern "docs" --include-pattern "*.md" \
    --output-filename "black-docs-structured.json"

# SWE analysis: Comprehensive documentation extraction
cocode swe from-repo extract_onboarding_documentation ../pipelex/ \
    --include-pattern "*.md" --include-pattern "*.mdc" \
    --include-pattern "Makefile" --include-pattern "mkdocs.yml" \
    --include-pattern "pyproject.toml" --include-pattern ".env.example" \
    --output-filename "docs-structured.json"

# SWE analysis: Extract features recap from file
cocode swe from-file extract_features_recap ./results/pipelex-docs.txt \
    --output-filename "pipelex-features-recap.md"

# SWE analysis: Generate changelog from git diff (local repo)
cocode swe from-repo-diff write_changelog v0.2.4 ../pipelex-cookbook/ \
    --output-filename "changelog.md"

# SWE analysis: Generate changelog from GitHub repo
cocode swe from-repo-diff write_changelog v2.0.0 requests/requests \
    --output-filename "requests-changelog.md"

# GitHub operations
cocode github auth  # Check authentication status
cocode github repo-info pipelex/cocode  # Get repository information
cocode github check-branch pipelex/cocode main  # Check if branch exists
cocode github list-branches pipelex/cocode --limit 10  # List branches
cocode github sync-labels pipelex/cocode ./labels.json  # Sync labels
```

## Overview

CoCode provides powerful tools for repository analysis and Software Engineering automation through a command-line interface. It can convert repository structures to text files and perform AI-powered analysis using configurable pipelines.

### GitHub Repository Support

CoCode supports analyzing both local repositories and GitHub repositories directly. You can specify GitHub repositories in several formats:

- **Short format**: `owner/repo` (e.g., `microsoft/vscode`)
- **Full HTTPS URL**: `https://github.com/owner/repo` 
- **SSH URL**: `git@github.com:owner/repo.git`
- **Branch-specific**: `owner/repo@branch` or full URLs with `/tree/branch`

**Features:**
- **Smart Caching**: Repositories are cached locally for faster subsequent analysis
- **Authentication**: Supports GitHub Personal Access Tokens (PAT) and GitHub CLI authentication
- **Private Repositories**: Access private repositories with proper authentication
- **Shallow Cloning**: Fast cloning with minimal history for analysis purposes
- **Branch Support**: Analyze specific branches or tags

**Authentication Setup:**
```bash
# Option 1: Set environment variable
export GITHUB_PAT=your_personal_access_token

# Option 2: Use GitHub CLI (recommended)
gh auth login

# Verify authentication
cocode github auth
```

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
cocode repox convert

# Specify output file
cocode repox convert --output-filename my-repo.txt

# Analyze external repository
cocode repox convert ../my-project/ --output-filename project-analysis.txt
```

**Advanced Filtering:**
```bash
# Filter by file patterns
cocode repox convert --include-pattern "*.py" --python-rule interface

# Extract Python imports from specific directory
cocode repox convert ../pipelex/ \
    --output-filename "pipelex-tools-imports.txt" \
    --path-pattern "tools" \
    --python-rule imports \
    --output-style import_list \
    --include-pattern "*.py"

# Analyze documentation with filtering
cocode repox convert ../project/ \
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

### `swe from-repo` - SWE Analysis from Repository

Perform Software Engineering analysis on repositories using AI pipelines. Supports both local repositories and GitHub repositories.

**Local Repository Examples:**
```bash
# Extract fundamentals from documentation
cocode swe from-repo extract_fundamentals ../pipelex/ \
    --path-pattern "docs" \
    --include-pattern "*.md" \
    --output-filename "fundamentals.json"

# Extract comprehensive documentation structure
cocode swe from-repo extract_onboarding_documentation ../pipelex/ \
    --include-pattern "*.md" \
    --include-pattern "*.mdc" \
    --include-pattern "Makefile" \
    --include-pattern "mkdocs.yml" \
    --include-pattern "pyproject.toml" \
    --include-pattern ".env.example" \
    --output-filename "docs-structured.json"

# Dry run to test pipeline
cocode swe from-repo extract_fundamentals . --dry
```

**GitHub Repository Examples:**
```bash
# Analyze public GitHub repository (short format)
cocode swe from-repo extract_fundamentals requests/requests \
    --output-filename "requests-fundamentals.txt"

# Analyze with full GitHub URL
cocode swe from-repo extract_onboarding_documentation https://github.com/psf/black \
    --output-filename "black-onboarding.txt"

# Analyze specific branch
cocode swe from-repo extract_coding_standards pallets/click@main \
    --output-filename "click-standards.txt"

# Focus on documentation from GitHub repo
cocode swe from-repo extract_fundamentals pytest-dev/pytest \
    --path-pattern "doc" --include-pattern "*.rst" --include-pattern "*.md" \
    --output-filename "pytest-docs-analysis.txt"
```

### `swe from-file` - SWE Analysis from File

Process SWE analysis from existing text files.

```bash
# Extract features recap from documentation
cocode swe from-file extract_features_recap ./results/docs.txt \
    --output-filename "features-recap.md"
```

### `swe from-repo-diff` - SWE Analysis from Git Diff

Analyze git diffs using AI pipelines.

```bash
# Generate changelog from git diff
cocode swe from-repo-diff write_changelog v0.2.4 ../project/ \
    --output-filename "changelog.md"

# With ignore patterns
cocode swe from-repo-diff write_changelog v1.0.0 . \
    --ignore-patterns "*.log" \
    --ignore-patterns "temp/" \
    --output-filename "CHANGELOG.md"
```

### `swe doc-update` - Documentation Update Suggestions

This command generates documentation update suggestions based on the differences detected in the git repository.

**Usage**:
```bash
cocode swe doc-update
```

**Examples**:
```bash
cocode swe doc-update --help
```

### `swe doc-proofread` - Documentation Proofreading

Systematically proofread documentation against actual codebase to find inconsistencies that could break user code or cause major confusion.

**Usage**:
```bash
# Proofread docs directory against current repository
cocode swe doc-proofread

# Specify custom documentation directory
cocode swe doc-proofread --doc-dir documentation

# Proofread external project documentation
cocode swe doc-proofread ../my-project/ --doc-dir docs --output-filename my-project-issues

# Focus on specific file patterns in codebase analysis
cocode swe doc-proofread --include-pattern "*.py" --include-pattern "*.ts"

# Exclude certain patterns from codebase analysis
cocode swe doc-proofread --ignore-pattern "test_*" --ignore-pattern "*.md"
```

**Options:**
- `repo_path`: Repository path to analyze (default: current directory)
- `--doc-dir, -d`: Directory containing documentation files (default: "docs")
- `--output-dir, -o`: Output directory (default: "results")
- `--output-filename, -n`: Output filename (default: "doc-proofread-report")
- `--include-pattern, -r`: Include patterns for codebase analysis (can be repeated)
- `--ignore-pattern, -i`: Ignore patterns for codebase analysis (can be repeated)

**Output Format:**
The command generates a markdown report with the following structure for each inconsistency:

- **Doc file path:** Path to the documentation file with issues
- **Issue:** Description of the inconsistency found
- **Related files:** Code files that are relevant to the issue
- **Suggested fix:** Specific actionable solution

The tool focuses on critical issues that would break user code, such as:
- Wrong function/class signatures
- Required parameters marked as optional (or vice versa)
- Incorrect examples that would fail
- Wrong import paths
- Critical type mismatches

### `github` - GitHub Repository Management

Manage GitHub repositories, branches, and labels.

**Subcommands:**

#### `github auth`
Check GitHub authentication status and display rate limit information.

```bash
cocode github auth
```

#### `github repo-info`
Get detailed information about a GitHub repository.

```bash
# Using owner/repo format
cocode github repo-info pipelex/cocode

# Using repository ID
cocode github repo-info 123456789
```

#### `github check-branch`
Check if a specific branch exists in a repository.

```bash
cocode github check-branch pipelex/cocode main
cocode github check-branch pipelex/cocode feature-branch
```

#### `github list-branches`
List branches in a repository with optional limit.

```bash
# List first 10 branches (default)
cocode github list-branches pipelex/cocode

# List first 20 branches
cocode github list-branches pipelex/cocode --limit 20
```

#### `github sync-labels`
Synchronize issue labels from a JSON file to a repository.

```bash
# Dry run to preview changes
cocode github sync-labels pipelex/cocode ./labels.json --dry-run

# Sync labels, keeping existing ones
cocode github sync-labels pipelex/cocode ./labels.json

# Sync labels and delete extras not in JSON file
cocode github sync-labels pipelex/cocode ./labels.json --delete-extra
```

**Label JSON Format:**
```json
[
  {
    "name": "bug",
    "color": "d73a4a",
    "description": "Something isn't working"
  },
  {
    "name": "enhancement",
    "color": "a2eeef",
    "description": "New feature or request"
  }
]
```

**Options:**
- `--dry-run`: Preview changes without making them
- `--delete-extra`: Remove labels not in the JSON file
- `--limit`: Maximum number of items to display (for list commands)

### `validation` - Configuration Validation

Validate setup and pipelines.

```bash
# Validate configuration and pipelines
cocode validation validate

# Run dry validation without full setup
cocode validation dry-run

# Check configuration only
cocode validation check-config

# Backward compatibility (deprecated)
cocode validate
```

### `help` - Show Help

Display comprehensive help and examples.

```bash
cocode --help
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

### GitHub Authentication

For GitHub commands, authentication is handled via the `GITHUB_TOKEN` environment variable or PyGithub's default authentication methods:

1. **Environment Variable**: Set `GITHUB_TOKEN` in your `.env` file or environment
2. **GitHub CLI**: If you have `gh` CLI installed and authenticated
3. **Personal Access Token**: Create at https://github.com/settings/tokens

```bash
# Check authentication status
cocode github auth
```

## Getting Started

1. **Validate Setup**: Run `cocode validate` to ensure everything is configured correctly
2. **Basic Analysis**: Try `cocode repox` to analyze your current directory
3. **Explore Pipelines**: Use `cocode swe-from-repo --dry` to test SWE pipelines
4. **Get Help**: Use `cocode --help` for command overview and `<command> --help` for specific options

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