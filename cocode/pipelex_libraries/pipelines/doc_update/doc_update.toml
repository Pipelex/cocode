domain = "doc_update"
definition = "Pipeline for updating documentation in docs/ directory based on git diff"

[concept]
GitDiffCitation = "A citation from the git diff that supports a documentation change"
DocumentationItem = "A specific change that needs documentation analysis"
DocumentationAnalysis = "Analysis of what documentation updates are needed"
DocumentationChangeItem = "A specific documentation change with its supporting git diff citations"
ExactChange = "Exact change instruction with old and new patterns"
DocumentationSuggestions = "Final suggestions for updating documentation"

[pipe]

[pipe.extract_git_citations]
type = "PipeLLM"
definition = "Extract relevant git diff citations for documentation changes with old/new code patterns"
inputs = { git_diff = "swe_diff.GitDiff" }
output = "GitDiffCitation"
multiple_output = true
system_prompt = """
You are a git diff analyzer. Extract specific citations from git diffs that show changes affecting user-facing functionality.
IMPORTANT: The git diff shows changes from CURRENT version to an OLD version, so interpret accordingly:
- Lines with "+" are what was ADDED in the current version (what documentation should reflect)
- Lines with "-" are what was REMOVED from the old version (what documentation should no longer show)
"""
prompt_template = """
Analyze this git diff and extract citations for changes that affect user-facing documentation:

@git_diff

IMPORTANT CONTEXT: This diff shows changes from CURRENT → OLD version.
- "+" lines show what the current code HAS (documentation should match this)
- "-" lines show what the old code HAD (documentation should NOT show this anymore)

For each relevant change, extract:
- The file path where the change occurred
- The line range affected (if available)
- The specific diff section showing the change
- The OLD code pattern (what was in the previous version, shown with "-")
- The NEW code pattern (what is in the current version, shown with "+")

Focus on changes that would require documentation updates such as:
- New or modified CLI commands and their parameters
- API function signatures and their parameters
- Import statements and module names
- Installation/setup commands
- Configuration file formats
- User-facing feature changes

EXCLUDE:
- Changes in CHANGELOG.md, CHANGELOG.rst, or any changelog files
- Changes in version files or release notes
- Internal refactoring that doesn't affect user-facing APIs
- Test changes
- Build system changes that don't affect users
- Code style changes without functional impact

For each citation, identify what the CURRENT code does (+ lines) vs what the OLD code did (- lines).
"""

[pipe.identify_doc_changes]
type = "PipeLLM"
definition = "Identify changes that affect documentation with specific patterns"
inputs = { git_diff = "swe_diff.GitDiff", git_citations = "GitDiffCitation" }
output = "DocumentationItem"
multiple_output = true
system_prompt = """
You are a documentation analyst. Identify changes that affect documentation in the docs/ directory.
IMPORTANT: The git diff shows CURRENT → OLD, so focus on what the CURRENT version does that documentation should reflect.
Use the provided git citations to support your analysis and identify exact patterns that changed.
"""
prompt_template = """
Analyze this git diff to identify changes that need docs/ directory updates:

@git_diff

Available git citations with old/new patterns:
@git_citations

IMPORTANT: This diff shows CURRENT → OLD version. Focus on:
- What the CURRENT code does (+ lines in diff) that documentation should show
- What the OLD code did (- lines in diff) that documentation should stop showing

IDENTIFY CHANGES FOR DOCUMENTATION:
- New/removed CLI commands or parameters in current vs old version
- Changed function signatures or API calls between versions
- Modified import statements or module names
- Installation/setup changes
- Configuration changes
- Usage instruction changes

EXCLUDE:
- CHANGELOG.md, CHANGELOG.rst, or any changelog files
- Version bumps or release notes
- Internal refactoring that doesn't affect user-facing functionality
- Test changes
- Implementation details that users don't interact with

For each change, include relevant git citations that show what the CURRENT version does vs what the OLD version did.
"""

