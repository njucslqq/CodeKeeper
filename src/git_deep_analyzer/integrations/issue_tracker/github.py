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
                issue = self._parse_issue(issue_data, owner, repo)
                all_issues.append(issue)

            page += 1

        return all_issues

    def _parse_issue(self, issue_data: dict, repo_owner: str, repo_name: str) -> Issue:
        """
        Parse issue data from GitHub API response.

        Args:
            issue_data: Issue data from API
            repo_owner: Repository owner
            repo_name: Repository name

        Returns:
            Issue object
        """
        # Distinguish Issue from Pull Request
        is_pr = "pull_request" in issue_data and issue_data["pull_request"] is not None

        # Map GitHub state to IssueStatus
        state = issue_data.get("state", "open")
        if state == "open":
            status = IssueStatus.IN_PROGRESS
        elif state == "closed":
            status = IssueStatus.DONE
        else:
            status = IssueStatus.TODO

        # Map labels to priority
        labels = [label.get("name", "") for label in issue_data.get("labels", [])]
        priority = self._map_labels_to_priority(labels)

        # Parse author
        user_data = issue_data.get("user", {})
        reporter = user_data.get("login", "")
        reporter_email = f"{reporter}@users.noreply.github.com" if reporter else ""

        # Parse assignee
        assignee_data = issue_data.get("assignee")
        assignee = None
        assignee_email = None
        if assignee_data:
            assignee = assignee_data.get("login", "")
            assignee_email = f"{assignee}@users.noreply.github.com"

        # Parse times
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

        # Parse milestone
        milestone = issue_data.get("milestone")
        milestone_title = milestone.get("title") if milestone else None

        # Project info
        project_key = f"{repo_owner}/{repo_name}"
        project_name = repo_name

        # Build issue summary (include milestone if present)
        summary = issue_data.get("title", "")
        if milestone_title:
            summary = f"[{milestone_title}] {summary}"

        return Issue(
            id=str(issue_data.get("id", "")),
            key=str(issue_data.get("number", "")),
            summary=summary,
            description=issue_data.get("body", "") or "",
            status=status,
            priority=priority,
            labels=labels,
            created_at=created_at,
            updated_at=updated_at,
            resolved_at=resolved_at,
            reporter=reporter,
            reporter_email=reporter_email,
            assignee=assignee,
            assignee_email=assignee_email,
            comments=[],
            attachments=[],
            relations=[],
            project_key=project_key,
            project_name=project_name
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

    def fetch_issue_detail(
        self,
        issue_number: int,
        owner: str,
        repo: str
    ) -> Issue:
        """
        Fetch issue details including comments.

        Args:
            issue_number: Issue number
            owner: Repository owner
            repo: Repository name

        Returns:
            Issue with comments
        """
        if not self.session:
            raise RuntimeError("Not connected to GitHub API")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        params = {"per_page": 100}

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error: {response.text}")

        issue_data = response.json()
        issue = self._parse_issue(issue_data, owner, repo)

        # Fetch comments
        comments = self.fetch_comments(issue_number, owner, repo)
        issue.comments = comments

        return issue

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
            user_login = comment_data.get("user", {}).get("login", "")
            comment = IssueComment(
                id_str=str(comment_data.get("id")),
                author=user_login,
                author_email=f"{user_login}@users.noreply.github.com" if user_login else "",
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
            issue = self._parse_issue(item, owner, repo)
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
        if not self.session:
            raise RuntimeError("Not connected to GitHub API")

        # Use GitHub pull requests API directly
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"

        params = {}
        if state:
            params["state"] = state
        params["per_page"] = 100
        params["sort"] = "created"
        params["direction"] = "asc"

        all_prs = []
        page = 1

        while True:
            params["page"] = page

            response = self.session.get(url, params=params, timeout=30)

            if response.status_code != 200:
                raise RuntimeError(f"GitHub API error: {response.text}")

            data = response.json()

            if not data:
                break

            # Parse pull requests
            for pr_data in data:
                # Use PR number as key
                pr_issue = self._parse_issue(
                    {
                        **pr_data,
                        "id": pr_data.get("id", ""),
                        "number": pr_data.get("number", ""),
                        "title": f"[PR] {pr_data.get('title', '')}",
                        "body": pr_data.get("body", "") or "",
                        "state": pr_data.get("state", "open"),
                        "labels": pr_data.get("labels", []),
                        "user": pr_data.get("user", {}),
                        "created_at": pr_data.get("created_at", ""),
                        "updated_at": pr_data.get("updated_at", ""),
                        "closed_at": pr_data.get("closed_at"),
                        "assignee": pr_data.get("assignee")
                    },
                    owner,
                    repo
                )
                all_prs.append(pr_issue)

            page += 1

        return all_prs

    def search_issues(self, query: str, owner: Optional[str] = None, repo: Optional[str] = None) -> List[Issue]:
        """
        Search issues and pull requests.

        Args:
            query: Search query (GitHub search syntax)
            owner: Repository owner (optional, defaults to repo_owner from config)
            repo: Repository name (optional, defaults to repo_name from config)

        Returns:
            List of Issues/PRs matching the search query
        """
        if not self.session:
            raise RuntimeError("Not connected to GitHub API")

        owner = owner or self.config.get("repo_owner", "")
        repo = repo or self.config.get("repo_name", "")

        if not owner or not repo:
            raise ValueError("owner and repo are required")

        # Use GitHub search API
        url = f"{self.base_url}/search/issues"

        # Build search query with repo qualifier
        full_query = f"repo:{owner}/{repo} {query}"

        params = {
            "q": full_query,
            "per_page": 100
        }

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error: {response.text}")

        data = response.json()

        issues = []
        for item in data.get("items", []):
            issue = self._parse_issue(item, owner, repo)
            issues.append(issue)

        return issues
