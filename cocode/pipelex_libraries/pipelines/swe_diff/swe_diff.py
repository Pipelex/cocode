from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Self

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field, model_validator


class ChangeType(str, Enum):
    """Enumeration of changelog change types."""

    ADDED = "added"
    CHANGED = "changed"
    FIXED = "fixed"
    REMOVED = "removed"
    DEPRECATED = "deprecated"
    SECURITY = "security"


class ChangelogSection(StructuredContent):
    """
    A specific type of change in a changelog with categorized entries.
    """

    change_type: ChangeType = Field(description="Type of change (added, changed, fixed, etc.).")
    description: str = Field(description="User-friendly description of the change.")
    section_title: str = Field(description="Title of the section this change belongs to.")


class ReleaseChangelog(StructuredContent):
    """
    Single-release entry for a Keep-a-Changelog-style file.
    """

    version: str = Field(pattern=r"^\d+\.\d+\.\d+$", description="Semantic-version tag, e.g. '1.2.0'.")
    release_date: date = Field(description="Release date (UTC).")

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
            raise ValueError("A release must contain at least one change entry.")
        return self
