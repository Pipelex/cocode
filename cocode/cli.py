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

from cocode.github.github_cli import github_app
from cocode.repox.repox_cli import repox_app
from cocode.swe.swe_cli import swe_app
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

# Add command groups
app.add_typer(repox_app, name="repox", help="Repository processing and analysis commands")
app.add_typer(swe_app, name="swe", help="Software Engineering analysis and automation commands")
app.add_typer(validation_app, name="validation", help="Pipeline validation and setup commands")
app.add_typer(github_app, name="github", help="GitHub-related operations and utilities")


@app.callback(invoke_without_command=True)
def main(ctx: TyperContext) -> None:
    """Initialize Pipelex system before any command runs."""
    Pipelex.make(relative_config_folder_path="./pipelex_libraries")

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
