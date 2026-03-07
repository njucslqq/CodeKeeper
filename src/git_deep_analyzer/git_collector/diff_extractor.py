"""Diff extractor for getting code diff and file change information."""

from typing import List
from git import Diff


class DiffExtractor:
    """代码diff提取器"""

    def __init__(self, repo):
        """初始化diff提取器

        Args:
            repo: Git Repo对象
        """
        self.repo = repo

    def get_changed_files(self, commit) -> List:
        """获取变更的文件列表

        Args:
            commit: Git commit对象

        Returns:
            List[FileChange]: 文件变更列表
        """
        from .models import FileChange

        changes = []

        try:
            for diff in commit.diff(commit.parents[0] if commit.parents else None):
                changes.append(FileChange(
                    path=diff.b_path or diff.a_path,
                    old_path=diff.a_path,
                    change_type=self._get_change_type(diff),
                    additions=self._count_additions(diff),
                    deletions=self._count_deletions(diff),
                    is_binary=diff.b_blob is None or diff.b_blob.is_binary
                ))
        except Exception as e:
            raise RuntimeError(f"Failed to get changed files: {e}") from e

        return changes

    def get_diff(self, commit) -> str:
        """获取完整diff文本

        Args:
            commit: Git commit对象

        Returns:
            str: diff文本
        """
        try:
            diff_obj = commit.diff(
                commit.parents[0] if commit.parents else None,
                create_patch=True,
                unified=3
            )
            return diff_obj.diff.decode('utf-8', errors='ignore')
        except Exception as e:
            raise RuntimeError(f"Failed to get diff: {e}") from e

    @staticmethod
    def _get_change_type(diff: Diff) -> str:
        """判断变更类型

        Args:
            diff: Git diff对象

        Returns:
            str: 变更类型
        """
        if diff.new_file:
            return "added"
        elif diff.deleted_file:
            return "deleted"
        elif diff.renamed:
            return "renamed"
        elif diff.renamed_file:
            return "renamed"
        else:
            return "modified"

    @staticmethod
    def _count_additions(diff: Diff) -> int:
        """统计添加行数

        Args:
            diff: Git diff对象

        Returns:
            int: 添加行数
        """
        try:
            diff_text = diff.diff.decode('utf-8', errors='ignore')
            # 减去"+++"开头的行
            return diff_text.count('+') - diff_text.count('+++')
        except Exception:
            return 0

    @staticmethod
    def _count_deletions(diff: Diff) -> int:
        """统计删除行数

        Args:
            diff: Git diff对象

        Returns:
            int: 删除行数
        """
        try:
            diff_text = diff.diff.decode('utf-8', errors='ignore')
            # 减去"---"开头的行
            return diff_text.count('-') - diff_text.count('---')
        except Exception:
            return 0
