"""
Integration tests for GitHub functionality.

These tests require network access and may use GitHub API.
Mark as slow or skip in CI if needed.
"""

import logging
import os
import tempfile
from pathlib import Path

import pytest

from cocode.github.github_repo_manager import GitHubRepoManager, GitHubRepoManagerError


@pytest.mark.integration
@pytest.mark.gha_disabled
class TestGitHubIntegration:
    """Integration tests for GitHub repository manager."""

    def test_clone_public_repository(self):
        """Test cloning a small public repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            # Use a small, stable public Python repository for testing
            repo_path = manager.get_local_repo_path("jazzband/pip-tools", shallow=True)

            # Verify the repository was cloned
            assert os.path.exists(repo_path)
            assert os.path.isdir(repo_path)

            # Verify it's a git repository
            git_dir = Path(repo_path) / ".git"
            assert git_dir.exists()

            # Verify some expected files exist
            readme_path = Path(repo_path) / "README.md"
            assert readme_path.exists()

            # Verify it's a Python project
            setup_py = Path(repo_path) / "setup.py"
            pyproject_toml = Path(repo_path) / "pyproject.toml"
            assert setup_py.exists() or pyproject_toml.exists()

    def test_clone_nonexistent_repository(self, suppress_error_logs: None) -> None:
        """Test cloning a non-existent repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            with pytest.raises(GitHubRepoManagerError):
                manager.get_local_repo_path("nonexistent-user/nonexistent-repo-12345", shallow=True)

    def test_cache_functionality(self):
        """Test that caching works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            # First clone
            repo_path1 = manager.get_local_repo_path("jazzband/pip-tools", shallow=True)

            # Second access should use cache
            repo_path2 = manager.get_local_repo_path("jazzband/pip-tools", shallow=True)

            # Paths should be the same
            assert repo_path1 == repo_path2

            # Verify cache directory contains the repo
            cached_repos = manager.list_cached_repos()
            assert "jazzband/pip-tools" in cached_repos

    def test_force_refresh(self):
        """Test force refresh functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            # First clone
            repo_path1 = manager.get_local_repo_path("jazzband/pip-tools", shallow=True)

            # Create a marker file to detect refresh
            marker_file = Path(repo_path1) / "test_marker"
            marker_file.touch()

            # Force refresh should remove the marker
            repo_path2 = manager.get_local_repo_path("jazzband/pip-tools", force_refresh=True)

            assert repo_path1 == repo_path2
            assert not marker_file.exists()  # Should be gone after refresh

    def test_temp_directory_mode(self):
        """Test temporary directory mode."""
        manager = GitHubRepoManager()

        repo_path = manager.get_local_repo_path("jazzband/pip-tools", temp_dir=True, shallow=True)

        # Verify it's in a temporary location (not in cache)
        # Check for common temp directory patterns across different OS
        temp_indicators = ["/tmp", "temp", "/var/folders", "\\temp\\", "AppData\\Local\\Temp"]
        assert any(indicator in repo_path.lower() for indicator in temp_indicators)

        # Verify the repository exists and is valid
        assert os.path.exists(repo_path)
        git_dir = Path(repo_path) / ".git"
        assert git_dir.exists()

    def test_branch_specification(self):
        """Test cloning specific branches."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            # First clone without branch to get the default branch
            default_repo_path = manager.get_local_repo_path("jazzband/pip-tools", shallow=True)
            assert os.path.exists(default_repo_path)
            assert os.path.isdir(default_repo_path)

            # Now clone main branch specifically (most modern Python repos use main)
            repo_path = manager.get_local_repo_path("jazzband/pip-tools@main", shallow=True, force_refresh=True)

            # Verify the repository was cloned
            assert os.path.exists(repo_path)
            assert os.path.isdir(repo_path)
