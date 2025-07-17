from typing import List, Optional

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field


class FileChangeAnalysis(StructuredContent):
    """Analysis of changes in a specific file and their documentation impact."""
    
    file_path: str = Field(description="Path to the file that was changed")
    change_type: str = Field(description="Type of change (new feature, API change, configuration change, etc.)")
    impact_level: str = Field(description="Impact level (critical, important, minor)")
    description: str = Field(description="Description of the change")
    documentation_impact: str = Field(description="How this change affects documentation")
    affected_doc_files: List[str] = Field(default_factory=list, description="List of documentation files that may need updates")


class DocumentationFile(StructuredContent):
    """A documentation file that may need updates based on code changes."""
    
    file_path: str = Field(description="Path to the documentation file")
    file_type: str = Field(description="Type of documentation (README, API docs, user guide, etc.)")
    current_content: Optional[str] = Field(default=None, description="Current content of the file")
    sections: List[str] = Field(default_factory=list, description="Main sections in the file")
    update_priority: str = Field(description="Priority for updating this file (high, medium, low)")


class DocumentationUpdate(StructuredContent):
    """A suggested update to documentation based on code changes."""
    
    file_path: str = Field(description="Path to the documentation file to update")
    section: str = Field(description="Section of the file to update")
    update_type: str = Field(description="Type of update (add, modify, remove, restructure)")
    current_content: Optional[str] = Field(default=None, description="Current content to be updated")
    new_content: str = Field(description="New content to add or replace with")
    reasoning: str = Field(description="Explanation of why this update is needed")
    location_hint: Optional[str] = Field(default=None, description="Hint about where to place the update")


class DocumentationUpdateSuggestion(StructuredContent):
    """A comprehensive suggestion for updating documentation based on git diff analysis."""
    
    overview: str = Field(description="Brief overview of the changes and their documentation impact")
    affected_files: List[str] = Field(description="List of files that were changed in the git diff")
    doc_updates: List[DocumentationUpdate] = Field(description="List of specific documentation updates needed")
    new_docs_needed: List[str] = Field(default_factory=list, description="List of new documentation files or sections needed")
    cross_references: List[str] = Field(default_factory=list, description="Links and references that need updating")
    verification_checklist: List[str] = Field(description="Checklist for verifying the documentation updates") 