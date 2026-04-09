import os
import shutil
import tempfile
import unittest.mock as mock
from pathlib import Path

import pytest
import typer
from git import Repo

from sync_template.git import GitManager
from sync_template.main import init


@pytest.fixture
def temp_dir():
    dir_path = tempfile.mkdtemp()
    yield Path(dir_path)
    shutil.rmtree(dir_path)


def test_init_existing_repo(temp_dir):
    """Verify that init --existing only adds the remote to an existing repo."""
    project_path = temp_dir / "existing_repo"
    project_path.mkdir()
    repo = Repo.init(project_path)
    (project_path / "README.md").write_text("Local README")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    # Call init with --existing
    # We use mock.patch to avoid actual clone if it were called
    with mock.patch("sync_template.git.GitManager.clone") as mock_clone:
        init("https://github.com/owner/repo.git", project_path, existing=True)
        assert mock_clone.call_count == 0

    # Verify remote was added
    repo = Repo(project_path)
    remote = repo.remote("template")
    assert remote.url == "https://github.com/owner/repo.git"
    assert (project_path / "README.md").read_text() == "Local README"


def test_url_transformation():
    """Verify that gh: and glab: shortcuts are transformed correctly."""
    # We mock GitManager.clone to check the URL passed
    with mock.patch("sync_template.git.GitManager.clone") as mock_clone:
        # 1. gh: transformation
        try:
            init("gh:owner/repo", Path("dest"), existing=False)
        except (SystemExit, typer.Exit):
            pass
        mock_clone.assert_called_with("https://github.com/owner/repo.git", Path("dest"))

        # 2. glab: transformation
        try:
            init("glab:owner/repo", Path("dest_glab"), existing=False)
        except (SystemExit, typer.Exit):
            pass
        mock_clone.assert_called_with(
            "https://gitlab.com/owner/repo.git", Path("dest_glab")
        )

        # 3. Standard URL (no change)
        try:
            init("https://example.com/repo.git", Path("dest_std"), existing=False)
        except (SystemExit, typer.Exit):
            pass
        mock_clone.assert_called_with("https://example.com/repo.git", Path("dest_std"))


def test_init_non_empty_dir_fails(temp_dir):
    """Verify that init fails when target directory is not empty."""
    dest = temp_dir / "not_empty"
    dest.mkdir()
    (dest / "somefile.txt").write_text("content")

    # We should see an Exit exception or it should return early
    with pytest.raises(typer.Exit) as excinfo:
        init("http://fake-url.com", dest, existing=False)
    assert excinfo.value.exit_code == 1


def test_sync_dirty_worktree_fails(temp_dir):
    """Verify that sync fails when there are untracked files."""
    project_path = temp_dir / "dirty_project"
    project_path.mkdir()
    repo = Repo.init(project_path)
    (project_path / "README.md").write_text("Initial")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    # Create untracked file
    (project_path / "untracked.txt").write_text("dirty")

    manager = GitManager(project_path)
    # We need to add a dummy remote to avoid failure before is_dirty check
    repo.create_remote("template", "http://fake.com")

    with pytest.raises(typer.BadParameter, match="Working directory is not clean"):
        manager.merge_with_ignore("main")


def test_recursive_syncignore(temp_dir):
    """Complex test case for recursive directories in .syncignore."""
    # 1. Setup template repo
    template_path = temp_dir / "template_repo"
    template_path.mkdir()
    template_repo = Repo.init(template_path)

    # Create deep structure
    content_dir = template_path / "content" / "subdir"
    content_dir.mkdir(parents=True)
    (content_dir / "file1.txt").write_text("v1 file1")
    (content_dir / "file2.txt").write_text("v1 file2")
    (template_path / ".syncignore").write_text("content/\n")

    template_repo.index.add(["content/", ".syncignore"])
    template_repo.index.commit("Initial commit")
    template_repo.git.branch("-M", "main")

    # 2. Init project
    project_path = temp_dir / "project"
    GitManager.clone(str(template_path), project_path)

    # Local changes in ignored directory
    (project_path / "content" / "subdir" / "file1.txt").write_text("local modification")
    repo = Repo(project_path)
    repo.index.add(["content/subdir/file1.txt"])
    repo.index.commit("Local change")

    # 3. Update template repo with various operations
    # a) Modify existing file
    (content_dir / "file1.txt").write_text("v2 file1")
    # b) Delete existing file
    os.remove(content_dir / "file2.txt")
    # c) Add new file in deep recursive subdir
    new_sub = content_dir / "deep" / "nested"
    new_sub.mkdir(parents=True)
    (new_sub / "new_file.txt").write_text("v2 new file")
    # d) Add unrelated change
    (template_path / "ROOT_UPDATE.md").write_text("Root update")

    template_repo.git.add(A=True)
    template_repo.index.commit("Template major update")

    # 4. Sync project
    manager = GitManager(project_path)
    manager.fetch_template()
    manager.merge_with_ignore("main")

    # 5. Verifications
    # Root update should be applied
    assert (project_path / "ROOT_UPDATE.md").exists()

    # content/ should be UNTOUCHED:
    # file1.txt: should keep local mod, NOT v2
    file1_path = project_path / "content" / "subdir" / "file1.txt"
    assert file1_path.read_text() == "local modification"

    # file2.txt: should still EXIST (template deleted it, but we ignore content/)
    file2_path = project_path / "content" / "subdir" / "file2.txt"
    assert file2_path.exists()
    assert file2_path.read_text() == "v1 file2"

    # content/subdir/deep/nested/new_file.txt:
    # should NOT exist (template added it, but we ignore)
    assert not (project_path / "content" / "subdir" / "deep").exists()
