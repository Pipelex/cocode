"""
Software Engineering analysis CLI commands.
"""

import asyncio
from typing import Annotated, List, Optional

import typer
from pipelex.core.pipes.pipe_run_params import PipeRunMode
from pipelex.hub import get_pipeline_tracker

from cocode.common import PipeCode, get_output_dir, get_pipe_descriptions, validate_repo_path
from cocode.repox.models import OutputStyle
from cocode.repox.process_python import PythonProcessingRule

from .swe_cmd import (
    swe_ai_instruction_update_from_diff,
    swe_doc_proofread,
    swe_doc_update_from_diff,
    swe_from_file,
    swe_from_repo,
    swe_from_repo_diff,
)

swe_app = typer.Typer(
    name="swe",
    help="Software Engineering analysis and automation commands",
    add_completion=False,
    rich_markup_mode="rich",
)


@swe_app.command("from-repo")
def swe_from_repo_cmd(
    pipe_code: Annotated[
        PipeCode,
        typer.Argument(help=f"Pipeline code to execute for SWE analysis.\n\n{get_pipe_descriptions()}"),
    ] = PipeCode.EXTRACT_ONBOARDING_DOCUMENTATION,
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
    ] = "swe-analysis.txt",
    ignore_patterns: Annotated[
        Optional[List[str]],
        typer.Option("--ignore-pattern", "-i", help="List of patterns to ignore (in gitignore format)"),
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
    """Convert repository structure and contents to a text file with SWE analysis. Supports both local repositories and GitHub repositories."""
    repo_path = validate_repo_path(repo_path)
    output_dir = get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"
    pipe_run_mode = PipeRunMode.DRY if dry_run else PipeRunMode.LIVE

    asyncio.run(
        swe_from_repo(
            pipe_code=pipe_code,
            repo_path=repo_path,
            ignore_patterns=ignore_patterns,
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


@swe_app.command("from-file")
def swe_from_file_cmd(
    pipe_code: Annotated[
        PipeCode,
        typer.Argument(help=f"Pipeline code to execute for SWE analysis.\n\n{get_pipe_descriptions()}"),
    ],
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
    ] = "swe-analysis.txt",
    dry_run: Annotated[
        bool,
        typer.Option("--dry", help="Run pipeline in dry mode (no actual execution)"),
    ] = False,
) -> None:
    """Process SWE analysis from an existing text file."""
    output_dir = get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"
    pipe_run_mode = PipeRunMode.DRY if dry_run else PipeRunMode.LIVE

    asyncio.run(
        swe_from_file(
            pipe_code=pipe_code,
            input_file_path=input_file_path,
            output_filename=output_filename,
            output_dir=output_dir,
            to_stdout=to_stdout,
            pipe_run_mode=pipe_run_mode,
        )
    )


@swe_app.command("from-repo-diff")
def swe_from_repo_diff_cmd(
    pipe_code: Annotated[
        str,
        typer.Argument(help="Pipeline code to execute for SWE analysis"),
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
    ] = "swe-diff-analysis.md",
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
    """Process SWE analysis from git diff comparing current version to specified version. Supports both local repositories and GitHub repositories."""
    repo_path = validate_repo_path(repo_path)
    output_dir = get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"
    pipe_run_mode = PipeRunMode.DRY if dry_run else PipeRunMode.LIVE

    asyncio.run(
        swe_from_repo_diff(
            pipe_code=pipe_code,
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


@swe_app.command("doc-update")
def swe_doc_update_cmd(
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
    ignore_patterns: Annotated[
        Optional[List[str]],
        typer.Option(
            "--ignore-pattern", "-i", help="Patterns to exclude from git diff (e.g., '*.log', 'temp/', 'build/'). Can be specified multiple times."
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
            ignore_patterns=ignore_patterns,
        )
    )

    get_pipeline_tracker().output_flowchart()


@swe_app.command("ai-instruction-update")
def swe_ai_instruction_update_cmd(
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
    ignore_patterns: Annotated[
        Optional[List[str]],
        typer.Option(
            "--ignore-pattern", "-i", help="Patterns to exclude from git diff (e.g., '*.log', 'temp/', 'build/'). Can be specified multiple times."
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
            ignore_patterns=ignore_patterns,
        )
    )

    get_pipeline_tracker().output_flowchart()


@swe_app.command("doc-proofread")
def swe_doc_proofread_cmd(
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
    ignore_patterns: Annotated[
        Optional[List[str]],
        typer.Option("--ignore-pattern", "-i", help="Patterns to ignore in codebase analysis (gitignore format) - can be repeated"),
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
    if ignore_patterns is None:
        ignore_patterns = [
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
            ignore_patterns=ignore_patterns,
        )
    )

    get_pipeline_tracker().output_flowchart()
