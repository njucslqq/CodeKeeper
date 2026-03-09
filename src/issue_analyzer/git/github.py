"""GitHub Git client implementation."""

import re
from typing import List, Optional
from datetime import datetime
import requests
from issue_analyzer.models import Commit, CommitFileChange, ChangeType
from .base import GitClient


class GitHubClient(GitClient):
    """GitHub Git client implementation."""

    def __init__(
        self,
        token: str,
        repo_owner: str,
        repo_name: str,
        base_url: str = "https://api.github.com"
    ):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })

    @property
    def repository(self) -> str:
        """Get repository identifier."""
        return f"{self.repo_owner}/{self.repo_name}"

    def get_commits(
        self,
        issue_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Commit]:
        """Get commits related to an issue."""
        # Search for commits referencing the issue
        search_query = f"{issue_id} repo:{self.repo_owner}/{self.repo_name}"
        url = f"{self.base_url}/search/commits"

        params = {"q": search_query, "per_page": 100}
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()

        commits: List[Commit] = []
        page = 1

        while True:
            params["page"] = page
            response = self.session.get(url, params=params)

            if response.status_code != 200:
                break

            data = response.json()
            if "items" not in data or not data["items"]:
                break

            for item in data["items"]:
                commit = self._parse_commit(item)
                commits.append(commit)

            page += 1

        return commits

    def get_commit_diff(self, commit_hash: str) -> str:
        """Get diff for a commit."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/commits/{commit_hash}"
        response = self.session.get(url, params={"per_page": 1})

        if response.status_code != 200:
            return ""

        data = response.json()
        return data.get("files_diff_url", "")

    def _parse_commit(self, item: dict) -> Commit:
        """Parse GitHub commit response to Commit model."""
        commit_data = item.get("commit", {})

        # Parse commit
        author = commit_data.get("author", {})
        author_info = author.get("name", "")
        author_email = author.get("email", "")

        # Parse author time
        author_time = None
        if "date" in author:
            author_time = datetime.fromisoformat(author["date"].replace('Z', '+00:00'))

        # Parse commit time
        commit_time = None
        if "committer" in commit_data:
            committer = commit_data["committer"]
            if "date" in committer:
                commit_time = datetime.fromisoformat(committer["date"].replace('Z', '+00:00'))

        # Parse file changes
        files_changed = []
        if "files" in commit_data:
            for file_item in commit_data["files"]:
                change_type = self._parse_change_type(file_item)
                file_change = CommitFileChange(
                    path=file_item.get("filename", ""),
                    old_path=file_item.get("previous_filename"),
                    change_type=change_type,
                    additions=file_item.get("additions", 0),
                    deletions=file_item.get("deletions", 0),
                    is_binary=file_item.get("status", "") == "removed" and "blob" not in file_item
                )
                files_changed.append(file_change)

        # Parse parents
        parents = []
        if "parents" in commit_data:
            parents = [p.get("sha", "") for p in commit_data["parents"]]

        return Commit(
            hash=commit_data.get("sha", ""),
            message=commit_data.get("message", ""),
            author=author_info,
            author_email=author_email,
            author_time=author_time or datetime.utcnow(),
            commit_time=commit_time or datetime.utcnow(),
            parents=parents,
            files_changed=files_changed,
            repository=f"{self.repo_owner}/{self.repo_name}"
        )

    @staticmethod
    def _parse_change_type(file_item: dict) -> str:
        """Parse file change type from GitHub status."""
        status = file_item.get("status", "")

        if status == "added":
            return ChangeType.ADDED
        elif status == "removed":
            return ChangeType.DELETED
        elif status == "modified":
            return ChangeType.MODIFIED
        elif status == "renamed":
            return ChangeType.RENAMED
        else:
            return ChangeType.MODIFIED
