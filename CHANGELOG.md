# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2026-04-09

### Changed
- Updated author email and refined project metadata.

## [0.2.1] - 2026-04-09

### Added
- `--version` command to display project name, version, author, and website.
- Official documentation link to `https://xxcc-unicorn-press.github.io`.

### Changed
- Updated project author and copyright to `XXCC Unicorn Press Editorial Board`.

## [0.2.0] - 2026-04-09

### Added
- `--existing` flag to `init` command to initialize the template remote within an existing repository without cloning.
- Recursive directory handling in `.syncignore` with automatic cleanup of empty directories.
- Improved working tree safety check before syncing (now includes untracked files).

## [0.1.1] - 2026-04-09

### Added
- Support for `gh:<owner>/<repo>` and `glab:<owner>/<repo>` URL shortcuts in the `init` command.
- Comprehensive package metadata (classifiers, keywords, project URLs).

### Fixed
- CI test failures by configuring a dummy Git identity in the GitHub Actions environment.

## [0.1.0] - 2026-04-09

### Added
- Initial release of `sync-template` CLI.
- `init` command for creating projects from template repositories.
- `sync` command for merging template updates with `.syncignore` support.
- Modern Python environment with Poetry, Ruff, and Pytest.
- Automated CI/CD for publishing to PyPI using Trusted Publishers (OIDC).
