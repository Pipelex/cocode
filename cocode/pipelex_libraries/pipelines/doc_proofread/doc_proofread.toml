domain = "doc_proofread"
definition = "Systematically proofread documentation against actual codebase to find inconsistencies using chunking"

[concept]
DocumentationFile = "A documentation file that needs to be proofread against the codebase"
FilePath = "A path to a file in the codebase"
RepositoryMap = "A repository map containing the codebase structure and file contents"
CodebaseFileContent = "Content of a codebase file"
DocumentationInconsistency = "An inconsistency found between documentation and actual code"
MarkdownReport = "A markdown report containing documentation inconsistencies formatted as a Cursor prompt"

[pipe]

[pipe.find_related_code_files]
type = "PipeLLM"
definition = "Find code files that implement or use elements mentioned in docs"
inputs = { doc_file = "DocumentationFile", repo_map = "RepositoryMap" }
output = "FilePath"
multiple_output = true
llm = "llm_for_large_text"
system_prompt = """
Extract code elements mentioned in docs (classes, functions, commands) and find their actual implementations or usages in the codebase.
"""
prompt_template = """
Find files that implement or use code elements from this documentation:

@doc_file

Available files in repo:
@repo_map

Only include files with actual code evidence, not just similar names or concepts.
"""

[pipe.proofread_single_doc]
type = "PipeLLM"
definition = "Find major inconsistencies between docs and code"
inputs = { doc_file = "DocumentationFile", related_files = "CodebaseFileContent" }
output = "DocumentationInconsistency"
multiple_output = true
llm = "llm_for_swe"
system_prompt = """
Find MAJOR inconsistencies between documentation and code that would cause user code to fail.
Only report issues that would completely break functionality or lead users down the wrong path.
"""
prompt_template = """
Find critical problems between these docs and code:

@doc_file.doc_content

CODE:
@related_files

Look for things that would BREAK user code, like:
- Completely wrong function/class signatures
- Required parameters marked as optional (or vice versa)
- Fundamentally incorrect examples
- Wrong import paths that would fail
- Critically wrong types that would crash

Skip anything that's not a showstopper. If it would just be confusing but still work, ignore it.
"""

[pipe.proofread_doc_sequence]
type = "PipeSequence"
definition = "Process a single documentation file to find inconsistencies"
inputs = { doc_file = "DocumentationFile", repo_map = "RepositoryMap" }
output = "DocumentationInconsistency"
steps = [
    { pipe = "find_related_code_files", result = "related_file_paths" },
    { pipe = "read_doc_file", result = "related_files" },
    { pipe = "proofread_single_doc", result = "inconsistencies" }
]

[pipe.create_cursor_report]
type = "PipeLLM"
definition = "Create a markdown report with inconsistencies formatted as a Cursor prompt"
inputs = { all_inconsistencies = "DocumentationInconsistency" }
output = "MarkdownReport"
llm = "llm_for_swe"
system_prompt = """
Create a concise markdown report for Cursor AI with specific, actionable fixes for documentation inconsistencies.
Focus only on critical issues that would break user code or cause major confusion.
"""
prompt_template = """
Create a markdown report for an AI agent to fix these documentation inconsistencies:

@all_inconsistencies

Start the report with a direct, conversational opening that conveys: "I found some documentation inconsistencies that need fixing" - but use natural, helpful language.

Then format each inconsistency with this exact structure:

**Doc file path:** [path to documentation file]

**Issue:** [description of the inconsistency]

**Related codebase files:** [list of related codebase files]

**Suggested fix:** [specific actionable fix]

---

Make it concise and focused on the most critical issues only.
"""

[pipe.doc_proofread]
type = "PipeSequence"
definition = "Complete documentation proofreading pipeline for CLI usage"
inputs = { repo_map = "RepositoryMap", doc_files = "DocumentationFile" }
output = "MarkdownReport"
steps = [
    { pipe = "proofread_doc_sequence", batch_over = "doc_files", batch_as = "doc_file", result = "all_inconsistencies" },
    { pipe = "create_cursor_report", result = "cursor_report" }
]

[pipe.read_doc_file]
type = "PipeFunc"
definition = "Read the content of related codebase files"
inputs = { related_file_paths = "FilePath" }
output = "CodebaseFileContent"
function_name = "read_file_content"

