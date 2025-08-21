from typing import List, Optional

from pipelex.core.stuffs.stuff_content import StructuredContent
from pydantic import Field


class DocumentationFile(StructuredContent):
    """A documentation file that needs to be proofread against the codebase."""

    file_path: str = Field(description="Path to the documentation file")
    doc_content: str = Field(description="Content of the documentation file")
    title: str = Field(description="Title or main topic of the documentation")


class FilePath(StructuredContent):
    """A path to a file in the codebase."""

    path: str = Field(description="Path to the file")


class RepositoryMap(StructuredContent):
    """A repository map containing the codebase structure and file contents."""

    repo_content: str = Field(description="Full repository content in repo_map format")


class CodebaseFileContent(StructuredContent):
    """Content of a codebase file."""

    file_path: str = Field(description="Path to the codebase file")
    file_content: str = Field(description="Content of the codebase file")


class DocumentationInconsistency(StructuredContent):
    """An inconsistency found between documentation and actual code."""

    doc_file_path: str = Field(description="Path to the documentation file with the issue")
    related_files: List[str] = Field(default_factory=list, description="Code files that support this finding")
    issue_description: str = Field(description="Description of the inconsistency")
    doc_content: str = Field(description="The problematic content in the documentation")
    actual_code: Optional[str] = Field(None, description="The actual code that contradicts the documentation")
