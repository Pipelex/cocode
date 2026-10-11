import importlib.util
import os
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

ROOT_CONFTEST_PATH = Path(__file__).parents[1] / "conftest.py"


class TestTestsNeverReport:
    @pytest.mark.parametrize("do_not_track_before", [None, "0"])
    def test_root_conftest_forces_do_not_track(self, mocker: MockerFixture, do_not_track_before: str | None) -> None:
        """Loading the root conftest sets `DO_NOT_TRACK=1`, whatever the environment held before, so no test sends usage statistics."""
        mocker.patch.dict(os.environ)
        os.environ.pop("DO_NOT_TRACK", None)
        if do_not_track_before is not None:
            os.environ["DO_NOT_TRACK"] = do_not_track_before

        spec = importlib.util.spec_from_file_location("cocode_root_conftest_loaded_again", ROOT_CONFTEST_PATH)
        assert spec is not None
        assert spec.loader is not None
        spec.loader.exec_module(importlib.util.module_from_spec(spec))

        assert os.environ.get("DO_NOT_TRACK") == "1"
