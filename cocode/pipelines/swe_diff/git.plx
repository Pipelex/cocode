domain = "git"
description = "Pipelines for analyzing git diffs."

[concept]
GitDiff = "A git diff output showing changes between two versions of a codebase"

[pipe.analyze_git_diff]
type = "PipeLLM"
description = "Analyze the git diff based on a prompt."
inputs = { git_diff = "GitDiff", prompt = "Text" }
output = "Text"
model = "llm_for_git_diff"
system_prompt = """
You are an expert technical writer and software architect. Your task is to carefully review and analyze the code diff.
"""
prompt = """
Analyze the following code diff based on this prompt: $prompt

@git_diff

Answer in markdown format.
"""
