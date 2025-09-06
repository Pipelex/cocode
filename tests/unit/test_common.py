"""
Unit tests for common utilities.
"""

import logging

import pytest
import typer

from cocode.common import validate_repo_path


class TestValidateRepoPath:
    """Test cases for repository path validation."""

    def test_validate_local_path_exists(self, mocker):
        """Test validation of existing local path."""
        mock_path_exists = mocker.patch("cocode.common.path_exists")
        mock_path_exists.return_value = True

        result = validate_repo_path("/existing/local/path")

        # Should return absolute path
        assert result.endswith("/existing/local/path")
        mock_path_exists.assert_called_once()

    def test_validate_local_path_not_exists(self, mocker, suppress_error_logs):
        """Test validation of non-existing local path."""
        mock_path_exists = mocker.patch("cocode.common.path_exists")
        mock_path_exists.return_value = False

        with pytest.raises(typer.Exit):
            validate_repo_path("/nonexistent/local/path")

    def test_validate_github_url_success(self, mocker):
        """Test validation of GitHub URL with successful cloning."""
        mock_manager_class = mocker.patch("cocode.common.GitHubRepoManager")
        mock_manager = mocker.MagicMock()
        mock_manager.get_local_repo_path.return_value = "/tmp/cloned/repo"
        mock_manager_class.return_value = mock_manager
        mock_manager_class.is_github_url.return_value = True

        result = validate_repo_path("https://github.com/owner/repo")

        assert result == "/tmp/cloned/repo"
        mock_manager.get_local_repo_path.assert_called_once_with("https://github.com/owner/repo", shallow=True)

    def test_validate_github_url_failure(self, mocker, suppress_error_logs):
        """Test validation of GitHub URL with cloning failure."""
        mock_manager_class = mocker.patch("cocode.common.GitHubRepoManager")
        mock_manager = mocker.MagicMock()
        mock_manager.get_local_repo_path.side_effect = Exception("Clone failed")
        mock_manager_class.return_value = mock_manager
        mock_manager_class.is_github_url.return_value = True

        with pytest.raises(typer.Exit):
            validate_repo_path("https://github.com/owner/repo")

    def test_validate_short_github_format(self, mocker):
        """Test validation of short GitHub format."""
        mock_manager_class = mocker.patch("cocode.common.GitHubRepoManager")
        mock_manager = mocker.MagicMock()
        mock_manager.get_local_repo_path.return_value = "/tmp/cloned/repo"
        mock_manager_class.return_value = mock_manager
        mock_manager_class.is_github_url.return_value = True

        result = validate_repo_path("owner/repo")

        assert result == "/tmp/cloned/repo"
        mock_manager.get_local_repo_path.assert_called_once_with("owner/repo", shallow=True)
