"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import subprocess


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory."""
    return tmp_path


@pytest.fixture
def mock_git_repo(tmp_path):
    """Create a mock git repository for testing."""
    import os
    repo_path = tmp_path / "test_repo"
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

    # Create initial commit
    test_file = repo_path / "test.txt"
    test_file.write_text("initial content")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path, check=True, capture_output=True
    )

    return repo_path


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary for testing."""
    return {
        "analysis": {
            "git": {
                "repo_path": "/tmp/test",
                "branch": "main",
                "time_filter": {
                    "mode": "date_range",
                    "time_basis": "author_time"
                }
            },
            "output": {
                "formats": ["html", "markdown"],
                "directory": "./reports"
            }
        },
        "ai": {
            "enabled": True,
            "provider": {
                "type": "api",
                "name": "openai",
                "model": "gpt-4o"
            }
        },
        "reporting": {
            "language": "zh-CN",
            "detail_level": "standard"
        }
    }


@pytest.fixture
def sample_code_cpp():
    """Sample C++ code for testing."""
    return """
#include <iostream>
#include <vector>

class Singleton {
private:
    Singleton() {}
    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;
    static Singleton* instance;

public:
    static Singleton& getInstance() {
        if (!instance) {
            instance = new Singleton();
        }
        return *instance;
    }
};

Singleton* Singleton::instance = nullptr;

int main() {
    auto& s = Singleton::getInstance();
    std::cout << "Singleton pattern" << std::endl;
    return 0;
}
"""


@pytest.fixture
def sample_code_python():
    """Sample Python code for testing."""
    return """
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

def process_data(items):
    \"\"\"Process a list of items.\"\"\"
    if not items:
        return 0
    return sum(1 for item in items if item > 0)
"""


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Custom markers
pytestmark = {
    "unit": pytest.mark.unit,
    "integration": pytest.mark.integration,
    "e2e": pytest.mark.e2e,
    "slow": pytest.mark.slow,
}


# Exception testing helper
def assert_raises(exception_class):
    """Helper to assert an exception is raised."""
    class _AssertRaises:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return exc_type is not None and issubclass(exc_type, exception_class)

    return _AssertRaises()


# Monkey patch for testing
@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    def set_var(key, value):
        monkeypatch.setenv(key, value, raising=False)

    return set_var
