"""
Repository analysis CLI commands.
"""

import asyncio
from typing import Annotated, List, Optional

import typer
from pipelex.pipe_run.pipe_run_mode import PipeRunMode

from cocode.common import PipeCode, get_output_dir, validate_repo_path
from cocode.repox.models import OutputStyle
from cocode.repox.process_python import PythonProcessingRule
from cocode.swe.swe_cmd import swe_from_repo

repo_app = typer.Typer(
    name="repo",
    help="Repository analysis and processing commands",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@repo_app.command("extract_fundamentals")
def repo_extract_fundamentals_cmd(
    repo_path: Annotated[
        str,
        typer.Argument(help="Repository path (local directory) or GitHub URL/identifier (owner/repo or https://github.com/owner/repo)"),
    ] = ".",
    output_dir: Annotated[
        Optional[str],
        typer.Option("--output-dir", "-o", help="Output directory path. Use 'stdout' to print to console. Defaults to config value if not provided"),
    ] = None,
    output_filename: Annotated[
        str,
        typer.Option("--output-filename", "-n", help="Output filename"),
    ] = "fundamentals.json",
    exclude_patterns: Annotated[
        Optional[List[str]],
        typer.Option("--exclude-pattern", "-i", help="List of patterns to ignore (in gitignore format)"),
    ] = None,
    python_processing_rule: Annotated[
        PythonProcessingRule,
        typer.Option("--python-rule", "-p", help="Python processing rule to apply", case_sensitive=False),
    ] = PythonProcessingRule.INTERFACE,
    output_style: Annotated[
        OutputStyle,
        typer.Option(
            "--output-style", "-s", help="One of: repo_map, flat (contents only), or import_list (for --python-rule imports)", case_sensitive=False
        ),
    ] = OutputStyle.REPO_MAP,
    include_patterns: Annotated[
        Optional[List[str]],
        typer.Option("--include-pattern", "-r", help="Optional pattern to filter files in the tree structure (glob pattern) - can be repeated"),
    ] = None,
    path_pattern: Annotated[
        Optional[str],
        typer.Option("--path-pattern", "-pp", help="Optional pattern to filter paths in the tree structure (regex pattern)"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry", help="Run pipeline in dry mode (no actual execution)"),
    ] = False,
) -> None:
    """Extract project fundamentals and architecture insights from repository. Supports both local repositories and GitHub repositories."""
    repo_path = validate_repo_path(repo_path)
    output_dir = get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"
    pipe_run_mode = PipeRunMode.DRY if dry_run else PipeRunMode.LIVE

    asyncio.run(
        swe_from_repo(
            pipe_code=PipeCode.EXTRACT_FUNDAMENTALS,
            repo_path=repo_path,
            exclude_patterns=exclude_patterns,
            include_patterns=include_patterns,
            path_pattern=path_pattern,
            python_processing_rule=python_processing_rule,
            output_style=output_style,
            output_filename=output_filename,
            output_dir=output_dir,
            to_stdout=to_stdout,
            pipe_run_mode=pipe_run_mode,
        )
    )
