"""P1.3 GitLab client tests."""

from unittest.mock import Mock, patch


def test_gitlab_client_init():
    from issue_analyzer.git import GitLabClient
    client = GitLabClient(
        token="test_token",
        project_id=123
    )
    assert client is not None
    assert client.project_id == 123


def test_get_commits():
    from issue_analyzer.git import GitLabClient
    client = GitLabClient(
        token="test_token",
        project_id=123,
        base_url="https://gitlab.example.com"
    )

    with patch.object(client, 'session') as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_session.get.return_value = mock_response

        commits = client.get_commits("PROJ-123")
        assert isinstance(commits, list)


def test_get_commit_diff():
    from issue_analyzer.git import GitLabClient
    client = GitLabClient(
        token="test_token",
        project_id=123,
        base_url="https://gitlab.example.com"
    )

    with patch.object(client, 'session') as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_session.get.return_value = mock_response

        diff = client.get_commit_diff("abc123")
        assert isinstance(diff, str)
