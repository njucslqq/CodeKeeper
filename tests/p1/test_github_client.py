"""P1.2 GitHub client tests."""

from unittest.mock import Mock, patch
from issue_analyzer.models import Commit
from datetime import datetime


def test_github_client_init():
    from issue_analyzer.git import GitHubClient
    client = GitHubClient(
        token="test_token",
        repo_owner="test_owner",
        repo_name="test_repo"
    )
    assert client is not None
    assert client.repo_owner == "test_owner"
    assert client.repo_name == "test_repo"
    assert client.repository == "test_owner/test_repo"


def test_get_commits():
    from issue_analyzer.git import GitHubClient
    client = GitHubClient(
        token="test_token",
        repo_owner="test_owner",
        repo_name="test_repo"
    )

    with patch.object(client, 'session') as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_session.get.return_value = mock_response

        commits = client.get_commits("PROJ-123")
        assert isinstance(commits, list)


def test_get_commit_diff():
    from issue_analyzer.git import GitHubClient
    client = GitHubClient(
        token="test_token",
        repo_owner="test_owner",
        repo_name="test_repo"
    )

    with patch.object(client, 'session') as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response

        diff = client.get_commit_diff("abc123")
        assert isinstance(diff, str)
