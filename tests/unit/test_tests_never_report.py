import importlib.util
import os
from pathlib import Path
from types import ModuleType

import pytest
from pipelex.system.runtime import IntegrationMode
from pytest_mock import MockerFixture

ROOT_CONFTEST_PATH = Path(__file__).parents[1] / "conftest.py"


def load_root_conftest_again() -> ModuleType:
    spec = importlib.util.spec_from_file_location("cocode_root_conftest_loaded_again", ROOT_CONFTEST_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestTestsNeverReport:
    @pytest.mark.parametrize("usage_stats_before", [None, "1"])
    def test_root_conftest_turns_usage_stats_off(self, mocker: MockerFixture, usage_stats_before: str | None) -> None:
        """Loading the root conftest sets `PIPELEX_USAGE_STATS=0`, whatever the environment held before, so no test sends usage statistics."""
        mocker.patch.dict(os.environ)
        os.environ.pop("PIPELEX_USAGE_STATS", None)
        if usage_stats_before is not None:
            os.environ["PIPELEX_USAGE_STATS"] = usage_stats_before

        load_root_conftest_again()

        assert os.environ.get("PIPELEX_USAGE_STATS") == "0"

    @pytest.mark.parametrize("needs_inference", [False, True])
    def test_root_conftest_boots_pipelex_as_a_test_run(self, mocker: MockerFixture, needs_inference: bool) -> None:
        """The root conftest boots pipelex as a test run, with or without inference: a pipelex with usage statistics reads that as off."""
        mocker.patch.dict(os.environ)
        root_conftest = load_root_conftest_again()
        pipelex_make = mocker.patch.object(root_conftest.Pipelex, "make")
        load_libraries = mocker.patch.object(root_conftest, "load_libraries_and_activate")
        bundle_validator = mocker.patch.object(root_conftest, "BundleValidator")
        bundle_validator.return_value.validate_current_library = mocker.AsyncMock()

        root_conftest.boot_pipelex_for_tests(needs_inference=needs_inference)

        pipelex_make.assert_called_once_with(
            integration_mode=IntegrationMode.PYTEST,
            needs_inference=needs_inference,
            library_dirs=root_conftest.PIPELINE_LIBRARY_DIRS_FOR_TESTS,
        )
        load_libraries.assert_called_once_with(root_conftest.PIPELINE_LIBRARY_DIRS_FOR_TESTS)
        assert bundle_validator.return_value.validate_current_library.await_count == (1 if needs_inference else 0)
