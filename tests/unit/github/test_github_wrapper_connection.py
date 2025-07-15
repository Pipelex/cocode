"""Unit tests for GitHub wrapper connection functionality."""

import subprocess

import github
import pytest
from pytest_mock import MockerFixture

from cocode.github.github_wrapper import GithubWrapper, GithubWrapperError


@pytest.mark.unit
class TestGithubWrapperConnection:
    def test_init(self):
        wrapper = GithubWrapper()
        assert isinstance(wrapper.github_client, github.Github)

    def test_connect_with_pat_token(self, mocker: MockerFixture):
        mocker.patch("cocode.github.github_wrapper.get_optional_env", return_value="test_token")
        mock_auth_token = mocker.patch("github.Auth.Token")
        mock_github = mocker.patch("github.Github")

        mock_auth_instance = mocker.Mock()
        mock_auth_token.return_value = mock_auth_instance
        mock_client = mocker.Mock()
        mock_github.return_value = mock_client

        wrapper = GithubWrapper()
        result = wrapper.connect()

        mock_auth_token.assert_called_once_with(token="test_token")
        assert mock_github.call_count == 2  # Once in __init__, once in connect()
        mock_github.assert_called_with(auth=mock_auth_instance)
        assert wrapper.github_client == mock_client
        assert result == mock_client

    def test_connect_with_cli_token(self, mocker: MockerFixture):
        mocker.patch("cocode.github.github_wrapper.get_optional_env", return_value=None)
        mock_subprocess = mocker.patch("cocode.github.github_wrapper.subprocess.run")
        mock_auth_token = mocker.patch("github.Auth.Token")
        mock_github = mocker.patch("github.Github")

        mock_subprocess.return_value = mocker.Mock(stdout="cli_token\n")
        mock_auth_instance = mocker.Mock()
        mock_auth_token.return_value = mock_auth_instance
        mock_client = mocker.Mock()
        mock_github.return_value = mock_client

        wrapper = GithubWrapper()
        result = wrapper.connect()

        mock_subprocess.assert_called_once_with(["gh", "auth", "token"], capture_output=True, text=True, check=True)
        mock_auth_token.assert_called_once_with(token="cli_token")
        assert mock_github.call_count == 2  # Once in __init__, once in connect()
        mock_github.assert_called_with(auth=mock_auth_instance)
        assert wrapper.github_client == mock_client
        assert result == mock_client

    def test_connect_cli_command_error(self, mocker: MockerFixture):
        mocker.patch("cocode.github.github_wrapper.get_optional_env", return_value=None)
        mock_subprocess = mocker.patch("cocode.github.github_wrapper.subprocess.run")
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "gh")

        wrapper = GithubWrapper()

        with pytest.raises(GithubWrapperError) as exc_info:
            wrapper.connect()

        assert "No GITHUB_PAT in environment and GitHub CLI authentication failed" in str(exc_info.value)

    def test_connect_cli_file_not_found(self, mocker: MockerFixture):
        mocker.patch("cocode.github.github_wrapper.get_optional_env", return_value=None)
        mock_subprocess = mocker.patch("cocode.github.github_wrapper.subprocess.run")
        mock_subprocess.side_effect = FileNotFoundError()

        wrapper = GithubWrapper()

        with pytest.raises(GithubWrapperError) as exc_info:
            wrapper.connect()

        assert "No GITHUB_PAT in environment and GitHub CLI authentication failed" in str(exc_info.value)
