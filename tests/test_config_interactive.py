from unittest.mock import patch
from pathlib import Path
from git_deep_analyzer.config.interactive import interactive_setup

def test_interactive_setup():
    with patch('builtins.input') as mock_input:
        # 模拟用户输入
        mock_input.side_effect = [
            "/tmp/test",  # Git仓库路径
        ]

        with patch('click.confirm', return_value=True):
            with patch('click.echo'):
                config = interactive_setup()
                assert config.analysis.git.repo_path == Path("/tmp/test")
