"""
GitHub repository manager for cloning and caching repositories.
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from pipelex import log
from pipelex.system.environment import get_optional_env

from .github_wrapper import GithubWrapper


class GitHubRepoManagerError(Exception):
    """Exception raised for GitHub repository manager errors."""

    pass


class GitHubRepoManager:
    """Manages GitHub repository cloning and caching."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the GitHub repository manager.

        Args:
            cache_dir: Directory to cache cloned repositories. If None, uses system temp directory.
        """
        if cache_dir is None:
            # Use a subdirectory in the user's home directory for persistent caching
            home_dir = Path.home()
            cache_dir = str(home_dir / ".cocode" / "cache" / "repos")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.github_wrapper = GithubWrapper()

    @staticmethod
    def is_github_url(url_or_path: str) -> bool:
        """
        Check if the given string is a GitHub URL or repository identifier.

        Args:
            url_or_path: String that might be a GitHub URL or local path

        Returns:
            True if it's a GitHub URL or repo identifier, False otherwise
        """
        # Check for full GitHub URLs
        if url_or_path.startswith(("https://github.com/", "http://github.com/", "git@github.com:")):
            return True

        # Check for short format (owner/repo)
        if "/" in url_or_path and not url_or_path.startswith((".", "/", "~")):
            # Simple heuristic: contains slash but doesn't look like a file path
            parts = url_or_path.split("/")
            if len(parts) == 2 and all(part.strip() for part in parts):
                # Additional check: shouldn't contain typical file extensions or multiple levels
                if not any(part.endswith((".txt", ".md", ".py", ".js", ".json", ".xml", ".html", ".css")) for part in parts):
                    # Basic validation: both parts should be non-empty after stripping
                    return True

        return False

    @staticmethod
    def parse_github_url(url_or_identifier: str) -> Tuple[str, str, Optional[str]]:
        """
        Parse a GitHub URL or identifier to extract owner, repo, and branch.

        Args:
            url_or_identifier: GitHub URL or owner/repo format

        Returns:
            Tuple of (owner, repo, branch) where branch can be None

        Raises:
            GitHubRepoManagerError: If the URL format is invalid
        """
        branch = None

        # Handle different GitHub URL formats
        if url_or_identifier.startswith("git@github.com:"):
            # SSH format: git@github.com:owner/repo.git
            match = re.match(r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?(?:/tree/(.+))?$", url_or_identifier)
            if not match:
                raise GitHubRepoManagerError(f"Invalid GitHub SSH URL format: {url_or_identifier}")
            owner, repo, branch = match.groups()

        elif url_or_identifier.startswith(("https://github.com/", "http://github.com/")):
            # HTTPS format: https://github.com/owner/repo[/tree/branch]
            parsed = urlparse(url_or_identifier)
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) < 2:
                raise GitHubRepoManagerError(f"Invalid GitHub URL format: {url_or_identifier}")

            owner, repo = path_parts[0], path_parts[1]

            # Remove .git extension if present
            if repo.endswith(".git"):
                repo = repo[:-4]

            # Check for branch specification in URL
            if len(path_parts) >= 4 and path_parts[2] == "tree":
                branch = "/".join(path_parts[3:])

        elif "/" in url_or_identifier and not url_or_identifier.startswith((".", "/", "~")):
            # Short format: owner/repo[@branch]
            if "@" in url_or_identifier:
                repo_part, branch = url_or_identifier.rsplit("@", 1)
            else:
                repo_part = url_or_identifier

            parts = repo_part.split("/")
            if len(parts) != 2:
                raise GitHubRepoManagerError(f"Invalid GitHub repository identifier format: {url_or_identifier}")

            owner, repo = parts

        else:
            raise GitHubRepoManagerError(f"Invalid GitHub URL or identifier: {url_or_identifier}")

        return owner, repo, branch

    def _get_cache_path(self, owner: str, repo: str) -> Path:
        """Get the cache path for a repository."""
        return self.cache_dir / f"{owner}_{repo}"

    def _get_clone_url(self, owner: str, repo: str) -> str:
        """
        Get the appropriate clone URL based on available authentication.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Clone URL (HTTPS with token if available, otherwise HTTPS public)
        """
        # Try to get GitHub token for private repos
        token = get_optional_env("GITHUB_PAT")

        if not token:
            try:
                # Try GitHub CLI
                result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
                token = result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                # No authentication available, use public HTTPS
                pass

        if token:
            return f"https://{token}@github.com/{owner}/{repo}.git"
        else:
            return f"https://github.com/{owner}/{repo}.git"

    def _clone_repository(self, owner: str, repo: str, branch: Optional[str], cache_path: Path, shallow: bool = True) -> None:
        """
        Clone a repository to the cache directory.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Optional branch to clone
            cache_path: Path where to clone the repository
            shallow: Whether to perform a shallow clone

        Raises:
            GitHubRepoManagerError: If cloning fails
        """
        clone_url = self._get_clone_url(owner, repo)

        # Prepare git clone command
        cmd = ["git", "clone"]

        if shallow:
            cmd.append("--depth=1")

        if branch:
            cmd.extend(["--branch", branch])

        cmd.extend([clone_url, str(cache_path)])

        log.info(f"Cloning {owner}/{repo} to {cache_path}")

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=self.cache_dir)
            log.info(f"Successfully cloned {owner}/{repo}")
        except subprocess.CalledProcessError as exc:
            error_msg = f"Failed to clone {owner}/{repo}: {exc.stderr}"
            log.error(error_msg)
            # Clean up partial clone if it exists
            if cache_path.exists():
                shutil.rmtree(cache_path)
            raise GitHubRepoManagerError(error_msg) from exc

    def _update_repository(self, cache_path: Path, branch: Optional[str] = None) -> None:
        """
        Update an existing cached repository.

        Args:
            cache_path: Path to the cached repository
            branch: Optional branch to checkout

        Raises:
            GitHubRepoManagerError: If update fails
        """
        log.info(f"Updating cached repository at {cache_path}")

        try:
            # Fetch latest changes
            subprocess.run(["git", "fetch", "origin"], cwd=cache_path, capture_output=True, text=True, check=True)

            # Checkout specific branch if requested
            if branch:
                subprocess.run(["git", "checkout", branch], cwd=cache_path, capture_output=True, text=True, check=True)

            # Pull latest changes
            subprocess.run(["git", "pull"], cwd=cache_path, capture_output=True, text=True, check=True)

            log.info(f"Successfully updated repository at {cache_path}")

        except subprocess.CalledProcessError as exc:
            error_msg = f"Failed to update repository at {cache_path}: {exc.stderr}"
            log.error(error_msg)
            raise GitHubRepoManagerError(error_msg) from exc

    def get_local_repo_path(
        self,
        github_url_or_identifier: str,
        force_refresh: bool = False,
        shallow: bool = True,
        temp_dir: bool = False,
    ) -> str:
        """
        Get a local path to a GitHub repository, cloning if necessary.

        Args:
            github_url_or_identifier: GitHub URL or owner/repo format
            force_refresh: If True, force a fresh clone even if cached
            shallow: Whether to perform shallow clone (faster, less history)
            temp_dir: If True, clone to a temporary directory instead of cache

        Returns:
            Local path to the repository

        Raises:
            GitHubRepoManagerError: If repository cannot be accessed
        """
        owner, repo, branch = self.parse_github_url(github_url_or_identifier)

        if temp_dir:
            # Clone to a temporary directory
            temp_path = Path(tempfile.mkdtemp(prefix=f"cocode_{owner}_{repo}_"))
            self._clone_repository(owner, repo, branch, temp_path, shallow=shallow)
            return str(temp_path)

        cache_path = self._get_cache_path(owner, repo)

        # Check if we need to clone or update
        if force_refresh and cache_path.exists():
            log.info(f"Force refresh requested, removing cached repository at {cache_path}")
            shutil.rmtree(cache_path)

        if not cache_path.exists():
            # Clone the repository
            self._clone_repository(owner, repo, branch, cache_path, shallow=shallow)
        else:
            # Repository exists, update it
            try:
                self._update_repository(cache_path, branch)
            except GitHubRepoManagerError:
                # If update fails, try a fresh clone
                log.warning(f"Update failed, attempting fresh clone of {owner}/{repo}")
                shutil.rmtree(cache_path)
                self._clone_repository(owner, repo, branch, cache_path, shallow=shallow)

        return str(cache_path)

    def cleanup_cache(self, max_age_days: int = 7) -> None:
        """
        Clean up old cached repositories.

        Args:
            max_age_days: Remove cached repos older than this many days
        """
        import time

        current_time = time.time()
        cutoff_time = current_time - (max_age_days * 24 * 60 * 60)

        log.info(f"Cleaning up cached repositories older than {max_age_days} days")

        for repo_dir in self.cache_dir.iterdir():
            if repo_dir.is_dir():
                repo_mtime = repo_dir.stat().st_mtime
                if repo_mtime < cutoff_time:
                    log.info(f"Removing old cached repository: {repo_dir}")
                    shutil.rmtree(repo_dir)

    def list_cached_repos(self) -> List[str]:
        """
        List all cached repositories.

        Returns:
            List of cached repository identifiers
        """
        cached_repos: List[str] = []
        for repo_dir in self.cache_dir.iterdir():
            if repo_dir.is_dir():
                # Convert cache directory name back to owner/repo format
                dir_name = repo_dir.name
                if "_" in dir_name:
                    cached_repos.append(dir_name.replace("_", "/", 1))

        return cached_repos
