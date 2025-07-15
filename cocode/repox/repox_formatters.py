"""
Static utility functions for formatting repository output data.
"""

import os
from typing import Dict, List, Optional, Set


def build_flat_output(file_contents: Dict[str, str]) -> str:
    """Generate flat output by joining all file contents.

    Args:
        file_contents: Dictionary mapping file paths to their contents

    Returns:
        String with all file contents joined by double newlines
    """
    return "\n\n".join(file_contents.values())


def extract_full_path(line: str, repo_path: str) -> Optional[str]:
    """Extract the full path from a line of tree output.

    Args:
        line: Line from tree command output
        repo_path: Base repository path

    Returns:
        Extracted full path or None if not found
    """
    # Check for relative path patterns
    for prefix in ["./", "../"]:
        idx = line.find(prefix)
        if idx != -1:
            return line[idx:].strip()

    # Fallback to exact path match
    idx = line.find(repo_path)
    return line[idx:].strip() if idx != -1 else None


def build_import_list(file_contents: Dict[str, str]) -> str:
    """Generate import list from Python file contents.

    Args:
        file_contents: Dictionary mapping file paths to their contents

    Returns:
        String with import statements joined by double newlines
    """
    import_statements: List[str] = []
    for relative_path, file_content in file_contents.items():
        if not file_content.strip():
            continue
        if relative_path.endswith(".py"):
            module_path = relative_path.replace(".py", "").replace("/", ".")
            import_statement = f"from {module_path} import {file_content}"
            import_statements.append(import_statement)
    return "\n\n".join(import_statements)


def mark_non_empty_dirs(relative_path: str, non_empty_dirs: Set[str]) -> None:
    """Mark all parent directories of a file as non-empty.

    Args:
        relative_path: Path to the file relative to repository root
        non_empty_dirs: Set to store non-empty directory paths
    """
    dir_path: str = os.path.dirname(relative_path)
    while dir_path:
        non_empty_dirs.add(dir_path)
        dir_path = os.path.dirname(dir_path)
