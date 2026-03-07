"""Claude CLI integration for local AI analysis."""

import subprocess
import os
import json
from typing import Dict, Any, Optional
from .clients import AIClientBase, AIClientFactory
from .logger import AILogger, LogConfig


class ClaudeCLIClient(AIClientBase):
    """Claude CLI client using local Claude CLI tool."""

    def __init__(self, config: Dict[str, Any], logger: Optional[AILogger] = None):
        """
        Initialize Claude CLI client.

        Args:
            config: Configuration dict with command path and args
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or AILogger(LogConfig())

        # Claude CLI command path
        self.claude_command = config.get(
            "claude_command",
            config.get("claude_path", "claude")  # Default: try 'claude'
        )

        # Additional CLI arguments
        self.cli_args = config.get("claude_args", [])

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate completion using Claude CLI.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            AI-generated completion text
        """
        try:
            # Build CLI command
            cmd = [self.claude_command]

            # Add CLI arguments
            cmd.extend(self.cli_args)

            # Build prompt file (Claude CLI reads from file)
            prompt_file = self._create_prompt_file(prompt, system_prompt)
            cmd.extend(["--file", prompt_file])

            # Execute CLI command
            self.logger.log_request("claude-cli", prompt[:200])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", 300),
                check=False
            )

            # Log response
            response = result.stdout.strip()
            self.logger.log_response("claude-cli", response, duration=0.1)

            # Clean up prompt file
            os.remove(prompt_file)

            return response

        except subprocess.TimeoutExpired:
            self.logger.log_error("claude-cli", TimeoutError("Claude CLI timeout"))
            raise
        except FileNotFoundError:
            self.logger.log_error("claude-cli", FileNotFoundError(f"Claude CLI not found: {self.claude_command}"))
            raise RuntimeError(f"Claude CLI not found: {self.claude_command}")
        except Exception as e:
            self.logger.log_error("claude-cli", e)
            raise RuntimeError(f"Claude CLI error: {e}") from e

    def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate JSON completion using Claude CLI.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response
        """
        # Request JSON in prompt
        if "json" not in prompt.lower():
            prompt = f"{prompt}\n\nRespond with valid JSON only."

        response_text = self.complete(prompt, system_prompt, **kwargs)

        try:
            # Parse JSON response
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            self.logger.log_error("claude-cli", e)
            # Try to extract JSON from text
            # Look for JSON blocks in markdown
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass

            # If JSON parsing fails, return error
            raise ValueError(f"Failed to parse JSON response: {e}") from e

    def _create_prompt_file(self, prompt: str, system_prompt: Optional[str]) -> str:
        """
        Create a temporary prompt file for Claude CLI.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Path to prompt file
        """
        import tempfile

        # Create temporary file
        fd, prompt_file = tempfile.mkstemp(suffix=".txt", text=False)
        os.close(fd)

        # Write prompt to file
        with open(prompt_file, 'w', encoding='utf-8') as f:
            if system_prompt:
                f.write(f"{system_prompt}\n\n")
            f.write(prompt)

        return prompt_file


class CodexCLIClient(AIClientBase):
    """Codex CLI client using local Codex CLI tool."""

    def __init__(self, config: Dict[str, Any], logger: Optional[AILogger] = None):
        """
        Initialize Codex CLI client.

        Args:
            config: Configuration dict with command path and args
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or AILogger(LogConfig())

        # Codex CLI command path
        self.codex_command = config.get(
            "codex_command",
            config.get("codex_path", "codex")
        )

        # Additional CLI arguments
        self.cli_args = config.get("codex_args", [])

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate completion using Codex CLI.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            AI-generated completion text
        """
        try:
            # Build CLI command
            cmd = [self.codex_command]
            cmd.extend(self.cli_args)

            # Create prompt file
            prompt_file = self._create_prompt_file(prompt, system_prompt)
            cmd.extend(["--file", prompt_file])

            # Execute CLI command
            self.logger.log_request("codex-cli", prompt[:200])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", 300),
                check=False
            )

            # Log response
            response = result.stdout.strip()
            self.logger.log_response("codex-cli", response, duration=0.1)

            # Clean up prompt file
            os.remove(prompt_file)

            return response

        except subprocess.TimeoutExpired:
            self.logger.log_error("codex-cli", TimeoutError("Codex CLI timeout"))
            raise
        except FileNotFoundError:
            self.logger.log_error("codex-cli", FileNotFoundError(f"Codex CLI not found: {self.codex_command}"))
            raise RuntimeError(f"Codex CLI not found: {self.codex_command}")
        except Exception as e:
            self.logger.log_error("codex-cli", e)
            raise RuntimeError(f"Codex CLI error: {e}") from e

    def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate JSON completion using Codex CLI.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response
        """
        # Request JSON in prompt
        if "json" not in prompt.lower():
            prompt = f"{prompt}\n\nRespond with valid JSON only."

        response_text = self.complete(prompt, system_prompt, **kwargs)

        try:
            # Parse JSON response
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            self.logger.log_error("codex-cli", e)
            raise ValueError(f"Failed to parse JSON response: {e}") from e

    def _create_prompt_file(self, prompt: str, system_prompt: Optional[str]) -> str:
        """
        Create a temporary prompt file for Codex CLI.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Path to prompt file
        """
        import tempfile

        # Create temporary file
        fd, prompt_file = tempfile.mkstemp(suffix=".txt", text=False)
        os.close(fd)

        # Write prompt to file
        with open(prompt_file, 'w', encoding='utf-8') as f:
            if system_prompt:
                f.write(f"{system_prompt}\n\n")
            f.write(prompt)

        return prompt_file


# Register CLI clients with factory
AIClientFactory.register("claude-cli", ClaudeCLIClient)
AIClientFactory.register("codex-cli", CodexCLIClient)
