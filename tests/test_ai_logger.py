"""Tests for AI logger."""

import pytest
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from git_deep_analyzer.ai.logger import AILogger, LogConfig


class TestLogConfig:
    """Test LogConfig dataclass."""

    def test_default_config(self):
        """Given: LogConfig with no arguments
        When: Creating default config
        Then: Uses sensible defaults
        """
        # When
        config = LogConfig()

        # Then
        assert config.level == logging.INFO
        assert config.log_to_console is True
        assert config.log_to_file is False
        assert config.log_requests is True
        assert config.log_responses is True
        assert config.log_performance is True

    def test_custom_config(self):
        """Given: Custom log parameters
        When: Creating LogConfig
        Then: Uses custom values
        """
        # When
        config = LogConfig(
            level=logging.DEBUG,
            log_to_console=False,
            log_to_file=True,
            log_file="test.log",
            log_requests=False,
            log_responses=False,
            log_performance=False
        )

        # Then
        assert config.level == logging.DEBUG
        assert config.log_to_console is False
        assert config.log_to_file is True
        assert config.log_file == "test.log"
        assert config.log_requests is False
        assert config.log_responses is False
        assert config.log_performance is False


class TestAILogger:
    """Test AILogger class."""

    @pytest.fixture
    def log_config(self):
        """Create test log config."""
        return LogConfig(
            level=logging.DEBUG,
            log_to_console=True,
            log_to_file=False
        )

    @pytest.fixture
    def ai_logger(self, log_config):
        """Create AILogger instance."""
        return AILogger(log_config)

    def test_logger_initialization(self, ai_logger):
        """Given: LogConfig
        When: AILogger is created
        Then: Logger is configured correctly
        """
        # Then
        assert ai_logger.config.level == logging.DEBUG
        assert ai_logger.logger.level == logging.DEBUG
        assert len(ai_logger.logger.handlers) > 0

    def test_log_request(self, ai_logger, caplog):
        """Given: AILogger instance
        When: log_request() is called
        Then: Request is logged at INFO level
        """
        # Given
        caplog.set_level(logging.INFO)

        # When
        ai_logger.log_request("test_provider", "test prompt")

        # Then
        assert len(caplog.records) >= 1
        log_messages = [record.message for record in caplog.records]
        assert any("test_provider" in msg and "test prompt" in msg for msg in log_messages)

    def test_log_response(self, ai_logger, caplog):
        """Given: AILogger instance
        When: log_response() is called
        Then: Response is logged at INFO level
        """
        # Given
        caplog.set_level(logging.INFO)

        # When
        ai_logger.log_response("test_provider", "test response", 1.5)

        # Then
        log_messages = [record.message for record in caplog.records]
        assert any("test_provider" in msg and "1.50s" in msg for msg in log_messages)

    def test_log_error(self, ai_logger, caplog):
        """Given: AILogger instance
        When: log_error() is called
        Then: Error is logged at ERROR level
        """
        # Given
        caplog.set_level(logging.ERROR)
        error = ValueError("test error")

        # When
        ai_logger.log_error("test_provider", error)

        # Then
        assert len(caplog.records) >= 1
        assert caplog.records[-1].levelname == "ERROR"
        assert "test error" in caplog.records[-1].message

    def test_log_performance(self, ai_logger, caplog):
        """Given: AILogger instance
        When: log_performance() is called
        Then: Performance metrics are logged at DEBUG level
        """
        # Given
        caplog.set_level(logging.DEBUG)

        # When
        ai_logger.log_performance(
            "test_operation",
            duration=2.5,
            tokens=1000,
            cost=0.05
        )

        # Then
        log_messages = [record.message for record in caplog.records]
        assert any("test_operation" in msg and "2.50s" in msg for msg in log_messages)

    def test_file_logging(self, log_config, tmp_path):
        """Given: LogConfig with file logging enabled
        When: AILogger logs messages
        Then: Messages are written to file
        """
        # Given
        log_file = tmp_path / "test.log"
        config = LogConfig(
            level=logging.INFO,
            log_to_console=False,
            log_to_file=True,
            log_file=str(log_file)
        )
        logger = AILogger(config)

        # When
        logger.log_request("test", "message")

        # Then
        assert log_file.exists()
        content = log_file.read_text()
        assert "test" in content
        assert "message" in content

    def test_console_logging_disabled(self, log_config, caplog):
        """Given: LogConfig with console logging disabled
        When: AILogger logs messages
        Then: Messages are not logged to console
        """
        # Given
        config = LogConfig(
            level=logging.INFO,
            log_to_console=False,
            log_to_file=False
        )
        logger = AILogger(config)

        # When
        logger.log_request("test", "message")

        # Then - Should not have console handlers
        console_handlers = [
            h for h in logger.logger.handlers
            if isinstance(h, logging.StreamHandler)
        ]
        # Note: caplog captures all records regardless of handler
        # So this test verifies handler configuration
        assert not any(
            isinstance(h, logging.StreamHandler) and h.stream.name == "<stdout>"
            for h in logger.logger.handlers
        )

    def test_set_level(self, ai_logger):
        """Given: ALogger instance
        When: set_level() is called
        Then: Logger level is updated
        """
        # When
        ai_logger.set_level(logging.WARNING)

        # Then
        assert ai_logger.logger.level == logging.WARNING

    def test_context_manager_for_performance_tracking(self, ai_logger, caplog):
        """Given: AILogger instance
        When: Using track_performance() context manager
        Then: Performance is logged on exit
        """
        # Given
        caplog.set_level(logging.DEBUG)

        # When
        with ai_logger.track_performance("test_operation"):
            import time
            time.sleep(0.1)

        # Then
        log_messages = [record.message for record in caplog.records]
        assert any("test_operation" in msg for msg in log_messages)
        # Should have logged duration
        assert any("0." in msg for msg in log_messages)

    def test_log_with_metadata(self, ai_logger, caplog):
        """Given: AILogger instance
        When: log_request() is called with metadata
        Then: Metadata is included in log
        """
        # Given
        caplog.set_level(logging.INFO)

        # When
        ai_logger.log_request(
            "test_provider",
            "prompt",
            metadata={"model": "gpt-4", "tokens": 100}
        )

        # Then
        log_messages = [record.message for record in caplog.records]
        assert any("gpt-4" in msg or "100" in msg for msg in log_messages)

    def test_multiple_loggers_with_different_configs(self, tmp_path):
        """Given: Multiple AILogger instances
        When: Each has different config
        Then: Loggers operate independently
        """
        # Given
        log_file1 = tmp_path / "logger1.log"
        log_file2 = tmp_path / "logger2.log"

        config1 = LogConfig(log_to_file=True, log_file=str(log_file1))
        config2 = LogConfig(log_to_file=True, log_file=str(log_file2))

        logger1 = AILogger(config1)
        logger2 = AILogger(config2)

        # When
        logger1.log_request("logger1", "message1")
        logger2.log_request("logger2", "message2")

        # Then
        assert log_file1.exists()
        assert log_file2.exists()
        content1 = log_file1.read_text()
        content2 = log_file2.read_text()
        assert "message1" in content1
        assert "message2" in content2
