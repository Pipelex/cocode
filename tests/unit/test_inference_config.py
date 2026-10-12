import os
from pathlib import Path

import pytest
from pipelex.cogt.models.model_manager import ModelManager
from pipelex.plugins.plugin_model_declarations import PluginModelDeclarations
from pipelex.system.environment import PIPELEX_HOME_ENV_KEY
from pipelex.tools.secrets.secrets_provider_abstract import SecretsProviderAbstract
from pytest_mock import MockerFixture
from typer import Context as TyperContext

from cocode.cli.main import main
from cocode.inference_config import CocodeModelManager, shipped_inference_dir


class TestInferenceConfig:
    def test_shipped_configuration_switches_on_openai(self) -> None:
        """The inference configuration cocode ships carries its backends file, catalogs, routing profiles and deck, with OpenAI on."""
        inference_dir = shipped_inference_dir()

        assert (inference_dir / "backends" / "openai.toml").is_file()
        assert (inference_dir / "routing_profiles.toml").is_file()
        assert (inference_dir / "deck" / "1_llm_deck.toml").is_file()
        assert '[openai]\ndisplay_name = "OpenAI"\nenabled = true\n' in (inference_dir / "backends.toml").read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        ("project_files", "expected_overrides_tiers"),
        [
            ([], ["home"]),
            ([".pipelex/inference/backends_override.toml"], ["home", "project"]),
        ],
    )
    def test_project_without_inference_config_reads_the_shipped_one(
        self,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        project_files: list[str],
        expected_overrides_tiers: list[str],
    ) -> None:
        """Outside a project with inference files of its own, the boot reads cocode's, with the personal override files merged over it."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        (project_dir / ".git").mkdir(parents=True)
        for project_file in project_files:
            (project_dir / project_file).parent.mkdir(parents=True, exist_ok=True)
            (project_dir / project_file).write_text("", encoding="utf-8")
        mocker.patch.dict(os.environ, {PIPELEX_HOME_ENV_KEY: str(home_dir)})
        monkeypatch.chdir(project_dir)
        parent_setup = mocker.patch.object(ModelManager, "setup")

        CocodeModelManager().setup(
            secrets_provider=mocker.Mock(spec=SecretsProviderAbstract),
            plugin_model_declarations=mocker.Mock(spec=PluginModelDeclarations),
            needs_inference=False,
        )

        override_dirs = {"home": home_dir / "inference", "project": project_dir.resolve() / ".pipelex" / "inference"}
        inference_dir = shipped_inference_dir()
        parent_setup.assert_called_once()
        setup_kwargs = parent_setup.call_args.kwargs
        assert setup_kwargs["needs_inference"] is False
        assert setup_kwargs["backends_library_paths"] == [
            inference_dir / "backends.toml",
            *[override_dirs[tier] / "backends_override.toml" for tier in expected_overrides_tiers],
        ]
        assert setup_kwargs["routing_profile_library_paths"] == [
            inference_dir / "routing_profiles.toml",
            *[override_dirs[tier] / "routing_profiles_override.toml" for tier in expected_overrides_tiers],
        ]
        assert setup_kwargs["backends_dir_path"] == str(inference_dir / "backends")
        assert setup_kwargs["deck_dir_path"] == str(inference_dir / "deck")

    def test_project_with_inference_config_is_read_as_pipelex_reads_it(
        self, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """A project with a `backends.toml` of its own, as cocode's checkout or a project set up by `pipelex init` has, keeps Pipelex's resolution."""
        project_dir = tmp_path / "project"
        (project_dir / ".pipelex" / "inference").mkdir(parents=True)
        (project_dir / ".pipelex" / "inference" / "backends.toml").write_text("", encoding="utf-8")
        mocker.patch.dict(os.environ, {PIPELEX_HOME_ENV_KEY: str(tmp_path / "home")})
        monkeypatch.chdir(project_dir)
        parent_setup = mocker.patch.object(ModelManager, "setup")

        CocodeModelManager().setup(
            secrets_provider=mocker.Mock(spec=SecretsProviderAbstract),
            plugin_model_declarations=mocker.Mock(spec=PluginModelDeclarations),
        )

        parent_setup.assert_called_once()
        setup_kwargs = parent_setup.call_args.kwargs
        assert setup_kwargs["needs_inference"] is True
        for path_argument in ("backends_library_paths", "backends_dir_path", "routing_profile_library_paths", "deck_dir_path"):
            assert setup_kwargs[path_argument] is None

    def test_cli_boots_with_the_cocode_model_manager(self, mocker: MockerFixture) -> None:
        """The CLI boots Pipelex with the model manager that reads cocode's inference configuration."""
        pipelex_make = mocker.patch("cocode.cli.main.Pipelex.make")
        ctx = mocker.Mock(spec=TyperContext)
        ctx.invoked_subcommand = "validate"

        main(ctx=ctx)

        pipelex_make.assert_called_once()
        assert isinstance(pipelex_make.call_args.kwargs["models_manager"], CocodeModelManager)
