"""GitLab Issue Tracker integration."""

import requests
from typing import List, Optional
from datetime import datetime
from .base import IssueTrackerBase
from .models import Issue, IssueComment, IssueStatus, IssuePriority


class GitLabTracker(IssueTrackerBase):
    """GitLab Issue Tracker集成"""

    def __init__(self, config: dict):
        """初始化GitLab Tracker

        Args:
            config: 配置字典，包含url和token
        """
        super().__init__(config)
        self.base_url = config.get("url", "https://gitlab.com")
        self.token = config.get("token", "")
        self.session = None

    def connect(self) -> bool:
        """连接到GitLab API

        Returns:
            bool: 连接成功返回True
        """
        import os

        self.session = requests.Session()

        # 支持多种认证方式
        if self.token:
            # Personal Access Token
            self.session.headers.update({
                "Authorization": f"PRIVATE-TOKEN {self.token}"
            })
        elif os.environ.get("GITLAB_TOKEN"):
            # Environment variable
            token = os.environ["GITLAB_TOKEN"]
            self.session.headers.update({
                "Authorization": f"PRIVATE-TOKEN {token}"
            })

        # 测试连接
        try:
            response = self.session.get(f"{self.base_url}/api/v4/user", timeout=30)
            return response.status_code == 200
        except Exception:
            return False

    def fetch_issues(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        project_key: Optional[str] = None,
        project_id_or_path: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[List[str]] = None,
        milestone: Optional[str] = None
    ) -> List[Issue]:
        """获取GitLab Issues

        Args:
            since: 开始时间
            until: 结束时间
            project_key: 项目key（用于兼容接口）
            project_id_or_path: 项目ID或路径（如 "owner/repo"）
            state: 状态过滤（opened/closed/all）
            labels: 标签过滤
            milestone: Milestone过滤

        Returns:
            List[Issue]: Issue列表
        """
        if not self.session:
            raise RuntimeError("Not connected to GitLab API")

        # 构建URL
        project = project_id_or_path or project_key
        if not project:
            raise ValueError("project_id_or_path or project_key is required")

        url = f"{self.base_url}/api/v4/projects/{project}/issues"

        # 构建查询参数
        params = {}
        if state:
            params["state"] = state
        if since:
            params["created_after"] = since.isoformat()
        if until:
            params["created_before"] = until.isoformat()
        if labels:
            params["labels"] = ",".join(labels)
        if milestone:
            params["milestone"] = milestone

        # 获取所有页
        all_issues = []
        page = 1

        while True:
            params["page"] = page
            params["per_page"] = 100

            response = self.session.get(url, params=params, timeout=30)

            if response.status_code != 200:
                raise RuntimeError(f"GitLab API error: {response.text}")

            data = response.json()

            if not data:
                break

            # 解析issues
            for issue_data in data:
                issue = self._parse_issue(issue_data, project)
                all_issues.append(issue)

            # 检查是否还有更多页
            total_pages = int(response.headers.get("X-Total-Pages", 1))
            if page >= total_pages:
                break

            page += 1

        return all_issues

    def fetch_issue_detail(
        self,
        issue_id: str,
        project_id_or_path: Optional[str] = None
    ) -> Issue:
        """获取Issue详情（包括评论）

        Args:
            issue_id: Issue ID（GitLab使用iid）
            project_id_or_path: 项目ID或路径

        Returns:
            Issue: Issue详情
        """
        if not self.session:
            raise RuntimeError("Not connected to GitLab API")

        if not project_id_or_path:
            raise ValueError("project_id_or_path is required")

        # 获取issue详情
        url = f"{self.base_url}/api/v4/projects/{project_id_or_path}/issues/{issue_id}"
        response = self.session.get(url, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"GitLab API error: {response.text}")

        issue_data = response.json()
        issue = self._parse_issue(issue_data, project_id_or_path)

        # 获取评论
        comments_url = f"{self.base_url}/api/v4/projects/{project_id_or_path}/issues/{issue_id}/notes"
        comments_response = self.session.get(comments_url, timeout=30)

        if comments_response.status_code == 200:
            comments_data = comments_response.json()
            issue.comments = [
                self._parse_comment(comment_data)
                for comment_data in comments_data
            ]

        return issue

    def search_issues(
        self,
        query: str,
        project_id_or_path: Optional[str] = None
    ) -> List[Issue]:
        """搜索Issues

        Args:
            query: 搜索查询
            project_id_or_path: 项目ID或路径

        Returns:
            List[Issue]: Issue列表
        """
        if not self.session:
            raise RuntimeError("Not connected to GitLab API")

        if not project_id_or_path:
            raise ValueError("project_id_or_path is required")

        # 使用search参数
        url = f"{self.base_url}/api/v4/projects/{project_id_or_path}/issues"
        params = {
            "search": query,
            "per_page": 100
        }

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"GitLab API error: {response.text}")

        data = response.json()

        issues = []
        for issue_data in data:
            issue = self._parse_issue(issue_data, project_id_or_path)
            issues.append(issue)

        return issues

    def _parse_issue(self, issue_data: dict, project: str) -> Issue:
        """解析GitLab Issue数据

        Args:
            issue_data: GitLab API返回的Issue数据
            project: 项目标识

        Returns:
            Issue: Issue对象
        """
        # 解析状态
        state = issue_data.get("state", "opened")
        status = self._parse_state_to_status(state)

        # 解析优先级
        labels = issue_data.get("labels", [])
        priority = self._parse_labels_to_priority(labels)

        # 解析作者
        author_data = issue_data.get("author", {})
        author = author_data.get("username", "")
        author_email = author_data.get("email", "")

        # 解析指派人
        assignee_data = issue_data.get("assignee")
        assignee = None
        assignee_email = None
        if assignee_data:
            assignee = assignee_data.get("username", "")
            assignee_email = assignee_data.get("email", "")

        # 解析时间
        created_at = datetime.fromisoformat(
            issue_data.get("created_at", "").replace("Z", "+00:00")
        )
        updated_at = datetime.fromisoformat(
            issue_data.get("updated_at", "").replace("Z", "+00:00")
        )
        closed_at_str = issue_data.get("closed_at")
        resolved_at = None
        if closed_at_str:
            resolved_at = datetime.fromisoformat(closed_at_str.replace("Z", "+00:00"))

        # 解析项目信息
        project_dict = issue_data.get("project", {})
        project_id = project_dict.get("id", "")
        project_name = project_dict.get("path_with_namespace", "")

        return Issue(
            id=str(issue_data.get("id", "")),
            key=str(issue_data.get("iid", "")),
            summary=issue_data.get("title", ""),
            description=issue_data.get("description", "") or "",
            status=status,
            priority=priority,
            labels=labels,
            created_at=created_at,
            updated_at=updated_at,
            resolved_at=resolved_at,
            reporter=author,
            reporter_email=author_email,
            assignee=assignee,
            assignee_email=assignee_email,
            comments=[],
            attachments=[],
            relations=[],
            project_key=str(project_id),
            project_name=project_name
        )

    def _parse_comment(self, comment_data: dict) -> IssueComment:
        """解析评论数据

        Args:
            comment_data: GitLab API返回的评论数据

        Returns:
            IssueComment: 评论对象
        """
        author_data = comment_data.get("author", {})

        return IssueComment(
            id_str=str(comment_data.get("id", "")),
            author=author_data.get("username", ""),
            author_email=author_data.get("email", ""),
            content=comment_data.get("body", "") or "",
            created_at=datetime.fromisoformat(
                comment_data.get("created_at", "").replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                comment_data.get("updated_at", "").replace("Z", "+00:00")
            ) if comment_data.get("updated_at") else None
        )

    def _parse_state_to_status(self, state: str) -> IssueStatus:
        """将GitLab状态映射到IssueStatus

        Args:
            state: GitLab状态（opened/closed）

        Returns:
            IssueStatus
        """
        state_lower = state.lower()
        if state_lower == "opened":
            return IssueStatus.IN_PROGRESS
        elif state_lower == "closed":
            return IssueStatus.DONE
        else:
            return IssueStatus.TODO

    def _parse_labels_to_priority(self, labels: List[str]) -> IssuePriority:
        """将GitLab标签映射到优先级

        Args:
            labels: 标签列表

        Returns:
            IssuePriority
        """
        if any(label.lower() in ["critical", "urgent"] for label in labels):
            return IssuePriority.CRITICAL
        elif any(label.lower() == "high" for label in labels):
            return IssuePriority.HIGH
        elif any(label.lower() == "low" for label in labels):
            return IssuePriority.LOW
        elif any(label.lower() == "lowest" for label in labels):
            return IssuePriority.LOWEST
        else:
            return IssuePriority.MEDIUM
