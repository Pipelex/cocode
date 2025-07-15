import subprocess
from typing import Dict, List, Tuple

import github
from pipelex.tools.environment import get_optional_env


class GithubWrapperError(Exception):
    pass


class GithubWrapper:
    def __init__(self):
        self.github_client = github.Github()

    def connect(self) -> github.Github:
        """
        Establishes connection to GitHub using either PAT from environment or GitHub CLI.

        Raises:
            GithubWrapperError: If authentication fails
        """
        # First try to get token from environment
        token = get_optional_env("GITHUB_PAT")

        # If no token in environment, try CLI
        if not token:
            try:
                result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
                token = result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError) as exc:
                raise GithubWrapperError("No GITHUB_PAT in environment and GitHub CLI authentication failed") from exc

        github_auth = github.Auth.Token(token=token)
        self.github_client = github.Github(auth=github_auth)
        return self.github_client

    def is_existing_branch(self, repo_full_name_or_id: str | int, branch_name: str) -> bool:
        if not self.github_client:
            raise GithubWrapperError("GitHub client not connected. Call connect() first")

        try:
            repo = self.github_client.get_repo(full_name_or_id=repo_full_name_or_id)
        except github.GithubException as exc:
            raise GithubWrapperError(f"Repository '{repo_full_name_or_id}' not found") from exc

        try:
            repo.get_branch(branch_name)
            return True
        except github.GithubException:
            return False

    def sync_labels(
        self, repo_full_name_or_id: str | int, labels: List[Dict[str, str]], dry_run: bool = False, delete_extra: bool = False
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Sync labels to a GitHub repository.

        Args:
            repo_full_name_or_id: Repository identifier (owner/repo or repo ID)
            labels: List of label dictionaries with 'name', 'color', and 'description' keys
            dry_run: If True, only return what would be done without making changes
            delete_extra: If True, delete labels not in the provided set

        Returns:
            Tuple of (created_labels, updated_labels, deleted_labels)

        Raises:
            GithubWrapperError: If GitHub client not connected or repository not found
        """
        if not self.github_client:
            raise GithubWrapperError("GitHub client not connected. Call connect() first")

        try:
            repo = self.github_client.get_repo(full_name_or_id=repo_full_name_or_id)
        except github.GithubException as exc:
            raise GithubWrapperError(f"Repository '{repo_full_name_or_id}' not found") from exc

        # Get existing labels
        existing_labels = {label.name: label for label in repo.get_labels()}
        desired_labels = {label["name"]: label for label in labels}

        created_labels: List[str] = []
        updated_labels: List[str] = []
        deleted_labels: List[str] = []

        # Create or update labels
        for label_name, label_data in desired_labels.items():
            if label_name in existing_labels:
                # Check if label needs updating
                existing_label = existing_labels[label_name]
                needs_update = existing_label.color.lower() != label_data["color"].lower() or existing_label.description != label_data["description"]

                if needs_update:
                    updated_labels.append(label_name)
                    if not dry_run:
                        existing_label.edit(name=label_data["name"], color=label_data["color"], description=label_data["description"])
            else:
                # Create new label
                created_labels.append(label_name)
                if not dry_run:
                    repo.create_label(name=label_data["name"], color=label_data["color"], description=label_data["description"])

        # Find labels to delete (existing labels not in desired set)
        if delete_extra:
            for label_name in existing_labels:
                if label_name not in desired_labels:
                    deleted_labels.append(label_name)
                    if not dry_run:
                        existing_labels[label_name].delete()

        return created_labels, updated_labels, deleted_labels
