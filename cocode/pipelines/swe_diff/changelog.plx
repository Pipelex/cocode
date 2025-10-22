domain = "changelog"
description = "Pipelines for analyzing differences between two versions of a codebase."

[concept]
StructuredChangelog = "A structured changelog with sections for each type of change."
MarkdownChangelog = "A text report in markdown format that summarizes the changes made to the codebase between two versions."

[pipe]
[pipe.write_changelog]
type = "PipeSequence"
description = "Write a comprehensive changelog for a software project"
inputs = { git_diff = "git.GitDiff" }
output = "MarkdownChangelog"
steps = [
    { pipe = "structure_changelog_from_git_diff", result = "structured_changelog" },
    { pipe = "format_changelog_as_markdown", result = "markdown_changelog" },
]

[pipe.structure_changelog_from_git_diff]
type = "PipeLLM"
description = "Write a changelog for a software project."
inputs = { git_diff = "git.GitDiff" }
output = "StructuredChangelog"
model = "llm_for_git_diff"
system_prompt = """
You are an expert technical writer and software architect. Your task is to carefully review the code diff and write a structured changelog.
"""
prompt = """
Analyze the following code diff. Write a structured changelog that summarizes the changes made to the codebase between two versions.
Be sure to include changes to code but also complementary pipelines, scripts, docs.

@git_diff
"""

[pipe.format_changelog_as_markdown]
type = "PipeCompose"
description = "Format the final changelog in markdown with proper structure"
inputs = { structured_changelog = "StructuredChangelog" }
output = "MarkdownChangelog"

[pipe.format_changelog_as_markdown.template]
category = "markdown"
template = """
## Unreleased

{% if structured_changelog.added %}
### Added
    {% for item in structured_changelog.added %}
 - {{ item }}
    {% endfor %}
{% endif %}

{% if structured_changelog.changed %}
### Changed
    {% for item in structured_changelog.changed %}
 - {{ item }}
    {% endfor %}
{% endif %}

{% if structured_changelog.fixed %}
### Fixed
    {% for item in structured_changelog.fixed %}
 - {{ item }}
    {% endfor %}
{% endif %}

{% if structured_changelog.removed %}
### Removed
    {% for item in structured_changelog.removed %}
 - {{ item }}
    {% endfor %}
{% endif %}

{% if structured_changelog.deprecated %}
### Deprecated
    {% for item in structured_changelog.deprecated %}
 - {{ item }}
    {% endfor %}
{% endif %}

{% if structured_changelog.security %}
### Security
    {% for item in structured_changelog.security %}
 - {{ item }}
    {% endfor %}
{% endif %}
"""
