from typing import List, Optional

from pipelex.core.stuff_content import StructuredContent
from pydantic import Field


class DocumentationFile(StructuredContent):
    """A documentation file that needs to be proofread against the codebase."""

    file_path: str = Field(description="Path to the documentation file")
    doc_content: str = Field(description="Content of the documentation file")
    title: str = Field(description="Title or main topic of the documentation")


class DocumentationChunk(StructuredContent):
    """A chunk of documentation content for processing."""

    file_path: str = Field(description="Path to the original documentation file")
    chunk_content: str = Field(description="Content of this specific chunk")


class RelatedCodeFile(StructuredContent):
    """A code file that is related to a documentation file."""

    file_path: str = Field(description="Path to the related code file")
    relevance_reason: str = Field(description="Why this code file is related to the documentation")
    confidence: float = Field(description="Confidence score (0-1) that this file is relevant")


class FilePath(StructuredContent):
    """A path to a file in the codebase."""

    path: str = Field(description="Path to the file")


class CodeFileContent(StructuredContent):
    """Content of a specific code file extracted from the codebase."""

    file_path: str = Field(description="Path to the code file")
    code_content: str = Field(description="Content of the code file")
    file_type: str = Field(description="Type of file (e.g., 'python', 'toml', 'yaml')")


class DocumentationInconsistency(StructuredContent):
    """An inconsistency found between documentation and actual code."""

    doc_file_path: str = Field(description="Path to the documentation file with the issue")
    doc_section: str = Field(description="Section or line in the documentation that has the issue")
    issue_description: str = Field(description="Description of the inconsistency")
    doc_content: str = Field(description="The problematic content in the documentation")
    actual_code: Optional[str] = Field(None, description="The actual code that contradicts the documentation")
    suggested_fix: str = Field(description="Suggested fix for the documentation")
    severity: str = Field(description="Severity level: 'high', 'medium', 'low'")
    related_files: List[str] = Field(default_factory=list, description="Code files that support this finding")


class ProofreadingReport(StructuredContent):
    """Complete proofreading report for documentation consistency."""

    summary: str = Field(description="Executive summary of the proofreading results")
    total_files_checked: int = Field(description="Total number of documentation files checked")
    inconsistencies_found: int = Field(description="Total number of inconsistencies found")
    high_priority_issues: int = Field(description="Number of high-priority issues")
    inconsistencies: List[DocumentationInconsistency] = Field(description="List of all inconsistencies found")
    recommendations: List[str] = Field(description="General recommendations for improving documentation")
