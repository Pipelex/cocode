"""
CLI interface for cocode.
"""

import asyncio
from enum import StrEnum
from pathlib import Path
from typing import Annotated, List, Optional

import typer
from click import Command, Context
from pipelex import log
from pipelex.hub import get_pipeline_tracker
from pipelex.pipelex import Pipelex
from pipelex.tools.misc.file_utils import path_exists
from typer import Context as TyperContext
from typer.core import TyperGroup
from typing_extensions import override

from cocode.github.github_cli import github_app
from cocode.repox.models import OutputStyle
from cocode.repox.process_python import PythonProcessingRule
from cocode.repox.repox_cmd import repox_command
from cocode.repox.repox_processor import RESULTS_DIR
from cocode.swe.swe_cmd import (
    swe_ai_instruction_update_from_diff,
    swe_from_file,
    swe_from_repo,
    swe_from_repo_diff,
    swe_user_doc_update_from_diff,
)


class PipeCode(StrEnum):
    EXTRACT_ONBOARDING_DOCUMENTATION = "extract_onboarding_documentation"
    EXTRACT_FUNDAMENTALS = "extract_fundamentals"
    EXTRACT_ENVIRONMENT_BUILD = "extract_environment_build"
    EXTRACT_CODING_STANDARDS = "extract_coding_standards"
    EXTRACT_TEST_STRATEGY = "extract_test_strategy"
    EXTRACT_COLLABORATION = "extract_collaboration"
    USER_DOC_UPDATE = "user_doc_update"
    AI_INSTRUCTION_UPDATE = "ai_instruction_update"
    GENERATE_DOC_UPDATE_SUGGESTIONS = "generate_doc_update_suggestions"
    BATCH_ANALYZE_DOCUMENTATION_UPDATES = "batch_analyze_documentation_updates"


def _get_pipe_descriptions() -> str:
    """Generate help text with pipe descriptions from TOML."""
    descriptions = {
        "extract_onboarding_documentation": "Extract comprehensive onboarding documentation from software project docs",
        "extract_fundamentals": "Extract fundamental project information from documentation",
        "extract_environment_build": "Extract environment setup and build information from documentation",
        "extract_coding_standards": "Extract code quality and style information from documentation",
        "extract_test_strategy": "Extract testing strategy and procedures from documentation",
        "extract_collaboration": "Extract collaboration and workflow information from documentation",
        "user_doc_update": "Generate user documentation update suggestions for docs/ directory",
        "ai_instruction_update": "Generate AI instruction update suggestions for AGENTS.md, CLAUDE.md, cursor rules",
        "generate_doc_update_suggestions": "Generate comprehensive documentation update suggestions based on git diff",
        "batch_analyze_documentation_updates": "Analyze git diff and generate batched documentation update suggestions",
    }

    help_text = "\n\n"
    for code, description in descriptions.items():
        help_text += f"  • [bold cyan]{code}[/bold cyan]: {description}\n\n\n"

    return help_text


class CocodeCLI(TyperGroup):
    @override
    def get_command(self, ctx: Context, cmd_name: str) -> Optional[Command]:
        cmd = super().get_command(ctx, cmd_name)
        if cmd is None:
            typer.echo(f"Unknown command: {cmd_name}")
            typer.echo(ctx.get_help())
            ctx.exit(1)
        return cmd


app = typer.Typer(
    name="cocode",
    help="""
    🚀 CoCode - Repository Analysis and SWE Automation Tool
    
    Convert repository structure and contents to text files for analysis,
    and perform Software Engineering (SWE) analysis using AI pipelines.
    
    Use 'cocode help' for detailed usage examples and guides.
    """,
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
    invoke_without_command=True,
    cls=CocodeCLI,
)

# Add GitHub command group
app.add_typer(github_app, name="github", help="GitHub-related operations and utilities")


@app.callback(invoke_without_command=True)
def main(ctx: TyperContext) -> None:
    """Initialize Pipelex system before any command runs."""
    Pipelex.make(relative_config_folder_path="pipelex_libraries")

    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


def _validate_repo_path(repo_path: str) -> str:
    """Validate and convert repo_path to absolute path."""
    repo_path = str(Path(repo_path).resolve())

    if not path_exists(repo_path):
        log.error(f"[ERROR] Repo path '{repo_path}' does not exist")
        raise typer.Exit(code=1)

    return repo_path


def _get_output_dir(output_dir: Optional[str]) -> str:
    """Get output directory from parameter or config."""
    if output_dir is None:
        return RESULTS_DIR
    return output_dir


@app.command()
def repox(
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
) -> None:
    """Convert repository structure and contents to a text file."""
    repo_path = _validate_repo_path(repo_path)
    output_dir = _get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"

    repox_command(
        repo_path=repo_path,
        ignore_patterns=ignore_patterns,
        include_patterns=include_patterns,
        path_pattern=path_pattern,
        python_processing_rule=python_processing_rule,
        output_style=output_style,
        output_filename=output_filename,
        output_dir=output_dir,
        to_stdout=to_stdout,
    )


