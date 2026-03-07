"""Tests for DiffExtractor."""

import subprocess
from pathlib import Path
from git_deep_analyzer.git_collector.diff_extractor import DiffExtractor
from git_deep_analyzer.git_collector.models import FileChange
import pytest


@pytest.mark.unit
class TestDiffExtractor:
    """测试DiffExtractor"""

    def test_init_with_valid_repo(self, mock_git_repo):
        """测试使用有效仓库初始化"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        # When
        extractor = DiffExtractor(repo)

        # Then
        assert extractor is not None
        assert extractor.repo == repo

    def test_get_changed_files_with_commit(self, mock_git_repo):
        """测试获取提交的变更文件"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        # 创建新文件并提交
        test_file = mock_git_repo / "newfile.txt"
        test_file.write_text("new content")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add new file"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        extractor = DiffExtractor(repo)
        commits = list(repo.iter_commits("master"))
        latest_commit = commits[0]

        # When
        changes = extractor.get_changed_files(latest_commit)

        # Then
        assert isinstance(changes, list)
        assert len(changes) > 0

        # 验证文件变更类型
        file_changes = [c for c in changes if c.path == "newfile.txt"]
        assert len(file_changes) == 1
        assert file_changes[0].change_type == "added"

    def test_get_changed_files_with_modified_file(self, mock_git_repo):
        """测试获取修改文件的变更"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        # 修改现有文件
        test_file = mock_git_repo / "test.txt"
        test_file.write_text("modified content")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Modify file"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        extractor = DiffExtractor(repo)
        commits = list(repo.iter_commits("master"))
        latest_commit = commits[0]

        # When
        changes = extractor.get_changed_files(latest_commit)

        # Then
        assert isinstance(changes, list)
        assert len(changes) > 0

        # 验证文件变更类型
        file_changes = [c for c in changes if c.path == "test.txt"]
        assert len(file_changes) == 1
        assert file_changes[0].change_type == "modified"

    def test_get_changed_files_with_deleted_file(self, mock_git_repo):
        """测试获取删除文件的变更"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        # 创建文件
        test_file = mock_git_repo / "todelete.txt"
        test_file.write_text("will be deleted")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add file to delete"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        # 删除文件
        test_file.unlink()
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Delete file"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        extractor = DiffExtractor(repo)
        commits = list(repo.iter_commits("master"))
        latest_commit = commits[0]

        # When
        changes = extractor.get_changed_files(latest_commit)

        # Then
        assert isinstance(changes, list)

        # 验证删除的文件
        file_changes = [c for c in changes if c.path == "todelete.txt"]
        assert len(file_changes) == 1
        assert file_changes[0].change_type == "deleted"

    def test_get_changed_files_with_renamed_file(self, mock_git_repo):
        """测试获取重命名文件的变更"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        # 创建文件
        old_file = mock_git_repo / "oldname.txt"
        old_file.write_text("content")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add file"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        # 重命名文件
        new_file = mock_git_repo / "newname.txt"
        subprocess.run(
            ["git", "mv", str(old_file), str(new_file)],
            cwd=mock_git_repo, check=True, capture_output=True
        )
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Rename file"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        extractor = DiffExtractor(repo)
        commits = list(repo.iter_commits("master"))
        latest_commit = commits[0]

        # When
        changes = extractor.get_changed_files(latest_commit)

        # Then
        assert isinstance(changes, list)

        # 验证重命名的文件
        file_changes = [c for c in changes if c.old_path == "oldname.txt"]
        assert len(file_changes) == 1
        assert file_changes[0].change_type == "renamed"

    def test_get_diff_returns_string(self, mock_git_repo):
        """测试get_diff返回字符串"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        test_file = mock_git_repo / "diff.txt"
        test_file.write_text("line1\nline2\nline3")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add file for diff"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        extractor = DiffExtractor(repo)
        commits = list(repo.iter_commits("master"))
        latest_commit = commits[0]

        # When
        diff = extractor.get_diff(latest_commit)

        # Then
        assert isinstance(diff, str)
        assert len(diff) > 0
        assert "---" in diff or "+++" in diff or "@@" in diff

    def test_get_diff_with_no_parent_commit(self, mock_git_repo):
        """测试无父提交时获取diff"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)
        commits = list(repo.iter_commits("master"))
        first_commit = commits[-1]  # 第一个提交没有父提交

        extractor = DiffExtractor(repo)

        # When
        diff = extractor.get_diff(first_commit)

        # Then
        assert isinstance(diff, str)

    def test_get_diff_with_binary_file(self, mock_git_repo):
        """测试二进制文件的diff"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        # 创建二进制文件
        binary_file = mock_git_repo / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03')
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add binary file"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        extractor = DiffExtractor(repo)
        commits = list(repo.iter_commits("master"))
        latest_commit = commits[0]

        # When
        diff = extractor.get_diff(latest_commit)
        changes = extractor.get_changed_files(latest_commit)

        # Then
        assert isinstance(diff, str)
        assert isinstance(changes, list)

        # 验证二进制文件标记
        binary_changes = [c for c in changes if c.path == "binary.bin"]
        assert len(binary_changes) == 1
        assert binary_changes[0].is_binary is True

    def test_count_additions(self, mock_git_repo):
        """测试统计添加行数"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        test_file = mock_git_repo / "add.txt"
        test_file.write_text("line1\nline2\nline3")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add lines"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        extractor = DiffExtractor(repo)
        commits = list(repo.iter_commits("master"))
        latest_commit = commits[0]
        diff_obj = latest_commit.diff(latest_commit.parents[0])[0]

        # When
        additions = extractor._count_additions(diff_obj)

        # Then
        assert isinstance(additions, int)
        assert additions >= 0

    def test_count_deletions(self, mock_git_repo):
        """测试统计删除行数"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        # 创建文件
        test_file = mock_git_repo / "del.txt"
        test_file.write_text("line1\nline2\nline3")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add lines"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        # 删除内容
        test_file.write_text("")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Delete lines"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        extractor = DiffExtractor(repo)
        commits = list(repo.iter_commits("master"))
        latest_commit = commits[0]
        diff_obj = latest_commit.diff(latest_commit.parents[0])[0]

        # When
        deletions = extractor._count_deletions(diff_obj)

        # Then
        assert isinstance(deletions, int)
        assert deletions >= 0
