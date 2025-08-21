from pipelex import log, pretty_print
from pipelex.core.stuffs.stuff_content import TextContent
from pipelex.pipeline.execute import PipeOutput
from pipelex.tools.misc.file_utils import ensure_path, save_text_to_path

from cocode.repox.repox_processor import RepoxException, RepoxProcessor


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
