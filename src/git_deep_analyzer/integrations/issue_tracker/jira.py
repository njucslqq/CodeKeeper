"""Jira Issue Tracker integration."""

import requests
from .base import IssueTrackerBase
from .models import Issue, IssueStatus, IssuePriority
from datetime import datetime


class JiraTracker(IssueTrackerBase):
    """Jira Issue Tracker集成"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config["url"]
        self.token = config.get("token", "")
        self.username = config.get("username", "")
        self.project_key = config.get("project_key")
        self.session = None

    def connect(self) -> bool:
        """连接到Jira"""
        import os

        self.session = requests.Session()
        
        # 支持多种认证方式
        if self.token:
            # Personal Access Token
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
        elif self.username and config.get("password"):
            # Basic Auth
            self.session.auth = (self.username, config["password"])
        elif os.environ.get("JIRA_TOKEN"):
            # Environment variable
            self.session.headers.update({
                "Authorization": f"Bearer {os.environ['JIRA_TOKEN']}"
            })

        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

        # 测试连接
        try:
            response = self.session.get(f"{self.base_url}/rest/api/3/myself")
            return response.status_code == 200
        except Exception:
            return False

    def fetch_issues(
        self,
        since=None,
        until=None,
        project_key=None
    ) -> list:
        """获取Issues"""
        # 构建JQL查询
        jql_parts = []

        pk = project_key or self.project_key
        if pk:
            jql_parts.append(f'project = "{pk}"')

        if since:
            jql_parts.append(f'created >= "{since.strftime("%Y-%m-%d")}"')

        if until:
            jql_parts.append(f'created <= "{until.strftime("%Y-%m-%d")}"')

        jql_str = " AND ".join(jql_parts)

        # 调用Jira API
        url = f"{self.base_url}/rest/api/3/search"
        params = {
            "jql": jql_str,
            "fields": "*all",
            "expand": "changelog,comments,attachment",
            "maxResults": 100
        }

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Jira API error: {response.text}")

        data = response.json()

        # 解析Issues
        issues = []
        for issue_data in data.get("results", []):
            issues.append(self._parse_issue(issue_data))

        return issues

    def fetch_issue_detail(self, issue_id: str) -> Issue:
        """获取Issue详情"""
        url = f"{self.base_url}/rest/api/3/issue/{issue_id}"
        params = {
            "fields": "*all",
            "expand": "changelog,comments,attachment"
        }

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Jira API error: {response.text}")

        data = response.json()
        return self._parse_issue(data)

    def search_issues(self, query: str) -> list:
        """搜索Issues"""
        url = f"{self.base_url}/rest/api/3/search"
        params = {
            "jql": f'text ~ "{query}"',
            "fields": "*all",
            "expand": "changelog,comments",
            "maxResults": 50
        }

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Jira API error: {response.text}")

        data = response.json()
        return [self._parse_issue(issue_data) for issue_data in data.get("results", [])]

    def _parse_issue(self, issue_data: dict) -> Issue:
        """解析Issue数据"""
        fields = issue_data.get("fields", {})

        return Issue(
            id=issue_data["id"],
            key=issue_data["key"],
            summary=fields.get("summary", ""),
            description=fields.get("description", ""),
            status=self._parse_status(fields.get("status", {})),
            priority=self._parse_priority(fields.get("priority", {})),
            labels=fields.get("labels", []),
            created_at=datetime.fromisoformat(fields["created"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(fields["updated"].replace("Z", "+00:00")),
            resolved_at=datetime.fromisoformat(fields["resolutiondate"].replace("Z", "+00:00")) if fields.get("resolutiondate") else None,
            reporter=fields["reporter"].get("displayName", ""),
            reporter_email=fields["reporter"].get("emailAddress", ""),
            assignee=fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            assignee_email=fields.get("assignee", {}).get("emailAddress") if fields.get("assignee") else None
        )

    def _parse_status(self, status_data: dict) -> IssueStatus:
        """解析状态"""
        status_name = status_data.get("name", "").lower()
        for status in IssueStatus:
            if status.value in status_name:
                return status
        return IssueStatus.TODO

    def _parse_priority(self, priority_data: dict) -> IssuePriority:
        """解析优先级"""
        priority_name = priority_data.get("name", "").lower()
        for priority in IssuePriority:
            if priority.value in priority_name:
                return priority
        return IssuePriority.MEDIUM
