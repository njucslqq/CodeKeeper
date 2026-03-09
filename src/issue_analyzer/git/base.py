"""Base Git client and collector."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from issue_analyzer.models import Commit


class GitClient(ABC):
    """Abstract base class for Git clients."""

    @abstractmethod
    def get_commits(
        self,
        issue_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Commit]:
        """Get commits related to an issue."""
        pass

    @abstractmethod
    def get_commit_diff(self, commit_hash: str) -> str:
        """Get diff for a commit."""
        pass


class GitCollector:
    """Collect commits from configured Git repositories."""

    def __init__(self, clients: List[GitClient]):
        self.clients = clients

    def collect_commits(
        self,
        issue_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Commit]:
        """Collect commits from all configured repositories."""
        all_commits = []
        for client in self.clients:
            commits = client.get_commits(issue_id, since, until)
            all_commits.extend(commits)
        return all_commits
