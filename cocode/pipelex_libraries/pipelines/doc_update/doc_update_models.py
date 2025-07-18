from enum import Enum
from typing import List

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field


class ChangeCategory(str, Enum):
    ADDITION = "addition"
    DELETION = "deletion"
    MODIFICATION = "modification"
    MINOR_CHANGE = "minor_change"


class DocumentationType(str, Enum):
    DOCUMENTATION = "documentation"
    AI_INSTRUCTIONS = "ai_instructions"


class DocumentationItem(StructuredContent):
    """A specific item that requires documentation analysis."""

    file_path: str = Field(description="Path to the file where the change occurred")
    documentation_type: DocumentationType = Field(description="Type of documentation needed")
    change_category: ChangeCategory = Field(description="Category of change")
    description: str = Field(description="Brief description of what changed")
    reason_for_update: str = Field(description="Why documentation needs updating")
    affected_doc_files: List[str] = Field(description="Specific documentation files that need updates")


class DocumentationAnalysis(StructuredContent):
    """Detailed analysis of what needs to be added, deleted, or changed in documentation."""

    change_category: ChangeCategory = Field(description="Category of change")
    documentation_type: DocumentationType = Field(description="Type of documentation affected")
    affected_files: List[str] = Field(description="Exact documentation file paths")
    content_location: str = Field(description="Where in files to make changes")
    specific_content: str = Field(description="Exact text to add/modify/remove")
    impact_reasoning: str = Field(description="Why this change affects documentation")


class DocumentationSuggestions(StructuredContent):
    """Final structured suggestions for updating all documentation."""

    documentation_updates_prompt: str = Field(description="Complete prompt text for documentation updates")
