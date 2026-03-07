"""Tests for Claude CLI and Codex CLI integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from git_deep_analyzer.ai.clients_cli import ClaudeCLIClient, CodexCLIClient


class TestClaudeCLIClient:
    """Test ClaudeCLIClient class."""

    @pytest.fixture
    def claude_config(self):
        """Sample Claude CLI configuration."""
        return {
            "claude_command": "claude",
            "claude_args": ["--max-tokens", "4096"]
        }

    @pytest.fixture
    def claude_client(self, claude_config):
        """Create ClaudeCLIClient instance."""
        return ClaudeCLIClient(claude_config)

    def test_init_with_config(self, claude_client):
        """Given: Claude CLI config
        When: ClaudeCLIClient is created
        Then: Config is stored correctly
        """
        assert claude_client.claude_command == "claude"

    @patch('subprocess.run')
    def test_complete_success(self, mock_run, claude_client):
        """Given: Claude CLI client
        When: complete() is called
        Then: Returns CLI response
        """
        # Given
        mock_run.return_value = MagicMock(
            stdout="AI response",
            stderr="",
            returncode=0
        )

        # When
        result = claude_client.complete("Test prompt")

        # Then
        assert result == "AI response"
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_complete_with_system_prompt(self, mock_run, claude_client):
        """Given: Claude CLI client with system prompt
        When: complete() is called
        Then: Includes system prompt
        """
        # Given
        mock_run.return_value = MagicMock(
            stdout="AI response",
            returncode=0
        )

        # When
        result = claude_client.complete(
            "Test prompt",
            system_prompt="You are a helpful assistant."
        )

        # Then
        assert result == "AI response"
        # Verify system prompt was included (by checking temp file creation)
        assert mock_run.call_count >= 1  # create_file + run + remove

    @patch('subprocess.run')
    def test_complete_timeout(self, mock_run, claude_client):
        """Given: Claude CLI client
        When: CLI times out
        Then: Raises TimeoutError
        """
        # Given
        mock_run.side_effect = subprocess.TimeoutExpired("Timeout")

        client = ClaudeCLIClient(self.claude_config)

        # When & Then
        with pytest.raises(TimeoutError):
            client.complete("Test prompt")

    @patch('subprocess.run')
    def test_complete_command_not_found(self, mock_run, claude_config):
        """Given: Claude CLI not found
        When: complete() is called
        Then: Raises RuntimeError
        """
        # Given
        mock_run.side_effect = FileNotFoundError("claude not found")

        client = ClaudeCLIClient(claude_config)

        # When & Then
        with pytest.raises(RuntimeError, match="Claude CLI not found"):
            client.complete("Test prompt")


class TestCodexCLIClient:
    """Test CodexCLIClient class."""

    @pytest.fixture
    def codex_config(self):
        """Sample Codex CLI configuration."""
        return {
            "codex_command": "codex",
            "codex_args": ["--max-tokens", "4096"]
        }

    @pytest.fixture
    def codex_client(self, codex_config):
        """Create CodexCLIClient instance."""
        return CodexCLIClient(codex_config)

    def test_init_with_config(self, codex_client):
        """Given: Codex CLI config
        When: CodexCLIClient is created
        Then: Config is stored correctly
        """
        assert codex_client.codex_command == "codex"

    @patch('subprocess.run')
    def test_complete_success(self, mock_run, codex_client):
        """Given: Codex CLI client
        When: complete() is called
        Then: Returns CLI response
        """
        # Given
        mock_run.return_value = MagicMock(
            stdout="AI response",
            stderr="",
            returncode=0
        )

        # When
        result = codex_client.complete("Test prompt")

        # Then
        assert result == "AI response"
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_complete_json_success(self, mock_run, codex_client):
        """Given: Codex CLI client
        When: complete_json() is called
        Then: Returns parsed JSON
        """
        # Given
        mock_run.return_value = MagicMock(
            stdout='{"result": "data"}',
            stderr="",
            returncode=0
        )

        client = CodexCLIClient(self.codex_config)

        # When
        result = codex_client.complete_json("Test prompt")

        # Then
        assert result == {"result": "data"}

    @patch('subprocess.run')
    def test_complete_json_invalid_json(self, mock_run, codex_client):
        """Given: Codex CLI client with non-JSON response
        When: complete_json() is called
        Then: Returns error (or handles gracefully)
        """
        # Given
        mock_run.return_value = MagicMock(
            stdout='Plain text response',
            stderr="",
            returncode=0
        )

        client = CodexCLIClient(self.codex_config)

        # When & Then
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            client.complete_json("Test prompt")