@app.command("swe-from-repo")
def swe_from_repo_cmd(
    pipe_code: Annotated[
        PipeCode,
        typer.Argument(help=f"Pipeline code to execute for SWE analysis.\n\n{_get_pipe_descriptions()}"),
    ] = PipeCode.EXTRACT_ONBOARDING_DOCUMENTATION,
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
    """Convert repository structure and contents to a text file with SWE analysis."""
    repo_path = _validate_repo_path(repo_path)
    output_dir = _get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"

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
            dry_run=dry_run,
        )
    )


@app.command("swe-from-file")
def swe_from_file_cmd(
    pipe_code: Annotated[
        str,
        typer.Argument(help="Pipeline code to execute for SWE analysis"),
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
    output_dir = _get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"

    asyncio.run(
        swe_from_file(
            pipe_code=pipe_code,
            input_file_path=input_file_path,
            output_filename=output_filename,
            output_dir=output_dir,
            to_stdout=to_stdout,
            dry_run=dry_run,
        )
    )


@app.command("swe-from-repo-diff")
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
        typer.Argument(help="Input directory path", exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    ] = ".",
    output_dir: Annotated[
        Optional[str],
        typer.Option("--output-dir", "-o", help="Output directory path. Use 'stdout' to print to console. Defaults to config value if not provided"),
    ] = None,
    output_filename: Annotated[
        str,
        typer.Option("--output-filename", "-n", help="Output filename"),
    ] = "swe-diff-analysis.txt",
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
    """Process SWE analysis from git diff comparing current version to specified version."""
    repo_path = _validate_repo_path(repo_path)
    output_dir = _get_output_dir(output_dir)
    to_stdout = output_dir == "stdout"

    asyncio.run(
        swe_from_repo_diff(
            pipe_code=pipe_code,
            repo_path=repo_path,
            version=version,
            output_filename=output_filename,
            output_dir=output_dir,
            to_stdout=to_stdout,
            dry_run=dry_run,
            ignore_patterns=ignore_patterns,
        )
    )
    get_pipeline_tracker().output_flowchart()





@app.command("swe-user-doc-update")
def swe_user_doc_update_cmd(
    version: Annotated[
        str,
        typer.Argument(help="Git version/tag/commit to compare current version against"),
    ],
    repo_path: Annotated[
        str,
        typer.Argument(help="Input directory path", exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    ] = ".",
    output_dir: Annotated[
        str,
        typer.Option("--output-dir", "-o", help="Output directory path"),
    ] = "results",
    output_filename: Annotated[
        str,
        typer.Option("--output-filename", "-n", help="Output filename"),
    ] = "user-doc-update-suggestions.txt",
    doc_dir: Annotated[
        Optional[str],
        typer.Option("--doc-dir", "-d", help="Directory containing documentation files (e.g., 'docs', 'documentation')"),
    ] = None,
) -> None:
    """Generate user documentation update suggestions for docs/ directory based on git diff analysis."""
    repo_path = _validate_repo_path(repo_path)

    asyncio.run(
        swe_user_doc_update_from_diff(
            repo_path=repo_path,
            version=version,
            output_filename=output_filename,
            output_dir=output_dir,
            doc_dir=doc_dir,
        )
    )

    get_pipeline_tracker().output_flowchart()


@app.command("swe-ai-instruction-update")
def swe_ai_instruction_update_cmd(
    version: Annotated[
        str,
        typer.Argument(help="Git version/tag/commit to compare current version against"),
    ],
    repo_path: Annotated[
        str,
        typer.Argument(help="Input directory path", exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    ] = ".",
    output_dir: Annotated[
        str,
        typer.Option("--output-dir", "-o", help="Output directory path"),
    ] = "results",
    output_filename: Annotated[
        str,
        typer.Option("--output-filename", "-n", help="Output filename"),
    ] = "ai-instruction-update-suggestions.txt",
    doc_dir: Annotated[
        Optional[str],
        typer.Option("--doc-dir", "-d", help="Directory containing documentation files (e.g., 'docs', 'documentation')"),
    ] = None,
) -> None:
    """Generate AI instruction update suggestions for AGENTS.md, CLAUDE.md, and cursor rules based on git diff analysis."""
    repo_path = _validate_repo_path(repo_path)

    asyncio.run(
        swe_ai_instruction_update_from_diff(
            repo_path=repo_path,
            version=version,
            output_filename=output_filename,
            output_dir=output_dir,
            doc_dir=doc_dir,
        )
    )

    get_pipeline_tracker().output_flowchart()


if __name__ == "__main__":
    app()
