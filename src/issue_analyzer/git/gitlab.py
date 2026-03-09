"""GitLab Git client implementation."""

from typing import List, Optional
from datetime import datetime
import requests
from issue_analyzer.models import Commit, CommitFileChange, ChangeType
from .base import GitClient


class GitLabClient(GitClient):
    """GitLab Git client implementation."""

    def __init__(
        self,
        token: str,
        project_id: int,
        base_url: str = "https://gitlab.com"
    ):
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

    def get_commits(
        self,
        issue_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Commit]:
        """Get commits related to an issue."""
        # Search for commits referencing the issue
        search_query = f"#{issue_id}"
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/repository/commits"

        params = {"search": search_query, "per_page": 100}
        if since:
            params["after"] = since.isoformat()
        if until:
            params["before"] = until.isoformat()

        commits: List[Commit] = []
        page = 1

        while True:
            params["page"] = page
            response = self.session.get(url, params=params)

            if response.status_code != 200:
                break

            data = response.json()
            if not data:
                break

            for item in data:
                commit = self._parse_commit(item)
                commits.append(commit)

            page += 1

        return commits

    def get_commit_diff(self, commit_hash: str) -> str:
        """Get diff for a commit."""
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/repository/commits/{commit_hash}/diff"
        response = self.session.get(url)

        if response.status_code != 200:
            return ""

        return response.text

    def _parse_commit(self, item: dict) -> Commit:
        """Parse GitLab commit response to Commit model."""
        # Parse commit author
        author_name = item.get("author_name", "")
        author_email = item.get("author_email", "")

        # Parse commit time
        created_at = item.get("created_at")
        author_time = None
        if created_at:
            author_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        # Parse commit time (same as author time for GitLab)
        commit_time = author_time or datetime.utcnow()

        # Parse file changes
        files_changed = []
        if "diff_refs" in item:
            for diff_ref in item["diff_refs"]:
                # Try to parse files from the diff
                old_path = diff_ref.get("old_path")
                new_path = diff_ref.get("new_path")

                if new_path:
                    change_type = ChangeType.ADDED
                elif old_path:
                    change_type = ChangeType.DELETED
                else:
                    continue

                if old_path and new_path:
                    change_type = ChangeType.MODIFIED

                file_change = CommitFileChange(
                    path=new_path or old_path,
                    old_path=old_path,
                    change_type=change_type,
                    is_binary=False
                )
                files_changed.append(file_change)

        # Parse parents
        parents = []
        if "parent_ids" in item:
            parents = item["parent_ids"]

        # Parse commit message
        message = item.get("title", "")
        if "message" in item:
            message = f"{message}\n\n{item['message']}"

        return Commit(
            hash=item.get("id", ""),
            message=message,
            author=author_name,
            author_email=author_email,
            author_time=author_time or datetime.utcnow(),
            commit_time=commit_time,
            parents=parents,
            files_changed=files_changed,
            repository=str(self.project_id)
        )
