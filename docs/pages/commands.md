---
title: Commands
---

# Commands

## repox

Convert repository to text format.

```bash
cocode repox [OPTIONS] [REPO_PATH]
```

**Options:**

- `-o, --output-dir` - Output directory (default: `./results/`, use `stdout` for console)
- `-n, --output-filename` - Output filename
- `-i, --ignore-pattern` - Gitignore patterns to exclude (repeatable)
- `-r, --include-pattern` - Glob patterns to include (repeatable)
- `-pp, --path-pattern` - Regex for path filtering
- `-p, --python-rule` - Python processing: `interface`, `imports`, `integral`
- `-s, --output-style` - Output format: `repo_map`, `flat`, `tree`, `import_list`

## swe-from-repo

Analyze repository with AI pipelines.

```bash
cocode swe-from-repo [OPTIONS] PIPE_CODE REPO_PATH
```

**Pipelines:**

- `extract_fundamentals` - Project overview
- `extract_onboarding_documentation` - Onboarding docs
- `extract_environment_build` - Build setup
- `extract_coding_standards` - Code standards
- `extract_test_strategy` - Testing approach
- `extract_collaboration` - Team workflows

**Options:**

- `-o, --output-dir` - Output directory
- `-n, --output-filename` - Output filename
- `--dry` - Dry run without API calls
- Plus all filtering options from `repox`

## swe-from-file

Process text file with AI pipelines.

```bash
cocode swe-from-file [OPTIONS] PIPE_CODE INPUT_FILE
```

**Pipelines:**

- `extract_features_recap` - Summarize features
- `extract_fundamentals` - Extract project info
- `extract_onboarding_documentation` - Structure docs

## swe-from-repo-diff

Analyze git diffs with AI.

```bash
cocode swe-from-repo-diff [OPTIONS] PIPE_CODE GIT_REF REPO_PATH
```

**Main pipeline:**

- `write_changelog` - Generate changelog

**Git references:**

- Tags: `v1.0.0`
- Commits: `abc123`
- Ranges: `v1.0.0..v2.0.0`
- Relative: `HEAD~10`

## GitHub commands

GitHub-related operations and utilities.

### github auth

Check GitHub authentication status.

```bash
cocode github auth
```

Shows current authenticated user, rate limit info, and validates API access.

### github check-branch

Check if a branch exists in a GitHub repository.

```bash
cocode github check-branch REPO BRANCH
```

**Arguments:**
- `REPO` - Repository in format 'owner/repo' or repo ID
- `BRANCH` - Branch name to check

### github repo-info

Get basic information about a GitHub repository.

```bash
cocode github repo-info REPO
```

**Arguments:**
- `REPO` - Repository in format 'owner/repo' or repo ID

Shows repository details including description, language, stars, forks, and creation date.

### github list-branches

List branches in a GitHub repository.

```bash
cocode github list-branches [OPTIONS] REPO
```

**Arguments:**
- `REPO` - Repository in format 'owner/repo' or repo ID

**Options:**
- `-l, --limit` - Maximum number of branches to show (default: 10)

### github sync-labels

Sync labels to a GitHub repository from a JSON file.

```bash
cocode github sync-labels [OPTIONS] REPO LABELS_FILE
```

**Arguments:**
- `REPO` - Repository in format 'owner/repo' or repo ID
- `LABELS_FILE` - Path to JSON file containing labels to sync

**Options:**
- `--dry-run` - Show what would be done without making changes
- `--delete-extra` - Delete labels not in the standard set

## show-pipe

Show pipe definition from the pipe library.

```bash
cocode show-pipe PIPE_CODE
```

**Arguments:**
- `PIPE_CODE` - Pipeline code to show definition for

Displays the complete pipe definition including configuration, steps, and metadata from the pipe library.

## Other commands

- `cocode validate` - Check setup
- `cocode help` - Show help 