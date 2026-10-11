import importlib.util
import os
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

ROOT_CONFTEST_PATH = Path(__file__).parents[1] / "conftest.py"


class TestTestsNeverReport:
    @pytest.mark.parametrize("usage_stats_before", [None, "1"])
    def test_root_conftest_turns_usage_stats_off(self, mocker: MockerFixture, usage_stats_before: str | None) -> None:
        """Loading the root conftest sets `PIPELEX_USAGE_STATS=0`, whatever the environment held before, so no test sends usage statistics."""
        mocker.patch.dict(os.environ)
        os.environ.pop("PIPELEX_USAGE_STATS", None)
        if usage_stats_before is not None:
            os.environ["PIPELEX_USAGE_STATS"] = usage_stats_before

        spec = importlib.util.spec_from_file_location("cocode_root_conftest_loaded_again", ROOT_CONFTEST_PATH)
        assert spec is not None
        assert spec.loader is not None
        spec.loader.exec_module(importlib.util.module_from_spec(spec))

        assert os.environ.get("PIPELEX_USAGE_STATS") == "0"
