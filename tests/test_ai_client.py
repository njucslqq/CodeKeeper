"""Tests for AI clients."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from git_deep_analyzer.ai.clients import (
    AIClientBase,
    OpenAIClient,
    AnthropicClient,
    AIClientFactory
)


class TestAIClientBase:
    """Test AIClientBase abstract class."""

    def test_base_class_cannot_be_instantiated(self):
        """Given: AIClientBase abstract class
        When: Attempting to instantiate directly
        Then: Raises TypeError
        """
        # When & Then
        with pytest.raises(TypeError):
            AIClientBase()

    def test_concrete_client_implements_interface(self, sample_openai_config):
        """Given: A concrete client implementation
        When: Creating instance with config
        Then: Instance is created successfully
        """
        # Given & When
        client = OpenAIClient(sample_openai_config)

        # Then
        assert client is not None
        assert hasattr(client, 'complete')
        assert callable(client.complete)


class TestOpenAIClient:
    """Test OpenAI API client."""

    @pytest.fixture
    def sample_openai_config(self):
        """Sample OpenAI configuration."""
        return {
            "provider": "openai",
            "api_key": "test-key",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        }

    @pytest.fixture
    def openai_client(self, sample_openai_config):
        """Create OpenAI client instance."""
        return OpenAIClient(sample_openai_config)

    def test_init_with_config(self, sample_openai_config):
        """Given: OpenAI config
        When: OpenAIClient is created
        Then: Config is stored correctly
        """
        # When
        client = OpenAIClient(sample_openai_config)

        # Then
        assert client.api_key == "test-key"
        assert client.model == "gpt-4"
        assert client.temperature == 0.7
        assert client.max_tokens == 2000

    @patch('openai.OpenAI')
    def test_complete_success(self, mock_openai, sample_openai_config):
        """Given: Configured OpenAIClient
        When: complete() is called with prompt
        Then: Returns API response text
        """
        # Given
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "AI response"
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = OpenAIClient(sample_openai_config)

        # When
        result = client.complete("Test prompt")

        # Then
        assert result == "AI response"
        mock_openai.return_value.chat.completions.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_complete_with_system_prompt(self, mock_openai, sample_openai_config):
        """Given: Configured OpenAIClient
        When: complete() is called with system prompt
        Then: System prompt is included in API call
        """
        # Given
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = OpenAIClient(sample_openai_config)

        # When
        result = client.complete(
            "User prompt",
            system_prompt="System instruction"
        )

        # Then
        assert result == "Response"
        call_args = mock_openai.return_value.chat.completions.create.call_args
        messages = call_args.kwargs.get('messages', [])
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == 'System instruction'


class TestAnthropicClient:
    """Test Anthropic API client."""

    @pytest.fixture
    def sample_anthropic_config(self):
        """Sample Anthropic configuration."""
        return {
            "provider": "anthropic",
            "api_key": "test-key",
            "model": "claude-3-opus-20240229",
            "temperature": 0.5
        }

    @pytest.fixture
    def anthropic_client(self, sample_anthropic_config):
        """Create Anthropic client instance."""
        return AnthropicClient(sample_anthropic_config)

    def test_init_with_config(self, sample_anthropic_config):
        """Given: Anthropic config
        When: AnthropicClient is created
        Then: Config is stored correctly
        """
        # When
        client = AnthropicClient(sample_anthropic_config)

        # Then
        assert client.api_key == "test-key"
        assert client.model == "claude-3-opus-20240229"
        assert client.temperature == 0.5

    @patch('anthropic.Anthropic')
    def test_complete_success(self, mock_anthropic, sample_anthropic_config):
        """Given: Configured AnthropicClient
        When: complete() is called with prompt
        Then: Returns API response text
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="Anthropic response")]
        mock_anthropic.return_value.messages.create.return_value = mock_response

        client = AnthropicClient(sample_anthropic_config)

        # When
        result = client.complete("Test prompt")

        # Then
        assert result == "Anthropic response"
        mock_anthropic.return_value.messages.create.assert_called_once()


class TestAIClientFactory:
    """Test AI client factory."""

    def test_create_openai_client(self):
        """Given: OpenAI config
        When: AIClientFactory.create() is called
        Then: Returns OpenAIClient instance
        """
        # Given
        config = {
            "provider": "openai",
            "api_key": "test-key",
            "model": "gpt-4"
        }

        # When
        client = AIClientFactory.create(config)

        # Then
        assert isinstance(client, OpenAIClient)
        assert client.api_key == "test-key"

    def test_create_anthropic_client(self):
        """Given: Anthropic config
        When: AIClientFactory.create() is called
        Then: Returns AnthropicClient instance
        """
        # Given
        config = {
            "provider": "anthropic",
            "api_key": "test-key",
            "model": "claude-3"
        }

        # When
        client = AIClientFactory.create(config)

        # Then
        assert isinstance(client, AnthropicClient)
        assert client.api_key == "test-key"

    def test_create_unsupported_provider(self):
        """Given: Config with unsupported provider
        When: AIClientFactory.create() is called
        Then: Raises ValueError
        """
        # Given
        config = {
            "provider": "unknown",
            "api_key": "test-key"
        }

        # When & Then
        with pytest.raises(ValueError, match="Unsupported AI provider"):
            AIClientFactory.create(config)
