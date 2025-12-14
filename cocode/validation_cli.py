"""
Pipeline validation CLI commands.
"""

import asyncio

import typer
from pipelex import log
from pipelex.cli.commands.validate_cmd import do_validate_all_libraries_and_dry_run
from pipelex.hub import get_pipes
from pipelex.pipe_run.dry_run import dry_run_pipes
from pipelex.pipelex import Pipelex

validation_app = typer.Typer(
    name="validation",
    help="Pipeline validation and setup commands",
    add_completion=False,
    rich_markup_mode="rich",
)


@validation_app.command("validate")
def validate() -> None:
    """Run the setup sequence and validate all pipelines."""
    do_validate_all_libraries_and_dry_run()
    asyncio.run(dry_run_pipes(get_pipes()))
    log.info("Setup sequence passed OK, config and pipelines are validated.")


@validation_app.command("dry-run")
def dry_run() -> None:
    """Run dry validation of all pipelines without full setup."""
    asyncio.run(dry_run_pipes(get_pipes()))
    log.info("Dry run completed successfully.")


@validation_app.command("check-config")
def check_config() -> None:
    """Validate Pipelex configuration and libraries."""
    do_validate_all_libraries_and_dry_run()
    log.info("Configuration validation passed OK.")
