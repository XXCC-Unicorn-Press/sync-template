from pathlib import Path

import typer

from .git import GitManager

app = typer.Typer(help="CLI tool to synchronize projects with their templates.")


@app.command()
def init(
    url: str = typer.Argument(..., help="Template repository URL"),
    dest: Path | None = typer.Argument(
        None, help="Destination directory (defaults to repo name)"
    ),
):
    """Initialize a new project from a template."""
    if dest is None:
        dest = Path(url.split("/")[-1].replace(".git", ""))

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
