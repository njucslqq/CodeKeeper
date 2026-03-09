"""Git repository integration module."""

from .base import GitClient, GitCollector
from .github import GitHubClient

__all__ = [
    "GitClient",
    "GitCollector",
    "GitHubClient",
]
