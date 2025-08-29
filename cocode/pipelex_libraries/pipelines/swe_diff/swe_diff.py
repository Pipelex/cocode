from __future__ import annotations

from typing import List

from pipelex import log
from pipelex.core.stuffs.stuff_content import StructuredContent
from pydantic import Field, model_validator
from typing_extensions import Self


class StructuredChangelog(StructuredContent):
    added: List[str] = Field(default_factory=list, description="New features.")
    changed: List[str] = Field(default_factory=list, description="Updates to existing behavior.")
    fixed: List[str] = Field(default_factory=list, description="Bug fixes.")
    removed: List[str] = Field(default_factory=list, description="Features removed.")
    deprecated: List[str] = Field(default_factory=list, description="Soon-to-be removed features.")
    security: List[str] = Field(default_factory=list, description="Security-related changes.")

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
