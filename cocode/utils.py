import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from pipelex import log
from pipelex.tools.exceptions import RootException
from pipelex.tools.misc.file_utils import load_text_from_path
from pipelex.tools.misc.filetype_utils import FileType, detect_file_type_from_path


class NoDifferencesFound(RootException):
    pass


def run_tree_command(
    path: str,
    nb_levels: Optional[int] = None,
    ignored_patterns: Optional[List[str]] = None,
    required_pattern: Optional[str] = None,
    gitignore: bool = True,
    path_pattern: Optional[str] = None,
) -> str:
    """Run the tree command and return its output."""
    if shutil.which("tree") is None:
        raise RuntimeError(
            """The 'tree' command is not available.
                Please install it using one of the following commands:
                For MacOS: brew install tree
                For Debian-based systems (e.g., Ubuntu): sudo apt-get install tree
                For Red Hat-based systems (e.g., Fedora, CentOS): sudo yum install tree
            """
        )

    tree_params = ["tree"]
    if ignored_patterns:
        for ignored_path in ignored_patterns:
            tree_params.extend(["-I", ignored_path])
    if required_pattern:
        tree_params.extend(["-P", required_pattern])
        log.debug(f"Required pattern: {required_pattern}")
    tree_params.extend(["-a", "-f", "--noreport", path])
    if nb_levels is not None:
        tree_params.extend(["-L", str(nb_levels)])
    if gitignore:
        tree_params.extend(["--gitignore"])

    # Run tree command
    result = subprocess.run(tree_params, stdout=subprocess.PIPE, check=True)

    # Filter output based on path_pattern if specified
    if path_pattern:
        lines = result.stdout.decode("utf-8").splitlines()
        filtered_lines = [line for line in lines if re.search(path_pattern, line)]
        return "\n".join(filtered_lines)

    return result.stdout.decode("utf-8")


def format_with_ruff(python_code: str) -> str:
    """
    Format the python code using ruff.
    Returns the formatted code or the original code if formatting fails.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py") as temp_file:
        temp_file.write(python_code)
        temp_file.flush()
        try:
            subprocess.run(
                args=["ruff", "format", temp_file.name],
                check=True,
                capture_output=True,
                text=True,
            )
            return Path(temp_file.name).read_text()
        except subprocess.CalledProcessError:
            return python_code


def check_type_and_load_if_text(file_path: str) -> FileType | Tuple[FileType, str]:
    """
    Check the file type and load its content if it's a text file.

    This function attempts to load a file as text and determine its type. If the file
    can be decoded as UTF-8 text, it returns a tuple containing the determined text
    file type along with the file content. If the file cannot be decoded as UTF-8
    (e.g., binary files), it returns only the detected file type.

    Args:
        file_path (str): Path to the file to check and potentially load.

    Returns:
        FileType | Tuple[FileType, str]: Either:
            - FileType: The detected file type for binary files
            - Tuple[FileType, str]: A tuple containing the file type and text content for text files

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read due to permissions.
    """
    try:
        text = load_text_from_path(file_path)
        text_file_type = determine_text_file_type(file_path)
        return text_file_type, text
    except UnicodeDecodeError:
        # this is not an utf-8 text file
        file_type = detect_file_type_from_path(file_path)
        return file_type


def determine_text_file_type(file_path: str) -> FileType:
    mime: str
    extension = Path(file_path).suffix
    match extension:
        # Python files
        case ".py":
            mime = "text/x-python"
        case ".pyi":
            mime = "text/x-python"

        # JavaScript/TypeScript files
        case ".js":
            mime = "text/javascript"
        case ".jsx":
            mime = "text/javascript"
        case ".ts":
            mime = "text/typescript"
        case ".tsx":
            mime = "text/typescript"

        # Web files
        case ".html":
            mime = "text/html"
        case ".css":
            mime = "text/css"

        # Configuration files
        case ".json":
            mime = "application/json"
        case ".yaml":
            mime = "text/yaml"
        case ".yml":
            mime = "text/yaml"
        case ".toml":
            mime = "text/toml"
        case ".env":
            mime = "text/plain"

        # Documentation
        case ".md":
            mime = "text/markdown"
        case ".txt":
            mime = "text/plain"

        # Shell scripts
        case ".sh":
            mime = "text/x-sh"

        # Other common languages
        case ".java":
            mime = "text/x-java"
        case ".c":
            mime = "text/x-c"
        case ".cpp":
            mime = "text/x-c++"
        case ".h":
            mime = "text/x-c"
        case ".go":
            mime = "text/x-go"
        case ".rs":
            mime = "text/x-rust"
        case ".rb":
            mime = "text/x-ruby"
        case ".sql":
            mime = "text/x-sql"

        # Build files
        case ".gitignore":
            mime = "text/plain"
        case "Dockerfile":
            mime = "text/x-dockerfile"

        # Data files
        case ".csv":
            mime = "text/csv"
        case ".xml":
            mime = "text/xml"

        # Default case
        case _:
            mime = "text/plain"
    return FileType(extension=extension, mime=mime)


def run_git_diff_command(repo_path: str, version: str, ignore_patterns: Optional[List[str]] = None) -> str:
    """Run git diff command comparing current version to specified version."""
    if shutil.which("git") is None:
        raise RuntimeError(
            """The 'git' command is not available.
                Please install git to use this functionality.
            """
        )

    try:
        # Default patterns to exclude from diff
        default_ignore_patterns = [
            "uv.lock",
            "poetry.lock",
            "node_modules",
            "node_modules/**",
            "*.lock",
            "*.pyc",
            "__pycache__",
            ".git",
            ".venv",
            "build/",
            "dist/",
            "*.log",
            "temp/",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        ]

        # Combine default patterns with user-provided patterns
        all_ignore_patterns = default_ignore_patterns + (ignore_patterns or [])

        # Build git command with exclusions
        git_cmd = [
            "git",
            "diff",
            version,
            "--unified=0",
            "--",
            ".",
        ]

        # Add exclusion patterns
        for pattern in all_ignore_patterns:
            git_cmd.append(f":(exclude){pattern}")

        # Change to the repository directory and run git diff
        result = subprocess.run(
            git_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

        diff_text = result.stdout
        if not diff_text.strip():
            raise NoDifferencesFound(f"No differences found between current version and '{version}' in '{repo_path}'")

        log.info(f"Generated git diff with {len(diff_text.splitlines())} lines")
        return diff_text

    except subprocess.CalledProcessError as e:
        error_msg = f"Git diff command failed: {e.stderr}"
        log.error(error_msg)
        raise RuntimeError(error_msg)
