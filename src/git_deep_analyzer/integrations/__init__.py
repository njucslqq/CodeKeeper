"""External systems integration module."""

from .issue_tracker.base import IssueTrackerBase
from .issue_tracker.models import Issue, IssueComment, IssueAttachment, IssueStatus, IssuePriority
from .issue_tracker.jira import JiraTracker
from .issue_tracker.github import GitHubTracker
from .docs.base import DocsSystemBase
from .docs.models import Document, DocumentType
from .docs.confluence import ConfluenceDocs
from .docs.feishu import FeishuDocs

__all__ = [
    "IssueTrackerBase",
    "Issue",
    "IssueComment",
    "IssueAttachment",
    "IssueStatus",
    "IssuePriority",
    "JiraTracker",
    "GitHubTracker",
    "DocsSystemBase",
    "Document",
    "DocumentType",
    "ConfluenceDocs",
    "FeishuDocs"
]
