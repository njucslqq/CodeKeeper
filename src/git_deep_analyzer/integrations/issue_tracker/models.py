"""Issue Tracker data models."""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum


class IssueStatus(Enum):
    """Issue状态"""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class IssuePriority(Enum):
    """Issue优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    LOWEST = "lowest"


@dataclass
class IssueComment:
    """Issue评论"""
    id: str
    author: str
    author_email: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None


@dataclass
class IssueAttachment:
    """Issue附件"""
    id: str
    filename: str
    url: str
    size: int
    content_type: str
    created_at: datetime


@dataclass
class IssueRelation:
    """Issue关联"""
    type: str  # "blocks", "is_blocked_by", "relates_to", "duplicates", "is_duplicated_by"
    issue_id: str
    issue_summary: str


@dataclass
class Issue:
    """Issue数据模型"""
    id: str
    key: str  # 如 PROJ-123
    summary: str
    description: str
    status: IssueStatus
    priority: IssuePriority
    labels: List[str]

    # 时间
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    # 作者
    reporter: str
    reporter_email: str
    assignee: Optional[str] = None
    assignee_email: Optional[str] = None

    # 关联数据
    comments: List[IssueComment] = None
    attachments: List[IssueAttachment] = None
    relations: List[IssueRelation] = None

    # 项目信息
    project_key: str
    project_name: str

    def __post_init__(self):
        if self.comments is None:
            self.comments = []
        if self.attachments is None:
            self.attachments = []
        if self.relations is None:
            self.relations = []
