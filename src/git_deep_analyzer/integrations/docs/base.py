"""Docs system base class."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .models import Document


class DocsSystemBase(ABC):
    """文档系统基类"""

    def __init__(self, config: dict, ai_client=None):
        self.config = config
        self.ai_client = ai_client
        self.session = None

    @abstractmethod
    def connect(self) -> bool:
        """连接到文档系统"""
        pass

    @abstractmethod
    def fetch_documents(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        labels: Optional[List[str]] = None,
        space_key: Optional[str] = None
    ) -> List[Document]:
        """获取文档列表"""
        pass

    @abstractmethod
    def fetch_document_detail(self, document_id: str) -> Document:
        """获取文档详情"""
        pass

    def parse_document_with_llm(self, document: Document) -> Document:
        """使用LLM解析文档内容"""
        if not self.ai_client:
            return document

        # 这里可以调用AI客户端进行深度解析
        # 暂时返回原文档
        return document
