"""Issue related models."""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class IssueStatus(str, Enum):
    """Issue status enumeration."""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CLOSED = "closed"


class IssueRelationType(str, Enum):
    """Issue relation type enumeration."""
    RELATED = "related"
    DERIVED = "derived"
    BLOCKED = "blocked"
    BLOCKS = "blocks"


class IssueRelation(BaseModel):
    """Issue relation model."""
    type: IssueRelationType
    issue_id: str
    url: Optional[str] = None


class Issue(BaseModel):
    """Issue model."""
    id: str
    key: str
    summary: str
    description: Optional[str] = None
    status: str = IssueStatus.TODO
    priority: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    reporter: Optional[str] = None
    assignee: Optional[str] = None
    relations: List[IssueRelation] = Field(default_factory=list)
