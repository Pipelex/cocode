import logging
import os
from pathlib import Path

import pytest
from pipelex.config import get_config
from pipelex.pipelex import Pipelex
from pipelex.pipeline.execution_seams import load_libraries_and_activate
from pipelex.system.configuration.config_check import check_is_initialized
from pipelex.system.configuration.configs import PipelexConfig
from pipelex.system.runtime import IntegrationMode
from pipelex.test_extras.shared_pytest_plugins import needs_inference_in_pipelex
from pytest import FixtureRequest
from rich import print
from rich.console import Console
from rich.traceback import Traceback

from cocode.common import PIPELINE_LIBRARY_DIRS
from cocode.inference_config import CocodeModelManager

# Our tests never report usage statistics, whatever pipelex they run against. `PIPELEX_USAGE_STATS=0` is pipelex's own
# statistics switch, the one its test helpers set, and it touches nothing else, so a pipelex that has no statistics, as
# the pinned one has none, ignores it. `DO_NOT_TRACK` would turn them off too, along with every telemetry destination a
# developer configured, which is more than this guard is about. Forced, not defaulted, so no value in the shell turns
# statistics back on, and set when this conftest loads, before any fixture or plugin hook boots pipelex.
os.environ["PIPELEX_USAGE_STATS"] = "0"

PIPELINE_LIBRARY_DIRS_FOR_TESTS = [*PIPELINE_LIBRARY_DIRS, Path("tests/pipelines")]

pytest_plugins = [
    "pipelex.test_extras.shared_pytest_plugins",
]


def boot_pipelex_for_tests(*, needs_inference: bool) -> None:
    """Boot pipelex as a test run and load cocode's pipelines.

    It boots with the model manager the CLI boots with, so the tests read the inference configuration the CLI reads.
    `IntegrationMode.PYTEST` tells pipelex the process is a test run: a pipelex that sends usage statistics turns them
    off for it without reading the machine's shared statistics state. Without inference, pipelex still loads every
    enabled backend and its models but resolves no provider key, and every run is a dry run. The boot dry-runs no pipe:
    `test_dry_run_all_pipes` does that once, with or without inference.
    """
    Pipelex.make(
        integration_mode=IntegrationMode.PYTEST,
        needs_inference=needs_inference,
        library_dirs=PIPELINE_LIBRARY_DIRS_FOR_TESTS,
        models_manager=CocodeModelManager(),
    )
    load_libraries_and_activate(PIPELINE_LIBRARY_DIRS_FOR_TESTS)


@pytest.fixture(scope="session", autouse=True)
def check_pipelex_initialized():
    if not check_is_initialized():
        pytest.exit("Pipelex must be initialized before running the tests")
    yield


@pytest.fixture(scope="module", autouse=True)
def reset_pipelex_config_fixture(request: FixtureRequest):
    # Code to run before each test
    print("\n[magenta]pipelex setup[/magenta]")
    try:
        boot_pipelex_for_tests(needs_inference=needs_inference_in_pipelex(request))
        config = get_config()
        assert isinstance(config, PipelexConfig)
    except Exception as exc:
        Console().print(Traceback())
        pytest.exit(f"Critical Pipelex setup error: {exc}")
    yield
    # Code to run after each test
    print("\n[magenta]pipelex teardown[/magenta]")
    Pipelex.teardown_if_needed()


@pytest.fixture(scope="function", autouse=True)
def pretty():
    # Code to run before each test
    print("\n")
    yield
    # Code to run after each test
    print("\n")


@pytest.fixture
def suppress_error_logs():
    """
    Fixture to suppress error logs during tests that expect failures.

    This prevents confusing error messages in test output when testing
    expected failure scenarios (e.g., invalid repositories, network errors).

    Usage:
        def test_expected_failure(self, mocker, suppress_error_logs):
            # Test code that expects errors without showing error logs
    """
    # Store original log level
    logger = logging.getLogger("cocode")
    original_level = logger.level

    # Set to CRITICAL to suppress INFO and ERROR logs
    logger.setLevel(logging.CRITICAL)

    yield

    # Restore original log level
    logger.setLevel(original_level)
