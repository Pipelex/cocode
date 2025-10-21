import logging

import pipelex.config
import pipelex.pipelex
import pytest
from pipelex.config import get_config
from rich import print
from rich.console import Console
from rich.traceback import Traceback

pytest_plugins = [
    "pipelex.test_extras.shared_pytest_plugins",
]


@pytest.fixture(scope="module", autouse=True)
def reset_pipelex_config_fixture():
    # Code to run before each test
    print("\n[magenta]pipelex setup[/magenta]")
    try:
        pipelex_instance = pipelex.pipelex.Pipelex.make()
        pipelex_instance.validate_libraries()
        config = get_config()
        assert isinstance(config, pipelex.config.PipelexConfig)
    except Exception as exc:
        Console().print(Traceback())
        pytest.exit(f"Critical Pipelex setup error: {exc}")
    yield
    # Code to run after each test
    print("\n[magenta]pipelex teardown[/magenta]")
    pipelex_instance.teardown()


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
