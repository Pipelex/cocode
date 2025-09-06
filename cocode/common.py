"""
Common utilities and types shared across CLI modules.
"""

from pathlib import Path
from typing import Optional

import typer
from pipelex import log
from pipelex.tools.misc.file_utils import path_exists
from pipelex.types import StrEnum

from cocode.github.github_repo_manager import GitHubRepoManager
from cocode.repox.repox_processor import RESULTS_DIR


class PipeCode(StrEnum):
    """Pipeline codes for SWE analysis operations."""

    EXTRACT_ONBOARDING_DOCUMENTATION = "extract_onboarding_documentation"
    EXTRACT_FUNDAMENTALS = "extract_fundamentals"
    EXTRACT_ENVIRONMENT_BUILD = "extract_environment_build"
    EXTRACT_CODING_STANDARDS = "extract_coding_standards"
    EXTRACT_TEST_STRATEGY = "extract_test_strategy"
    EXTRACT_CONTEXTUAL_GUIDELINES = "extract_contextual_guidelines"
    EXTRACT_COLLABORATION = "extract_collaboration"
    EXTRACT_FEATURES_RECAP = "extract_features_recap"

    DOC_PROOFREAD = "doc_proofread"
    DOC_UPDATE = "doc_update"
    AI_INSTRUCTION_UPDATE = "ai_instruction_update"

    # SWE diff analysis
    WRITE_CHANGELOG = "write_changelog"
    WRITE_CHANGELOG_ENHANCED = "write_changelog_enhanced"

    # Text utilities
    GENERATE_SPLIT_IDENTIFIERS = "generate_split_identifiers"

    # SWE docs consistency check
    CHECK_DOCS_INCONSISTENCIES = "check_doc_inconsistencies"


def get_pipe_descriptions() -> str:
    """Generate help text with pipe descriptions from TOML."""
    descriptions = {
        "extract_onboarding_documentation": "Extract comprehensive onboarding documentation from software project docs",
        "extract_fundamentals": "Extract fundamental project information from documentation",
        "extract_environment_build": "Extract environment setup and build information from documentation",
        "extract_coding_standards": "Extract code quality and style information from documentation",
        "extract_test_strategy": "Extract testing strategy and procedures from documentation",
        "extract_contextual_guidelines": "Extract contextual development guidelines from documentation",
        "extract_collaboration": "Extract collaboration and workflow information from documentation",
        "extract_features_recap": "Extract and analyze software features from documentation",
        "doc_proofread": "Systematically proofread documentation against actual codebase to find inconsistencies",
        "doc_update": "Generate documentation update suggestions for docs/ directory",
        "ai_instruction_update": "Generate AI instruction update suggestions for AGENTS.md, CLAUDE.md, cursor rules",
        "write_changelog": "Write a comprehensive changelog for a software project from git diff",
        "write_changelog_enhanced": "Write a comprehensive changelog with draft and polish steps from git diff",
        "generate_split_identifiers": "Analyze large text and generate optimal split identifiers",
        "check_doc_inconsistencies": "Identify inconsistencies in a set of software engineering documents",
    }

    help_text = "\n\n"
    for code, description in descriptions.items():
        help_text += f"  • [bold cyan]{code}[/bold cyan]: {description}\n\n\n"

    return help_text


def validate_repo_path(repo_path: str) -> str:
    """
    Validate and convert repo_path to absolute path.

    For GitHub URLs, this will clone the repository and return the local path.
    For local paths, this validates the path exists.
    """
    # Check if it's a GitHub URL or identifier
    if GitHubRepoManager.is_github_url(repo_path):
        log.info(f"Detected GitHub repository: {repo_path}")
        repo_manager = GitHubRepoManager()
        try:
            local_path = repo_manager.get_local_repo_path(repo_path, shallow=True)
            log.info(f"GitHub repository cloned to: {local_path}")
            return local_path
        except Exception as exc:
            log.error(f"[ERROR] Failed to clone GitHub repository '{repo_path}': {exc}")
            raise typer.Exit(code=1) from exc

    # Handle local path
    repo_path = str(Path(repo_path).resolve())

    if not path_exists(repo_path):
        log.error(f"[ERROR] Repo path '{repo_path}' does not exist")
        raise typer.Exit(code=1)

    return repo_path


def get_output_dir(output_dir: Optional[str]) -> str:
    """Get output directory from parameter or config."""
    if output_dir is None:
        return RESULTS_DIR
    return output_dir
