"""Tests for GitCollector."""

import tempfile
from pathlib import Path
from git_deep_analyzer.git_collector.models import (
    CommitData, FileChange, AuthorStats, TagData, BranchData
)
from git_deep_analyzer.git_collector.collector import GitCollector
import pytest


@pytest.mark.unit
class TestGitCollector:
    """测试GitCollector"""

    def test_init_with_valid_repo(self, mock_git_repo):
        """测试使用有效的git仓库初始化"""
        # Given
        config = {"branch": "main"}

        # When
        collector = GitCollector(mock_git_repo, config)

        # Then
        assert collector is not None
        assert collector.config == config
        assert collector.repo is not None

    def test_init_with_nonexistent_repo(self):
        """测试使用不存在的仓库初始化"""
        # Given
        nonexistent_path = Path("/nonexistent/path")
        config = {"branch": "main"}

        # When & Then
        with pytest.raises(FileNotFoundError, match="not found"):
            GitCollector(nonexistent_path, config)

    def test_init_with_non_git_directory(self, temp_dir):
        """测试使用非git目录初始化"""
        # Given
        config = {"branch": "main"}

        # When & Then
        with pytest.raises(ValueError, match="not a git repository"):
            GitCollector(temp_dir, config)

    def test_collect_all_returns_complete_data(self, mock_git_repo):
        """测试collect_all返回完整数据"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)

        # When
        result = collector.collect_all()

        # Then
        assert "commits" in result
        assert "tags" in result
        assert "branches" in result
        assert "author_stats" in result
        assert isinstance(result["commits"], list)
        assert isinstance(result["tags"], list)
        assert isinstance(result["branches"], list)
        assert isinstance(result["author_stats"], dict)

    def test_collect_commits_returns_commit_data(self, mock_git_repo):
        """测试collect_commits返回提交数据"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)

        # When
        commits = collector._collect_commits()

        # Then
        assert len(commits) > 0
        assert all(isinstance(c, CommitData) for c in commits)

    def test_collect_tags_returns_tag_data(self, mock_git_repo):
        """测试collect_tags返回标签数据"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)

        # When
        tags = collector._collect_tags()

        # Then
        assert isinstance(tags, list)
        # 初始仓库可能没有标签

    def test_collect_branches_returns_branch_data(self, mock_git_repo):
        """测试collect_branches返回分支数据"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)

        # When
        branches = collector._collect_branches()

        # Then
        assert len(branches) > 0
        assert all(isinstance(b, BranchData) for b in branches)

    def test_collect_branches_identifies_head_branch(self, mock_git_repo):
        """测试collect_branches识别HEAD分支"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)

        # When
        branches = collector._collect_branches()

        # Then
        head_branches = [b for b in branches if b.is_head]
        assert len(head_branches) == 1
        assert head_branches[0].name == "master"

    def test_calculate_author_stats(self, mock_git_repo):
        """测试计算作者统计"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)
        commits = collector._collect_commits()

        # When
        stats = collector._calculate_author_stats(commits)

        # Then
        assert isinstance(stats, dict)
        assert len(stats) > 0

        # 验证AuthorStats字段
        for author_name, author_stat in stats.items():
            assert isinstance(author_stat, AuthorStats)
            assert author_stat.author == author_name
            assert author_stat.commit_count > 0
            assert author_stat.files_changed >= 0
            assert author_stat.lines_added >= 0
            assert author_stat.lines_deleted >= 0
            assert author_stat.first_commit is not None
            assert author_stat.last_commit is not None

    def test_get_changed_files_with_single_commit(self, mock_git_repo):
        """测试获取单个提交的变更文件"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)
        commits = collector._collect_commits()
        commit = commits[0]

        # When
        changes = collector._get_changed_files(commit)

        # Then
        assert isinstance(changes, list)
        # 至少有一个文件变更
        assert len(changes) > 0

    def test_get_diff_returns_string(self, mock_git_repo):
        """测试get_diff返回字符串"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)
        commits = collector._collect_commits()
        commit = commits[0]

        # When
        diff = collector._get_diff(commit)

        # Then
        assert isinstance(diff, str)
        assert len(diff) > 0

    def test_get_diff_with_no_parent_commit(self, mock_git_repo):
        """测试无父提交时获取diff"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)
        commits = collector._collect_commits()
        commit = commits[0]  # 第一个提交没有父提交

        # When
        diff = collector._get_diff(commit)

        # Then
        assert isinstance(diff, str)
        # 仍然应该返回diff内容

    def test_collect_with_empty_repository(self, mock_git_repo):
        """测试收集空仓库"""
        # Given
        config = {"branch": "master"}
        collector = GitCollector(mock_git_repo, config)

        # When
        result = collector.collect_all()

        # Then
        # 至少应该有初始提交
        assert len(result["commits"]) >= 1
        assert result["author_stats"] is not None

    @pytest.mark.parametrize("branch_name", ["master", "main"])
    def test_collect_with_different_branches(self, mock_git_repo, branch_name):
        """测试收集不同分支"""
        # Given
        # 创建新分支
        import subprocess
        subprocess.run(["git", "checkout", "-b", branch_name],
                      cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "master"],
                      cwd=mock_git_repo, check=True, capture_output=True)

        config = {"branch": branch_name}
        collector = GitCollector(mock_git_repo, config)

        # When
        result = collector.collect_all()

        # Then
        assert "commits" in result
        assert "branches" in result


@pytest.mark.unit
class TestFileChange:
    """测试FileChange数据模型"""

    def test_file_change_added(self):
        """测试添加文件变更"""
        # Given
        change = FileChange(
            path="test.txt",
            old_path=None,
            change_type="added",
            additions=10,
            deletions=0,
            is_binary=False
        )

        # Then
        assert change.path == "test.txt"
        assert change.change_type == "added"
        assert change.additions == 10
        assert change.deletions == 0

    def test_file_change_modified(self):
        """测试修改文件变更"""
        # Given
        change = FileChange(
            path="test.txt",
            old_path="test.txt",
            change_type="modified",
            additions=5,
            deletions=3,
            is_binary=False
        )

        # Then
        assert change.change_type == "modified"
        assert change.additions == 5
        assert change.deletions == 3

    def test_file_change_binary(self):
        """测试二进制文件变更"""
        # Given
        change = FileChange(
            path="image.png",
            old_path=None,
            change_type="added",
            additions=0,
            deletions=0,
            is_binary=True
        )

        # Then
        assert change.is_binary is True


@pytest.mark.unit
class TestCommitData:
    """测试CommitData数据模型"""

    def test_commit_data_fields(self):
        """测试提交数据字段"""
        # Given
        commit = CommitData(
            hash="abc123",
            short_hash="abc123",
            author="Test User",
            author_email="test@example.com",
            author_time=None,  # 在实际使用中会是datetime
            commit_time=None,
            merge_time=None,
            message="Test commit",
            parents=[],
            files_changed=[],
            diff=""
        )

        # Then
        assert commit.hash == "abc123"
        assert commit.author == "Test User"
        assert commit.message == "Test commit"
