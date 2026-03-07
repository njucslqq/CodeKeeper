"""Time analyzer for handling different time bases in git commits."""

from datetime import datetime
from git import Commit


class TimeAnalyzer:
    """时间分析器 - 处理author/commit/merge时间"""

    def __init__(self, repo):
        """初始化时间分析器

        Args:
            repo: Git Repo对象
        """
        self.repo = repo
        self.reflog_cache = {}  # 缓存reflog数据

    def get_commit_time(self, commit: Commit, basis: str) -> datetime:
        """获取指定基准的时间

        Args:
            commit: Git commit对象
            basis: 时间基准（author_time, commit_time, merge_time）

        Returns:
            datetime: 提交时间

        Raises:
            ValueError: 无效的时间基准
        """
        if basis == "author_time":
            return datetime.fromtimestamp(commit.authored_date)
        elif basis == "commit_time":
            return datetime.fromtimestamp(commit.committed_date)
        elif basis == "merge_time":
            return self._get_merge_time(commit)
        else:
            raise ValueError(f"Invalid time basis: {basis}")

    def _get_merge_time(self, commit: Commit) -> datetime:
        """获取合并时间（处理fast forward）

        Args:
            commit: Git commit对象

        Returns:
            datetime: 合并时间
        """
        # 检查是否是merge commit
        if len(commit.parents) > 1:
            # 正常merge，使用commit_time
            return datetime.fromtimestamp(commit.committed_date)
        else:
            # 可能是fast forward，通过reflog查找
            return self._get_ff_merge_time(commit)

    def _get_ff_merge_time(self, commit: Commit) -> datetime:
        """获取fast forward提交的合并时间

        Args:
            commit: Git commit对象

        Returns:
            datetime: 合并时间（如果无法从reflog获取，则返回author_time）
        """
        # 方法1: 从reflog查找
        try:
            reflog_entries = self.repo.head.log()
            for entry in reversed(reflog_entries):
                if entry.newhexsha == commit.hexsha:
                    return datetime.fromtimestamp(entry.time[0])
        except Exception:
            pass

        # 方法2: 回退到author_time
        return datetime.fromtimestamp(commit.authored_date)
