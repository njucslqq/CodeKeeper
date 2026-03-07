"""Issue Tracker data models."""

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


class Issue:
    """Issue数据模型"""
    def __init__(
        self,
        id: str,
        key: str,  # 如 PROJ-123
        summary: str,
        description: str,
        status: IssueStatus,
        priority: IssuePriority,
        labels: List[str],
        created_at: datetime,
        updated_at: datetime,
        resolved_at: Optional[datetime] = None,
        reporter: str,
        reporter_email: str,
        assignee: Optional[str] = None,
        assignee_email: Optional[str] = None,
        comments: Optional[List["IssueComment"]] = None,
        attachments: Optional[List["IssueAttachment"]] = None,
        relations: Optional[List["IssueRelation"]] = None,
        project_key: str,
        project_name: str
    ):
        """初始化Issue

        Args:
            id: Issue ID
            key: Issue key
            summary: Issue标题
            description: Issue描述
            status: Issue状态
            priority: Issue优先级
            labels: 标签列表
            created_at: 创建时间
            updated_at: 更新时间
            resolved_at: 解决时间
            reporter: 作者
            reporter_email: 作者邮箱
            assignee: 指派人
            assignee_email: 指派人邮箱
            comments: 评论列表
            attachments: 附件列表
            relations: 关联列表
            project_key: 项目key
            project_name: 项目名称
        """
        self.id = id
        self.key = key
        self.summary = summary
        self.description = description
        self.status = status
        self.priority = priority
        self.labels = labels or []
        self.created_at = created_at
        self.updated_at = updated_at
        self.resolved_at = resolved_at
        self.reporter = reporter
        self.reporter_email = reporter_email
        self.assignee = assignee
        self.assignee_email = assignee_email
        self.comments = comments or []
        self.attachments = attachments or []
        self.relations = relations or []
        self.project_key = project_key
        self.project_name = project_name

    # 使用@property装饰器的只读属性
    @property
    def created_since(self) -> float:
        """计算创建后经过的时间（秒）"""
        from datetime import datetime, timezone
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()


class IssueComment:
    """Issue评论"""
    def __init__(
        self,
        id_str: str,
        author: str,
        author_email: str,
        content: str,
        created_at: datetime,
        updated_at: Optional[datetime] = None
    ):
        self.id_str = id_str
        self.author = author
        self.author_email = author_email
        self.content = content
        self.created_at = created_at
        self.updated_at = updated_at


class IssueAttachment:
    """Issue附件"""
    def __init__(
        self,
        id: str,
        filename: str,
        url: str,
        size: int,
        content_type: str,
        created_at: datetime
    ):
        self.id = id
        self.filename = filename
        self.url = url
        self.size = size
        self.content_type = content_type
        self.created_at = created_at


class IssueRelation:
    """Issue关联"""
    def __init__(
        self,
        type: str,  # "blocks", "is_blocked_by", "relates_to", "duplicates", "is_duplicated_by"
        issue_id: str,
        issue_summary: str
    ):
        self.type = type
        self.issue_id = issue_id
        self.issue_summary = issue_summary
