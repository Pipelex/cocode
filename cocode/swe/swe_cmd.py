from datetime import datetime
from typing import Callable, Dict, List, Optional

from pipelex import log, pretty_print
from pipelex.core.concept_native import NativeConcept
from pipelex.core.pipe_run_params import PipeRunMode
from pipelex.core.stuff import Stuff
from pipelex.core.stuff_content import ListContent
from pipelex.core.stuff_factory import StuffFactory
from pipelex.core.working_memory_factory import WorkingMemoryFactory
from pipelex.hub import get_concept_provider, get_report_delegate
from pipelex.pipeline.execute import execute_pipeline
from pipelex.tools.misc.file_utils import ensure_path, save_text_to_path
from pipelex.tools.misc.json_utils import save_as_json_to_path

from cocode.repox.models import OutputStyle
from cocode.repox.process_python import PythonProcessingRule, python_imports_list, python_integral, python_interface
from cocode.repox.repox_processor import RepoxException, RepoxProcessor
from cocode.utils import run_git_diff_command


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
    dry_run: bool,
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
    repo_text = process_repox(repox_processor=processor)

    # Process through SWE pipeline and handle output
    await process_swe_pipeline(
        text=repo_text,
        pipe_code=pipe_code,
        dry_run=dry_run,
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
    dry_run: bool,
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

    # Process through SWE pipeline and handle output
    await process_swe_pipeline(
        text=text,
        pipe_code=pipe_code,
        dry_run=dry_run,
        output_filename=output_filename,
        output_dir=output_dir,
        to_stdout=to_stdout,
    )


async def process_swe_pipeline(
    text: str,
    pipe_code: str,
    dry_run: bool,
    output_filename: str,
    output_dir: str,
    to_stdout: bool,
    variable_name: str = "repo_text",
) -> None:
    """Common function to process text through SWE pipeline and handle output."""
    # Interpret the dry_run flag to determine pipe_run_mode
    pipe_run_mode = PipeRunMode.DRY if dry_run else PipeRunMode.LIVE
    swe_stuff = await process_swe(text=text, pipe_code=pipe_code, pipe_run_mode=pipe_run_mode, variable_name=variable_name)

    if to_stdout:
        print(swe_stuff)
    else:
        ensure_path(output_dir)
        output_file_path = f"{output_dir}/{output_filename}"
        if get_concept_provider().is_compatible_by_concept_code(
            tested_concept_code=swe_stuff.concept_code,
            wanted_concept_code=NativeConcept.TEXT.code,
        ) and not isinstance(swe_stuff.content, ListContent):
            save_text_to_path(text=swe_stuff.as_str, path=output_file_path)
        else:
            save_as_json_to_path(object_to_save=swe_stuff, path=output_file_path)
        log.info(f"Done, output saved as text to file: '{output_file_path}'")


def process_repox(
    repox_processor: RepoxProcessor,
    nb_padding_lines: int = 2,
) -> str:
    """Save repository structure and contents to a text file."""

    tree_structure: str = repox_processor.get_tree_structure()
    if not tree_structure.strip():
        log.error(f"No tree structure found for path: {repox_processor.repo_path}")
        raise RepoxException(f"No tree structure found for path: {repox_processor.repo_path}")
    log.verbose(f"Final tree structure to be written: {tree_structure}")

    file_contents = repox_processor.process_file_contents()

    output_content = repox_processor.build_output_content(
        tree_structure=tree_structure,
        file_contents=file_contents,
    )

    output_content = "\n" * nb_padding_lines + output_content
    output_content = output_content + "\n" * nb_padding_lines
    return output_content


async def process_swe(text: str, pipe_code: str, pipe_run_mode: PipeRunMode, variable_name: str = "text") -> Stuff:
    # Load the working memory with the text
    release_stuff = StuffFactory.make_from_str(str_value=f"{datetime.now().strftime('%Y-%m-%d')}", name="release_date")
    text_stuff = StuffFactory.make_from_str(str_value=text, name=variable_name)
    working_memory = WorkingMemoryFactory.make_from_multiple_stuffs(stuff_list=[release_stuff, text_stuff])
    # Run the pipe
    pipe_output = await execute_pipeline(
        pipe_code=pipe_code,
        working_memory=working_memory,
        pipe_run_mode=pipe_run_mode,
    )
    pretty_print(pipe_output, title="Pipe output")
    swe_stuff = pipe_output.main_stuff

    get_report_delegate().generate_report()

    return swe_stuff


async def swe_from_repo_diff(
    pipe_code: str,
    repo_path: str,
    version: str,
    output_filename: str,
    output_dir: str,
    to_stdout: bool,
    dry_run: bool,
    ignore_patterns: Optional[List[str]] = None,
) -> None:
    """Process SWE analysis from a git diff comparing current version to specified version."""
    log.info(f"Processing SWE from git diff: comparing current to '{version}' in '{repo_path}'")

    # Generate git diff
    diff_text = run_git_diff_command(repo_path=repo_path, version=version, ignore_patterns=ignore_patterns)

    # Process through SWE pipeline and handle output
    await process_swe_pipeline(
        text=diff_text,
        pipe_code=pipe_code,
        dry_run=dry_run,
        output_filename=output_filename,
        output_dir=output_dir,
        to_stdout=to_stdout,
        variable_name="text",
    )
