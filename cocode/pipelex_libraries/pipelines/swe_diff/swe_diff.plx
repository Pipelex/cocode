domain = "swe_diff"
definition = "Pipelines for analyzing differences between two versions of a codebase."

[concept]
GitDiff = "A git diff output showing changes between two versions of a codebase"
DraftChangelog = "A draft changelog with sections for each type of change."
StructuredChangelog = "A structured changelog with sections for each type of change."
MarkdownChangelog = "A text report in markdown format that summarizes the changes made to the codebase between two versions."
TwitterPost = "A Twitter-optimized social media post with character limits and hashtags"
LinkedInPost = "A LinkedIn-optimized social media post with professional tone"
SocialMediaPosts = "Combined social media posts for multiple platforms"

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

[pipe.write_changelog_enhanced]
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

[pipe.write_social_posts_twitter]
type = "PipeLLM"
definition = "Generate Twitter-optimized social media posts from git diff changes"
inputs = { git_diff = "GitDiff" }
output = "TwitterPost"
llm = "llm_for_swe"
system_prompt = """
You are a social media expert specializing in developer and tech content for Twitter. Your task is to create engaging, concise Twitter posts that highlight software development updates and changes.
"""
prompt_template = """
Analyze the following git diff and create an engaging Twitter post that highlights the key changes and improvements.

Guidelines:
- Keep the main content under 240 characters to leave room for hashtags
- Use an engaging, developer-friendly tone
- Focus on the most impactful changes
- Include relevant hashtags (3-5 maximum)
- If there are many changes, consider creating a thread with additional posts
- Use emojis sparingly but effectively
- Make it appealing to developers and tech enthusiasts

@git_diff
"""

[pipe.write_social_posts_linkedin]
type = "PipeLLM"
definition = "Generate LinkedIn-optimized social media posts from git diff changes"
inputs = { git_diff = "GitDiff" }
output = "LinkedInPost"
llm = "llm_for_swe"
system_prompt = """
You are a professional content creator specializing in software development and technology content for LinkedIn. Your task is to create engaging, professional posts that showcase software development progress and technical achievements.
"""
prompt_template = """
Analyze the following git diff and create a professional LinkedIn post that highlights the development progress and technical improvements.

Guidelines:
- Use a professional, engaging tone suitable for LinkedIn
- Focus on the business value and technical achievements
- Include context about why these changes matter
- Use 2-4 professional hashtags
- Aim for 150-500 characters for good engagement
- Include a subtle call-to-action if appropriate
- Highlight innovation, problem-solving, or improvements
- Make it appealing to both technical and non-technical professionals

@git_diff
"""

[pipe.write_social_posts_both]
type = "PipeSequence"
definition = "Generate social media posts for both Twitter and LinkedIn from git diff changes"
inputs = { git_diff = "GitDiff" }
output = "SocialMediaPosts"
steps = [
    { pipe = "write_social_posts_twitter", result = "twitter_post" },
    { pipe = "write_social_posts_linkedin", result = "linkedin_post" },
    { pipe = "combine_social_posts", result = "social_media_posts" }
]

[pipe.combine_social_posts]
type = "PipeFunc"
definition = "Combine Twitter and LinkedIn posts into a single structure"
inputs = { twitter_post = "TwitterPost", linkedin_post = "LinkedInPost" }
output = "SocialMediaPosts"
function_name = "combine_social_media_posts"

