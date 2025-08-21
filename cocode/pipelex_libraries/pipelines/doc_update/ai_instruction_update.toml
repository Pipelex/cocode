domain = "ai_instruction_update"
definition = "Pipeline for updating AI instruction files (AGENTS.md, CLAUDE.md, cursor rules) based on git diff"

[concept]
AgentsContent = "Content of the AGENTS.md file"
ClaudeContent = "Content of the CLAUDE.md file"
CursorRulesContent = "Content of cursor rules files"
AIInstructionFileAnalysis = "Analysis of changes needed for a specific AI instruction file"
AIInstructionParallelResults = "Results from parallel analysis of AI instruction files"
AIInstructionUpdateSuggestions = "Comprehensive suggestions for updating all AI instruction files"

[pipe]

[pipe.analyze_agents_md_changes]
type = "PipeLLM"
definition = "Analyze changes needed for AGENTS.md file"
inputs = { git_diff = "swe_diff.GitDiff", agents_content = "AgentsContent" }
output = "AIInstructionFileAnalysis"
system_prompt = """
You are an AI instruction expert specializing in AGENTS.md files.
Focus on extracting CODING PRINCIPLES and identifying SPECIFIC UTILITY METHODS/PATTERNS used in the codebase.
Recognize established utility functions and patterns that should be used consistently across the project.
Filter out maintenance updates, version changes, and configuration tweaks that don't improve coding skills.
"""
prompt_template = """
Analyze changes needed for AGENTS.md based on git diff and current file content.

CRITICAL FOCUS: Extract coding principles AND identify specific utility methods/patterns that are established in the codebase.

GIT DIFF:
@git_diff

CURRENT AGENTS.MD CONTENT:
@agents_content

Look for TWO TYPES of patterns in the changes:

**1. GENERAL CODING PRINCIPLES:**
- Error handling patterns
- Validation approaches
- Code organization patterns
- Performance practices

**2. SPECIFIC UTILITY METHODS/PATTERNS:**
- Established utility functions that should be used consistently
- Specific patterns or methods that are part of the codebase standards
- Helper functions that are meant to be reused across the project
- Established error handling utilities or validation helpers

**RECOGNIZE ESTABLISHED PATTERNS:**
- If you see utility functions being used in the changes, identify them specifically
- If you see specific exception classes being created/used, identify them specifically
- If you see established helper functions, mention them by name
- Don't overgeneralize utility methods into vague principles

**COMPLETELY IGNORE:**
- Version number updates
- Configuration file changes that don't affect coding
- Documentation formatting or typo fixes
- Gitignore pattern updates
- Dependency version bumps without API changes

Be specific about utility methods and helper functions that are part of the codebase standards.
"""

[pipe.analyze_claude_md_changes]
type = "PipeLLM"
definition = "Analyze changes needed for CLAUDE.md file"
inputs = { git_diff = "swe_diff.GitDiff", claude_content = "ClaudeContent" }
output = "AIInstructionFileAnalysis"
system_prompt = """
You are an AI instruction expert specializing in CLAUDE.md files.
Focus on extracting CODE GENERATION PRINCIPLES and identifying SPECIFIC UTILITY METHODS/PATTERNS used in the codebase.
Recognize established utility functions and patterns that should be used consistently across the project.
Filter out maintenance updates, version changes, and configuration tweaks that don't improve code quality.
"""
prompt_template = """
Analyze changes needed for CLAUDE.md based on git diff and current file content.

CRITICAL FOCUS: Extract code generation principles AND identify specific utility methods/patterns that are established in the codebase.

GIT DIFF:
@git_diff

CURRENT CLAUDE.MD CONTENT:
@claude_content

Look for TWO TYPES of patterns in the changes:

**1. GENERAL CODE GENERATION PRINCIPLES:**
- Error handling patterns
- Validation approaches
- Code structure patterns
- Performance patterns
and so on...

**2. SPECIFIC UTILITY METHODS/PATTERNS:**
- Established utility functions that should be used consistently
- Specific patterns or methods that are part of the codebase standards
- Helper functions that are meant to be reused across the project
- Established error handling utilities or validation helpers

**RECOGNIZE ESTABLISHED PATTERNS:**
- If you see utility functions being used in the changes, identify them specifically
- If you see specific exception classes being created/used, identify them specifically
- If you see established helper functions, mention them by name
- Don't overgeneralize utility methods into vague principles

**COMPLETELY IGNORE:**
- Version number updates
- Configuration file changes that don't affect code generation
- Documentation formatting or typo fixes
- Gitignore pattern updates
- Dependency version bumps without API changes

Be specific about utility methods and helper functions that are part of the codebase standards.
"""

[pipe.analyze_cursor_rules_changes]
type = "PipeLLM"
definition = "Analyze changes needed for cursor rules files"
inputs = { git_diff = "swe_diff.GitDiff", cursor_rules_content = "CursorRulesContent" }
output = "AIInstructionFileAnalysis"
system_prompt = """
You are an AI instruction expert specializing in cursor rules files.
Focus on extracting CODING PRINCIPLES and identifying SPECIFIC UTILITY METHODS/PATTERNS used in the codebase.
Recognize established utility functions and patterns that should be used consistently across the project.
Filter out maintenance updates, version changes, and configuration tweaks that don't improve code quality.
"""
prompt_template = """
Analyze changes needed for cursor rules based on git diff and current file content.

CRITICAL FOCUS: Extract coding principles AND identify specific utility methods/patterns that are established in the codebase.

GIT DIFF:
@git_diff

CURRENT CURSOR RULES CONTENT:
@cursor_rules_content

Look for TWO TYPES of patterns in the changes:

**1. GENERAL CODING PRINCIPLES:**
- Error handling patterns
- Validation approaches
- Code organization patterns
- Performance practices

**2. SPECIFIC UTILITY METHODS/PATTERNS:**
- Established utility functions that should be used consistently
- Specific patterns or methods that are part of the codebase standards
- Helper functions that are meant to be reused across the project
- Established error handling utilities or validation helpers

**RECOGNIZE ESTABLISHED PATTERNS:**
- If you see utility functions being used in the changes, identify them specifically
- If you see specific exception classes being created/used, identify them specifically
- If you see established helper functions, mention them by name
- Don't overgeneralize utility methods into vague principles

**COMPLETELY IGNORE:**
- Version number updates
- Configuration file changes that don't affect coding practices
- Documentation formatting or typo fixes
- Gitignore pattern updates
- Dependency version bumps without API changes

Be specific about utility methods and helper functions that are part of the codebase standards.
"""

