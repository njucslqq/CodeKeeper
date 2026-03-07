"""Issue Tracker base class."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .models import Issue


class IssueTrackerBase(ABC):
    """Issue Tracker基类"""

    def __init__(self, config: dict):
        """初始化Issue Tracker

        Args:
            config: 配置字典
        """
        self.config = config
        self.session = None  # 子类实现

    @abstractmethod
    def connect(self) -> bool:
        """连接到Issue Tracker

        Returns:
            bool: 连接成功返回True
        """
        pass

    @abstractmethod
    def fetch_issues(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        project_key: Optional[str] = None
    ) -> List[Issue]:
        """获取Issues

        Args:
            since: 开始时间
            until: 结束时间
            project_key: 项目key

        Returns:
            List[Issue]: Issue列表
        """
        pass

    @abstractmethod
    def fetch_issue_detail(self, issue_id: str) -> Issue:
        """获取Issue详情（包括评论、附件、关联）

        Args:
            issue_id: Issue ID

        Returns:
            Issue: Issue详情
        """
        pass

    @abstractmethod
    def search_issues(self, query: str) -> List[Issue]:
        """搜索Issues

        Args:
            query: 搜索查询

        Returns:
            List[Issue]: Issue列表
        """
        pass
