from pipelex import log
from pipelex.core.stuffs.structured_content import StructuredContent
from pydantic import Field, field_validator, model_validator
from typing_extensions import Self


class StructuredChangelog(StructuredContent):
    added: list[str] = Field(default_factory=list, description="New features.")
    changed: list[str] = Field(default_factory=list, description="Updates to existing behavior.")
    fixed: list[str] = Field(default_factory=list, description="Bug fixes.")
    removed: list[str] = Field(default_factory=list, description="Features removed.")
    deprecated: list[str] = Field(default_factory=list, description="Soon-to-be removed features.")
    security: list[str] = Field(default_factory=list, description="Security-related changes.")

    # --- normalization ------------------------------------------------------
    @field_validator("added", "changed", "fixed", "removed", "deprecated", "security", mode="before")
    @classmethod
    def _none_to_empty_list(cls, value: object) -> object:
        """Coerce an explicit null section to an empty list.

        LLMs often emit `"deprecated": null` for an empty section instead of
        omitting the key. `default_factory` only fills absent keys, so without
        this coercion such a payload would fail list validation.
        """
        return [] if value is None else value

    # --- validation ---------------------------------------------------------
    @model_validator(mode="after")
    def _at_least_one_section(self) -> Self:
        """Require at least one non-empty change section."""
        if not any(
            (
                self.added,
                self.changed,
                self.fixed,
                self.removed,
                self.deprecated,
                self.security,
            )
        ):
            log.warning("No change sections were generated in the changelog.")
        return self
