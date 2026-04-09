from pathlib import Path

import typer

from .git import GitManager

app = typer.Typer(help="CLI tool to synchronize projects with their templates.")


@app.command()
def init(
    url: str = typer.Argument(
        ..., help="Template repository URL or shortcut (gh:, glab:)"
    ),
    dest: Path | None = typer.Argument(
        None, help="Destination directory (defaults to repo name)"
    ),
    existing: bool = typer.Option(
        False, "--existing", help="Initialize on an existing repository (skip clone)"
    ),
):
    """Initialize a new project from a template."""
    # Transform shortcuts
    if url.startswith("gh:"):
        repo_path = url.split("gh:")[1]
        url = f"https://github.com/{repo_path}.git"
    elif url.startswith("glab:"):
        repo_path = url.split("glab:")[1]
        url = f"https://gitlab.com/{repo_path}.git"

    if dest is None:
        if existing:
            dest = Path.cwd()
        else:
            # Extract name from URL, handling potential .git suffix
            repo_name = url.split("/")[-1].replace(".git", "")
            dest = Path(repo_name)

    if existing:
        typer.echo(f"Setting up template remote in existing repository at {dest}...")
        GitManager.setup_remote(url, dest)
        typer.echo("Project initialized successfully.")
    else:
        if dest.exists() and any(dest.iterdir()):
            typer.echo(f"Error: Directory {dest} already exists and is not empty.")
            raise typer.Exit(code=1)

        typer.echo(f"Creating project from {url} in {dest}...")
        GitManager.clone(url, dest)
        typer.echo("Project initialized successfully.")


@app.command()
def sync(
    branch: str = typer.Option("main", help="Branch from template to sync from"),
):
    """Sync updates from the template repository."""
    current_dir = Path.cwd()
    if not (current_dir / ".git").exists():
        typer.echo("Error: Current directory is not a Git repository.")
        raise typer.Exit(code=1)

    try:
        git_manager = GitManager(current_dir)
        git_manager.fetch_template()
        git_manager.merge_with_ignore(branch)
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
