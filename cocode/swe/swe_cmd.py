import json
import os
from typing import Any, Callable, Dict, List, Optional, cast

from pipelex import log, pretty_print
from pipelex.core.pipe_run_params import PipeRunMode
from pipelex.core.stuff_content import ListContent
from pipelex.core.stuff_factory import StuffFactory
from pipelex.core.working_memory_factory import WorkingMemoryFactory
from pipelex.hub import get_report_delegate
from pipelex.pipeline.execute import PipeOutput, execute_pipeline
from pipelex.tools.misc.file_utils import ensure_path, save_text_to_path

from cocode.pipelex_libraries.pipelines.doc_proofread.doc_proofread_models import DocumentationFile, DocumentationInconsistency, RepositoryMap
from cocode.pipelex_libraries.pipelines.doc_proofread.file_utils import create_documentation_files_from_paths
from cocode.repox.models import OutputStyle
from cocode.repox.process_python import PythonProcessingRule, python_imports_list, python_integral, python_interface
from cocode.repox.repox_processor import RepoxProcessor
from cocode.swe.swe_utils import get_repo_text_for_swe, process_swe_pipeline_result
from cocode.utils import NoDifferencesFound, run_git_diff_command


async def swe_from_repo(
    pipe_code: str,
    repo_path: str,
    ignore_patterns: Optional[List[str]],
    include_patterns: Optional[List[str]],
    path_pattern: Optional[str],
    python_processing_rule: PythonProcessingRule,
    output_style: OutputStyle,
    output_filename: str,
    output_dir: str,
    to_stdout: bool,
    pipe_run_mode: PipeRunMode,
) -> None:
    text_processing_funcs: Dict[str, Callable[[str], str]] = {}
    match python_processing_rule:
        case PythonProcessingRule.INTEGRAL:
            text_processing_funcs["text/x-python"] = python_integral
        case PythonProcessingRule.INTERFACE:
            text_processing_funcs["text/x-python"] = python_interface
        case PythonProcessingRule.IMPORTS:
            text_processing_funcs["text/x-python"] = python_imports_list

    log.info(f"generate_repox processing: '{repo_path}' with output style: '{output_style}'")
    processor = RepoxProcessor(
        repo_path=repo_path,
        ignore_patterns=ignore_patterns,
        include_patterns=include_patterns,
        path_pattern=path_pattern,
        text_processing_funcs=text_processing_funcs,
        output_style=output_style,
    )
    repo_text = get_repo_text_for_swe(repox_processor=processor)

    # Load the working memory with the text
    repo_text_stuff = StuffFactory.make_from_str(str_value=repo_text, name="repo_text", concept_str="swe.RepoText")
    working_memory = WorkingMemoryFactory.make_from_single_stuff(stuff=repo_text_stuff)

    # Run the pipe
    pipe_output = await execute_pipeline(
        pipe_code=pipe_code,
        working_memory=working_memory,
        pipe_run_mode=pipe_run_mode,
    )

    get_report_delegate().generate_report()

    #  handle output
    await process_swe_pipeline_result(
        pipe_output=pipe_output,
        output_filename=output_filename,
        output_dir=output_dir,
        to_stdout=to_stdout,
    )


async def swe_from_file(
    pipe_code: str,
    input_file_path: str,
    output_filename: str,
    output_dir: str,
    to_stdout: bool,
    pipe_run_mode: PipeRunMode,
) -> None:
    """Process SWE analysis from an existing text file instead of building from repository."""
    log.info(f"Processing SWE from file: '{input_file_path}'")

    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            text = file.read()
    except FileNotFoundError:
        log.error(f"Input file not found: '{input_file_path}'")
        raise
    except Exception as e:
        log.error(f"Error reading input file '{input_file_path}': {e}")
        raise

    # Load the working memory with the text
    text_stuff = StuffFactory.make_from_str(str_value=text, name="text", concept_str="swe.RepoText")
    working_memory = WorkingMemoryFactory.make_from_single_stuff(stuff=text_stuff)

    # Run the pipe
    pipe_output = await execute_pipeline(
        pipe_code=pipe_code,
        working_memory=working_memory,
        pipe_run_mode=pipe_run_mode,
    )

    get_report_delegate().generate_report()

    # Process through SWE pipeline and handle output
    await process_swe_pipeline_result(
        pipe_output=pipe_output,
        output_filename=output_filename,
        output_dir=output_dir,
        to_stdout=to_stdout,
    )


