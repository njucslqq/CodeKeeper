"""Tests for GitLab Issue Tracker integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from git_deep_analyzer.integrations.issue_tracker.gitlab import GitLabTracker
from git_deep_analyzer.integrations.issue_tracker.models import Issue, IssueStatus, IssuePriority


class TestGitLabTracker:
    """Test GitLabTracker class."""

    @pytest.fixture
    def gitlab_config(self):
        """Sample GitLab configuration."""
        return {
            "url": "https://gitlab.com",
            "token": "test_token"
        }

    @pytest.fixture
    def gitlab_tracker(self, gitlab_config):
        """Create GitLabTracker instance."""
        return GitLabTracker(gitlab_config)

    def test_init_with_config(self, gitlab_tracker):
        """Given: GitLab config
        When: GitLabTracker is created
        Then: Config is stored correctly
        """
        assert gitlab_tracker.base_url == "https://gitlab.com"
        assert gitlab_tracker.token == "test_token"

    def test_init_with_custom_url(self):
        """Given: GitLab config with custom URL
        When: GitLabTracker is created
        Then: Custom URL is used
        """
        config = {"url": "https://gitlab.example.com", "token": "test_token"}
        tracker = GitLabTracker(config)
        assert tracker.base_url == "https://gitlab.example.com"

    @patch('git_deep_analyzer.integrations.issue_tracker.gitlab.requests.Session')
    def test_connect_success(self, mock_session_class, gitlab_config):
        """Given: GitLab tracker with valid token
        When: connect() is called
        Then: Returns True and session is configured
        """
        # Given
        mock_session = Mock()
        mock_session.get.return_value.status_code = 200
        mock_session.headers = {"Authorization": "PRIVATE-TOKEN test_token"}
        mock_session_class.return_value = mock_session

        # When
        tracker = GitLabTracker(gitlab_config)
        result = tracker.connect()

        # Then
        assert result is True
        assert tracker.session is not None
        assert "PRIVATE-TOKEN" in mock_session.headers.get("Authorization", "")

    @patch('git_deep_analyzer.integrations.issue_tracker.gitlab.requests.Session')
    def test_connect_with_env_token(self, mock_session_class):
        """Given: GitLab tracker without token in config but with env var
        When: connect() is called
        Then: Uses environment variable token
        """
        # Given
        import os
        os.environ["GITLAB_TOKEN"] = "env_token"
        config = {"url": "https://gitlab.com"}
        mock_session = Mock()
        mock_session.get.return_value.status_code = 200
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        # When
        tracker = GitLabTracker(config)
        result = tracker.connect()

        # Then
        assert result is True
        assert "PRIVATE-TOKEN env_token" in str(mock_session.headers.get("Authorization", ""))
        del os.environ["GITLAB_TOKEN"]

    @patch('git_deep_analyzer.integrations.issue_tracker.gitlab.requests.Session')
    def test_connect_failure(self, mock_session_class, gitlab_config):
        """Given: GitLab tracker with invalid connection
        When: connect() is called
        Then: Returns False
        """
        # Given
        mock_session = Mock()
        mock_session.get.side_effect = Exception("Connection error")
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        # When
        tracker = GitLabTracker(gitlab_config)
        result = tracker.connect()

        # Then
        assert result is False

    @patch('git_deep_analyzer.integrations.issue_tracker.gitlab.requests.Session')
    def test_fetch_issues_success(self, mock_session_class, gitlab_tracker):
        """Given: GitLab tracker with active session
        When: fetch_issues() is called
        Then: Returns list of issues
        """
        # Given
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "iid": 101,
                "project_id": 123,
                "title": "Test Issue",
                "description": "Test description",
                "state": "opened",
                "labels": ["bug", "high"],
                "author": {
                    "username": "testuser",
                    "email": "test@example.com"
                },
                "assignee": {
                    "username": "assignee",
            "email": "assignee@example.com"
                },
                "created_at": "2024-01-01T00:00:00.000Z",
                "updated_at": "2024-01-02T00:00:00.000Z",
                "closed_at": None,
                "milestone": {
                    "title": "v1.0",
                    "id": 10
                },
                "web_url": "https://gitlab.com/owner/repo/-/issues/101",
                "weight": 5,
                "confidential": False,
                "project": {
                    "id": 123,
                    "path_with_namespace": "owner/repo"
                }
            }
        ]
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        gitlab_tracker.session = mock_session

        # When
        issues = gitlab_tracker.fetch_issues(
            project_id_or_path="owner/repo",
            state="opened"
        )

        # Then
        assert len(issues) == 1
        assert isinstance(issues[0], Issue)
        assert issues[0].key == "101"
        assert issues[0].summary == "Test Issue"

    @patch('git_deep_analyzer.integrations.issue_tracker.gitlab.requests.Session')
    def test_fetch_issues_with_labels(self, mock_session_class, gitlab_tracker):
        """Given: GitLab tracker with labels filter
        When: fetch_issues() is called with labels
        Then: URL includes labels parameter
        """
        # Given
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        gitlab_tracker.session = mock_session

        # When
        gitlab_tracker.fetch_issues(
            project_id_or_path="owner/repo",
            labels=["bug", "feature"]
        )

        # Then
        call_args = mock_session.get.call_args
        # URL encoding for labels
        assert "labels" in str(call_args) and "bug" in str(call_args) and "feature" in str(call_args)

    @patch('git_deep_analyzer.integrations.issue_tracker.gitlab.requests.Session')
    def test_fetch_issues_pagination(self, mock_session_class, gitlab_tracker):
        """Given: GitLab tracker with multiple pages
        When: fetch_issues() is called
        Then: Fetches all pages
        """
        # Given
        mock_session = Mock()

        # First page
        first_response = Mock()
        first_response.status_code = 200
        first_response.json.return_value = [
            {"id": 1, "iid": 101, "title": "Issue 1", "state": "opened",
             "author": {"username": "user", "email": "user@example.com"},
             "created_at": "2024-01-01T00:00:00.000Z",
             "updated_at": "2024-01-01T00:00:00.000Z"}
        ]
        first_response.headers = {"X-Total-Pages": "2"}

        # Second page
        second_response = Mock()
        second_response.status_code = 200
        second_response.json.return_value = [
            {"id": 2, "iid": 102, "title": "Issue 2", "state": "opened",
             "author": {"username": "user", "email": "user@example.com"},
             "created_at": "2024-01-02T00:00:00.000Z",
             "updated_at": "2024-01-02T00:00:00.000Z"}
        ]
        # Mock headers.get to return page count
        first_response.headers.get = Mock(return_value="1")
        second_response.headers.get = Mock(return_value="2")

        mock_session.get.side_effect = [first_response, second_response]
        mock_session.headers = {}
        mock_session.headers.get = Mock(return_value="1")
        mock_session_class.return_value = mock_session

        gitlab_tracker.session = mock_session

        # When
        issues = gitlab_tracker.fetch_issues(project_id_or_path="owner/repo")

        # Then
        assert len(issues) == 2
        assert issues[0].key == "101"
        assert issues[1].key == "102"

    @patch('git_deep_analyzer.integrations.issue_tracker.gitlab.requests.Session')
    def test_fetch_issues_not_connected(self, mock_session_class):
        """Given: GitLab tracker without connection
        When: fetch_issues() is called
        Then: Raises RuntimeError
        """
        # Given
        gitlab_config = {"url": "https://gitlab.com", "token": "test_token"}
        tracker = GitLabTracker(gitlab_config)
        # Don't connect

        # When & Then
        with pytest.raises(RuntimeError, match="Not connected"):
            tracker.fetch_issues(project_id_or_path="owner/repo")

    @patch('git_deep_analyzer.integrations.issue_tracker.gitlab.requests.Session')
    def test_fetch_issue_detail(self, mock_session_class, gitlab_tracker):
        """Given: GitLab tracker with active session
        When: fetch_issue_detail() is called
        Then: Returns issue with comments
        """
        # Given
        mock_session = Mock()

        # Issue response
        issue_response = Mock()
        issue_response.status_code = 200
        issue_response.json.return_value = {
            "id": 1,
            "iid": 101,
            "project_id": 123,
            "title": "Test Issue",
            "description": "Test description",
            "state": "opened",
            "labels": ["bug"],
            "author": {
                "username": "testuser",
                "email": "test@example.com"
            },
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-02T00:00:00.000Z"
        }

        # Comments response
        comments_response = Mock()
        comments_response.status_code = 200
        comments_response.json.return_value = [
            {
                "id": 1,
                "author": {"username": "commenter", "email": "commenter@example.com"},
                "body": "Test comment",
                "created_at": "2024-01-03T00:00:00.000Z",
                "updated_at": "2024-01-03T00:00:00.000Z"
            }
        ]

        mock_session.get.side_effect = [issue_response, comments_response]
        mock_session.headers = {}
        mock_session.headers.get.return_value = "1"
        mock_session_class.return_value = mock_session

        gitlab_tracker.session = mock_session

        # When
        issue = gitlab_tracker.fetch_issue_detail(
            project_id_or_path="owner/repo",
            issue_id="101"
        )

        # Then
        assert isinstance(issue, Issue)
        assert issue.key == "101"
        assert len(issue.comments) == 1
        assert issue.comments[0].content == "Test comment"

    @patch('git_deep_analyzer.integrations.issue_tracker.gitlab.requests.Session')
    def test_search_issues(self, mock_session_class, gitlab_tracker):
        """Given: GitLab tracker with active session
        When: search_issues() is called
        Then: Returns matching issues
        """
        # Given
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "iid": 101,
                "title": "Bug in login",
                "description": "Users cannot login",
                "state": "opened",
                "labels": ["bug"],
                "author": {"username": "user", "email": "user@example.com"},
                "created_at": "2024-01-01T00:00:00.000Z",
                "updated_at": "2024-01-01T00:00:00.000Z",
                "project": {
                    "id": 123,
                    "path_with_namespace": "owner/repo"
                }
            }
        ]
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session.headers.get.return_value = "1"
        mock_session_class.return_value = mock_session

        gitlab_tracker.session = mock_session

        # When
        issues = gitlab_tracker.search_issues(
            project_id_or_path="owner/repo",
            query="login"
        )

        # Then
        assert len(issues) == 1
        assert "login" in issues[0].summary.lower()

    def test_parse_state_to_status_opened(self, gitlab_tracker):
        """Given: GitLab issue state 'opened'
        When: _parse_state_to_status() is called
        Then: Returns IssueStatus.IN_PROGRESS
        """
        status = gitlab_tracker._parse_state_to_status("opened")
        assert status == IssueStatus.IN_PROGRESS

    def test_parse_state_to_status_closed(self, gitlab_tracker):
        """Given: GitLab issue state 'closed'
        When: _parse_state_to_status() is called
        Then: Returns IssueStatus.DONE
        """
        status = gitlab_tracker._parse_state_to_status("closed")
        assert status == IssueStatus.DONE

    def test_parse_labels_to_priority_critical(self, gitlab_tracker):
        """Given: GitLab issue labels include 'critical'
        When: _parse_labels_to_priority() is called
        Then: Returns IssuePriority.CRITICAL
        """
        priority = gitlab_tracker._parse_labels_to_priority(["bug", "critical"])
        assert priority == IssuePriority.CRITICAL

    def test_parse_labels_to_priority_high(self, gitlab_tracker):
        """Given: GitLab issue labels include 'high'
        When: _parse_labels_to_priority() is called
        Then: Returns IssuePriority.HIGH
        """
        priority = gitlab_tracker._parse_labels_to_priority(["feature", "high"])
        assert priority == IssuePriority.HIGH

    def test_parse_labels_to_priority_low(self, gitlab_tracker):
        """Given: GitLab issue labels include 'low'
        When: _parse_labels_to_priority() is called
        Then: Returns IssuePriority.LOW
        """
        priority = gitlab_tracker._parse_labels_to_priority(["task", "low"])
        assert priority == IssuePriority.LOW

    def test_parse_labels_to_priority_default(self, gitlab_tracker):
        """Given: GitLab issue without priority labels
        When: _parse_labels_to_priority() is called
        Then: Returns IssuePriority.MEDIUM
        """
        priority = gitlab_tracker._parse_labels_to_priority(["feature"])
        assert priority == IssuePriority.MEDIUM
