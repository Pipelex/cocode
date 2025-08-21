from enum import Enum
from typing import List, Optional

from pipelex.core.stuffs.stuff_content import StructuredContent
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


class GitDiffCitation(StructuredContent):
    """A citation from the git diff that supports a documentation change."""

    file_path: str = Field(description="Path to the file in the git diff")
    line_range: Optional[str] = Field(None, description="Line range in the format 'start,count' or 'line_number'")
    diff_section: str = Field(description="The relevant section of the git diff showing the change")
    change_type: str = Field(description="Type of change: added, removed, or modified")
    old_code: Optional[str] = Field(None, description="The old code that was changed or removed")
    new_code: Optional[str] = Field(None, description="The new code that was added or modified")


class ExactChange(StructuredContent):
    """Exact change instruction with old and new patterns."""

    old_pattern: Optional[str] = Field(None, description="The exact old code/text pattern to find and replace")
    new_pattern: Optional[str] = Field(None, description="The exact new code/text pattern to replace with")
    change_description: str = Field(description="Human-readable description of what this change does")
    context_hint: Optional[str] = Field(None, description="Additional context about where to find this pattern")


class DocumentationItem(StructuredContent):
    """A specific item that requires documentation analysis."""

    file_path: str = Field(description="Path to the file where the change occurred")
    documentation_type: DocumentationType = Field(description="Type of documentation needed")
    change_category: ChangeCategory = Field(description="Category of change")
    description: str = Field(description="Brief description of what changed")
    reason_for_update: str = Field(description="Why documentation needs updating")
    affected_doc_files: List[str] = Field(description="Specific documentation files that need updates")
    git_citations: List[GitDiffCitation] = Field(default_factory=list, description="Git diff citations supporting this change")


class DocumentationAnalysis(StructuredContent):
    """Detailed analysis of what needs to be added, deleted, or changed in documentation."""

    change_category: ChangeCategory = Field(description="Category of change")
    documentation_type: DocumentationType = Field(description="Type of documentation affected")
    affected_files: List[str] = Field(description="Exact documentation file paths")
    content_location: str = Field(description="Where in files to make changes")
    specific_content: str = Field(description="Exact text to add/modify/remove")
    impact_reasoning: str = Field(description="Why this change affects documentation")
    git_citations: List[GitDiffCitation] = Field(default_factory=list, description="Git diff citations supporting this analysis")


class DocumentationChangeItem(StructuredContent):
    """A specific documentation change with its supporting git diff citations."""

    file_path: str = Field(description="Documentation file that needs to be updated")
    location: str = Field(description="Specific location within the file (e.g., section, line number)")
    content_description: str = Field(description="Description of what content needs to be updated")
    change_reason: str = Field(description="Why this change is needed")
    exact_changes: List[ExactChange] = Field(default_factory=list, description="Exact old/new patterns for specific changes")
    git_citations: List[GitDiffCitation] = Field(default_factory=list, description="Git diff citations supporting this change")


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
    structured_changes: List[DocumentationChangeItem] = Field(
        default_factory=list, description="Structured list of documentation changes with git citations"
    )
