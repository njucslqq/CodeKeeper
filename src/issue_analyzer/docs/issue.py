"""Issue information clients."""

import requests
from typing import Optional
from issue_analyzer.models import Issue, IssueStatus


class IssueClient:
    """Base interface for issue clients."""

    def __init__(self):
        pass

    @property
    def repository(self) -> str:
        """Get repository/system identifier."""
        return "unknown"

    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue information by ID."""
        pass


class GitHubIssueClient(IssueClient):
    """GitHub issue client."""

    def __init__(self, token: str, repo_owner: str, repo_name: str):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })

    @property
    def repository(self) -> str:
        """Get repository identifier."""
        return f"{self.repo_owner}/{self.repo_name}"

    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue information by ID."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_id}"

        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return self._parse_issue(data)
        except Exception:
            pass

        return None

    def _parse_issue(self, data: dict) -> Issue:
        """Parse GitHub issue response."""
        return Issue(
            id=data.get("number", ""),
            key=data.get("number", ""),
            summary=data.get("title", ""),
            description=data.get("body"),
            status=self._parse_status(data),
            priority=data.get("labels", []) and self._extract_priority(data.get("labels", [])),
            labels=[l["name"] for l in data.get("labels", [])] if "labels" in data else [],
        )

    def _parse_status(self, data: dict) -> str:
        """Parse issue status."""
        state = data.get("state", "open")
        status_map = {
            "open": IssueStatus.TODO,
            "in_progress": IssueStatus.IN_PROGRESS,
            "closed": IssueStatus.DONE
        }
        return status_map.get(state, IssueStatus.TODO)

    def _extract_priority(self, labels: list) -> Optional[str]:
        """Extract priority from labels."""
        for label in labels:
            label_name = label.get("name", "")
            if label_name.lower() in ["high", "medium", "low"]:
                return label_name.lower()
        return None


class GitLabIssueClient(IssueClient):
    """GitLab issue client."""

    def __init__(self, token: str, project_id: int, base_url: str = "https://gitlab.com"):
        self.token = token
        self.project_id = project_id
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "PRIVATE-TOKEN": token,
            "Accept": "application/json"
        })

    @property
    def repository(self) -> str:
        """Get repository identifier."""
        return str(self.project_id)

    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue information by ID."""
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/issues/{issue_id}"

        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return self._parse_issue(data)
        except Exception:
            pass

        return None

    def _parse_issue(self, data: dict) -> Issue:
        """Parse GitLab issue response."""
        return Issue(
            id=data.get("iid", ""),
            key=data.get("iid", ""),
            summary=data.get("title", ""),
            description=data.get("description"),
            status=self._parse_status(data),
            priority=data.get("labels", []) and self._extract_priority(data.get("labels", [])),
            labels=[l for l in data.get("labels", [])] if "labels" in data else [],
        )

    def _parse_status(self, data: dict) -> str:
        """Parse issue status."""
        state = data.get("state", "opened")
        status_map = {
            "opened": IssueStatus.TODO,
            "active": IssueStatus.IN_PROGRESS,
            "closed": IssueStatus.DONE
        }
        return status_map.get(state, IssueStatus.TODO)

    def _extract_priority(self, labels: list) -> Optional[str]:
        """Extract priority from labels."""
        for label in labels:
            if label.lower() in ["high", "medium", "low"]:
                return label.lower()
        return None


class JiraIssueClient(IssueClient):
    """Jira issue client."""

    def __init__(self, base_url: str, username: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Basic {self._encode_auth(username, api_token)}",
            "Accept": "application/json"
        })

    def _encode_auth(self, username: str, api_token: str) -> str:
        """Encode basic auth."""
        import base64
        auth_str = f"{username}:{api_token}"
        return base64.b64encode(auth_str.encode()).decode()

    @property
    def repository(self) -> str:
        """Get repository identifier."""
        return "jira"

    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue information by ID."""
        url = f"{self.base_url}/rest/api/2/issue/{issue_id}"

        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return self._parse_issue(data)
        except Exception:
            pass

        return None

    def _parse_issue(self, data: dict) -> Issue:
        """Parse Jira issue response."""
        fields = data.get("fields", {})

        return Issue(
            id=data.get("key", ""),
            key=data.get("key", ""),
            summary=data.get("fields", {}).get("summary", ""),
            description=data.get("fields", {}).get("description", ""),
            status=self._parse_status(data),
            priority=fields.get("priority", {}).get("name", ""),
            labels=[f.get("name", "") for f in fields.get("labels", [])],
        )

    def _parse_status(self, data: dict) -> str:
        """Parse issue status."""
        status_name = data.get("fields", {}).get("status", {}).get("name", "").lower()
        status_map = {
            "todo": IssueStatus.TODO,
            "inprogress": IssueStatus.IN_PROGRESS,
            "inreview": IssueStatus.IN_REVIEW,
            "done": IssueStatus.DONE,
            "closed": IssueStatus.CLOSED
        }
        return status_map.get(status_name, IssueStatus.TODO)
