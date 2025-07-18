from enum import Enum
from typing import List, Optional

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


class AIInstructionFileType(str, Enum):
    AGENTS_MD = "AGENTS.md"
    CLAUDE_MD = "CLAUDE.md"
    CURSOR_RULES = "cursor_rules"


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


class AIInstructionFileAnalysis(StructuredContent):
    """Analysis of changes needed for a specific AI instruction file."""

    file_type: AIInstructionFileType = Field(description="Type of AI instruction file")
    file_exists: bool = Field(description="Whether the file currently exists")
    additions: List[str] = Field(default_factory=list, description="Content to add to the file")
    deletions: List[str] = Field(default_factory=list, description="Content to remove from the file")
    modifications: List[str] = Field(default_factory=list, description="Content to modify in the file")
    minor_changes: List[str] = Field(default_factory=list, description="Minor changes needed")
    reasoning: str = Field(description="Overall reasoning for changes to this file")


class AIInstructionUpdateSuggestions(StructuredContent):
    """Comprehensive suggestions for updating all AI instruction files."""

    agents_md_analysis: Optional[AIInstructionFileAnalysis] = Field(None, description="Analysis for AGENTS.md")
    claude_md_analysis: Optional[AIInstructionFileAnalysis] = Field(None, description="Analysis for CLAUDE.md")
    cursor_rules_analysis: Optional[AIInstructionFileAnalysis] = Field(None, description="Analysis for cursor rules")
    summary: str = Field(description="Overall summary of all changes needed")


class AIInstructionParallelResults(StructuredContent):
    """Results from parallel analysis of AI instruction files."""

    agents_analysis: Optional[AIInstructionFileAnalysis] = Field(None, description="Analysis for AGENTS.md")
    claude_analysis: Optional[AIInstructionFileAnalysis] = Field(None, description="Analysis for CLAUDE.md")
    cursor_analysis: Optional[AIInstructionFileAnalysis] = Field(None, description="Analysis for cursor rules")


class DocumentationSuggestions(StructuredContent):
    """Final structured suggestions for updating all documentation."""

    documentation_updates_prompt: str = Field(description="Complete prompt text for documentation updates")
