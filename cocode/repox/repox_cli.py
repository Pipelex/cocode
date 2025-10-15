"""
Repository processing CLI commands.
"""

from typing import Annotated, List, Optional

import typer

from cocode.common import get_output_dir, validate_repo_path

from .models import OutputStyle
from .process_python import PythonProcessingRule
from .repox_cmd import repox_command

repox_app = typer.Typer(
    name="repox",
    help="Repository processing and analysis commands",
    add_completion=False,
    rich_markup_mode="rich",
)


@repox_app.command("convert")
def repox_convert(
    repo_path: Annotated[
        str,
        typer.Argument(help="Input directory path", exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    ] = ".",
    output_dir: Annotated[
        Optional[str],
        typer.Option("--output-dir", "-o", help="Output directory path. Use 'stdout' to print to console. Defaults to config value if not provided"),
    ] = None,
    output_filename: Annotated[
        str,
        typer.Option("--output-filename", "-n", help="Output filename"),
    ] = "repo-to-text.txt",
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
) -> None:
    """Convert repository structure and contents to a text file."""
    repo_path = validate_repo_path(repo_path)
    output_dir = get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"

    repox_command(
        repo_path=repo_path,
        exclude_patterns=exclude_patterns,
        include_patterns=include_patterns,
        path_pattern=path_pattern,
        python_processing_rule=python_processing_rule,
        output_style=output_style,
        output_filename=output_filename,
        output_dir=output_dir,
        to_stdout=to_stdout,
    )


# Keep the original command name for backward compatibility
@repox_app.command("repo")
def repox_repo(
    repo_path: Annotated[
        str,
        typer.Argument(help="Input directory path", exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    ] = ".",
    output_dir: Annotated[
        Optional[str],
        typer.Option("--output-dir", "-o", help="Output directory path. Use 'stdout' to print to console. Defaults to config value if not provided"),
    ] = None,
    output_filename: Annotated[
        str,
        typer.Option("--output-filename", "-n", help="Output filename"),
    ] = "repo-to-text.txt",
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
) -> None:
    """Convert repository structure and contents to a text file."""
    repox_convert(
        repo_path=repo_path,
        output_dir=output_dir,
        output_filename=output_filename,
        exclude_patterns=exclude_patterns,
        python_processing_rule=python_processing_rule,
        output_style=output_style,
        include_patterns=include_patterns,
        path_pattern=path_pattern,
    )
