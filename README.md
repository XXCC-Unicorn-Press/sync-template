# sync-template

`sync-template` is a CLI tool designed for managing and synchronizing projects derived from template repositories. It helps you seamlessly merge updates from the template project into your existing project while protecting your local modifications using `.syncignore`.

## Core Features

- **Rapid Initialization**: Quickly create new projects from a template repository using `git clone --depth 1`.
- **Auto-configuration**: Automatically sets the template repository as a remote named `template`.
- **Shortcut Support**: Use `gh:<owner>/<repo>` for GitHub or `glab:<owner>/<repo>` for GitLab shortcuts.
- **Smart Synchronization**: Fetches and merges updates from the template repository via `git fetch` and `git merge`.
- **.syncignore Protection**: Automatically applies ignore rules after merging to ensure specific files or directories remain in their local state (supports recursive directories).
- **Safety Checks**: Automatically verifies the working tree for uncommitted or untracked files before syncing to prevent accidental data loss.

## Installation

Ensure your system has Python 3.13+ and Git installed.

To install via pip (after publishing):
```bash
pip install sync-template
```

To install from source (using Poetry):
```bash
git clone https://github.com/your-username/sync-template.git
cd sync-template
poetry install
```

## Usage

### 1. Initialize a New Project

Create a new project from a Git template repository:

```bash
sync-template init gh:user/my-python-template my-new-project
```

Or initialize within an **existing repository** by adding only the `template` remote:

```bash
cd my-existing-repo
sync-template init gh:user/my-python-template --existing
```

The `init` command supports:
- Full HTTPS URLs: `https://github.com/user/repo.git`
- SSH URLs: `git@github.com:user/repo.git`
- GitHub shortcuts: `gh:user/repo`
- GitLab shortcuts: `glab:user/repo`

### 2. Configure Ignore Rules

Create a `.syncignore` file in the project root. The syntax is identical to `.gitignore`.

Example:
```text
# Ignore configuration files
config.json
# Ignore the entire content directory (including additions, modifications, and deletions)
content/
# Ignore specific local-only scripts
scripts/local_only.sh
```

### 3. Sync Updates

When the template repository has updates, run the following in your project root:

```bash
sync-template sync
```

By default, it syncs the `main` branch. To sync a different branch, use the `--branch` parameter:

```bash
sync-template sync --branch develop
```

## How It Works

1. **Workflow Check**: Ensures there are no uncommitted or untracked changes in the current branch.
2. **Fetch Updates**: Executes `git fetch template`.
3. **Merge Attempt**: Executes `git merge --no-commit template/<branch>`.
4. **Apply Ignore Logic**:
   - Traverses all paths matched by `.syncignore`.
   - If a path existed before the sync, it uses `git checkout HEAD` to restore its content and automatically resolve conflicts.
   - If a path was added by the template, it physically removes the file and clears it from the Git index.
   - **Automatic Cleanup**: Recursively cleans up empty directories left behind by the removal process.
5. **Finalization**: Prompts the user to review the merge result and commit.

## Development & Contribution

This project uses [Poetry](https://python-poetry.org/) for dependency management.

- **Run Tests**: `poetry run pytest`
- **Linting Check**: `poetry run ruff check .`
- **Format Code**: `poetry run ruff format .`

## License

This project is licensed under the [MIT License](LICENSE).
