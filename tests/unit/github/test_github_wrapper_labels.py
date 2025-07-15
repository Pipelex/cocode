"""Unit tests for GitHub wrapper label sync functionality."""

import github
import pytest
from pytest_mock import MockerFixture

from cocode.github.github_wrapper import GithubWrapper, GithubWrapperError


@pytest.mark.unit
class TestGithubWrapperLabels:
    def test_sync_labels_no_client(self):
        wrapper = GithubWrapper()
        wrapper.github_client = None  # type: ignore[assignment]

        with pytest.raises(GithubWrapperError) as exc_info:
            wrapper.sync_labels("test/repo", [])

        assert "GitHub client not connected. Call connect() first" in str(exc_info.value)

    def test_sync_labels_repo_not_found(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_client.get_repo.side_effect = github.GithubException(404, "Not Found", {})
        wrapper.github_client = mock_client

        with pytest.raises(GithubWrapperError) as exc_info:
            wrapper.sync_labels("nonexistent/repo", [])

        assert "Repository 'nonexistent/repo' not found" in str(exc_info.value)

    def test_sync_labels_create_new_labels(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()

        # Mock existing labels (empty)
        mock_repo.get_labels.return_value = []
        mock_client.get_repo.return_value = mock_repo
        wrapper.github_client = mock_client

        labels_to_sync = [
            {"name": "priority:high", "color": "d73a4a", "description": "High priority"},
            {"name": "type:bug", "color": "b60205", "description": "Something isn't working"},
        ]

        created, updated, deleted = wrapper.sync_labels("test/repo", labels_to_sync, dry_run=False)

        assert created == ["priority:high", "type:bug"]
        assert updated == []
        assert deleted == []

        # Verify labels were created
        assert mock_repo.create_label.call_count == 2
        mock_repo.create_label.assert_any_call(name="priority:high", color="d73a4a", description="High priority")
        mock_repo.create_label.assert_any_call(name="type:bug", color="b60205", description="Something isn't working")

    def test_sync_labels_update_existing_labels(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()

        # Mock existing labels
        mock_existing_label = mocker.Mock()
        mock_existing_label.name = "priority:high"
        mock_existing_label.color = "old_color"
        mock_existing_label.description = "Old description"
        mock_repo.get_labels.return_value = [mock_existing_label]
        mock_client.get_repo.return_value = mock_repo
        wrapper.github_client = mock_client

        labels_to_sync = [
            {"name": "priority:high", "color": "d73a4a", "description": "High priority"},
        ]

        created, updated, deleted = wrapper.sync_labels("test/repo", labels_to_sync, dry_run=False)

        assert created == []
        assert updated == ["priority:high"]
        assert deleted == []

        # Verify label was updated
        mock_existing_label.edit.assert_called_once_with(name="priority:high", color="d73a4a", description="High priority")

    def test_sync_labels_no_update_needed(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()

        # Mock existing labels with same color and description
        mock_existing_label = mocker.Mock()
        mock_existing_label.name = "priority:high"
        mock_existing_label.color = "d73a4a"
        mock_existing_label.description = "High priority"
        mock_repo.get_labels.return_value = [mock_existing_label]
        mock_client.get_repo.return_value = mock_repo
        wrapper.github_client = mock_client

        labels_to_sync = [
            {"name": "priority:high", "color": "d73a4a", "description": "High priority"},
        ]

        created, updated, deleted = wrapper.sync_labels("test/repo", labels_to_sync, dry_run=False)

        assert created == []
        assert updated == []
        assert deleted == []

        # Verify label was not updated
        mock_existing_label.edit.assert_not_called()

    def test_sync_labels_delete_extra_labels(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()

        # Mock existing labels - one we want to keep, one to delete
        mock_keep_label = mocker.Mock()
        mock_keep_label.name = "priority:high"
        mock_keep_label.color = "d73a4a"
        mock_keep_label.description = "High priority"

        mock_delete_label = mocker.Mock()
        mock_delete_label.name = "old:label"

        mock_repo.get_labels.return_value = [mock_keep_label, mock_delete_label]
        mock_client.get_repo.return_value = mock_repo
        wrapper.github_client = mock_client

        labels_to_sync = [
            {"name": "priority:high", "color": "d73a4a", "description": "High priority"},
        ]

        created, updated, deleted = wrapper.sync_labels("test/repo", labels_to_sync, dry_run=False, delete_extra=True)

        assert created == []
        assert updated == []
        assert deleted == ["old:label"]

        # Verify extra label was deleted
        mock_delete_label.delete.assert_called_once()
        mock_keep_label.delete.assert_not_called()

    def test_sync_labels_no_delete_extra_by_default(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()

        # Mock existing labels - one we want to keep, one that would be deleted if delete_extra=True
        mock_keep_label = mocker.Mock()
        mock_keep_label.name = "priority:high"
        mock_keep_label.color = "d73a4a"
        mock_keep_label.description = "High priority"

        mock_extra_label = mocker.Mock()
        mock_extra_label.name = "old:label"

        mock_repo.get_labels.return_value = [mock_keep_label, mock_extra_label]
        mock_client.get_repo.return_value = mock_repo
        wrapper.github_client = mock_client

        labels_to_sync = [
            {"name": "priority:high", "color": "d73a4a", "description": "High priority"},
        ]

        created, updated, deleted = wrapper.sync_labels("test/repo", labels_to_sync, dry_run=False, delete_extra=False)

        assert created == []
        assert updated == []
        assert deleted == []

        # Verify no labels were deleted
        mock_extra_label.delete.assert_not_called()

    def test_sync_labels_dry_run_mode(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()

        # Mock existing labels
        mock_existing_label = mocker.Mock()
        mock_existing_label.name = "priority:medium"
        mock_existing_label.color = "old_color"
        mock_existing_label.description = "Old description"

        mock_extra_label = mocker.Mock()
        mock_extra_label.name = "old:label"

        mock_repo.get_labels.return_value = [mock_existing_label, mock_extra_label]
        mock_client.get_repo.return_value = mock_repo
        wrapper.github_client = mock_client

        labels_to_sync = [
            {"name": "priority:high", "color": "d73a4a", "description": "High priority"},
            {"name": "priority:medium", "color": "fb8500", "description": "Medium priority"},
        ]

        created, updated, deleted = wrapper.sync_labels("test/repo", labels_to_sync, dry_run=True, delete_extra=True)

        assert created == ["priority:high"]
        assert updated == ["priority:medium"]
        assert deleted == ["old:label"]

        # Verify no actual changes were made
        mock_repo.create_label.assert_not_called()
        mock_existing_label.edit.assert_not_called()
        mock_extra_label.delete.assert_not_called()

    def test_sync_labels_case_insensitive_color_comparison(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()

        # Mock existing label with uppercase color
        mock_existing_label = mocker.Mock()
        mock_existing_label.name = "priority:high"
        mock_existing_label.color = "D73A4A"  # Uppercase
        mock_existing_label.description = "High priority"
        mock_repo.get_labels.return_value = [mock_existing_label]
        mock_client.get_repo.return_value = mock_repo
        wrapper.github_client = mock_client

        labels_to_sync = [
            {"name": "priority:high", "color": "d73a4a", "description": "High priority"},  # Lowercase
        ]

        created, updated, deleted = wrapper.sync_labels("test/repo", labels_to_sync, dry_run=False)

        assert created == []
        assert updated == []  # Should not update because colors match (case-insensitive)
        assert deleted == []

        # Verify label was not updated
        mock_existing_label.edit.assert_not_called()

    def test_sync_labels_mixed_operations(self, mocker: MockerFixture):
        wrapper = GithubWrapper()
        mock_client = mocker.Mock()
        mock_repo = mocker.Mock()

        # Mock existing labels
        mock_update_label = mocker.Mock()
        mock_update_label.name = "priority:high"
        mock_update_label.color = "old_color"
        mock_update_label.description = "Old description"

        mock_keep_label = mocker.Mock()
        mock_keep_label.name = "priority:medium"
        mock_keep_label.color = "fb8500"
        mock_keep_label.description = "Medium priority"

        mock_delete_label = mocker.Mock()
        mock_delete_label.name = "old:label"

        mock_repo.get_labels.return_value = [mock_update_label, mock_keep_label, mock_delete_label]
        mock_client.get_repo.return_value = mock_repo
        wrapper.github_client = mock_client

        labels_to_sync = [
            {"name": "priority:high", "color": "d73a4a", "description": "High priority"},  # Update
            {"name": "priority:medium", "color": "fb8500", "description": "Medium priority"},  # Keep
            {"name": "priority:low", "color": "6f42c1", "description": "Low priority"},  # Create
        ]

        created, updated, deleted = wrapper.sync_labels("test/repo", labels_to_sync, dry_run=False, delete_extra=True)

        assert created == ["priority:low"]
        assert updated == ["priority:high"]
        assert deleted == ["old:label"]

        # Verify operations
        mock_repo.create_label.assert_called_once_with(name="priority:low", color="6f42c1", description="Low priority")
        mock_update_label.edit.assert_called_once_with(name="priority:high", color="d73a4a", description="High priority")
        mock_delete_label.delete.assert_called_once()
        mock_keep_label.edit.assert_not_called()
        mock_keep_label.delete.assert_not_called()
