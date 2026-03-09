"""P1.4 Repository list mechanism tests."""

from unittest.mock import Mock, patch


def test_config_repo_list():
    from issue_analyzer.git.factory import create_repos_from_config

    config = {
        "repos": [
            {
                "type": "github",
                "url": "https://github.com/org/repo",
                "auth": {
                    "type": "token",
                    "token": "test_token"
                }
            }
        ]
    }

    with patch('issue_analyzer.git.GitHubClient') as mock_gh:
        clients = create_repos_from_config(config)
        assert len(clients) == 1


def test_submodule_repo_list():
    from issue_analyzer.git.factory import create_repos_from_submodule

    with patch('os.listdir') as mock_listdir:
        mock_listdir.return_value = ['repo1', 'repo2']

        clients = create_repos_from_submodule('/path/to/superproject')
        assert isinstance(clients, list)


def test_git_collector_integration():
    from issue_analyzer.git import GitCollector, create_repos_from_config

    config = {"repos": []}
    clients = create_repos_from_config(config)
    collector = GitCollector(clients)
    commits = collector.collect_commits("PROJ-123")
    assert isinstance(commits, list)
