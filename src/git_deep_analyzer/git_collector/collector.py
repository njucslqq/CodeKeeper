"""Git collector for extracting git repository data."""

from pathlib import Path
from typing import List, Dict
from datetime import datetime
from git import Repo

from .models import (
    CommitData, AuthorStats, TagData, BranchData
)
from .diff_extractor import DiffExtractor
from .time_analyzer import TimeAnalyzer


class GitCollector:
    """Git数据采集器"""

    def __init__(self, repo_path: Path, config: dict):
        """初始化Git采集器

        Args:
            repo_path: Git仓库路径
            config: 配置字典

        Raises:
            FileNotFoundError: 仓库路径不存在
            ValueError: 不是一个git仓库
        """
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository path not found: {repo_path}")

        try:
            self.repo = Repo(repo_path)
        except Exception as e:
            raise ValueError(f"Not a git repository: {repo_path}") from e

        self.config = config
        self.branch = config.get("branch", "main")
        self.diff_extractor = DiffExtractor(self.repo)
        self.time_analyzer = TimeAnalyzer(self.repo)

    def collect_all(self) -> dict:
        """采集所有数据

        Returns:
            dict: 包含commits、tags、branches、author_stats的字典

        Raises:
            Exception: 采集过程中发生错误
        """
        try:
            return {
                "commits": self._collect_commits(),
                "tags": self._collect_tags(),
                "branches": self._collect_branches(),
                "author_stats": self._calculate_author_stats(self._collect_commits())
            }
        except Exception as e:
            raise RuntimeError(f"Failed to collect git data: {e}") from e

    def _collect_commits(self) -> List[CommitData]:
        """采集提交数据

        Returns:
            List[CommitData]: 提交数据列表
        """
        commits = []

        try:
            for commit in self.repo.iter_commits(self.branch):
                commits.append(CommitData(
                    hash=commit.hexsha,
                    short_hash=commit.hexsha[:7],
                    author=commit.author.name,
                    author_email=commit.author.email,
                    author_time=datetime.fromtimestamp(commit.authored_date),
                    commit_time=datetime.fromtimestamp(commit.committed_date),
                    merge_time=self.time_analyzer.get_merge_time(commit),
                    message=commit.message.strip(),
                    parents=[p.hexsha for p in commit.parents],
                    files_changed=self.diff_extractor.get_changed_files(commit),
                    diff=self.diff_extractor.get_diff(commit)
                ))
        except Exception as e:
            raise RuntimeError(f"Failed to collect commits: {e}") from e

        return commits

    def _collect_tags(self) -> List[TagData]:
        """采集标签数据

        Returns:
            List[TagData]: 标签数据列表
        """
        tags = []

        try:
            for tag in self.repo.tags:
                tags.append(TagData(
                    name=tag.name,
                    commit=tag.commit.hexsha,
                    message=tag.tag.message if tag.tag else "",
                    tag_date=datetime.fromtimestamp(tag.tag.tagged_date) if tag.tag else None
                ))
        except Exception as e:
            raise RuntimeError(f"Failed to collect tags: {e}") from e

        return tags

    def _collect_branches(self) -> List[BranchData]:
        """采集分支数据

        Returns:
            List[BranchData]: 分支数据列表
        """
        branches = []

        try:
            for branch in self.repo.branches:
                branches.append(BranchData(
                    name=branch.name,
                    commit=branch.commit.hexsha,
                    is_head=(branch == self.repo.active_branch),
                    tracking=str(branch.tracking_branch()) if branch.tracking_branch() else None
                ))
        except Exception as e:
            raise RuntimeError(f"Failed to collect branches: {e}") from e

        return branches

    def _calculate_author_stats(self, commits: List[CommitData]) -> Dict[str, AuthorStats]:
        """计算作者统计

        Args:
            commits: 提交数据列表

        Returns:
            Dict[str, AuthorStats]: 作者统计字典

        Raises:
            ValueError: commits为空
        """
        if not commits:
            raise ValueError("Cannot calculate author stats from empty commits list")

        stats = {}

        try:
            for commit in commits:
                author = commit.author

                if author not in stats:
                    stats[author] = AuthorStats(
                        author=author,
                        email=commit.author_email,
                        commit_count=0,
                        files_changed=0,
                        lines_added=0,
                        lines_deleted=0,
                        first_commit=commit.author_time,
                        last_commit=commit.author_time
                    )

                stats[author].commit_count += 1
                stats[author].files_changed += len(commit.files_changed)
                stats[author].lines_added += sum(f.additions for f in commit.files_changed)
                stats[author].lines_deleted += sum(f.deletions for f in commit.files_changed)

                if commit.author_time < stats[author].first_commit:
                    stats[author].first_commit = commit.author_time
                if commit.author_time > stats[author].last_commit:
                    stats[author].last_commit = commit.author_time
        except Exception as e:
            raise RuntimeError(f"Failed to calculate author stats: {e}") from e

        return stats
