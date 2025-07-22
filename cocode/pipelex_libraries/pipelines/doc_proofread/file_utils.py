from pathlib import Path
from typing import List

from pipelex.core.stuff_content import ListContent, StuffContent
from pipelex.core.working_memory import WorkingMemory
from pipelex.tools.func_registry import func_registry

from cocode.pipelex_libraries.pipelines.doc_proofread.doc_proofread_models import FilePath


def list_docs_dir_files(working_memory: WorkingMemory) -> StuffContent:
    """List all documentation files in the docs directory.

    Args:
        working_memory: Working memory containing repo_text

    Returns:
        ListContent of FilePath objects
    """
    from cocode.pipelex_libraries.pipelines.doc_proofread.doc_proofread_models import FilePath

    # Get all markdown files in the docs directory
    doc_files: List[StuffContent] = []
    docs_dir = Path("docs")
    if docs_dir.exists():
        for file_path in docs_dir.rglob("*.md"):
            if "CHANGELOG.md" not in str(file_path):  # Skip changelog files
                doc_files.append(FilePath(path=str(file_path)))

    # Also include README.md from the root if it exists
    readme_path = Path("README.md")
    if readme_path.exists():
        doc_files.append(FilePath(path=str(readme_path)))

    # If no files found, return a dummy file
    if not doc_files:
        doc_files = [FilePath(path="docs/example.md")]

    return ListContent[StuffContent](items=doc_files)


def read_file_content(working_memory: WorkingMemory) -> StuffContent:
    """Read the content of a documentation file.

    Args:
        working_memory: Working memory containing file_path

    Returns:
        DocumentationFile object
    """
    from cocode.pipelex_libraries.pipelines.doc_proofread.doc_proofread_models import DocumentationFile

    # Extract the file path from working memory
    file_path_stuff = working_memory.get_stuff_as("file_path", content_type=FilePath)
    file_path = file_path_stuff.path

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            # Extract title from first heading in markdown
            title = ""
            for line in content.split("\n"):
                if line.startswith("#"):
                    title = line.lstrip("#").strip()
                    break
            if not title:
                title = Path(file_path).stem.replace("_", " ").title()

            return DocumentationFile(file_path=file_path, doc_content=content, title=title)
    except Exception:
        # For errors, return a dummy file
        return DocumentationFile(
            file_path=file_path, doc_content="# Example Documentation\n\nThis is example documentation content.", title="Example Documentation"
        )


# Register functions in the func_registry for PipeFunc usage
func_registry.register_function(read_file_content, name="read_file_content")
func_registry.register_function(list_docs_dir_files, name="list_docs_dir_files")
