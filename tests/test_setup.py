import os
from pathlib import Path

def test_project_structure():
    root = Path(__file__).parent.parent
    assert root.exists()
    assert (root / "src" / "git_deep_analyzer").exists()
    assert (root / "tests").exists()
    assert (root / "pyproject.toml").exists()
