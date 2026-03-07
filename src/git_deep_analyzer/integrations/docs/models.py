"""Docs system data models."""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DocumentType(Enum):
    """文档类型"""
    REQUIREMENT = "requirement"
    DESIGN = "design"
    SPEC = "spec"
    GUIDE = "guide"
    API = "api"
    OTHER = "other"


@dataclass
class Document:
    """文档数据模型"""
    id: str
    title: str
    content: str
    type: DocumentType
    created_at: datetime
    updated_at: datetime
    author: str
    author_email: str
    space_key: Optional[str] = None
    folder_id: Optional[str] = None
    url: Optional[str] = None

    # LLM解析结果
    requirements: List[dict] = None

    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
