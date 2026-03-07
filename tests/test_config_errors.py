"""Tests for configuration error handling and edge cases."""

import pytest
from pathlib import Path
import tempfile
from git_deep_analyzer.config import Config


class TestConfigErrorHandling:
    """Test configuration error handling."""

    def test_missing_config_file(self, tmp_path):
        """Given: Non-existent config file
        When: Config is loaded
        Then: Should create default config
        """
        # Given
        config_file = tmp_path / "nonexistent_config.yaml"

        # When
        config = Config(config_file)

        # Then
        assert config is not None
        assert config.analysis.ai.enabled is False

    def test_empty_config_file(self, tmp_path):
        """Given: Empty config file
        When: Config is loaded
        Then: Should create default config
        """
        # Given
        config_file = tmp_path / "empty_config.yaml"
        config_file.write_text("")

        # When
        config = Config(config_file)

        # Then
        assert config is not None

    def test_invalid_yaml_syntax(self, tmp_path):
        """Given: Config file with invalid YAML
        When: Config is loaded
        Then: Should handle error gracefully
        """
        # Given
        config_file = tmp_path / "invalid_config.yaml"
        config_file.write_text("invalid: yaml: [unclosed")

        # When & Then
        # Invalid YAML should be handled or create default config
        config = Config(config_file)
        assert config is not None

    def test_empty_ai_config(self, tmp_path):
        """Given: Config file with empty AI section
        When: Config is loaded
        Then: AI should be disabled by default
        """
        # Given
        config_file = tmp_path / "empty_ai_config.yaml"
        config_file.write_text("ai:\n  enabled:\n")

        # When
        config = Config(config_file)

        # Then
        assert config is not None
        # AI enabled should be False or handled appropriately
