domain = "changelog"
description = "Pipelines for analyzing differences between two versions of a codebase."

[concept]
DraftChangelog = "A draft changelog with sections for each type of change."

[pipe]

[pipe.write_changelog_enhanced]
type = "PipeSequence"
description = "Write a comprehensive changelog for a software project"
inputs = { git_diff = "git.GitDiff" }
output = "changelog.MarkdownChangelog"
steps = [
    { pipe = "draft_changelog_from_git_diff", result = "draft_changelog" },
    { pipe = "polish_changelog", result = "structured_changelog" },
    { pipe = "format_changelog_as_markdown", result = "markdown_changelog" },
]

[pipe.draft_changelog_from_git_diff]
type = "PipeLLM"
description = "Write a changelog for a software project."
inputs = { git_diff = "git.GitDiff" }
output = "DraftChangelog"
model = "llm_for_git_diff"
system_prompt = """
You are an expert technical writer and software architect.
"""
prompt = """
Analyze the following code diff and write a draft changelog that summarizes the changes made to the codebase between two versions.
Focus on identifying the key changes, improvements, bug fixes, and new features.
Write in a clear, concise style that would be useful for developers and users.
Be sure to include changes to code but also complementary pipelines, scripts, docs.

@git_diff

Output as markdown respecting the classic changelog sections:
### Added
### Changed
### Fixed
### Removed
### Deprecated
### Security

Of course, not all sections are required, only include the relevant ones.
"""

[pipe.polish_changelog]
type = "PipeLLM"
description = "Polish and improve the draft changelog"
inputs = { draft_changelog = "DraftChangelog" }
output = "changelog.StructuredChangelog"
model = "llm_for_swe"
structuring_method = "preliminary_text"
system_prompt = """
You are an expert technical writer. Your task is to polish and improve a draft changelog to make it more clear, concise, and well-structured.
"""
prompt = """
Review and polish the following draft changelog that was generated from a git diff.

@draft_changelog

Remove redundancy in the changelog. For instance, I don't want to see the same change presented both as a "Changed" and "Removed".
And when you see several changes that were made for the same purpose, groupd them as a single item.
Don't add fluff, stay sharp and to the point.
Use nice readable markdown formatting.
"""

