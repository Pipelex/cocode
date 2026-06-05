import asyncio
import logging
from pathlib import Path

import pytest
from pipelex.cli.cli_factory import make_pipelex_for_cli
from pipelex.cli.error_handlers import ErrorContext
from pipelex.config import get_config
from pipelex.pipelex import Pipelex
from pipelex.pipeline.bundle_validator import BundleValidator
from pipelex.pipeline.execution_seams import load_libraries_and_activate
from pipelex.system.configuration.config_check import check_is_initialized
from pipelex.system.configuration.configs import PipelexConfig
from pipelex.system.runtime import IntegrationMode
from pipelex.test_extras.shared_pytest_plugins import is_inference_disabled_in_pipelex
from pytest import FixtureRequest
from rich import print
from rich.console import Console
from rich.traceback import Traceback

from cocode.common import PIPELINE_LIBRARY_DIRS

PIPELINE_LIBRARY_DIRS_FOR_TESTS = [*PIPELINE_LIBRARY_DIRS, Path("tests/pipelines")]

pytest_plugins = [
    "pipelex.test_extras.shared_pytest_plugins",
]


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
        disable_inference = is_inference_disabled_in_pipelex(request)
        if disable_inference:
            # When inference is disabled, use Pipelex.make() directly with needs_inference=False:
            # this skips the gateway terms check and uses a mock content generator.
            Pipelex.make(
                integration_mode=IntegrationMode.CI,
                needs_inference=False,
                library_dirs=PIPELINE_LIBRARY_DIRS_FOR_TESTS,
            )
            # Load libraries and keep them loaded (no dry-run, which would need model resolution)
            load_libraries_and_activate(PIPELINE_LIBRARY_DIRS_FOR_TESTS)
        else:
            # When inference is enabled, use the CLI factory for proper error handling
            make_pipelex_for_cli(context=ErrorContext.VALIDATION, library_dirs=PIPELINE_LIBRARY_DIRS_FOR_TESTS)
            load_libraries_and_activate(PIPELINE_LIBRARY_DIRS_FOR_TESTS)
            asyncio.run(BundleValidator().validate_current_library())
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
