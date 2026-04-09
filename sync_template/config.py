from pathlib import Path

import pathspec


def get_syncignore_spec(root_dir: Path) -> pathspec.PathSpec:
    """Read .syncignore file and return a PathSpec object."""
    ignore_file = root_dir / ".syncignore"
    if not ignore_file.exists():
        return pathspec.PathSpec.from_lines("gitignore", [])

    with open(ignore_file) as f:
        return pathspec.PathSpec.from_lines("gitignore", f.readlines())


def is_ignored(path: str, spec: pathspec.PathSpec) -> bool:
    """Check if a path matches the .syncignore specification."""
    return spec.match_file(path)
