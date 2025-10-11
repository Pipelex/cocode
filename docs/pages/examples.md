---
title: Examples
---

# Examples

## Code analysis

### Extract Python API

```bash
# Get all Python interfaces
cocode repox --python-rule interface --include-pattern "*.py" \
  --output-filename api.txt

# Focus on source directory
cocode repox --path-pattern "src" --python-rule interface \
  --include-pattern "*.py" --output-filename src-api.txt
```

### Analyze dependencies

```bash
# Extract all imports
cocode repox --python-rule imports --output-style import_list \
  --include-pattern "*.py" --output-filename dependencies.txt
```

### Documentation only

```bash
# Extract all markdown files
cocode repox --include-pattern "*.md" --output-style flat \
  --output-filename docs.txt
```

## AI workflows

### Project overview

```bash
# Generate project fundamentals
cocode swe-from-repo extract_fundamentals . \
  --output-filename overview.json

# From specific docs
cocode swe-from-repo extract_fundamentals . \
  --include-pattern "*.md" --include-pattern "*.plx" \
  --output-filename project-info.json
```

### Generate changelog

```bash
# From last version
cocode swe-from-repo-diff write_changelog v1.0.0 . \
  --output-filename CHANGELOG.md

# Recent changes
cocode swe-from-repo-diff write_changelog HEAD~10 . \
  --output-filename recent.md

# Between branches
cocode swe-from-repo-diff write_changelog main..feature/new-api . \
  --output-filename feature-changes.md
```

### Feature summary

```bash
# First extract docs
cocode repox --include-pattern "*.md" --output-filename docs.txt

# Then summarize features
cocode swe-from-file extract_features_recap results/docs.txt \
  --output-filename features.md
```

## GitHub operations

### Repository management

```bash
# Check authentication
cocode github auth

# Get repo details
cocode github repo-info pipelex/cocode

# Check if feature branch exists
cocode github check-branch pipelex/cocode feature/new-feature

# List all branches
cocode github list-branches pipelex/cocode --limit 20
```

### Label synchronization

```bash
# Preview label changes
cocode github sync-labels pipelex/cocode ./labels.json --dry-run

# Apply labels (keep existing)
cocode github sync-labels pipelex/cocode ./labels.json

# Full sync (remove extras)
cocode github sync-labels pipelex/cocode ./labels.json --delete-extra
```

**Example labels.json:**
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
  },
  {
    "name": "documentation",
    "color": "0075ca",
    "description": "Improvements or additions to documentation"
  }
]
```

## Common workflows

### Full project analysis

```bash
# 1. Get structure
cocode repox --output-style tree --output-filename structure.txt

# 2. Extract interfaces
cocode repox --python-rule interface --include-pattern "*.py" \
  --output-filename interfaces.txt

# 3. Generate overview
cocode swe-from-repo extract_fundamentals . \
  --output-filename overview.json
```

### PR analysis

```bash
# Analyze changes
cocode swe-from-repo-diff write_changelog origin/main..HEAD . \
  --output-filename pr-changes.md
```

### Clean extraction

```bash
# Exclude common noise
cocode repox \
  --include-pattern "*.py" \
  --exclude-pattern "__pycache__" \
  --exclude-pattern "*.pyc" \
  --exclude-pattern ".git" \
  --exclude-pattern "test_*" \
  --python-rule interface \
  --output-filename clean-api.txt
``` 