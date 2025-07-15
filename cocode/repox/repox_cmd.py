from typing import Callable, Dict, List, Optional

from pipelex import log
from pipelex.tools.misc.file_utils import ensure_path, save_text_to_path

from cocode.repox.models import OutputStyle
from cocode.repox.process_python import PythonProcessingRule, python_imports_list, python_integral, python_interface
from cocode.repox.repox_processor import RepoxException, RepoxProcessor


def repox_command(
    repo_path: str,
    ignore_patterns: Optional[List[str]],
    include_patterns: Optional[List[str]],
    path_pattern: Optional[str],
    python_processing_rule: PythonProcessingRule,
    output_style: OutputStyle,
    output_filename: str,
    output_dir: str,
    to_stdout: bool,
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

    # Handle TREE output style separately - only output tree structure
    if output_style == OutputStyle.TREE:
        tree_structure = processor.get_tree_structure()
        repo_text = tree_structure
    else:
        repo_text = process_repox(repox_processor=processor)

    if to_stdout:
        print(repo_text)
    else:
        ensure_path(output_dir)
        output_file_path = f"{output_dir}/{output_filename}"
        save_text_to_path(text=repo_text, path=output_file_path)
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
