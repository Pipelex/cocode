"""
Analyze management CLI commands.
"""

import asyncio
from typing import Annotated, List, Optional

import typer
from pipelex.hub import get_pipeline_tracker
from pipelex.pipe_run.pipe_run_params import PipeRunMode

from cocode.common import get_output_dir, validate_repo_path
from cocode.swe.swe_cmd import swe_from_repo_diff_with_prompt

analyze_app = typer.Typer(
    name="analyze",
    help="Analyze management and generation commands",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@analyze_app.command("diff")
def analyze_diff_cmd(
    prompt: Annotated[
        str,
        typer.Option("--prompt", "-p", help="Prompt to analyze the git diff"),
    ],
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
    ] = "analyze-diff.md",
    dry_run: Annotated[
        bool,
        typer.Option("--dry", help="Run pipeline in dry mode (no actual execution)"),
    ] = False,
    ignore_patterns: Annotated[
        Optional[List[str]],
        typer.Option(
            "--ignore-pattern", "-i", help="Patterns to exclude from git diff (e.g., '*.log', 'temp/', 'build/'). Can be specified multiple times."
        ),
    ] = None,
) -> None:
    """Generate analyze from git diff comparing current version to specified version. Supports both local repositories and GitHub repositories."""
    repo_path = validate_repo_path(repo_path)
    output_dir = get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"
    pipe_run_mode = PipeRunMode.DRY if dry_run else PipeRunMode.LIVE

    asyncio.run(
        swe_from_repo_diff_with_prompt(
            pipe_code="analyze_git_diff",
            prompt=prompt,
            repo_path=repo_path,
            version=version,
            output_filename=output_filename,
            output_dir=output_dir,
            to_stdout=to_stdout,
            pipe_run_mode=pipe_run_mode,
            ignore_patterns=ignore_patterns,
        )
    )
    get_pipeline_tracker().output_flowchart()
