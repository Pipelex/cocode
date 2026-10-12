"""The inference configuration cocode boots Pipelex on.

cocode is configured for OpenAI: its `.pipelex/inference/` directory switches on the OpenAI backend alone, beside Pipelex's
model catalogs and model deck. Pipelex finds that directory only from the working directory, as the configuration of the
project it runs in, so on its own it would read it only when cocode runs from its checkout. Run from anywhere else, as a
`pip install` runs it, Pipelex falls back to the home directory's inference files, and the ones it writes into a fresh home
switch every backend on, so the boot refuses to start for want of every provider's key.

cocode therefore carries the directory inside its package, and boots Pipelex with `CocodeModelManager`, which reads the
inference configuration this way:

- When the project cocode runs from has an inference configuration of its own, a `.pipelex/inference/backends.toml`, Pipelex
  resolves everything as it always does. cocode's checkout is such a project, and so is any project set up with `pipelex init`.
- Otherwise cocode's own directory stands where the home directory's inference files would: its backends, model catalogs,
  routing profiles and model deck. The personal override files, `backends_override.toml` and `routing_profiles_override.toml`,
  are still merged over it, the home directory's first and then the project's, as Pipelex merges them.
"""

from collections.abc import Sequence
from pathlib import Path

from pipelex.cogt.models.model_manager import ModelManager
from pipelex.plugins.plugin_model_declarations import PluginModelDeclarations
from pipelex.system.configuration.config_loader import (
    BACKENDS_DIR_NAME,
    BACKENDS_FILE_NAME,
    INFERENCE_DIR_NAME,
    MODEL_DECKS_DIR_NAME,
    ROUTING_PROFILES_FILE_NAME,
    config_manager,
)
from pipelex.system.environment import CONFIG_DIR_NAME
from pipelex.tools.secrets.secrets_provider_abstract import SecretsProviderAbstract
from typing_extensions import override

from cocode.exceptions import InferenceConfigNotFoundError

# Where a built package carries the repository's `.pipelex/inference/` directory: `pyproject.toml` copies it there.
PACKAGED_INFERENCE_DIR_NAME = "pipelex_inference"

_PACKAGE_DIR = Path(__file__).resolve().parent


def shipped_inference_dir() -> Path:
    """The inference configuration directory cocode ships, wherever this copy of cocode was installed from.

    An installed package carries it as `cocode/pipelex_inference/`. A source checkout, an editable install included, has the
    original itself, the repository's `.pipelex/inference/`.
    """
    candidates = [
        _PACKAGE_DIR / PACKAGED_INFERENCE_DIR_NAME,
        _PACKAGE_DIR.parent / CONFIG_DIR_NAME / INFERENCE_DIR_NAME,
    ]
    for candidate in candidates:
        if (candidate / BACKENDS_FILE_NAME).is_file():
            return candidate
    searched = ", ".join(str(candidate) for candidate in candidates)
    msg = f"cocode's inference configuration was not found in {searched}: reinstall cocode."
    raise InferenceConfigNotFoundError(msg)


def project_has_inference_config() -> bool:
    """Whether the project cocode runs from has an inference configuration of its own, which Pipelex then reads as it is."""
    project_config_dir = config_manager.project_config_dir
    if project_config_dir is None:
        return False
    return (project_config_dir / INFERENCE_DIR_NAME / BACKENDS_FILE_NAME).is_file()


class CocodeModelManager(ModelManager):
    """Pipelex's model manager, reading cocode's shipped inference configuration when the project it runs from has none."""

    @override
    def setup(
        self,
        *,
        secrets_provider: SecretsProviderAbstract,
        plugin_model_declarations: PluginModelDeclarations,
        needs_inference: bool = True,
        backends_library_paths: Sequence[Path] | None = None,
        backends_dir_path: str | None = None,
        routing_profile_library_paths: Sequence[Path] | None = None,
        deck_dir_path: str | None = None,
    ) -> None:
        is_any_path_given = any(
            path is not None for path in (backends_library_paths, backends_dir_path, routing_profile_library_paths, deck_dir_path)
        )
        if is_any_path_given or project_has_inference_config():
            super().setup(
                secrets_provider=secrets_provider,
                plugin_model_declarations=plugin_model_declarations,
                needs_inference=needs_inference,
                backends_library_paths=backends_library_paths,
                backends_dir_path=backends_dir_path,
                routing_profile_library_paths=routing_profile_library_paths,
                deck_dir_path=deck_dir_path,
            )
            return

        inference_dir = shipped_inference_dir()
        # Each sequence Pipelex resolves is its base file, then the personal override files of the home directory and of the
        # project: cocode's base takes the place of the first, and the override files are merged over it as Pipelex merges them.
        super().setup(
            secrets_provider=secrets_provider,
            plugin_model_declarations=plugin_model_declarations,
            needs_inference=needs_inference,
            backends_library_paths=[inference_dir / BACKENDS_FILE_NAME, *config_manager.backends_file_paths()[1:]],
            backends_dir_path=str(inference_dir / BACKENDS_DIR_NAME),
            routing_profile_library_paths=[inference_dir / ROUTING_PROFILES_FILE_NAME, *config_manager.routing_profiles_file_paths()[1:]],
            deck_dir_path=str(inference_dir / MODEL_DECKS_DIR_NAME),
        )
