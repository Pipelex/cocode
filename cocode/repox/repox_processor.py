"""
This file includes portions derived from an original work by Kirill Markin,
licensed under the MIT License, Version 2.0. Those portions are governed by the
MIT License. Copyright © 2024 Kirill Markin

All other portions of this code, including modifications, enhancements, and new features,
i.e. all of the following code as it's been entirely rewritten,
are © 2025 Evotis S.A.S., All rights reserved.
"""

import fnmatch
import os
import re
from typing import Callable, Dict, List, Optional, Set, Tuple

import pathspec
from pathspec import PathSpec
from pipelex import log
from pipelex.tools.exceptions import RootException
from pipelex.tools.misc.filetype_utils import FileType, FileTypeException

from cocode.repox.models import OutputStyle
from cocode.repox.repox_formatters import build_flat_output, build_import_list, extract_full_path, mark_non_empty_dirs
from cocode.utils import check_type_and_load_if_text, run_tree_command


class RepoxException(RootException):
    pass


REPOX_IGNORED_PATHS = [
    ".git",
    ".github",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".vscode",
    "__pycache__",
    "results/",
    "temp/",
    "__init__.py",
    "*.lock",
]

# Configuration constants for ignore patterns
IS_GITIGNORE_APPLIED = True

IGNORE_TREE_AND_CONTENT = [
    ".repo-to-text-settings.yaml",
    ".gitignore",
    ".github",
    ".DS_Store",
    ".env.example",
    ".ruff_cache/",
    ".vscode/",
    "trigger_pipeline",
    "LICENSE",
    "Makefile",
    "poetry.lock",
    "py.typed",
    "*.lock",
]

IGNORE_CONTENT = ["README.md", "LICENSE", "pyproject.toml"]

# Results directory constant
RESULTS_DIR = "results"


