"""
AI instructions management CLI commands.
"""

import asyncio
from typing import Annotated, List, Optional

import typer
from pipelex.hub import get_pipeline_tracker

from cocode.common import validate_repo_path
from cocode.swe.swe_cmd import swe_ai_instruction_update_from_diff

ai_instructions_app = typer.Typer(
    name="ai_instructions",
    help="AI instructions management and update commands",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@ai_instructions_app.command("update")
def ai_instructions_update_cmd(
    version: Annotated[
        str,
        typer.Argument(help="Git version/tag/commit to compare current version against"),
    ],
    repo_path: Annotated[
        str,
        typer.Argument(help="Repository path (local directory) or GitHub URL/identifier (owner/repo or https://github.com/owner/repo)"),
    ] = ".",
    output_dir: Annotated[
        str,
        typer.Option("--output-dir", "-o", help="Output directory path"),
    ] = "results",
    output_filename: Annotated[
        str,
        typer.Option("--output-filename", "-n", help="Output filename"),
    ] = "ai-instruction-update-suggestions.txt",
    exclude_patterns: Annotated[
        Optional[List[str]],
        typer.Option(
            "--exclude-pattern", "-i", help="Patterns to exclude from git diff (e.g., '*.log', 'temp/', 'build/'). Can be specified multiple times."
        ),
    ] = None,
) -> None:
    """
    Generate AI instruction update suggestions for AGENTS.md, CLAUDE.md, and cursor rules based on git diff analysis.
    Supports both local repositories and GitHub repositories.
    """
    repo_path = validate_repo_path(repo_path)

    asyncio.run(
        swe_ai_instruction_update_from_diff(
            repo_path=repo_path,
            version=version,
            output_filename=output_filename,
            output_dir=output_dir,
            exclude_patterns=exclude_patterns,
        )
    )

    get_pipeline_tracker().output_flowchart()
