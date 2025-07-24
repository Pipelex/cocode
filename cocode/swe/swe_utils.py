import json
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, cast

from pipelex import log, pretty_print
from pipelex.core.pipe_run_params import PipeRunMode
from pipelex.core.stuff_content import ListContent, TextContent
from pipelex.core.stuff_factory import StuffFactory
from pipelex.core.working_memory_factory import WorkingMemoryFactory
from pipelex.hub import get_concept_provider, get_report_delegate
from pipelex.pipeline.execute import PipeOutput, execute_pipeline
from pipelex.tools.misc.file_utils import ensure_path, save_text_to_path

from cocode.pipelex_libraries.pipelines.doc_proofread.doc_proofread_models import DocumentationFile, DocumentationInconsistency, RepositoryMap
from cocode.pipelex_libraries.pipelines.doc_proofread.file_utils import create_documentation_files_from_paths
from cocode.repox.models import OutputStyle
from cocode.repox.process_python import PythonProcessingRule, python_imports_list, python_integral, python_interface
from cocode.repox.repox_processor import RepoxException, RepoxProcessor
from cocode.utils import NoDifferencesFound, run_git_diff_command


def get_repo_text_for_swe(
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


async def process_swe_pipeline_result(
    pipe_output: PipeOutput,
    output_filename: str,
    output_dir: str,
    to_stdout: bool,
) -> None:
    """Common function to process text through SWE pipeline and handle output."""
    pretty_print(pipe_output, title="Pipe output")
    swe_stuff = pipe_output.main_stuff

    if to_stdout:
        if isinstance(swe_stuff.content, TextContent):
            print(swe_stuff.as_str)
        else:
            print(swe_stuff)
    else:
        ensure_path(output_dir)
        output_file_path = f"{output_dir}/{output_filename}"
        if isinstance(swe_stuff.content, TextContent):
            save_text_to_path(text=swe_stuff.as_str, path=output_file_path)
        else:
            save_text_to_path(text=str(swe_stuff), path=output_file_path)
        log.info(f"Done, output saved as text to file: '{output_file_path}'")
