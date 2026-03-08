"""TDD tests for GitCollector using real git repository."""

import pytest
import tempfile
from pathlib import Path
import subprocess
from git_deep_analyzer.git_collector.collector import GitCollector
from git_deep_analyzer.git_collector.models import (
    CommitData, FileChange, AuthorStats, TagData, BranchData
)
from datetime import datetime


class TestGitCollectorTDD:
    """TDD tests for GitCollector following RED-GREEN-REFACTOR cycle."""

    @pytest.fixture
    def tdd_git_repo(tmp_path):
        """Create a real git repository for TDD testing."""
        repo_path = tmp_path / "test_tdd_repo"
        repo_path.mkdir()

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path, check=True, capture_output=True
        )

        # Create initial commit with a file
        test_file = repo_path / "initial.txt"
        test_file.write_text("Initial content")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path, check=True, capture_output=True
        )

        return repo_path

    def test_collector_initialization(self, real_git_repo):
        """
        RED: Write test for GitCollector initialization

        Given: A real git repository path
        When: GitCollector is created with config
        Then: Should initialize successfully and have access to repo
        """
        # Given
        config = {"branch": "main"}

        # When
        collector = GitCollector(real_git_repo, config)

        # Then
        assert collector is not None
        assert collector.config == config
        assert collector.repo is not None
        assert str(collector.repo.git_dir) == str(real_git_repo)

    def test_collect_commits_basic(self, real_git_repo):
        """
        RED: Write test for basic commit collection

        Given: A git repository with commits
        When: collect_commits() is called
        Then: Should return list of CommitData
        """
        # Given - Create a commit
        test_file = real_git_repo / "test.txt"
        test_file.write_text("Test content")
        subprocess.run(["git", "add", "."], cwd=real_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add test file"],
            cwd=real_git_repo, check=True, capture_output=True
        )

        # When
        config = {"branch": "main"}
        collector = GitCollector(real_git_repo, config)
        commits = collector.collect_commits()

        # Then
        assert len(commits) >= 1
        assert all(isinstance(c, CommitData) for c in commits)
        assert all(c.hash for c in commits)

    def test_collect_commits_multiple(self, real_git_repo):
        """
        RED: Write test for multiple commit collection

        Given: A git repository with multiple commits
        When: collect_commits() is called
        Then: Should return all commits in order
        """
        # Given - Create multiple commits
        for i in range(3):
            test_file = real_git_repo / f"file_{i}.txt"
            test_file.write_text(f"Content {i}")
            subprocess.run(["git", "add", "."], cwd=real_git_repo, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", f"Commit {i}"],
                cwd=real_git_repo, check=True, capture_output=True
            )

        # When
        config = {"branch": "main"}
        collector = GitCollector(real_git_repo, config)
        commits = collector.collect_commits()

        # Then
        assert len(commits) >= 3
        assert len(commits) == len([c for c in commits if c.message and "Commit" in c.message])

    def test_collect_tags(self, real_git_repo):
        """
        RED: Write test for tag collection

        Given: A git repository with tags
        When: collect_tags() is called
        Then: Should return list of TagData
        """
        # Given - Create a tag
        subprocess.run(
            ["git", "tag", "v1.0.0"],
            cwd=real_git_repo, check=True, capture_output=True
        )

        # When
        config = {"branch": "main"}
        collector = GitCollector(real_git_repo, config)
        tags = collector.collect_tags()

        # Then
        assert len(tags) == 1
        assert tags[0].name == "v1.0.0"

    def test_collect_branches(self, real_git_repo):
        """
        RED: Write test for branch collection

        Given: A git repository with branches
        When: collect_branches() is called
        Then: Should return list of BranchData
        """
        # Given - Create a new branch
        subprocess.run(
            ["git", "checkout", "-b", "feature"],
            cwd=real_git_repo, check=True, capture_output=True
        )

        # When
        config = {"branch": "main"}
        collector = GitCollector(real_git_repo, config)
        branches = collector.collect_branches()

        # Then
        assert len(branches) == 2
        assert any(b.name == "main" for b in branches)
        assert any(b.name == "feature" for b in branches)

    def test_calculate_author_stats(self, real_git_repo):
        """
        RED: Write test for author statistics calculation

        Given: Commits from multiple authors
        When: calculate_author_stats() is called
        Then: Should return AuthorStats
        """
        # Given - Create commits from multiple authors
        for i, author in enumerate(["alice", "bob", "charlie"]):
            test_file = real_git_repo / f"file_{i}.txt"
            test_file.write_text(f"Content by {author}")
            subprocess.run(["git", "add", "."], cwd=real_git_repo, check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.name", author],
                cwd=real_git_repo, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", f"Commit by {author}"],
                cwd=real_git_repo, check=True, capture_output=True
            )

        # When
        config = {"branch": "main"}
        collector = GitCollector(real_git_repo, config)
        stats = collector.calculate_author_stats()

        # Then
        assert stats is not None
        assert len(stats.author_stats) == 3

    def test_get_changed_files(self, real_git_repo):
        """
        RED: Write test for changed files detection

        Given: A commit with file changes
        When: get_changed_files() is called
        Then: Should return list of FileChange
        """
        # Given - Create a commit with a file
        test_file = real_git_repo / "changed.txt"
        test_file.write_text("Original content")
        subprocess.run(["git", "add", "."], cwd=real_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=real_git_repo, check=True, capture_output=True
        )

        # Modify the file
        test_file.write_text("Modified content")
        subprocess.run(["git", "add", "."], cwd=real_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Modify file"],
            cwd=real_git_repo, check=True, capture_output=True
        )

        # When
        config = {"branch": "main"}
        collector = GitCollector(real_git_repo, config)
        files = collector.get_changed_files()

        # Then
        assert len(files) >= 1
        assert any("changed.txt" in f.filename for f in files)

    def test_collect_all_integration(self, real_git_repo):
        """
        RED: Write integration test for collect_all()

        Given: A repository with commits, tags, and branches
        When: collect_all() is called
        Then: Should return complete data
        """
        # Given - Create multiple commits, tags, and branches
        for i in range(2):
            test_file = real_git_repo / f"file_{i}.txt"
            test_file.write_text(f"Content {i}")
            subprocess.run(["git", "add", "."], cwd=real_git_repo, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", f"Commit {i}"],
                cwd=real_git_repo, check=True, capture_output=True
            )

        subprocess.run(["git", "tag", "v1.0.0"], cwd=real_git_repo, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-b", "dev"], cwd=real_git_repo, check=True, capture_output=True)

        # When
        config = {"branch": "main"}
        collector = GitCollector(real_git_repo, config)
        result = collector.collect_all()

        # Then
        assert result is not None
        assert result.commits is not None
        assert len(result.commits) >= 2
        assert result.tags is not None
        assert len(result.tags) >= 1
        assert result.branches is not None
        assert len(result.branches) >= 2
