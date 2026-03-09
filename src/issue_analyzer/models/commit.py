"""Commit related models."""

from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ChangeType(str, Enum):
    """File change type enumeration."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class CommitFileChange(BaseModel):
    """File change model."""
    path: str
    old_path: Optional[str] = None
    change_type: str = ChangeType.MODIFIED
    additions: int = 0
    deletions: int = 0
    is_binary: bool = False


class Commit(BaseModel):
    """Commit model."""
    hash: str
    short_hash: str = ""
    message: str
    author: str
    author_email: str
    author_time: datetime = Field(default_factory=datetime.utcnow)
    commit_time: datetime = Field(default_factory=datetime.utcnow)
    parents: List[str] = Field(default_factory=list)
    files_changed: List[CommitFileChange] = Field(default_factory=list)
    diff: Optional[str] = None
    repository: Optional[str] = None

    def __init__(self, **data):
        """Initialize commit and set short hash."""
        super().__init__(**data)
        if not self.short_hash and self.hash:
            self.short_hash = self.hash[:7]
