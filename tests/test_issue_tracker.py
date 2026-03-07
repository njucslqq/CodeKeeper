"""Tests for Issue Tracker base class."""

from datetime import datetime, timedelta
from git_deep_analyzer.integrations.issue_tracker.base import IssueTrackerBase
from git_deep_analyzer.integrations.issue_tracker.models import Issue, IssueStatus, IssuePriority
import pytest


@pytest.mark.unit
class TestIssueTrackerBase:
    """测试IssueTrackerBase"""

    def test_base_class_is_abstract(self):
        """测试基类是抽象的"""
        # Given & Then
        with pytest.raises(TypeError):
            IssueTrackerBase({})

    def test_abstract_methods_defined(self):
        """测试抽象方法已定义"""
        # Given & Then
        assert hasattr(IssueTrackerBase, "connect")
        assert hasattr(IssueTrackerBase, "fetch_issues")
        assert hasattr(IssueTrackerBase, "fetch_issue_detail")
        assert hasattr(IssueTrackerBase, "search_issues")


@pytest.mark.unit
class TestIssueModels:
    """测试Issue数据模型"""

    def test_issue_model_initialization(self):
        """测试Issue模型初始化"""
        # Given
        issue = Issue(
            id="123",
            key="PROJ-123",
            summary="Test issue",
            description="Test description",
            status=IssueStatus.TODO,
            priority=IssuePriority.HIGH,
            labels=["bug", "feature"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resolved_at=None,
            reporter="Test User",
            reporter_email="test@example.com"
        )

        # Then
        assert issue.id == "123"
        assert issue.key == "PROJ-123"
        assert issue.status == IssueStatus.TODO
        assert issue.priority == IssuePriority.HIGH
        assert len(issue.comments) == 0  # 应该初始化为空列表
        assert len(issue.attachments) == 0
        assert len(issue.relations) == 0

    @pytest.mark.parametrize("status", [
        IssueStatus.BACKLOG,
        IssueStatus.TODO,
        IssueStatus.IN_PROGRESS,
        IssueStatus.IN_REVIEW,
        IssueStatus.DONE,
        IssueStatus.CLOSED,
        IssueStatus.CANCELLED,
    ])
    def test_issue_status_enum(self, status):
        """测试IssueStatus枚举"""
        # Then
        assert isinstance(status.value, str)

    @pytest.mark.parametrize("priority", [
        IssuePriority.CRITICAL,
        IssuePriority.HIGH,
        IssuePriority.MEDIUM,
        IssuePriority.LOW,
        IssuePriority.LOWEST,
    ])
    def test_issue_priority_enum(self, priority):
        """测试IssuePriority枚举"""
        # Then
        assert isinstance(priority.value, str)

    def test_issue_with_resolved_date(self):
        """测试带解决日期的Issue"""
        # Given
        resolved_at = datetime.now()
        issue = Issue(
            id="124",
            key="PROJ-124",
            summary="Test resolved issue",
            description="Test description",
            status=IssueStatus.DONE,
            priority=IssuePriority.MEDIUM,
            labels=["resolved"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resolved_at=resolved_at,
            reporter="Test User",
            reporter_email="test@example.com"
        )

        # Then
        assert issue.resolved_at == resolved_at

    def test_issue_with_assignee(self):
        """测试带指派人的Issue"""
        # Given
        issue = Issue(
            id="125",
            key="PROJ-125",
            summary="Test assigned issue",
            description="Test description",
            status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.HIGH,
            labels=["in-progress"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            reporter="Test User",
            reporter_email="test@example.com",
            assignee="Assignee User",
            assignee_email="assignee@example.com"
        )

        # Then
        assert issue.assignee == "Assignee User"
        assert issue.assignee_email == "assignee@example.com"

    def test_issue_comment_model(self):
        """测试IssueComment模型"""
        # Given
        comment = {
            "id": "comment-1",
            "author": "Commenter",
            "author_email": "commenter@example.com",
            "content": "Test comment",
            "created_at": datetime.now()
        }

        # When
        from .models import IssueComment
        comment_obj = IssueComment(**comment)

        # Then
        assert comment_obj.id == "comment-1"
        assert comment_obj.author == "Commenter"
        assert isinstance(comment_obj.created_at, datetime)

    def test_issue_attachment_model(self):
        """测试IssueAttachment模型"""
        # Given
        attachment = {
            "id": "att-1",
            "filename": "test.png",
            "url": "http://example.com/test.png",
            "size": 1024,
            "content_type": "image/png",
            "created_at": datetime.now()
        }

        # When
        from .models import IssueAttachment
        attachment_obj = IssueAttachment(**attachment)

        # Then
        assert attachment_obj.filename == "test.png"
        assert attachment_obj.size == 1024
        assert attachment_obj.content_type == "image/png"

    def test_issue_relation_model(self):
        """测试IssueRelation模型"""
        # Given
        relation = {
            "type": "blocks",
            "issue_id": "PROJ-100",
            "issue_summary": "Blocked issue"
        }

        # When
        from .models import IssueRelation
        relation_obj = IssueRelation(**relation)

        # Then
        assert relation_obj.type == "blocks"
        assert relation_obj.issue_id == "PROJ-100"
