"""P0 configuration tests."""
import tempfile
from pathlib import Path

def test_config_from_file():
    config_content = """
git:
  repos:
    - type: github
      url: https://github.com/test/repo
  auth:
    type: token
    token: test_token
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()

        from issue_analyzer.config import Settings
        settings = Settings.from_file(Path(f.name))
        assert settings.config.git.repos[0].type == "github"
