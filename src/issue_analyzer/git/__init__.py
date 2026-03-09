"""Git repository integration module."""

from .base import GitClient, GitCollector
from .github import GitHubClient
from .gitlab import GitLabClient

__all__ = [
    "GitClient",
    "GitCollector",
    "GitHubClient",
    "GitLabClient",
]
