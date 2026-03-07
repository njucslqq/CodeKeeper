"""AI API and CLI clients."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json


class AIClientBase(ABC):
    """Abstract base class for AI clients."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AI client.

        Args:
            config: Client configuration dictionary
        """
        self.config = config
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "default")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2000)

    @abstractmethod
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate completion for given prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            AI-generated completion text
        """
        pass

    @abstractmethod
    def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate JSON completion for given prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response
        """
        pass


class OpenAIClient(AIClientBase):
    """OpenAI API client."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI client.

        Args:
            config: Configuration with api_key, model, etc.
        """
        super().__init__(config)
        self._client = None

    def _get_client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "openai package is required. Install with: pip install openai"
                )
        return self._client

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate completion using OpenAI API."""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate JSON completion using OpenAI API."""
        # Add JSON instruction to system prompt
        json_instruction = "You must respond with valid JSON only, no other text."
        if system_prompt:
            system_prompt = f"{json_instruction}\n\n{system_prompt}"
        else:
            system_prompt = json_instruction

        response_text = self.complete(prompt, system_prompt, **kwargs)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response_text}")


class AnthropicClient(AIClientBase):
    """Anthropic (Claude) API client."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Anthropic client.

        Args:
            config: Configuration with api_key, model, etc.
        """
        super().__init__(config)
        self._client = None

    def _get_client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package is required. Install with: pip install anthropic"
                )
        return self._client

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate completion using Anthropic API."""
        client = self._get_client()

        try:
            kwargs_message = {
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "messages": [{"role": "user", "content": prompt}],
            }

            if system_prompt:
                kwargs_message["system"] = system_prompt

            response = client.messages.create(**kwargs_message)
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate JSON completion using Anthropic API."""
        # Add JSON instruction to system prompt
        json_instruction = "You must respond with valid JSON only, no other text."
        if system_prompt:
            system_prompt = f"{json_instruction}\n\n{system_prompt}"
        else:
            system_prompt = json_instruction

        response_text = self.complete(prompt, system_prompt, **kwargs)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response_text}")


class AIClientFactory:
    """Factory for creating AI clients."""

    _clients = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
    }

    @classmethod
    def create(cls, config: Dict[str, Any]) -> AIClientBase:
        """
        Create AI client based on provider config.

        Args:
            config: Configuration dict with 'provider' key

        Returns:
            AIClientBase instance

        Raises:
            ValueError: If provider is not supported
        """
        provider = config.get("provider", "").lower()

        if provider not in cls._clients:
            raise ValueError(
                f"Unsupported AI provider: {provider}. "
                f"Supported: {list(cls._clients.keys())}"
            )

        client_class = cls._clients[provider]
        return client_class(config)

    @classmethod
    def register_client(cls, provider: str, client_class: type):
        """
        Register a new client type.

        Args:
            provider: Provider name
            client_class: Client class (subclass of AIClientBase)
        """
        if not issubclass(client_class, AIClientBase):
            raise ValueError("client_class must be subclass of AIClientBase")
        cls._clients[provider.lower()] = client_class
