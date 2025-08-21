domain = "swe_diff"
definition = "Pipelines for analyzing differences between two versions of a codebase."

[concept]
GitDiff = "A git diff output showing changes between two versions of a codebase"
DraftChangelog = "A draft changelog with sections for each type of change."
StructuredChangelog = "A structured changelog with sections for each type of change."
MarkdownChangelog = "A text report in markdown format that summarizes the changes made to the codebase between two versions."

[pipe]
[pipe.write_changelog]
type = "PipeSequence"
definition = "Write a comprehensive changelog for a software project"
inputs = { git_diff = "GitDiff" }
output = "MarkdownChangelog"
steps = [
    { pipe = "write_changelog_from_git_diff", result = "structured_changelog" },
    { pipe = "format_changelog_as_markdown", result = "markdown_changelog" },
]

[pipe.write_changelog_v2]
type = "PipeSequence"
definition = "Write a comprehensive changelog for a software project"
inputs = { git_diff = "GitDiff" }
output = "MarkdownChangelog"
steps = [
    { pipe = "draft_changelog_from_git_diff", result = "draft_changelog" },
    { pipe = "polish_changelog", result = "structured_changelog" },
    { pipe = "format_changelog_as_markdown", result = "markdown_changelog" },
]

[pipe.draft_changelog_from_git_diff]
type = "PipeLLM"
definition = "Write a changelog for a software project."
inputs = { git_diff = "GitDiff" }
output = "DraftChangelog"
llm = "llm_for_swe"
system_prompt = """
You are an expert technical writer and software architect. Your task is to carefully review the code diff and write a draft changelog.
"""
prompt_template = """
Analyze the following code diff and write a draft changelog that summarizes the changes made to the codebase between two versions.
Focus on identifying the key changes, improvements, bug fixes, and new features.
Write in a clear, concise style that would be useful for developers and users.
Be sure to include changes to code but also complementary pipelines, scripts, docs.

@git_diff
"""

[pipe.polish_changelog]
type = "PipeLLM"
definition = "Polish and improve the draft changelog"
inputs = { git_diff = "GitDiff", draft_changelog = "DraftChangelog" }
output = "StructuredChangelog"
llm = "llm_for_swe"
structuring_method = "preliminary_text"
system_prompt = """
You are an expert technical writer. Your task is to polish and improve a draft changelog to make it more clear, concise, and well-structured.
"""
prompt_template = """
Review and polish the following draft changelog that was generated from a git diff.

@git_diff

@draft_changelog

Remove redundancy in the changelog.
And when you see several changes that were made for the same purpose, groupd them as a single item.
Don't add fluff, stay sharp and to the point.
Use nice readable markdown formatting.
"""

[pipe.write_changelog_from_git_diff]
type = "PipeLLM"
definition = "Write a changelog for a software project."
inputs = { git_diff = "GitDiff" }
output = "StructuredChangelog"
llm = "llm_for_swe"
system_prompt = """
You are an expert technical writer and software architect. Your task is to carefully review the code diff and write a structured changelog.
"""
prompt_template = """
Analyze the following code diff. Write a structured changelog that summarizes the changes made to the codebase between two versions.
Be sure to include changes to code but also complementary pipelines, scripts, docs.

@git_diff
"""

[pipe.format_changelog_as_markdown]
type = "PipeJinja2"
definition = "Format the final changelog in markdown with proper structure"
inputs = { structured_changelog = "StructuredChangelog" }
output = "MarkdownChangelog"
template_category = "markdown"
jinja2 = """
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

