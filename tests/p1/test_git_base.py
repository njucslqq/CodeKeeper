"""P1.1 Git base architecture tests."""

def test_git_client_interface():
    from issue_analyzer.git import GitClient
    assert hasattr(GitClient, '__abstractmethods__')
    assert 'get_commits' in GitClient.__abstractmethods__
    assert 'get_commit_diff' in GitClient.__abstractmethods__

def test_git_collector_interface():
    from issue_analyzer.git import GitCollector
    assert hasattr(GitCollector, '__init__')
    assert hasattr(GitCollector, 'collect_commits')