async def swe_from_repo_diff(
    pipe_code: str,
    repo_path: str,
    version: str,
    output_filename: str,
    output_dir: str,
    to_stdout: bool,
    pipe_run_mode: PipeRunMode,
    ignore_patterns: Optional[List[str]] = None,
) -> None:
    """Process SWE analysis from a git diff comparing current version to specified version."""
    log.info(f"Processing SWE from git diff: comparing current to '{version}' in '{repo_path}'")

    # Generate git diff
    try:
        code_diff = run_git_diff_command(repo_path=repo_path, version=version, ignore_patterns=ignore_patterns)
    except NoDifferencesFound as exc:
        log.info(f"Aborting: {exc}")
        return

    # print(code_diff)
    # return

    # Load the working memory with the text
    code_diff_stuff = StuffFactory.make_from_str(str_value=code_diff, name="code_diff", concept_str="swe.CodeDiff")
    working_memory = WorkingMemoryFactory.make_from_single_stuff(stuff=code_diff_stuff)

    # Run the pipe
    pipe_output = await execute_pipeline(
        pipe_code=pipe_code,
        working_memory=working_memory,
        pipe_run_mode=pipe_run_mode,
    )

    get_report_delegate().generate_report()

    # Process through SWE pipeline and handle output
    await process_swe_pipeline_result(
        pipe_output=pipe_output,
        output_filename=output_filename,
        output_dir=output_dir,
        to_stdout=to_stdout,
    )


async def swe_doc_update_from_diff(
    repo_path: str,
    version: str,
    output_filename: str,
    output_dir: str,
    ignore_patterns: Optional[List[str]] = None,
    doc_dir: Optional[str] = None,
) -> None:
    """Generate documentation update suggestions for docs/ directory based on git diff analysis."""
    log.info(f"Generating documentation update suggestions from git diff: comparing current to '{version}' in '{repo_path}'")

    # Generate git diff
    diff_text = run_git_diff_command(repo_path=repo_path, version=version, ignore_patterns=ignore_patterns)

    git_diff_stuff = StuffFactory.make_from_str(str_value=diff_text, name="git_diff")

    working_memory = WorkingMemoryFactory.make_from_multiple_stuffs(stuff_list=[git_diff_stuff])

    pipe_output = await execute_pipeline(
        pipe_code="doc_update",
        working_memory=working_memory,
    )
    formatted_output = pipe_output.main_stuff_as_str

    get_report_delegate().generate_report()

    ensure_path(output_dir)
    output_file_path = f"{output_dir}/{output_filename}"
    save_text_to_path(text=formatted_output, path=output_file_path)
    log.info(f"Done, documentation update suggestions saved to file: '{output_file_path}'")


