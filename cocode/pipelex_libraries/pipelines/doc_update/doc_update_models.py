from typing import List, Optional

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field


class DocumentationItem(StructuredContent):
    """A specific item that requires documentation analysis."""
    
    file_path: str = Field(description="Path to the file where the change occurred")
    documentation_type: str = Field(description="Type of documentation needed (user_docs, ai_instructions)")
    change_category: str = Field(description="Category of change (addition, deletion, modification, minor_change)")
    description: str = Field(description="Brief description of what changed")
    reason_for_update: str = Field(description="Why documentation needs updating")
    affected_doc_files: List[str] = Field(description="Specific documentation files that need updates")


class DocumentationAnalysis(StructuredContent):
    """Detailed analysis of what needs to be added, deleted, or changed in documentation."""
    
    change_category: str = Field(description="Addition, Deletion, Modification, or Minor_Change")
    documentation_type: str = Field(description="user_docs, ai_instructions, or both")
    affected_files: List[str] = Field(description="Exact documentation file paths")
    content_location: str = Field(description="Where in files to make changes")
    specific_content: str = Field(description="Exact text to add/modify/remove")
    impact_reasoning: str = Field(description="Why this change affects documentation")


class DocumentationSuggestions(StructuredContent):
    """Final structured suggestions for updating all documentation."""
    
    user_documentation_updates: Optional[str] = Field(None, description="Updates needed for docs/ directory")
    ai_instruction_updates: Optional[str] = Field(None, description="Updates needed for AI instruction files")
    has_updates: bool = Field(description="Whether any updates are actually needed")
    summary: str = Field(description="Brief summary of all suggested changes")