[pipe.combine_ai_instruction_analyses]
type = "PipeLLM"
definition = "Combine all AI instruction file analyses into comprehensive suggestions"
inputs = { parallel_analyses = "AIInstructionParallelResults" }
output = "AIInstructionUpdateSuggestions"
system_prompt = """
You are an AI instruction coordinator. Combine individual file analyses into comprehensive, actionable suggestions.
Generate clear, structured output that separates each file's requirements.
"""
prompt_template = """
Combine these AI instruction file analyses into comprehensive suggestions:

@parallel_analyses

Extract the individual analyses for each file type and create a comprehensive summary that:
1. Assigns each analysis to the correct file type
2. Provides an overall summary of all changes needed
3. Maintains clear separation between file types
4. Ensures all specific content is preserved

The output should be structured to clearly show what needs to be done for each file type.
"""

[pipe.format_ai_instruction_output]
type = "PipeLLM"
definition = "Format AI instruction update suggestions into a clear, user-friendly text output"
inputs = { combined_suggestions = "AIInstructionUpdateSuggestions" }
output = "Text"
system_prompt = """
You are an expert technical writer specializing in AI instruction files.
Be HIGHLY SELECTIVE - only document changes that represent significant coding principles or patterns.
When a change IS important, write PRECISE, ACTIONABLE RULES - no explanations, no fluff, just direct commands.
Write rules as imperative statements that developers can immediately follow.
"""
prompt_template = """
Format these AI instruction update suggestions into a clear, well-structured text output:

@combined_suggestions

Create a professional document with the following structure:

# AI INSTRUCTION FILES UPDATE SUGGESTIONS

I have made changes to my codebase and need you to update the AI instruction files accordingly.

**IMPORTANT NOTE:** Write PRECISE, ACTIONABLE RULES. No explanations, no context, just direct commands.

## OVERALL SUMMARY
[Only mention changes that represent major shifts in coding approach]

## AGENTS.md UPDATES
[Only include if there are SIGNIFICANT changes to development principles]

**Reasoning:** [One sentence explaining why this matters]

**Additions:**
[List precise rules as imperative commands based on the analysis]

**Deletions:**
[List precise rules about what to stop doing]

**Modifications:**
[List precise rules about what to change]

## CLAUDE.md UPDATES
[Only include if there are SIGNIFICANT changes to code generation principles]

**Reasoning:** [One sentence explaining why this matters]

**Additions:**
[List precise code generation rules as imperative commands based on the analysis]

**Deletions:**
[List precise rules about what to stop doing]

**Modifications:**
[List precise rules about what to change]

## CURSOR RULES UPDATES
[Only include if there are SIGNIFICANT changes to coding practices]

**Reasoning:** [One sentence explaining why this matters]

**Additions:**
[List precise coding rules as imperative commands based on the analysis]

**Deletions:**
[List precise rules about what to stop doing]

**Modifications:**
[List precise rules about what to change]

## NO UPDATES NEEDED
[Include this section if no changes represent significant shifts in coding principles]

IMPORTANT FORMATTING RULES:
- Write rules as IMPERATIVE COMMANDS (Use X, Implement Y, Format Z)
- NO explanations, NO context, NO benefits - just the rule
- Maximum 1 line per rule
- Be specific about WHAT to do, not WHY to do it
- Focus on ACTIONABLE INSTRUCTIONS developers can immediately follow
- If no major changes exist, respond with: \"No AI instruction updates are needed. The changes are minor improvements that don't represent significant shifts in coding principles.\"
"""

[pipe.ai_instruction_update_parallel]
type = "PipeParallel"
definition = "Analyze changes for all AI instruction files in parallel"
inputs = { git_diff = "swe_diff.GitDiff", agents_content = "AgentsContent", claude_content = "ClaudeContent", cursor_rules_content = "CursorRulesContent" }
output = "AIInstructionParallelResults"
parallels = [
    { pipe = "analyze_agents_md_changes", result = "agents_analysis" },
    { pipe = "analyze_claude_md_changes", result = "claude_analysis" },
    { pipe = "analyze_cursor_rules_changes", result = "cursor_analysis" },
]
combined_output = "ai_instruction_update.AIInstructionParallelResults"

[pipe.ai_instruction_update]
type = "PipeSequence"
definition = "AI instruction update analysis with parallel file processing and formatting"
inputs = { git_diff = "swe_diff.GitDiff", agents_content = "AgentsContent", claude_content = "ClaudeContent", cursor_rules_content = "CursorRulesContent" }
output = "Text"
steps = [
    { pipe = "ai_instruction_update_parallel", result = "parallel_analyses" },
    { pipe = "combine_ai_instruction_analyses", result = "combined_suggestions" },
    { pipe = "format_ai_instruction_output", result = "ai_instruction_output" },
]

