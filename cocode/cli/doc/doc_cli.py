"""
Documentation management CLI commands.
"""

import asyncio
from typing import Annotated, List, Optional

import typer
from pipelex.hub import get_pipeline_tracker

from cocode.common import validate_repo_path
from cocode.swe.swe_cmd import swe_doc_proofread, swe_doc_update_from_diff

doc_app = typer.Typer(
    name="doc",
    help="Documentation management and automation commands",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@doc_app.command("update")
def doc_update_cmd(
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
    ] = "doc-update-suggestions.txt",
    exclude_patterns: Annotated[
        Optional[List[str]],
        typer.Option(
            "--exclude-pattern", "-i", help="Patterns to exclude from git diff (e.g., '*.log', 'temp/', 'build/'). Can be specified multiple times."
        ),
    ] = None,
    doc_dir: Annotated[
        Optional[str],
        typer.Option("--doc-dir", "-d", help="Directory containing documentation files (e.g., 'docs', 'documentation')"),
    ] = None,
) -> None:
    """
    Generate documentation update suggestions for docs/ directory based on git diff analysis.
    Supports both local repositories and GitHub repositories.
    """
    repo_path = validate_repo_path(repo_path)

    asyncio.run(
        swe_doc_update_from_diff(
            repo_path=repo_path,
            version=version,
            output_filename=output_filename,
            output_dir=output_dir,
            exclude_patterns=exclude_patterns,
        )
    )

    get_pipeline_tracker().output_flowchart()


@doc_app.command("proofread")
def doc_proofread_cmd(
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
    ] = "doc-proofread-report",
    doc_dir: Annotated[
        str,
        typer.Option("--doc-dir", "-d", help="Directory containing documentation files"),
    ] = "docs",
    include_patterns: Annotated[
        Optional[List[str]],
        typer.Option("--include-pattern", "-r", help="Patterns to include in codebase analysis (glob pattern) - can be repeated"),
    ] = None,
    exclude_patterns: Annotated[
        Optional[List[str]],
        typer.Option("--exclude-pattern", "-i", help="Patterns to ignore in codebase analysis (gitignore format) - can be repeated"),
    ] = None,
) -> None:
    """
    Systematically proofread documentation against actual codebase to find inconsistencies.
    Supports both local repositories and GitHub repositories.
    """
    repo_path = validate_repo_path(repo_path)

    # Set default include patterns to focus on documentation and code
    if include_patterns is None:
        include_patterns = ["*.md", "*.py", "*.toml", "*.yaml", "*.yml", "*.json", "*.sh", "*.js", "*.ts"]

    # Set default ignore patterns to exclude noise
    if exclude_patterns is None:
        exclude_patterns = [
            "__pycache__/",
            "*.pyc",
            ".git/",
            ".venv/",
            "node_modules/",
            "*.log",
            "build/",
            "dist/",
            ".pytest_cache/",
            "*.egg-info/",
        ]

    asyncio.run(
        swe_doc_proofread(
            repo_path=repo_path,
            doc_dir=doc_dir,
            output_filename=output_filename,
            output_dir=output_dir,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
    )

    get_pipeline_tracker().output_flowchart()
