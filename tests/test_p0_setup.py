"""P0 setup tests."""
import os
from pathlib import Path

def test_project_structure():
    root = Path(__file__).parent.parent
    assert root.exists()
    assert (root / "src" / "issue_analyzer").exists()
    assert (root / "tests").exists()
    assert (root / "pyproject.toml").exists()
    assert (root / "progress.md").exists()

def test_fastapi_import():
    from fastapi import FastAPI
    from pydantic import BaseModel
    assert True
