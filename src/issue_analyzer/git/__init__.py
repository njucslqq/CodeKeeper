"""Git repository integration module."""

from .base import GitClient, GitCollector
from .factory import create_repos_from_config, create_repos_from_submodule
from .github import GitHubClient
from .gitlab import GitLabClient

__all__ = [
    "GitClient",
    "GitCollector",
    "create_repos_from_config",
    "create_repos_from_submodule",
    "GitHubClient",
    "GitLabClient",
]
