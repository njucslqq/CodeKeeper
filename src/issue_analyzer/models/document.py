"""Document related models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration."""
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    RELEASE = "release"
    OPERATIONS = "operations"
    CUSTOM = "custom"


class Document(BaseModel):
    """Document model."""
    id: str
    type: str = DocumentType.REQUIREMENTS
    title: str
    content: str
    issue_id: str
    url: Optional[str] = None
    source: str  # e.g., "confluence", "feishu"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
