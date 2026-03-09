"""Git repository factory for creating clients."""

from typing import List
from .base import GitClient
from .github import GitHubClient
from .gitlab import GitLabClient


def create_repos_from_config(config: dict) -> List[GitClient]:
    """Create Git clients from configuration.

    Args:
        config: Configuration dictionary with 'repos' key

    Returns:
        List of GitClient instances
    """
    clients: List[GitClient] = []
    repos = config.get("repos", [])

    for repo_config in repos:
        repo_type = repo_config.get("type")

        if repo_type == "github":
            url = repo_config.get("url")
            if url:
                # Parse owner/repo from URL
                parts = str(url).rstrip('/').split('/')
                if len(parts) >= 2:
                    owner, repo_name = parts[-2], parts[-1]
                    auth_config = repo_config.get("auth", {})
                    token = auth_config.get("token")

                    if token:
                        clients.append(GitHubClient(
                            token=token,
                            repo_owner=owner,
                            repo_name=repo_name
                        ))

        elif repo_type == "gitlab":
            auth_config = repo_config.get("auth", {})
            token = auth_config.get("token")

            if token:
                # For GitLab, we need project_id (will be determined later)
                clients.append(GitLabClient(
                    token=token,
                    project_id=0,  # Placeholder
                ))

    return clients


def create_repos_from_submodule(superproject_path: str) -> List[GitClient]:
    """Create Git clients by scanning git submodules.

    Args:
        superproject_path: Path to git superproject

    Returns:
        List of GitClient instances
    """
    import os
    import subprocess

    clients: List[GitClient] = []

    try:
        # Get list of submodules
        result = subprocess.run(
            ['git', 'submodule', 'status'],
            cwd=superproject_path,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        # Parse submodule URL to get repo info
                        # This is a simplified implementation
                        # Real implementation would parse .gitmodules file
                        pass

    except Exception:
        pass

    return clients
