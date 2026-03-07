"""Tests for input validation and edge cases."""

import pytest
from git_deep_analyzer.integrations.issue_tracker.models import (
    Issue, IssueStatus, IssuePriority, IssueComment
)
from datetime import datetime


class TestIssueModelEdgeCases:
    """Test Issue model with edge cases."""

    def test_issue_with_empty_description(self):
        """Given: Issue with empty description
        When: Issue is created
        Then: Should handle empty string
        """
        # Given & When
        issue = Issue(
            id="123",
            key="PROJ-123",
            summary="Test",
            description="",  # Empty description
            status=IssueStatus.TODO,
            priority=IssuePriority.MEDIUM,
            labels=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            reporter="user",
            reporter_email="user@example.com",
            project_key="PROJ",
            project_name="Test"
        )

        # Then
        assert issue.description == ""

    def test_issue_with_long_summary(self):
        """Given: Issue with very long summary
        When: Issue is created
        Then: Should handle long strings
        """
        # Given
        long_summary = "A" * 500  # Very long summary

        # When
        issue = Issue(
            id="123",
            key="PROJ-123",
            summary=long_summary,
            description="Test",
            status=IssueStatus.TODO,
            priority=IssuePriority.MEDIUM,
            labels=[],
            created_at=datetime.now(),
            updated_at=datetime.now.now(),
            reporter="user",
            reporter_email="user@example.com",
            project_key="PROJ",
            project_name="Test"
        )

        # Then
        assert len(issue.summary) == 500

    def test_issue_with_many_labels(self):
        """Given: Issue with many labels
        When: Issue is created
        Then: Should handle list of labels
        """
        # Given
        many_labels = [f"label-{i}" for i in range(50)]

        # When
        issue = Issue(
            id="123",
            key="PROJ-123",
            summary="Test",
            description="Test",
            status=IssueStatus.TODO,
            priority=IssuePriority.MEDIUM,
            labels=many_labels,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            reporter="user",
            reporter_email="user@example.com",
            project_key="PROJ",
            project_name="Test"
        )

        # Then
        assert len(issue.labels) == 50
        assert issue.labels[0] == "label-0"
        assert issue.labels[49] == "label-49"

    def test_issue_with_special_characters_in_summary(self):
        """Given: Issue with special characters
        When: Issue is created
        Then: Should handle special characters
        """
        # Given
        special_summary = "Test <b>bold</b> & 'quote' emoji 😉"

        # When
        issue = Issue(
            id="123",
            key="PROJ-123",
            summary=special_summary,
            description="Test",
            status=IssueStatus.TODO,
            priority=IssuePriority.MEDIUM,
            labels=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            reporter="user",
            reporter_email="user@example.com",
            project_key="PROJ",
            project_name="Test"
        )

        # Then
        assert special_summary in issue.summary

    def test_issue_comment_with_empty_content(self):
        """Given: IssueComment with empty content
        When: IssueComment is created
        Then: Should handle empty content
        """
        # When
        comment = IssueComment(
            id_str="comment-1",
            author="user",
            author_email="user@example.com",
            content="",  # Empty content
            created_at=datetime.now()
        )

        # Then
        assert comment.content == ""

    def test_issue_with_none_assignee(self):
        """Given: Issue without assignee
        When: Issue is created
        Then: Should use None defaults
        """
        # When
        issue = Issue(
            id="123",
            key="PROJ-123",
            summary="Test",
            description="Test",
            status=IssueStatus.TODO,
            priority=IssuePriority.MEDIUM,
            labels=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            reporter="user",
            reporter_email="user@example.com",
            project_key="PROJ",
            project_name="Test",
            assignee=None,  # Explicit None
            assignee_email=None
        )

        # Then
        assert issue.assignee is None
        assert issue.assignee_email is None
