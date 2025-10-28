"""
Changelog management CLI commands.
"""

import asyncio
from typing import Annotated, List, Optional

import typer
from pipelex.hub import get_pipeline_tracker
from pipelex.pipe_run.pipe_run_mode import PipeRunMode

from cocode.common import get_output_dir, validate_repo_path
from cocode.swe.swe_cmd import swe_from_repo_diff

changelog_app = typer.Typer(
    name="changelog",
    help="Changelog management and generation commands",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@changelog_app.command("update")
def changelog_update_cmd(
    version: Annotated[
        str,
        typer.Argument(help="Git version/tag/commit to compare current version against"),
    ],
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
    ] = "changelog-update.md",
    dry_run: Annotated[
        bool,
        typer.Option("--dry", help="Run pipeline in dry mode (no actual execution)"),
    ] = False,
    include_patterns: Annotated[
        Optional[List[str]],
        typer.Option(
            "--include-pattern",
            help="Patterns to include in git diff (e.g., '*.py', 'src/', 'docs/'). "
            "Can be specified multiple times. If not provided, includes all files.",
        ),
    ] = None,
    exclude_patterns: Annotated[
        Optional[List[str]],
        typer.Option(
            "--exclude-pattern", "-i", help="Patterns to exclude from git diff (e.g., '*.log', 'temp/', 'build/'). Can be specified multiple times."
        ),
    ] = None,
) -> None:
    """Generate changelog from git diff comparing current version to specified version. Supports both local repositories and GitHub repositories."""
    repo_path = validate_repo_path(repo_path)
    output_dir = get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"
    pipe_run_mode = PipeRunMode.DRY if dry_run else PipeRunMode.LIVE

    asyncio.run(
        swe_from_repo_diff(
            pipe_code="write_changelog_enhanced",
            repo_path=repo_path,
            version=version,
            output_filename=output_filename,
            output_dir=output_dir,
            to_stdout=to_stdout,
            pipe_run_mode=pipe_run_mode,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
    )
    get_pipeline_tracker().output_flowchart()
