"""GitHub CLI commands for cocode."""

from typing import Annotated

import typer
from pipelex.tools.misc.json_utils import load_json_list_from_path
from rich.console import Console
from rich.table import Table

from cocode.github.github_wrapper import GithubWrapper, GithubWrapperError

console = Console()

github_app = typer.Typer(
    name="github",
    help="GitHub-related operations and utilities",
    add_completion=False,
    rich_markup_mode="rich",
)


@github_app.command("auth")
def auth_status() -> None:
    """Check GitHub authentication status."""
    try:
        wrapper = GithubWrapper()
        client = wrapper.connect()
        user = client.get_user()

        console.print(f"✅ [green]Authenticated as:[/green] [bold]{user.login}[/bold]")
        console.print(f"   [dim]Name:[/dim] {user.name or 'Not set'}")
        console.print(f"   [dim]Email:[/dim] {user.email or 'Not set'}")

        # Show rate limit info
        rate_limit = client.get_rate_limit()
        console.print(f"   [dim]API Rate Limit:[/dim] {rate_limit.core.remaining}/{rate_limit.core.limit}")

    except GithubWrapperError as e:
        console.print(f"❌ [red]Authentication failed:[/red] {e}")
        raise typer.Exit(code=1)


@github_app.command("check-branch")
def check_branch(
    repo: Annotated[str, typer.Argument(help="Repository in format 'owner/repo' or repo ID")],
    branch: Annotated[str, typer.Argument(help="Branch name to check")],
) -> None:
    """Check if a branch exists in a GitHub repository."""
    try:
        wrapper = GithubWrapper()
        wrapper.connect()

        # Try to convert to int for repo ID, otherwise use as string
        repo_id: str | int = repo
        try:
            repo_id = int(repo)
        except ValueError:
            pass

        exists = wrapper.is_existing_branch(repo_id, branch)

        if exists:
            console.print(f"✅ [green]Branch '[bold]{branch}[/bold]' exists in repository '[bold]{repo}[/bold]'[/green]")
        else:
            console.print(f"❌ [red]Branch '[bold]{branch}[/bold]' does not exist in repository '[bold]{repo}[/bold]'[/red]")
            raise typer.Exit(code=1)

    except GithubWrapperError as e:
        console.print(f"❌ [red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@github_app.command("repo-info")
def repo_info(
    repo: Annotated[str, typer.Argument(help="Repository in format 'owner/repo' or repo ID")],
) -> None:
    """Get basic information about a GitHub repository."""
    try:
        wrapper = GithubWrapper()
        client = wrapper.connect()

        # Try to convert to int for repo ID, otherwise use as string
        repo_id: str | int = repo
        try:
            repo_id = int(repo)
        except ValueError:
            pass

        github_repo = client.get_repo(repo_id)

        # Create a table for repo information
        table = Table(title=f"Repository: {github_repo.full_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Full Name", github_repo.full_name)
        table.add_row("Description", github_repo.description or "No description")
        table.add_row("Language", github_repo.language or "Not specified")
        table.add_row("Stars", str(github_repo.stargazers_count))
        table.add_row("Forks", str(github_repo.forks_count))
        table.add_row("Default Branch", github_repo.default_branch)
        table.add_row("Private", "Yes" if github_repo.private else "No")
        table.add_row("Created", github_repo.created_at.strftime("%Y-%m-%d"))
        table.add_row("Updated", github_repo.updated_at.strftime("%Y-%m-%d"))

        if github_repo.homepage:
            table.add_row("Homepage", github_repo.homepage)

        console.print(table)

    except GithubWrapperError as e:
        console.print(f"❌ [red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"❌ [red]Error accessing repository:[/red] {e}")
        raise typer.Exit(code=1)


@github_app.command("list-branches")
def list_branches(
    repo: Annotated[str, typer.Argument(help="Repository in format 'owner/repo' or repo ID")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum number of branches to show")] = 10,
) -> None:
    """List branches in a GitHub repository."""
    try:
        wrapper = GithubWrapper()
        client = wrapper.connect()

        # Try to convert to int for repo ID, otherwise use as string
        repo_id: str | int = repo
        try:
            repo_id = int(repo)
        except ValueError:
            pass

        github_repo = client.get_repo(repo_id)
        branches = github_repo.get_branches()

        console.print(f"📋 [bold]Branches in {github_repo.full_name}:[/bold]")

        for i, branch in enumerate(branches):
            if i >= limit:
                console.print(f"   [dim]... and {branches.totalCount - limit} more[/dim]")
                break

            is_default = "🌟 " if branch.name == github_repo.default_branch else "   "
            console.print(f"{is_default}[cyan]{branch.name}[/cyan]")

        if branches.totalCount == 0:
            console.print("   [dim]No branches found[/dim]")

    except GithubWrapperError as e:
        console.print(f"❌ [red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"❌ [red]Error accessing repository:[/red] {e}")
        raise typer.Exit(code=1)


@github_app.command("sync-labels")
def sync_labels(
    repo: Annotated[str, typer.Argument(help="Repository in format 'owner/repo' or repo ID")],
    labels_file: Annotated[str, typer.Argument(help="Path to JSON file containing labels to sync")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be done without making changes")] = False,
    delete_extra: Annotated[bool, typer.Option("--delete-extra", help="Delete labels not in the standard set")] = False,
) -> None:
    """Sync labels to a GitHub repository from a JSON file."""
    try:
        wrapper = GithubWrapper()
        wrapper.connect()

        # Try to convert to int for repo ID, otherwise use as string
        repo_id: str | int = repo
        try:
            repo_id = int(repo)
        except ValueError:
            pass

        # Get labels to sync
        try:
            labels_to_sync = load_json_list_from_path(labels_file)
            console.print(f"📂 [dim]Loading labels from: {labels_file}[/dim]")
        except Exception as e:
            console.print(f"❌ [red]Error loading labels file:[/red] {e}")
            raise typer.Exit(code=1)

        # If not deleting extra labels, only sync our labels
        labels_source = f"from {labels_file}"
        if not delete_extra:
            console.print(f"🔄 [yellow]Syncing labels {labels_source} to repository '[bold]{repo}[/bold]' (keeping existing labels)[/yellow]")
        else:
            console.print(f"🔄 [yellow]Syncing labels {labels_source} to repository '[bold]{repo}[/bold]' (will delete non-standard labels)[/yellow]")

        if dry_run:
            console.print("📋 [dim]DRY RUN - No changes will be made[/dim]")

        # Perform the sync
        created, updated, deleted = wrapper.sync_labels(
            repo_full_name_or_id=repo_id,
            labels=labels_to_sync,
            dry_run=dry_run,
            delete_extra=delete_extra,
        )

        # Show results
        if created:
            console.print(f"✅ [green]Created {len(created)} label(s):[/green]")
            for label in created:
                console.print(f"   + [green]{label}[/green]")

        if updated:
            console.print(f"🔄 [yellow]Updated {len(updated)} label(s):[/yellow]")
            for label in updated:
                console.print(f"   ~ [yellow]{label}[/yellow]")

        if deleted:
            console.print(f"❌ [red]Deleted {len(deleted)} label(s):[/red]")
            for label in deleted:
                console.print(f"   - [red]{label}[/red]")

        if not created and not updated and not deleted:
            console.print("✨ [green]All labels are already up to date![/green]")

        # Show summary
        total_changes = len(created) + len(updated) + len(deleted)
        if total_changes > 0:
            action = "would be made" if dry_run else "made"
            console.print(f"\n📊 [bold]Summary:[/bold] {total_changes} change(s) {action}")

    except GithubWrapperError as e:
        console.print(f"❌ [red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"❌ [red]Error syncing labels:[/red] {e}")
        raise typer.Exit(code=1)
