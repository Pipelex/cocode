"""
CLI interface for cocode.
"""

from typing import Optional

import typer
from click import Command, Context
from pipelex.pipelex import Pipelex
from typer import Context as TyperContext
from typer.core import TyperGroup
from typing_extensions import override

from cocode.cli.ai_instructions.ai_instructions_cli import ai_instructions_app
from cocode.cli.analyze.analyze_cli import analyze_app
from cocode.cli.changelog.changelog_cli import changelog_app
from cocode.cli.doc.doc_cli import doc_app
from cocode.cli.features.features_cli import features_app
from cocode.cli.repo.repo_cli import repo_app
from cocode.github.github_cli import github_app
from cocode.repox.repox_cli import repox_app
from cocode.validation_cli import validation_app


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
    🚀 CoCode - Repository Analysis and SWE Automation Tool.
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

# Add command groups
app.add_typer(doc_app, name="doc", help="Documentation management and automation commands")
app.add_typer(analyze_app, name="analyze", help="Analyze generation and management commands")
app.add_typer(changelog_app, name="changelog", help="Changelog generation and management commands")
app.add_typer(ai_instructions_app, name="ai_instructions", help="AI instructions update and management commands")
app.add_typer(repo_app, name="repo", help="Repository analysis and processing commands")
app.add_typer(features_app, name="features", help="Feature analysis and extraction commands")
app.add_typer(repox_app, name="repox", help="Repository processing and analysis commands")
app.add_typer(validation_app, name="validation", help="Pipeline validation and setup commands")
app.add_typer(github_app, name="github", help="GitHub-related operations and utilities")


@app.callback(invoke_without_command=True)
def main(ctx: TyperContext) -> None:
    """Initialize Pipelex system before any command runs."""
    Pipelex.make()

    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


# Keep the original validate command for backward compatibility
@app.command()
def validate() -> None:
    """Run the setup sequence. (Deprecated: use 'cocode validation validate' instead)"""
    from cocode.validation_cli import validate as validation_validate

    validation_validate()


if __name__ == "__main__":
    app()