[pipe.analyze_doc_change]
type = "PipeLLM"
definition = "Analyze a single change for specific documentation impact with exact patterns"
inputs = { change_item = "DocumentationItem" }
output = "DocumentationAnalysis"
system_prompt = """
You are a documentation expert. Analyze code changes to determine what specific documentation updates are needed.
Focus on docs/ directory files only. Provide exact patterns that need to be changed in documentation.
IMPORTANT: The changes show CURRENT → OLD, so ensure documentation reflects the CURRENT state.
"""
prompt_template = """
Analyze this change for specific documentation impact:

@change_item

Provide detailed analysis including:
- Specific documentation files that need updates
- Exact locations within those files (sections, code blocks, examples)
- What specific content needs to be changed (exact old patterns to find in docs)
- What the new content should be (exact new patterns to replace with, matching CURRENT code)
- Why the change is necessary
- Include the git citations that support this analysis

Be very specific about the exact text patterns that need to be updated in the documentation to match the CURRENT version of the code.
"""


[pipe.create_structured_changes]
type = "PipeLLM"
definition = "Create structured documentation changes with exact old/new patterns"
inputs = { doc_analyses = "DocumentationAnalysis" }
output = "DocumentationChangeItem"
multiple_output = true
system_prompt = """
You are a documentation coordinator. Convert documentation analyses into structured, actionable changes with exact patterns.
Each change should include specific file paths, locations, exact old patterns to find, and exact new patterns to replace with.
IMPORTANT: Ensure the new patterns reflect the CURRENT state of the code.
"""
prompt_template = """
Convert these documentation analyses into structured changes with exact patterns:

@doc_analyses

For each required change, create a structured item with:
- Exact documentation file path
- Specific location within the file
- Clear description of what needs to be updated
- Reason for the change
- EXACT CHANGES: old patterns to find and new patterns to replace with (reflecting CURRENT code state)
- Supporting git citations

Focus on providing exact, actionable find-and-replace instructions that can be easily implemented.

For code examples in documentation, provide:
- The exact old code pattern to find in documentation
- The exact new code pattern to replace it with (matching CURRENT code)
- Context about where to find it (e.g., "in the code block under 'Basic Usage' section")

For text descriptions, provide:
- The exact old text to find in documentation
- The exact new text to replace it with (reflecting CURRENT state)
- Context about the section or paragraph

Make each change as specific and actionable as possible, ensuring documentation matches the CURRENT version.
"""

[pipe.format_final_output]
type = "PipeLLM"
definition = "Format the final documentation update output with clean structure"
inputs = { structured_changes = "DocumentationChangeItem" }
output = "Text"
system_prompt = """
You are a documentation formatter. Create a clean, well-structured output for documentation updates.
Focus on clarity and actionability without unnecessary formatting complexity.
IMPORTANT: Ensure all suggestions reflect updating documentation to match the CURRENT code state.
"""
prompt_template = """
Format these documentation changes into a clean, actionable output:

@structured_changes

Create a well-structured document that includes:

1. A brief summary of files that need updates
2. For each file, provide:
   - File path
   - Location within the file
   - Exact old pattern to find in documentation
   - Exact new pattern to replace with (matching CURRENT code)
   - Brief reason for the change
   - Supporting git citations if relevant

Keep the formatting clean and professional. Use markdown formatting but avoid excessive decoration.
Focus on making it easy for someone to quickly understand what needs to be changed and how to do it.

Structure:
# Documentation Update Requirements

## Summary
[Brief list of files that need updates to match current code]

## Detailed Changes

### [File Path]
**Location:** [Where in the file]
**Change:** [Brief description]
**Reason:** [Why this change is needed to match current code]

**Find this:**
```
[exact old pattern in documentation]
```

**Replace with:**
```
[exact new pattern matching current code]
```

**Supporting Evidence:**
- Git change in [file] showing [brief description of what current code does]

[Repeat for each change]

Keep it simple, clear, and actionable. Focus on updating documentation to accurately reflect the CURRENT state of the code.
"""

[pipe.doc_update]
type = "PipeSequence"
definition = "Documentation update analysis with clean output formatting"
inputs = { git_diff = "swe_diff.GitDiff" }
output = "Text"
steps = [
    { pipe = "extract_git_citations", result = "git_citations" },
    { pipe = "identify_doc_changes", result = "doc_changes" },
    { pipe = "analyze_doc_change", batch_over = "doc_changes", batch_as = "change_item", result = "doc_analyses" },
    { pipe = "create_structured_changes", result = "structured_changes" },
    { pipe = "format_final_output", result = "final_output" },
]

