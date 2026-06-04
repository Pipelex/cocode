"""
Pipeline validation CLI commands.
"""

import asyncio
from pathlib import Path

import typer
from pipelex import log
from pipelex.hub import (
    get_current_library,
    get_library_manager,
    get_pipes,
    resolve_library_dirs,
    set_current_library,
)
from pipelex.pipeline.bundle_validator import BundleValidator

from cocode.common import PIPELINE_LIBRARY_DIRS

validation_app = typer.Typer(
    name="validation",
    help="Pipeline validation and setup commands",
    add_completion=False,
    rich_markup_mode="rich",
)


def load_all_pipeline_libraries() -> None:
    """Open the model library, mark it current, and load every configured pipeline directory."""
    library_manager = get_library_manager()
    library_id, _ = library_manager.open_library()
    set_current_library(library_id=library_id)
    effective_dirs, _ = resolve_library_dirs([Path(lib_dir) for lib_dir in PIPELINE_LIBRARY_DIRS])
    if effective_dirs:
        library_manager.load_libraries(library_id=library_id, library_dirs=effective_dirs)


async def dry_run_all_pipes() -> None:
    """Dry-run every non-signature pipe in the currently loaded library."""
    pipes = [pipe for pipe in get_pipes() if not pipe.is_signature]
    await BundleValidator().validate_pipes(pipes=pipes, library_id=get_current_library())


@validation_app.command("validate")
def validate() -> None:
    """Run the setup sequence and validate all pipelines."""
    load_all_pipeline_libraries()
    asyncio.run(dry_run_all_pipes())
    log.info("Setup sequence passed OK, config and pipelines are validated.")


@validation_app.command("dry-run")
def dry_run() -> None:
    """Run dry validation of all pipelines."""
    load_all_pipeline_libraries()
    asyncio.run(dry_run_all_pipes())
    log.info("Dry run completed successfully.")


@validation_app.command("check-config")
def check_config() -> None:
    """Validate Pipelex configuration and libraries."""
    load_all_pipeline_libraries()
    asyncio.run(dry_run_all_pipes())
    log.info("Configuration validation passed OK.")