class RepoxProcessor:
    def __init__(
        self,
        repo_path: str,
        ignore_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        path_pattern: Optional[str] = None,
        text_processing_funcs: Optional[Dict[str, Callable[[str], str]]] = None,
        output_style: OutputStyle = OutputStyle.REPO_MAP,
    ) -> None:
        """Initialize RepoxProcessor with repository path and ignore specifications.

        Args:
            repo_path: Base directory path
            ignore_patterns: List of patterns from command line to ignore
            include_patterns: Optional list of patterns that files must match
            path_pattern: Optional regex pattern to match against file paths
            text_processing_funcs: Optional dict of text processing functions by MIME type
            output_style: Style for output format
        """
        self.repo_path = repo_path
        self.text_processing_funcs = text_processing_funcs
        self.output_style = output_style
        self.include_patterns = include_patterns
        self.path_pattern = path_pattern
        self.cli_ignore_patterns = ignore_patterns or []
        self.gitignore_spec: Optional[PathSpec]
        self.content_ignore_spec: PathSpec
        self.tree_and_content_ignore_spec: PathSpec
        self.gitignore_spec, self.content_ignore_spec, self.tree_and_content_ignore_spec = self._ignore_specs(
            repo_path=repo_path,
            cli_ignore_patterns=ignore_patterns,
        )

    def _ignore_specs(
        self,
        repo_path: str,
        cli_ignore_patterns: Optional[List[str]] = None,
    ) -> Tuple[Optional[PathSpec], PathSpec, PathSpec]:
        """Load ignore specifications from various sources.

        Args:
            repo_path: Base directory path
            cli_ignore_patterns: List of patterns from command line

        Returns:
            Tuple[Optional[PathSpec], PathSpec, PathSpec]: Tuple of gitignore_spec,
            content_ignore_spec, and tree_and_content_ignore_spec
        """
        content_ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", IGNORE_CONTENT)

        tree_and_content_ignore_list = IGNORE_TREE_AND_CONTENT.copy()
        if cli_ignore_patterns:
            log.debug(f"Adding CLI ignore patterns: {cli_ignore_patterns}")
            tree_and_content_ignore_list.extend(cli_ignore_patterns)
        tree_and_content_ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", tree_and_content_ignore_list)

        gitignore_spec: Optional[PathSpec] = None
        if IS_GITIGNORE_APPLIED:
            gitignore_path = os.path.join(repo_path, ".gitignore")
            if os.path.exists(gitignore_path):
                log.debug(f"Loading .gitignore from path: {gitignore_path}")
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", f)

        return gitignore_spec, content_ignore_spec, tree_and_content_ignore_spec

    ##########################################################################################
    # Tree structure
    ##########################################################################################

    def get_tree_structure(self) -> str:
        """Generate tree structure of the directory."""
        log.debug(f"Generating tree structure for path: {self.repo_path}")

        # Collect all ignore patterns for the tree command
        tree_ignore_patterns = REPOX_IGNORED_PATHS.copy()

        # Add CLI ignore patterns if available and we're doing tree-based output
        if self.output_style in (OutputStyle.TREE, OutputStyle.REPO_MAP) and self.cli_ignore_patterns:
            log.debug(f"Adding CLI ignore patterns to tree command: {self.cli_ignore_patterns}")
            tree_ignore_patterns.extend(self.cli_ignore_patterns)
        tree_output = run_tree_command(
            path=self.repo_path,
            ignored_patterns=tree_ignore_patterns,
            required_pattern=self.include_patterns[0] if self.include_patterns else None,
            gitignore=True,
            path_pattern=self.path_pattern,
        )
        log.verbose(f"Tree output generated:\n{tree_output}")

        # For tree-based output styles, minimize post-processing to preserve structure
        if self.output_style in (OutputStyle.TREE, OutputStyle.REPO_MAP):
            log.debug("Using minimal post-processing for tree-based output to preserve structure")
            tree_structure = tree_output
        elif not self.gitignore_spec and not self.tree_and_content_ignore_spec:
            log.debug("No .gitignore or ignore-tree-and-content specification found")
            tree_structure = tree_output
        else:
            log.debug("Filtering tree output based on ignore specifications")
            tree_structure = self._filter_tree_output(tree_output=tree_output)

        # Normalize paths by removing absolute path prefix for cleaner tree display
        if self.repo_path.startswith("/"):
            # Replace the absolute path with nothing for relative display
            tree_structure = tree_structure.replace(self.repo_path + "/", "")
            tree_structure = tree_structure.replace(self.repo_path, "")

        return tree_structure

    def _filter_tree_output(self, tree_output: str) -> str:
        """Filter the tree output based on ignore specifications."""
        lines: List[str] = tree_output.splitlines()
        non_empty_dirs: Set[str] = set()
        log.verbose(f"Lines: {lines}")

        filtered_lines = [self._process_line(line=line, non_empty_dirs=non_empty_dirs) for line in lines]

        filtered_tree_output = "\n".join(filter(None, filtered_lines))
        log.verbose(f"Filtered tree structure:\n{filtered_tree_output}")
        if not filtered_tree_output.strip():
            log.error(f"No tree structure found for path: {self.repo_path}")
            raise RepoxException(f"No tree structure found for path: {self.repo_path}")
        return filtered_tree_output

    def _process_line(self, line: str, non_empty_dirs: Set[str]) -> Optional[str]:
        """Process a single line of the tree output."""
        full_path = extract_full_path(line=line, repo_path=self.repo_path)
        log.verbose(f"Processing line: {line}")
        log.verbose(f"Extracted full_path: {full_path}")

        if not full_path or full_path == ".":
            return None

        relative_path = os.path.relpath(full_path, self.repo_path).replace(os.sep, "/")
        log.verbose(f"Normalized relative_path: {relative_path}")

        if self._should_ignore_file(
            file_path=full_path,
            relative_path=relative_path,
            should_content_ignore_spec=False,
        ):
            log.verbose(f"Ignored: {relative_path}")
            return None

        if not os.path.isdir(full_path):
            mark_non_empty_dirs(relative_path=relative_path, non_empty_dirs=non_empty_dirs)

        return line.replace("./", "", 1)

    ##########################################################################################
    # File contents
    ##########################################################################################

    def process_file_contents(self) -> Dict[str, str]:
        """Generate contents of files in the repository."""
        file_contents: Dict[str, str] = {}

        for root, _, files in os.walk(self.repo_path):
            # Skip ignored paths
            if any(ignored in root for ignored in REPOX_IGNORED_PATHS):
                continue

            # If path_pattern is specified, check if this directory matches
            if self.path_pattern:
                relative_root = os.path.relpath(root, self.repo_path).replace(os.sep, "/")
                # Use regex to check if the path matches the pattern
                if not re.search(self.path_pattern, relative_root):
                    continue

            for filename in files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, self.repo_path)

                if self._should_ignore_file(
                    file_path=file_path,
                    relative_path=relative_path,
                    should_content_ignore_spec=True,
                ):
                    continue

                log.debug(f"File not ignored: {file_path}")
                relative_path = relative_path.replace("./", "", 1)
                file_content: str
                file_type: FileType
                try:
                    file_check = check_type_and_load_if_text(file_path=file_path)
                    if isinstance(file_check, FileType):
                        # not a text file
                        file_content = self._specific_binary_file_processing(file_path=file_path, file_type=file_check)
                    else:
                        # text file
                        file_type, text_if_applicable = file_check
                        file_content = self._specific_text_file_processing(file_type=file_type, text=text_if_applicable)
                except FileTypeException as exc:
                    log.warning(f"Skipping '{file_path}' - could not determine file type: {exc}")
                    continue
                file_contents[relative_path] = file_content

        log.debug("File contents stored in dictionary")
        return file_contents

    def _specific_text_file_processing(self, file_type: FileType, text: str) -> str:
        """Process a specific text file based on its type."""
        log.debug(f"_specific_text_file_processing for type '{file_type}', text={text[:50]}")
        if self.text_processing_funcs and (text_processing_func := self.text_processing_funcs.get(file_type.mime)):
            return text_processing_func(text)
        return text

    def _specific_binary_file_processing(self, file_path: str, file_type: FileType) -> str:
        """Process a specific binary file based on its type."""
        # TODO: handle pdf files and other formats
        return f"Binary content: '{file_type.mime}'"

    def _should_ignore_file(
        self,
        file_path: str,
        relative_path: str,
        should_content_ignore_spec: bool,
        should_ignore_empty_files: bool = True,
    ) -> bool:
        """Check if a file should be ignored based on various ignore specifications.

        Args:
            file_path: Full path to the file
            relative_path: Path relative to the repository root
            should_content_ignore_spec: Whether to use the content ignore specification
            should_ignore_empty_files: Whether to ignore empty files

        Returns:
            bool: True if file should be ignored, False otherwise
        """
        relative_path = relative_path.replace(os.sep, "/")

        if relative_path.startswith("./"):
            relative_path = relative_path[2:]

        if os.path.isdir(file_path):
            relative_path += "/"

        log.verbose("Checking if file should be ignored:")
        log.verbose(f"    file_path: {file_path}")
        log.verbose(f"    relative_path: {relative_path}")
        if self._is_ignored_path(file_path=file_path):
            log.debug(f"File '{relative_path} 'is ignored because of is_ignored_path")
            return True
        if self.gitignore_spec and self.gitignore_spec.match_file(relative_path):
            log.debug(f"File '{relative_path}' is ignored because of gitignore_spec")
            return True
        if should_content_ignore_spec and self.content_ignore_spec and self.content_ignore_spec.match_file(relative_path):
            log.debug(f"File '{relative_path}' is ignored because of content_ignore_spec")
            return True
        if self.tree_and_content_ignore_spec and self.tree_and_content_ignore_spec.match_file(relative_path):
            log.debug(f"File '{relative_path}' is ignored because of tree_and_content_ignore_spec")
            return True
        if os.path.basename(file_path).startswith("repo-to-text_"):
            log.debug(f"File '{relative_path}' is ignored because of repo-to-text_ prefix")
            return True
        if should_ignore_empty_files and os.path.getsize(file_path) == 0:
            log.debug(f"File '{relative_path}' is ignored because it is empty")
            return True

        return False

    ##########################################################################################
    # Output content
    ##########################################################################################

    def build_output_content(
        self,
        tree_structure: str,
        file_contents: Dict[str, str],
    ) -> str:
        """Generate the output content for the repository."""
        match self.output_style:
            case OutputStyle.REPO_MAP:
                return self._build_repo_map(tree_structure=tree_structure, file_contents=file_contents)
            case OutputStyle.FLAT:
                return build_flat_output(file_contents=file_contents)
            case OutputStyle.IMPORT_LIST:
                return build_import_list(file_contents=file_contents)
            case OutputStyle.TREE:
                return tree_structure

    def _build_repo_map(
        self,
        tree_structure: str,
        file_contents: Dict[str, str],
    ) -> str:
        """Generate the output content for the repository."""
        output_content: List[str] = []
        project_name = os.path.basename(self.repo_path)
        output_content.append(f"Directory: {project_name}\n\n")
        output_content.append("Directory Structure:\n")
        output_content.append(f"{self.repo_path}: ```tree\n")

        if self.repo_path.startswith("/"):
            tree_structure = tree_structure.replace(self.repo_path, "")

        output_content.append(tree_structure + "\n```\n")

        for relative_path, file_content in file_contents.items():
            output_content.append(f"\n{relative_path}: ```\n")
            output_content.append(file_content)
            output_content.append("\n```\n")

        output_content.append("\n")
        return "".join(output_content)

    def _is_ignored_path(
        self,
        file_path: str,
    ) -> bool:
        """Check if a file path should be ignored based on predefined rules.

        Args:
            file_path: Path to check

        Returns:
            bool: True if path should be ignored, False otherwise
        """
        # Check for .png files
        if file_path.endswith(".png"):
            log.verbose(f"Path ignored: {file_path} (PNG file)")
            return True

        # Check against ignored paths from config
        if any(ignored in file_path for ignored in REPOX_IGNORED_PATHS):
            log.verbose(f"Path ignored: {file_path} (matches config ignored paths)")
            return True

        # Check include patterns if specified
        if self.include_patterns:
            filename = os.path.basename(file_path)
            # If none of the patterns match, ignore the file
            if not any(fnmatch.fnmatch(filename, pattern) for pattern in self.include_patterns):
                log.verbose(f"Path ignored: {file_path} (doesn't match any include patterns)")
                return True

        # Check predefined ignore rules
        ignored_dirs: List[str] = [".git"]
        ignored_files_prefix: List[str] = ["repo-to-text_"]
        is_ignored_dir = any(ignored in file_path for ignored in ignored_dirs)
        is_ignored_file = any(file_path.startswith(prefix) for prefix in ignored_files_prefix)
        result = is_ignored_dir or is_ignored_file
        if result:
            log.verbose(f"Path ignored: {file_path}")
        return result
