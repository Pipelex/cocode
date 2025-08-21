from pathlib import Path
from typing import List

from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.stuffs.stuff_content import ListContent
from pipelex.tools.func_registry import func_registry

from cocode.pipelex_libraries.pipelines.doc_proofread.doc_proofread_models import CodebaseFileContent, DocumentationFile, FilePath


def create_documentation_files_from_paths(doc_file_paths: List[str], doc_dir: str = "docs/") -> List[DocumentationFile]:
    """Create DocumentationFile objects from file paths.

    Args:
        doc_file_paths: List of documentation file paths
        doc_dir: Base documentation directory (used for filtering)

    Returns:
        List of DocumentationFile objects
    """
    doc_files: List[DocumentationFile] = []

    for file_path in doc_file_paths:
        # Skip if not in doc_dir (when specified)
        if doc_dir and doc_dir not in file_path:
            continue

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

                doc_files.append(DocumentationFile(file_path=file_path, doc_content=content, title=title))
        except Exception as e:
            print(f"Warning: Could not read file {file_path}: {e}")
            continue

    return doc_files


def read_file_content(working_memory: WorkingMemory) -> ListContent[CodebaseFileContent]:
    """Read the content of related codebase files.

    Args:
        working_memory: Working memory containing related_file_paths

    Returns:
        ListContent of CodebaseFileContent objects
    """

    file_paths_list = working_memory.get_stuff_as_list("related_file_paths", item_type=FilePath)

    codebase_files: List[CodebaseFileContent] = []
    for file_path in file_paths_list.items:
        try:
            with open(file_path.path, "r", encoding="utf-8") as file:
                content = file.read()
                codebase_files.append(CodebaseFileContent(file_path=file_path.path, file_content=content))
        except Exception as e:
            codebase_files.append(
                CodebaseFileContent(file_path=file_path.path, file_content=f"# File not found or unreadable: {file_path.path}\n# Error: {str(e)}")
            )

    return ListContent[CodebaseFileContent](items=codebase_files)


func_registry.register_function(read_file_content, name="read_file_content")
