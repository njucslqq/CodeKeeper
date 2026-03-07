"""External systems integration module."""

from .issue_tracker.base import IssueTrackerBase
from .issue_tracker.models import Issue, IssueComment, IssueAttachment, IssueStatus, IssuePriority
from .issue_tracker.jira import JiraTracker
from .issue_tracker.github import GitHubTracker

__all__ = [
    "IssueTrackerBase",
    "Issue",
    "IssueComment",
    "IssueAttachment",
    "IssueStatus",
    "IssuePriority",
    "JiraTracker",
    "GitHubTracker"
]
