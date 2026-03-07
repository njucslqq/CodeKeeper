"""GitHub Issue Tracker integration."""

import requests
from typing import List, Optional
from datetime import datetime
from .base import IssueTrackerBase
from .models import Issue, IssueComment, IssueAttachment, IssueStatus, IssuePriority


class GitHubTracker(IssueTrackerBase):
    """GitHub Issue Tracker integration."""

    def __init__(self, config: dict):
        """
        Initialize GitHub tracker.

        Args:
            config: Configuration dict with url and token
        """
        super().__init__(config)
        self.base_url = config.get("url", "https://api.github.com")
        self.token = config.get("token", "")
        self.session = None

    def connect(self) -> bool:
        """Connect to GitHub API."""
        import os

        self.session = requests.Session()

        # Support multiple authentication methods
        if self.token:
            # Personal Access Token
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            })
        elif os.environ.get("GITHUB_TOKEN"):
            # Environment variable
            token = os.environ["GITHUB_TOKEN"]
            self.session.headers.update({
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            })

        # Test connection
        try:
            response = self.session.get(f"{self.base_url}/user")
            return response.status_code == 200
        except Exception:
            return False

    def fetch_issues(
        self,
        owner: str,
        repo: str,
        state: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        labels: Optional[List[str]] = None,
        milestone: Optional[str] = None
    ) -> List[Issue]:
        """
        Fetch issues from GitHub repository.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Filter by state (open/closed/all)
            since: Start date filter
            until: End date filter
            labels: Filter by labels
            milestone: Filter by milestone

        Returns:
            List of issues
        """
        if not self.session:
            raise RuntimeError("Not connected to GitHub API")

        # Build query parameters
        params = {}
        if state:
            params["state"] = state
        if since:
            params["since"] = since.isoformat() + "Z"
        if until:
            params["until"] = until.isoformat() + "Z"
        if labels:
            params["labels"] = ",".join(labels)
        if milestone:
            params["milestone"] = milestone

        # Sort by created date
        params["sort"] = "created"
        params["direction"] = "asc"

        url = f"{self.base_url}/repos/{owner}/{repo}/issues"

        all_issues = []
        page = 1

        while True:
            params["page"] = page
            params["per_page"] = 100

            response = self.session.get(url, params=params, timeout=30)

            if response.status_code != 200:
                raise RuntimeError(f"GitHub API error: {response.text}")

            data = response.json()

            if not data:
                break

            # Parse issues (both issues and PRs)
            for issue_data in data:
                issue = self._parse_issue(issue_data)
                all_issues.append(issue)

            page += 1

        return all_issues

    def _parse_issue(self, issue_data: dict) -> Issue:
        """
        Parse issue data from GitHub API response.

        Args:
            issue_data: Issue data from API

        Returns:
            Issue object
        """
        # Distinguish Issue from Pull Request
        is_pr = "pull_request" in issue_data and issue_data["pull_request"] is not None

        # Map GitHub state to IssueStatus
        state = issue_data.get("state", "open")
        if state == "open":
            status = IssueStatus.OPEN
        elif state == "closed":
            status = IssueStatus.CLOSED
        else:
            status = IssueStatus.IN_PROGRESS

        # Map labels to priority
        labels = [label.get("name", "") for label in issue_data.get("labels", [])]
        priority = self._map_labels_to_priority(labels)

        # Parse comments count
        comments_count = issue_data.get("comments", 0)

        # Parse milestone
        milestone = issue_data.get("milestone")
        milestone_title = milestone.get("title") if milestone else None

        return Issue(
            key=str(issue_data.get("number")),
            title=issue_data.get("title", ""),
            description=issue_data.get("body", "") or "",
            status=status,
            priority=priority,
            author=issue_data.get("user", {}).get("login", ""),
            created_at=datetime.fromisoformat(
                issue_data.get("created_at", "").replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                issue_data.get("updated_at", "").replace("Z", "+00:00")
            ),
            comments=[],
            attachments=[],
            labels=labels,
            milestone=milestone_title,
            url=issue_data.get("html_url", ""),
            is_pull_request=is_pr
        )

    def _map_labels_to_priority(self, labels: List[str]) -> IssuePriority:
        """
        Map GitHub labels to priority.

        Args:
            labels: List of label names

        Returns:
            IssuePriority
        """
        if any(label.lower() in ["critical", "urgent"] for label in labels):
            return IssuePriority.CRITICAL
        elif any(label.lower() == "high" for label in labels):
            return IssuePriority.HIGH
        elif any(label.lower() == "low" for label in labels):
            return IssuePriority.LOW
        else:
            return IssuePriority.MEDIUM

    def fetch_comments(
        self,
        issue_number: int,
        owner: str,
        repo: str
    ) -> List[IssueComment]:
        """
        Fetch comments for an issue.

        Args:
            issue_number: Issue number
            owner: Repository owner
            repo: Repository name

        Returns:
            List of comments
        """
        if not self.session:
            raise RuntimeError("Not connected to GitHub API")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        params = {"per_page": 100}

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error: {response.text}")

        comments_data = response.json()

        comments = []
        for comment_data in comments_data:
            comment = IssueComment(
                id=str(comment_data.get("id")),
                author=comment_data.get("user", {}).get("login", ""),
                content=comment_data.get("body", ""),
                created_at=datetime.fromisoformat(
                    comment_data.get("created_at", "").replace("Z", "+00:00")
                )
            )
            comments.append(comment)

        return comments

    def search(self, query: str, owner: str, repo: str) -> List[Issue]:
        """
        Search issues in GitHub repository.

        Args:
            query: Search query
            owner: Repository owner
            repo: Repository name

        Returns:
            List of matching issues
        """
        if not self.session:
            raise RuntimeError("Not connected to GitHub API")

        # Build search query with repo qualifier
        full_query = f"{query} repo:{owner}/{repo}"

        url = f"{self.base_url}/search/issues"
        params = {"q": full_query, "per_page": 100}

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error: {response.text}")

        data = response.json()

        # Parse issues from search results
        issues = []
        for item in data.get("items", []):
            issue = self._parse_issue(item)
            issues.append(issue)

        return issues

    def fetch_pull_requests(
        self,
        owner: str,
        repo: str,
        state: Optional[str] = None
    ) -> List[Issue]:
        """
        Fetch pull requests.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Filter by state (open/closed/all)

        Returns:
            List of pull requests
        """
        # Fetch all issues and filter PRs
        issues = self.fetch_issues(owner=owner, repo=repo, state=state)
        prs = [issue for issue in issues if issue.is_pull_request]
        return prs
