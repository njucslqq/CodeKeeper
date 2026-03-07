"""Git collector data models."""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class FileChange:
    """文件变更"""
    path: str
    old_path: Optional[str]
    change_type: str  # added, modified, deleted, renamed
    additions: int
    deletions: int
    is_binary: bool


@dataclass
class CommitData:
    """提交数据"""
    hash: str
    short_hash: str
    author: str
    author_email: str
    author_time: datetime
    commit_time: datetime
    merge_time: datetime
    message: str
    parents: List[str]
    files_changed: List[FileChange]
    diff: str


@dataclass
class AuthorStats:
    """作者统计"""
    author: str
    email: str
    commit_count: int
    files_changed: int
    lines_added: int
    lines_deleted: int
    first_commit: datetime
    last_commit: datetime


@dataclass
class TagData:
    """标签数据"""
    name: str
    commit: str
    message: str
    tag_date: Optional[datetime]


@dataclass
class BranchData:
    """分支数据"""
    name: str
    commit: str
    is_head: bool
    tracking: Optional[str]
