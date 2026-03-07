"""Tests for TimeAnalyzer."""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from git_deep_analyzer.git_collector.time_analyzer import TimeAnalyzer
import pytest


@pytest.mark.unit
class TestTimeAnalyzer:
    """测试TimeAnalyzer"""

    def test_get_commit_time_author_time(self, mock_git_repo):
        """测试获取author_time"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)
        analyzer = TimeAnalyzer(repo)
        commit = list(repo.iter_commits())[0]

        # When
        result = analyzer.get_commit_time(commit, "author_time")

        # Then
        assert isinstance(result, datetime)
        assert result == datetime.fromtimestamp(commit.authored_date)

    def test_get_commit_time_commit_time(self, mock_git_repo):
        """测试获取commit_time"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)
        analyzer = TimeAnalyzer(repo)
        commit = list(repo.iter_commits())[0]

        # When
        result = analyzer.get_commit_time(commit, "commit_time")

        # Then
        assert isinstance(result, datetime)
        assert result == datetime.fromtimestamp(commit.committed_date)

    def test_get_commit_time_merge_time_regular_merge(self, mock_git_repo):
        """测试获取merge_time（普通merge）"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        # 创建一个merge commit
        # 首先创建两个分支
        subprocess.run(
            ["git", "checkout", "-b", "branch1"],
            cwd=mock_git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "checkout", "-b", "branch2"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        # 在branch1上创建提交
        test_file = mock_git_repo / "branch1.txt"
        test_file.write_text("branch1 content")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Branch1 commit"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        # 在branch2上创建提交
        test_file2 = mock_git_repo / "branch2.txt"
        test_file2.write_text("branch2 content")
        subprocess.run(["git", "checkout", "branch2"], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Branch2 commit"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        # Merge branch1 to branch2
        subprocess.run(
            ["git", "merge", "branch1", "--no-ff"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        analyzer = TimeAnalyzer(repo)
        merge_commit = list(repo.iter_commits("branch2"))[0]

        # When
        result = analyzer.get_commit_time(merge_commit, "merge_time")

        # Then
        assert isinstance(result, datetime)
        assert len(merge_commit.parents) == 2  # merge commit有2个父提交

    def test_get_commit_time_invalid_basis(self, mock_git_repo):
        """测试无效的时间基准"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)
        analyzer = TimeAnalyzer(repo)
        commit = list(repo.iter_commits())[0]

        # When & Then
        with pytest.raises(ValueError, match="Invalid time basis"):
            analyzer.get_commit_time(commit, "invalid_basis")

    def test_get_merge_time_for_ff_merge(self, mock_git_repo):
        """测试获取fast forward merge的时间"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)

        # 创建分支并切换
        subprocess.run(
            ["git", "checkout", "-b", "feature"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        # 在feature分支创建提交
        test_file = mock_git_repo / "feature.txt"
        test_file.write_text("feature content")
        subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Feature commit"],
            cwd=mock_git_repo, check=True, capture_output=True
        )

        # 切回master，fast forward merge
        subprocess.run(["git", "checkout", "master"], cwd=mock_git_repo, check=True, capture_output=True)
        subprocess.run(["git", "merge", "feature"], cwd=mock_git_repo, check=True, capture_output=True)

        analyzer = TimeAnalyzer(repo)
        ff_commit = list(repo.iter_commits("master"))[0]

        # When
        result = analyzer._get_merge_time(ff_commit)

        # Then
        assert isinstance(result, datetime)

    def test_get_ff_merge_time_reflog_fallback(self, mock_git_repo):
        """测试reflog失败时回退到author_time"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)
        analyzer = TimeAnalyzer(repo)
        commit = list(repo.iter_commits())[0]

        # When
        result = analyzer._get_ff_merge_time(commit)

        # Then
        # 当无法从reflog获取时，应该回退到author_time
        assert isinstance(result, datetime)
        assert result == datetime.fromtimestamp(commit.authored_date)

    def test_get_merge_time_for_non_ff_commit(self, mock_git_repo):
        """测试普通commit的merge_time"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)
        analyzer = TimeAnalyzer(repo)
        commit = list(repo.iter_commits())[0]

        # When
        result = analyzer._get_merge_time(commit)

        # Then
        # 普通commit（非merge）也返回commit_time
        assert isinstance(result, datetime)
        assert result == datetime.fromtimestamp(commit.committed_date)

    @pytest.mark.parametrize("basis", ["author_time", "commit_time", "merge_time"])
    def test_get_commit_time_all_basis(self, mock_git_repo, basis):
        """测试所有时间基准"""
        # Given
        from git import Repo
        repo = Repo(mock_git_repo)
        analyzer = TimeAnalyzer(repo)
        commit = list(repo.iter_commits())[0]

        # When
        result = analyzer.get_commit_time(commit, basis)

        # Then
        assert isinstance(result, datetime)
