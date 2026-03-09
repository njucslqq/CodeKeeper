"""Document system integration module."""

from .base import DocClient, DocCollector
from .confluence import ConfluenceClient
from .feishu import FeishuClient
from .issue import IssueClient, GitHubIssueClient, GitLabIssueClient, JiraIssueClient

__all__ = [
    "DocClient",
    "DocCollector",
    "ConfluenceClient",
    "FeishuClient",
    "IssueClient",
    "GitHubIssueClient",
    "GitLabIssueClient",
    "JiraIssueClient",
]
