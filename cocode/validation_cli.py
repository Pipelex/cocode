"""
Pipeline validation CLI commands.
"""

import asyncio

import typer
from pipelex import log
from pipelex.pipeline.bundle_validator import BundleValidator
from pipelex.pipeline.execution_seams import load_libraries_and_activate

from cocode.common import PIPELINE_LIBRARY_DIRS

validation_app = typer.Typer(
    name="validation",
    help="Pipeline validation and setup commands",
    add_completion=False,
    rich_markup_mode="rich",
)


@validation_app.command("validate")
def validate() -> None:
    """Run the setup sequence and validate all pipelines."""
    load_libraries_and_activate(PIPELINE_LIBRARY_DIRS)
    asyncio.run(BundleValidator().validate_current_library())
    log.info("Setup sequence passed OK, config and pipelines are validated.")


@validation_app.command("dry-run")
def dry_run() -> None:
    """Run dry validation of all pipelines."""
    load_libraries_and_activate(PIPELINE_LIBRARY_DIRS)
    asyncio.run(BundleValidator().validate_current_library())
    log.info("Dry run completed successfully.")


@validation_app.command("check-config")
def check_config() -> None:
    """Validate Pipelex configuration and libraries."""
    load_libraries_and_activate(PIPELINE_LIBRARY_DIRS)
    asyncio.run(BundleValidator().validate_current_library())
    log.info("Configuration validation passed OK.")
