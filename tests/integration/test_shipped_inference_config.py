import os
from pathlib import Path

import pytest
from pipelex.pipelex import Pipelex
from pipelex.system.environment import PIPELEX_HOME_ENV_KEY
from pipelex.system.runtime import IntegrationMode
from pipelex.tools.misc.toml_utils import load_toml_from_path
from pytest_mock import MockerFixture

from cocode.inference_config import CocodeModelManager


class TestShippedInferenceConfig:
    def test_boot_outside_a_configured_project_runs_on_openai_alone(
        self, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Run from a project with no inference files, on a fresh home, cocode boots with OpenAI as its one provider backend.

        This is how a `pip install` runs. Pipelex fills the fresh home with inference files that switch every backend on, and
        a boot that read them would refuse to start without every provider's key.
        """
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        (project_dir / ".git").mkdir(parents=True)
        mocker.patch.dict(os.environ, {PIPELEX_HOME_ENV_KEY: str(home_dir)})
        monkeypatch.chdir(project_dir)
        # This test boots on a configuration of its own: the module's boot goes first, and the fixture boots the next module afresh.
        Pipelex.teardown_if_needed()
        model_manager = CocodeModelManager()
        try:
            Pipelex.make(integration_mode=IntegrationMode.PYTEST, needs_inference=False, models_manager=model_manager)
            enabled_backends = model_manager.inference_backend_library.all_enabled_backends()
        finally:
            Pipelex.teardown_if_needed()

        assert sorted(enabled_backends) == ["internal", "openai"]
        home_backends = load_toml_from_path(path=home_dir / "inference" / "backends.toml")
        assert home_backends["anthropic"]["enabled"] is True
