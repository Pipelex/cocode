"""
Feature analysis CLI commands.
"""

import asyncio
from typing import Annotated, Optional

import typer
from pipelex.pipe_run.pipe_run_mode import PipeRunMode

from cocode.common import PipeCode, get_output_dir
from cocode.swe.swe_cmd import swe_from_file

features_app = typer.Typer(
    name="features",
    help="Feature analysis and extraction commands",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@features_app.command("extract")
def features_extract_cmd(
    input_file_path: Annotated[
        str,
        typer.Argument(help="Input text file path", exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    ],
    output_dir: Annotated[
        Optional[str],
        typer.Option("--output-dir", "-o", help="Output directory path. Use 'stdout' to print to console. Defaults to config value if not provided"),
    ] = None,
    output_filename: Annotated[
        str,
        typer.Option("--output-filename", "-n", help="Output filename"),
    ] = "features.md",
    dry_run: Annotated[
        bool,
        typer.Option("--dry", help="Run pipeline in dry mode (no actual execution)"),
    ] = False,
) -> None:
    """Extract and document features from analysis text file."""
    output_dir = get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"
    pipe_run_mode = PipeRunMode.DRY if dry_run else PipeRunMode.LIVE

    asyncio.run(
        swe_from_file(
            pipe_code=PipeCode.EXTRACT_FEATURES_RECAP,
            input_file_path=input_file_path,
            output_filename=output_filename,
            output_dir=output_dir,
            to_stdout=to_stdout,
            pipe_run_mode=pipe_run_mode,
        )
    )
