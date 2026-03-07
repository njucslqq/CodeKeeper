import tempfile
from pathlib import Path
from git_deep_analyzer.config import Config, GitConfig, AnalysisConfig

def test_load_yaml_config():
    config_content = """
analysis:
  git:
    repo_path: /tmp/test
    branch: main
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        temp_path = Path(f.name)

        try:
            config = Config.load_from_file(temp_path)
            assert config.analysis.git.repo_path == Path("/tmp/test")
            assert config.analysis.git.branch == "main"
        finally:
            temp_path.unlink()

def test_validate_git_repo():
    config = Config(
        analysis=AnalysisConfig(
            git=GitConfig(repo_path=Path("/nonexistent/repo"))
        )
    )
    errors = config.validate()
    assert len(errors) > 0
    assert any("repository" in str(e).lower() for e in errors)