async def swe_ai_instruction_update_from_diff(
    repo_path: str,
    version: str,
    output_filename: str,
    output_dir: str,
    ignore_patterns: Optional[List[str]] = None,
    doc_dir: Optional[str] = None,
) -> None:
    """Generate AI instruction update suggestions for AGENTS.md, CLAUDE.md, and cursor rules based on git diff analysis."""
    log.info(f"Generating AI instruction update suggestions from git diff: comparing current to '{version}' in '{repo_path}'")

    diff_text = run_git_diff_command(repo_path=repo_path, version=version, ignore_patterns=ignore_patterns)

    def read_file_content(file_path: str) -> str:
        """Read file content, return empty string if file doesn't exist."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""
        except Exception as e:
            log.warning(f"Error reading file {file_path}: {e}")
            return ""

    # Read AGENTS.md content
    agents_md_path = os.path.join(repo_path, "AGENTS.md")
    agents_content = read_file_content(agents_md_path)

    # Read CLAUDE.md content
    claude_md_path = os.path.join(repo_path, "CLAUDE.md")
    claude_content = read_file_content(claude_md_path)

    # Read cursor rules content (check two possible patterns)
    cursor_rules_content = ""
    # Pattern 1: Single .cursorrules file
    cursorrules_path = os.path.join(repo_path, ".cursorrules")
    if os.path.exists(cursorrules_path) and os.path.isfile(cursorrules_path):
        content = read_file_content(cursorrules_path)
        if content:
            cursor_rules_content = content

    # Pattern 2: Multiple .md files in .cursor/rules/ directory
    elif os.path.exists(os.path.join(repo_path, ".cursor/rules")) and os.path.isdir(os.path.join(repo_path, ".cursor/rules")):
        cursor_rules_dir = os.path.join(repo_path, ".cursor/rules")
        try:
            # Get all .md files in the directory and sort them for consistent ordering
            md_files: List[str] = []
            for file in os.listdir(cursor_rules_dir):
                if file.endswith(".mdc"):
                    md_files.append(file)

            # Sort files for consistent ordering
            md_files.sort()

            # Concatenate all .md files
            for file in md_files:
                file_path = os.path.join(cursor_rules_dir, file)
                content = read_file_content(file_path)
                if content:
                    cursor_rules_content += f"=== {file} ===\n{content}\n\n"
        except Exception as e:
            log.warning(f"Error reading cursor rules directory {cursor_rules_dir}: {e}")

    # Create working memory with git diff and AI instruction file contents
    git_diff_stuff = StuffFactory.make_from_str(str_value=diff_text, name="git_diff")
    agents_content_stuff = StuffFactory.make_from_str(str_value=agents_content, name="agents_content")
    claude_content_stuff = StuffFactory.make_from_str(str_value=claude_content, name="claude_content")
    cursor_rules_content_stuff = StuffFactory.make_from_str(str_value=cursor_rules_content, name="cursor_rules_content")

    working_memory = WorkingMemoryFactory.make_from_multiple_stuffs(
        stuff_list=[git_diff_stuff, agents_content_stuff, claude_content_stuff, cursor_rules_content_stuff]
    )

    pipe_output = await execute_pipeline(
        pipe_code="ai_instruction_update",
        working_memory=working_memory,
    )

    pretty_print(pipe_output, title="AI Instruction Update Analysis")
    formatted_output = pipe_output.main_stuff

    get_report_delegate().generate_report()

    # Always output to file as text
    ensure_path(output_dir)
    output_file_path = f"{output_dir}/{output_filename}"

    # The output is already formatted by the LLM in the pipeline
    text_content = formatted_output.as_str

    save_text_to_path(text=text_content, path=output_file_path)
    log.info(f"Done, AI instruction update suggestions saved to file: '{output_file_path}'")


async def swe_doc_proofread(
    repo_path: str,
    doc_dir: str,
    output_filename: str,
    output_dir: str,
    ignore_patterns: Optional[List[str]] = None,
    include_patterns: Optional[List[str]] = None,
    to_stdout: bool = False,
) -> PipeOutput:
    """Proofread documentation against codebase using CLI approach with RepoxProcessor."""
    log.info(f"Proofreading documentation in '{repo_path}' using CLI approach")

    # Create processor to get repo map
    processor = RepoxProcessor(
        repo_path=repo_path,
        ignore_patterns=ignore_patterns,
        include_patterns=include_patterns,
        output_style=OutputStyle.REPO_MAP,
    )
    repo_text = get_repo_text_for_swe(repox_processor=processor)

    # Get documentation files from the specified doc_dir
    doc_file_paths: List[str] = []
    doc_dir_path = os.path.join(repo_path, doc_dir)
    if os.path.exists(doc_dir_path):
        for root, _, files in os.walk(doc_dir_path):
            for file in files:
                if file.endswith(".md") and "CHANGELOG" not in file:
                    doc_file_paths.append(os.path.join(root, file))

    # Also include README.md from the root if it exists
    readme_path = os.path.join(repo_path, "README.md")
    if os.path.exists(readme_path):
        doc_file_paths.append(readme_path)

    if not doc_file_paths:
        log.warning(f"No documentation files found in {doc_dir_path}")
        raise ValueError(f"No documentation files found in {doc_dir_path}")

    doc_files = create_documentation_files_from_paths(doc_file_paths, doc_dir)

    repo_map_stuff = StuffFactory.make_stuff(
        concept_str="doc_proofread.RepositoryMap", content=RepositoryMap(repo_content=repo_text), name="repo_map"
    )
    doc_files_stuff = StuffFactory.make_stuff(
        concept_str="doc_proofread.DocumentationFile", content=ListContent[DocumentationFile](items=doc_files), name="doc_files"
    )

    working_memory = WorkingMemoryFactory.make_from_multiple_stuffs(stuff_list=[repo_map_stuff, doc_files_stuff])

    pipe_output = await execute_pipeline(
        pipe_code="doc_proofread",
        working_memory=working_memory,
    )

    main_stuff = pipe_output.working_memory.get_stuff("all_inconsistencies")
    main_stuff_content = cast(ListContent[ListContent[DocumentationInconsistency]], main_stuff.content)

    all_inconsistencies: List[DocumentationInconsistency] = []
    for inner_list in main_stuff_content.items:
        for inconsistency in inner_list.items:
            all_inconsistencies.append(inconsistency)

    pretty_print(all_inconsistencies, title="All inconsistencies")

    inconsistencies_data: List[Dict[str, Any]] = []
    for inconsistency in all_inconsistencies:
        inconsistencies_data.append(
            {
                "doc_file_path": inconsistency.doc_file_path,
                "related_files": inconsistency.related_files,
                "issue_description": inconsistency.issue_description,
                "doc_content": inconsistency.doc_content,
                "actual_code": inconsistency.actual_code,
            }
        )

    json_output = json.dumps(inconsistencies_data, indent=2, ensure_ascii=False)

    ensure_path(output_dir)
    output_file_path = f"{output_dir}/{output_filename}.json"
    save_text_to_path(text=json_output, path=output_file_path)
    log.info(f"Done, output saved as JSON to file: '{output_file_path}'")

    report = pipe_output.main_stuff_as_str
    save_text_to_path(text=report, path=f"{output_dir}/{output_filename}.md")

    return pipe_output
