"""Unit tests for GitHub wrapper branch functionality."""

import github
import pytest
from pytest_mock import MockerFixture

from cocode.github.github_wrapper import GithubWrapper, GithubWrapperError


@pytest.mark.unit
class TestGithubWrapperBranches:
    def test_is_existing_branch_no_client(self):
        wrapper = GithubWrapper()
        wrapper.github_client = None  # type: ignore[assignment]

        with pytest.raises(GithubWrapperError) as exc_info:
            wrapper.is_existing_branch("test/repo", "main")

        assert "GitHub client not connected. Call connect() first" in str(exc_info.value)

    def test_is_existing_branch_repo_not_found(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_client.get_repo.side_effect = github.GithubException(404, "Not Found", {})
        wrapper.github_client = mock_client

        with pytest.raises(GithubWrapperError) as exc_info:
            wrapper.is_existing_branch("nonexistent/repo", "main")

        assert "Repository 'nonexistent/repo' not found" in str(exc_info.value)

    def test_is_existing_branch_branch_exists(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()
        mock_branch = mocker.Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_repo.get_branch.return_value = mock_branch
        wrapper.github_client = mock_client

        result = wrapper.is_existing_branch("test/repo", "existing_branch")

        mock_client.get_repo.assert_called_once_with(full_name_or_id="test/repo")
        mock_repo.get_branch.assert_called_once_with("existing_branch")
        assert result is True

    def test_is_existing_branch_branch_not_exists(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_repo.get_branch.side_effect = github.GithubException(404, "Not Found", {})
        wrapper.github_client = mock_client

        result = wrapper.is_existing_branch("test/repo", "nonexistent_branch")

        mock_client.get_repo.assert_called_once_with(full_name_or_id="test/repo")
        mock_repo.get_branch.assert_called_once_with("nonexistent_branch")
        assert result is False

    def test_is_existing_branch_with_repo_id(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()
        mock_branch = mocker.Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_repo.get_branch.return_value = mock_branch
        wrapper.github_client = mock_client

        result = wrapper.is_existing_branch(12345, "main")

        mock_client.get_repo.assert_called_once_with(full_name_or_id=12345)
        mock_repo.get_branch.assert_called_once_with("main")
        assert result is True
