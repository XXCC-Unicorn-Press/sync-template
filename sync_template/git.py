import os
import shutil
from pathlib import Path

import typer
from git import Repo

from .config import get_syncignore_spec


class GitManager:
    def __init__(self, path: Path):
        self.repo = Repo(path)

    @classmethod
    def clone(cls, url: str, dest: Path) -> "GitManager":
        """Clone a template repository as a new project."""
        repo = Repo.clone_from(url, dest, depth=1)
        # Rename origin to template for clarity
        repo.delete_remote("origin")
        repo.create_remote("template", url)
        return cls(dest)

    @classmethod
    def setup_remote(cls, url: str, path: Path) -> "GitManager":
        """Set up template remote for an existing git repository."""
        if not (path / ".git").exists():
            raise typer.BadParameter(f"Directory {path} is not a git repository.")

        repo = Repo(path)
        # Check if template remote already exists
        try:
            repo.remote("template")
            typer.echo("Remote 'template' already exists. Updating its URL.")
            repo.delete_remote("template")
        except ValueError:
            pass

        repo.create_remote("template", url)
        return cls(path)

    def fetch_template(self):
        """Fetch updates from the template remote."""
        template_remote = self.repo.remote("template")
        template_remote.fetch()

    def merge_with_ignore(self, branch: str = "main"):
        """Merge updates from template and apply .syncignore."""
        template_ref = f"template/{branch}"

        if self.repo.is_dirty(untracked_files=True):
            raise typer.BadParameter(
                "Working directory is not clean. Commit, stash, "
                "or remove untracked files first."
            )

        # 2. Try to merge without committing
        typer.echo(f"Merging from {template_ref}...")
        try:
            self.repo.git.merge(
                template_ref, "--no-commit", "--no-ff", "--allow-unrelated-histories"
            )
        except Exception as e:
            if "CONFLICT" not in str(e):
                raise e
            typer.echo(
                "Merge resulted in conflicts. Will apply .syncignore "
                "and let user resolve others."
            )

        # 3. Apply .syncignore logic
        spec = get_syncignore_spec(Path(self.repo.working_dir))

        # Get all files currently in the index (post-merge state)
        # and all files in HEAD (pre-merge state)
        # We need to check both to handle additions and deletions/modifications

        all_potential_paths = set()
        # Paths in the current merged index
        for path, _ in self.repo.index.entries.keys():
            all_potential_paths.add(path)
        # Paths in the HEAD (before merge)
        for entry in self.repo.tree("HEAD").traverse():
            if entry.type == "blob":
                all_potential_paths.add(entry.path)

        ignored_count = 0
        for path in all_potential_paths:
            if spec.match_file(path):
                # Check if file existed in HEAD
                exists_in_head = False
                try:
                    self.repo.tree("HEAD")[path]
                    exists_in_head = True
                except KeyError:
                    exists_in_head = False

                if exists_in_head:
                    # Case: Modified or Deleted by template -> Restore from HEAD
                    typer.echo(f"Restoring ignored path: {path}")
                    self.repo.git.checkout("HEAD", "--", path)
                    ignored_count += 1
                else:
                    # Case: Added by template -> Remove completely
                    typer.echo(f"Removing new ignored path: {path}")
                    full_path = os.path.join(self.repo.working_dir, path)
                    if os.path.exists(full_path):
                        if os.path.isdir(full_path):
                            shutil.rmtree(full_path)
                        else:
                            os.remove(full_path)

                    # Remove from git index
                    try:
                        self.repo.git.rm("-rf", "--cached", path)
                    except Exception:
                        pass
                    ignored_count += 1

        # 4. Cleanup empty directories left by removed files (if they match .syncignore)
        # We walk the tree and remove empty dirs that match the spec
        for root, dirs, _files in os.walk(self.repo.working_dir, topdown=False):
            # Skip .git
            if ".git" in root:
                continue

            for d in dirs:
                dir_path = os.path.join(root, d)
                rel_dir_path = os.path.relpath(dir_path, self.repo.working_dir)

                # If this dir matches syncignore AND is empty, remove it
                if spec.match_file(rel_dir_path + "/") or spec.match_file(rel_dir_path):
                    try:
                        if not os.listdir(dir_path):
                            os.rmdir(dir_path)
                    except OSError:
                        pass

        if ignored_count > 0:
            typer.echo(f"Successfully processed {ignored_count} ignored paths.")

        typer.echo("Sync complete. Please review changes and commit.")
