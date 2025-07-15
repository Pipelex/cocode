import os
import subprocess

import pytest

from cocode.github.github_wrapper import GithubWrapper, GithubWrapperError


@pytest.mark.integration
@pytest.mark.gha_disabled
class TestGithubWrapperIntegration:
    """Integration tests that require actual GitHub connectivity."""

    def test_connect_with_real_credentials(self):
        """Test connecting to GitHub with real credentials (PAT or CLI)."""
        wrapper = GithubWrapper()

        # Skip if no credentials available
        if not os.getenv("GITHUB_PAT"):
            try:
                subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pytest.skip("No GitHub credentials available (no GITHUB_PAT env var and no gh CLI auth)")

        # Should be able to connect without raising an exception
        github_client = wrapper.connect()
        assert github_client is not None
        assert wrapper.github_client is not None

    def test_get_authenticated_user(self):
        """Test that we can get the authenticated user info."""
        wrapper = GithubWrapper()

        # Skip if no credentials available
        if not os.getenv("GITHUB_PAT"):
            try:
                subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pytest.skip("No GitHub credentials available")

        github_client = wrapper.connect()
        user = github_client.get_user()

        # Should have a login name
        assert user.login is not None
        assert isinstance(user.login, str)
        assert len(user.login) > 0

    def test_is_existing_branch_real_repo(self):
        """Test checking for existing branches on a real public repository."""
        wrapper = GithubWrapper()

        # Skip if no credentials available
        if not os.getenv("GITHUB_PAT"):
            try:
                subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pytest.skip("No GitHub credentials available")

        wrapper.connect()

        # Test with a well-known public repository
        # GitHub's own Hello-World repository should have a main/master branch
        public_repo = "octocat/Hello-World"

        # Test existing branch (main is common, but some repos use master)
        has_main = wrapper.is_existing_branch(public_repo, "main")
        has_master = wrapper.is_existing_branch(public_repo, "master")

        # At least one of these should exist
        assert has_main or has_master, "Public repo should have either 'main' or 'master' branch"

        # Test non-existing branch
        has_nonexistent = wrapper.is_existing_branch(public_repo, "definitely-does-not-exist-branch-name-12345")
        assert not has_nonexistent

    def test_is_existing_branch_nonexistent_repo(self):
        """Test checking branches on a repository that doesn't exist."""
        wrapper = GithubWrapper()

        # Skip if no credentials available
        if not os.getenv("GITHUB_PAT"):
            try:
                subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pytest.skip("No GitHub credentials available")

        wrapper.connect()

        # Use a repository name that definitely doesn't exist
        nonexistent_repo = "this-user-definitely-does-not-exist-12345/this-repo-does-not-exist-67890"

        with pytest.raises(GithubWrapperError) as exc_info:
            wrapper.is_existing_branch(nonexistent_repo, "main")

        assert "not found" in str(exc_info.value).lower()

    def test_rate_limit_info(self):
        """Test that we can get rate limit information from GitHub API."""
        wrapper = GithubWrapper()

        # Skip if no credentials available
        if not os.getenv("GITHUB_PAT"):
            try:
                subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pytest.skip("No GitHub credentials available")

        github_client = wrapper.connect()
        rate_limit = github_client.get_rate_limit()

        # Should have core rate limit info
        assert rate_limit.core is not None
        assert rate_limit.core.limit > 0
        assert rate_limit.core.remaining >= 0
        assert rate_limit.core.reset is not None
