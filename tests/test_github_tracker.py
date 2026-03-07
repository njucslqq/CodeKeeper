"""Tests for GitHub Issue Tracker integration."""

import pytest
from unittest.mock import Mock, patch
from git_deep_analyzer.integrations.issue_tracker.github import GitHubTracker


class TestGitHubTracker:
    """Test GitHubTracker class."""

    @pytest.fixture
    def github_config(self):
        """Sample GitHub configuration."""
        return {
            "url": "https://api.github.com",
            "token": "test-token"
        }

    @pytest.fixture
    def github_tracker(self, github_config):
        """Create GitHubTracker instance."""
        return GitHubTracker(github_config)

    def test_init_with_config(self, github_tracker):
        """Given: GitHub config
        When: GitHubTracker is created
        Then: Config is stored correctly
        """
        assert github_tracker.base_url == "https://api.github.com"
        assert github_tracker.token == "test-token"

    @patch('requests.Session')
    def test_connect_success(self, mock_session, github_config):
        """Given: GitHub config
        When: connect() is called with valid token
        Then: Returns True
        """
        # Given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response

        tracker = GitHubTracker(github_config)

        # When
        result = tracker.connect()

        # Then
        assert result is True

    @patch('requests.Session')
    def test_fetch_issues_success(self, mock_session, github_tracker):
        """Given: GitHub tracker and config
        When: fetch_issues() is called
        Then: Returns list of issues
        """
        # Given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": 1,
                    "number": 100,
                    "title": "Test Issue",
                    "state": "open",
                    "body": "Issue description",
                    "user": {"login": "testuser"},
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z",
                    "html_url": "https://github.com/test/repo/issues/100"
                }
            ]
        }
        mock_session.return_value.get.return_value = mock_response

        # When
        issues = github_tracker.fetch_issues(
            owner="testowner",
            repo="testrepo"
        )

        # Then
        assert len(issues) == 1
        assert issues[0].key == "100"
        assert issues[0].title == "Test Issue"

    @patch('requests.Session')
    def test_parse_issue(self, mock_session, github_tracker):
        """Given: Issue data from GitHub API
        When: _parse_issue() is called
        Then: Returns Issue object with all fields
        """
        # Given
        issue_data = {
            "id": 1,
            "number": 100,
            "title": "Test Issue",
            "state": "open",
            "body": "Issue description",
            "user": {"login": "testuser"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "html_url": "https://github.com/test/repo/issues/100",
            "labels": [{"name": "bug"}],
            "milestone": {"title": "v1.0"},
            "pull_request": None
        }

        # When
        issue = github_tracker._parse_issue(issue_data)

        # Then
        assert issue.key == "100"
        assert issue.title == "Test Issue"
        assert issue.status.value == "open"

    @patch('requests.Session')
    def test_distinguish_issue_from_pr(self, mock_session, github_tracker):
        """Given: Issue data
        When: Issue has pull_request field
        Then: Can distinguish Issue from PR
        """
        # Given - Issue
        issue_data = {"number": 100, "title": "Issue", "pull_request": None}
        issue = github_tracker._parse_issue(issue_data)
        assert not issue.is_pull_request

        # Given - Pull Request
        pr_data = {"number": 101, "title": "PR", "pull_request": {}}
        pr = github_tracker._parse_issue(pr_data)
        assert pr.is_pull_request

    @patch('requests.Session')
    def test_fetch_issue_comments(self, mock_session, github_tracker):
        """Given: Issue number
        When: fetch_comments() is called
        Then: Returns issue comments
        """
        # Given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "user": {"login": "commenter"},
                "body": "Comment text",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        mock_session.return_value.get.return_value = mock_response

        # When
        comments = github_tracker.fetch_comments(100, owner="owner", repo="repo")

        # Then
        assert len(comments) == 1
        assert comments[0].content == "Comment text"
