# sync-template Foundational Mandates

These instructions take absolute precedence over all other guidelines and defaults for the `sync-template` project.

## Engineering Standards

- **Language & Documentation**: All code comments, docstrings, and documentation must be in **English only**. No Chinese is allowed in any code-related files.
- **Python Version**: Minimum Python 3.13. Utilize modern Python features (e.g., `|` for types instead of `Union`, `f-strings`).
- **Tooling**:
    - **Poetry**: Always use Poetry for dependency management and building.
    - **Ruff**: Use Ruff for linting and formatting. Run `ruff check .` and `ruff format .` before any commit.
    - **Pytest**: All new features and bug fixes must have corresponding tests in `tests/`.
- **Git Hook**: Pre-commit hooks must be followed.

## Architectural Guidelines

- **.syncignore logic**: Ensure that any modification to the sync logic handles recursive directories correctly. This includes:
    - Restoring modified/deleted files that exist in `HEAD`.
    - Removing new files added by the template that are covered by `.syncignore`.
    - Cleaning up empty directories created by the removal of ignored files.
- **Git Implementation**: Use `GitPython` where possible, but use `subprocess` for complex git commands if `GitPython` doesn't provide a clean interface.
- **CLI Framework**: Use `Typer`. Ensure help messages and arguments are clear and documented.

## Safety Rules

- Always verify that the worktree is clean before performing a `sync` operation.
- Never hardcode credentials or secrets.
- Use `OIDC` (Trusted Publishers) for any CI/CD publishing flows.
