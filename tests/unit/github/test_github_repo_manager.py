"""
Unit tests for GitHub repository manager functionality.
"""

import logging
import os
import shutil
import tempfile
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from cocode.github.github_repo_manager import GitHubRepoManager, GitHubRepoManagerError


class TestGitHubRepoManager:
    """Test cases for GitHub repository manager."""

    def test_is_github_url_https_format(self):
        """Test detection of HTTPS GitHub URLs."""
        assert GitHubRepoManager.is_github_url("https://github.com/owner/repo")
        assert GitHubRepoManager.is_github_url("http://github.com/owner/repo")
        assert GitHubRepoManager.is_github_url("https://github.com/owner/repo.git")
        assert GitHubRepoManager.is_github_url("https://github.com/owner/repo/tree/main")

    def test_is_github_url_ssh_format(self):
        """Test detection of SSH GitHub URLs."""
        assert GitHubRepoManager.is_github_url("git@github.com:owner/repo.git")
        assert GitHubRepoManager.is_github_url("git@github.com:owner/repo")

    def test_is_github_url_short_format(self):
        """Test detection of short GitHub identifiers."""
        assert GitHubRepoManager.is_github_url("owner/repo")
        assert GitHubRepoManager.is_github_url("microsoft/vscode")
        assert GitHubRepoManager.is_github_url("facebook/react")

        # Test ambiguous cases that should be treated as GitHub repos
        assert GitHubRepoManager.is_github_url("username/project")
        assert GitHubRepoManager.is_github_url("org/library")

    def test_is_github_url_local_paths(self):
        """Test that local paths are not detected as GitHub URLs."""
        assert not GitHubRepoManager.is_github_url("./local/path")
        assert not GitHubRepoManager.is_github_url("/absolute/path")
        assert not GitHubRepoManager.is_github_url("~/home/path")
        assert not GitHubRepoManager.is_github_url("relative/path.txt")
        assert not GitHubRepoManager.is_github_url("docs/readme.md")
        assert not GitHubRepoManager.is_github_url(".")
        assert not GitHubRepoManager.is_github_url("..")

    def test_is_github_url_invalid_formats(self):
        """Test that invalid formats are not detected as GitHub URLs."""
        assert not GitHubRepoManager.is_github_url("just-a-string")
        assert not GitHubRepoManager.is_github_url("owner/")
        assert not GitHubRepoManager.is_github_url("/repo")
        assert not GitHubRepoManager.is_github_url("")

    def test_parse_github_url_https_format(self):
        """Test parsing of HTTPS GitHub URLs."""
        owner, repo, branch = GitHubRepoManager.parse_github_url("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None

        owner, repo, branch = GitHubRepoManager.parse_github_url("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None

        owner, repo, branch = GitHubRepoManager.parse_github_url("https://github.com/owner/repo/tree/main")
        assert owner == "owner"
        assert repo == "repo"
        assert branch == "main"

        owner, repo, branch = GitHubRepoManager.parse_github_url("https://github.com/owner/repo/tree/feature/branch")
        assert owner == "owner"
        assert repo == "repo"
        assert branch == "feature/branch"

    def test_parse_github_url_ssh_format(self):
        """Test parsing of SSH GitHub URLs."""
        owner, repo, branch = GitHubRepoManager.parse_github_url("git@github.com:owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None

        owner, repo, branch = GitHubRepoManager.parse_github_url("git@github.com:owner/repo")
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None

    def test_parse_github_url_short_format(self):
        """Test parsing of short GitHub identifiers."""
        owner, repo, branch = GitHubRepoManager.parse_github_url("owner/repo")
        assert owner == "owner"
        assert repo == "repo"
        assert branch is None

        owner, repo, branch = GitHubRepoManager.parse_github_url("owner/repo@main")
        assert owner == "owner"
        assert repo == "repo"
        assert branch == "main"

    def test_parse_github_url_invalid_formats(self):
        """Test that invalid formats raise appropriate errors."""
        with pytest.raises(GitHubRepoManagerError):
            GitHubRepoManager.parse_github_url("invalid-url")

        with pytest.raises(GitHubRepoManagerError):
            GitHubRepoManager.parse_github_url("https://github.com/owner")

        with pytest.raises(GitHubRepoManagerError):
            GitHubRepoManager.parse_github_url("owner/repo/extra")

    def test_get_cache_path(self):
        """Test cache path generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)
            cache_path = manager._get_cache_path("owner", "repo")  # pyright: ignore[reportPrivateUsage]
            expected_path = Path(temp_dir) / "owner_repo"
            assert cache_path == expected_path

    def test_clone_repository_success(self, mocker: MockerFixture) -> None:
        """Test successful repository cloning."""
        mock_get_env = mocker.patch("cocode.github.github_repo_manager.get_optional_env")
        mock_get_env.return_value = "test_token"  # Mock token to avoid GitHub CLI call
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=0)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)
            cache_path = Path(temp_dir) / "test_repo"

            manager._clone_repository("owner", "repo", None, cache_path)  # pyright: ignore[reportPrivateUsage]

            # Verify git clone command was called
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "git" in args
            assert "clone" in args
            assert "--depth=1" in args

    def test_clone_repository_failure(self, mocker: MockerFixture, suppress_error_logs: None) -> None:
        """Test repository cloning failure handling."""
        from subprocess import CalledProcessError

        mock_get_env = mocker.patch("cocode.github.github_repo_manager.get_optional_env")
        mock_get_env.return_value = "test_token"
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = CalledProcessError(1, "git", stderr="Repository not found")

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)
            cache_path = Path(temp_dir) / "test_repo"

            with pytest.raises(GitHubRepoManagerError):
                manager._clone_repository("owner", "repo", None, cache_path)  # pyright: ignore[reportPrivateUsage]

    def test_get_clone_url_with_token(self, mocker: MockerFixture) -> None:
        """Test clone URL generation with authentication token."""
        mock_get_env = mocker.patch("cocode.github.github_repo_manager.get_optional_env")
        mock_get_env.return_value = "test_token"

        manager = GitHubRepoManager()
        clone_url = manager._get_clone_url("owner", "repo")  # pyright: ignore[reportPrivateUsage]  # pyright: ignore[reportPrivateUsage]

        assert clone_url == "https://test_token@github.com/owner/repo.git"

    def test_get_clone_url_with_gh_cli(self, mocker: MockerFixture) -> None:
        """Test clone URL generation using GitHub CLI."""
        mock_get_env = mocker.patch("cocode.github.github_repo_manager.get_optional_env")
        mock_get_env.return_value = None
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(stdout="cli_token\n", returncode=0)

        manager = GitHubRepoManager()
        clone_url = manager._get_clone_url("owner", "repo")  # pyright: ignore[reportPrivateUsage]

        assert clone_url == "https://cli_token@github.com/owner/repo.git"

    def test_get_clone_url_no_auth(self, mocker: MockerFixture) -> None:
        """Test clone URL generation without authentication."""
        from subprocess import CalledProcessError

        mock_get_env = mocker.patch("cocode.github.github_repo_manager.get_optional_env")
        mock_get_env.return_value = None
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = CalledProcessError(1, "gh")

        manager = GitHubRepoManager()
        clone_url = manager._get_clone_url("owner", "repo")  # pyright: ignore[reportPrivateUsage]

        assert clone_url == "https://github.com/owner/repo.git"

    def test_update_repository_success(self, mocker: MockerFixture) -> None:
        """Test successful repository update."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=0)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)
            cache_path = Path(temp_dir) / "test_repo"
            cache_path.mkdir()

            manager._update_repository(cache_path)  # pyright: ignore[reportPrivateUsage]

            # Verify git commands were called
            assert mock_run.call_count == 2  # fetch and pull

    def test_update_repository_failure(self, mocker: MockerFixture, suppress_error_logs: None) -> None:
        """Test repository update failure handling."""
        from subprocess import CalledProcessError

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = CalledProcessError(1, "git", stderr="Update failed")

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)
            cache_path = Path(temp_dir) / "test_repo"
            cache_path.mkdir()

            with pytest.raises(GitHubRepoManagerError):
                manager._update_repository(cache_path)  # pyright: ignore[reportPrivateUsage]

    def test_list_cached_repos(self):
        """Test listing cached repositories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            # Create some fake cached repos
            (Path(temp_dir) / "owner1_repo1").mkdir()
            (Path(temp_dir) / "owner2_repo2").mkdir()
            (Path(temp_dir) / "not_a_repo_file.txt").touch()

            cached_repos = manager.list_cached_repos()

            assert "owner1/repo1" in cached_repos
            assert "owner2/repo2" in cached_repos
            assert len(cached_repos) == 2

    def test_cleanup_cache(self):
        """Test cache cleanup functionality."""
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            # Create an old directory
            old_repo_dir = Path(temp_dir) / "old_repo"
            old_repo_dir.mkdir()

            # Set modification time to 10 days ago
            old_time = time.time() - (10 * 24 * 60 * 60)
            os.utime(old_repo_dir, (old_time, old_time))

            # Create a new directory
            new_repo_dir = Path(temp_dir) / "new_repo"
            new_repo_dir.mkdir()

            # Cleanup repos older than 7 days
            manager.cleanup_cache(max_age_days=7)

            # Old repo should be deleted, new repo should remain
            assert not old_repo_dir.exists()
            assert new_repo_dir.exists()

    def test_get_local_repo_path_temp_dir(self, mocker: MockerFixture) -> None:
        """Test getting local repo path with temporary directory."""
        manager = GitHubRepoManager()

        mock_clone = mocker.patch("cocode.github.github_repo_manager.GitHubRepoManager._clone_repository")
        mock_mkdtemp = mocker.patch("tempfile.mkdtemp")
        mock_mkdtemp.return_value = "/tmp/test_temp_dir"

        result = manager.get_local_repo_path("owner/repo", temp_dir=True)

        assert result == "/tmp/test_temp_dir"
        mock_clone.assert_called_once()

    def test_get_local_repo_path_cached(self, mocker: MockerFixture) -> None:
        """Test getting local repo path with existing cache."""
        mock_clone = mocker.patch("cocode.github.github_repo_manager.GitHubRepoManager._clone_repository")
        mock_update = mocker.patch("cocode.github.github_repo_manager.GitHubRepoManager._update_repository")

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            # Create existing cache directory
            cache_path = Path(temp_dir) / "owner_repo"
            cache_path.mkdir()

            result = manager.get_local_repo_path("owner/repo")

            assert result == str(cache_path)
            mock_update.assert_called_once()
            mock_clone.assert_not_called()

    def test_get_local_repo_path_fresh_clone(self, mocker: MockerFixture) -> None:
        """Test getting local repo path with fresh clone."""
        mock_clone = mocker.patch("cocode.github.github_repo_manager.GitHubRepoManager._clone_repository")

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            result = manager.get_local_repo_path("owner/repo")

            expected_path = str(Path(temp_dir) / "owner_repo")
            assert result == expected_path
            mock_clone.assert_called_once()

    def test_get_local_repo_path_force_refresh(self, mocker: MockerFixture) -> None:
        """Test getting local repo path with force refresh."""
        mock_clone = mocker.patch("cocode.github.github_repo_manager.GitHubRepoManager._clone_repository")
        mock_update = mocker.patch("cocode.github.github_repo_manager.GitHubRepoManager._update_repository")

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitHubRepoManager(cache_dir=temp_dir)

            # Create existing cache directory
            cache_path = Path(temp_dir) / "owner_repo"
            cache_path.mkdir()

            result = manager.get_local_repo_path("owner/repo", force_refresh=True)

            assert result == str(cache_path)
            mock_clone.assert_called_once()
            mock_update.assert_not_called()
