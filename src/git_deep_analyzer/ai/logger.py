"""AI request/response logger with performance tracking."""

import logging
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, ContextManager
from contextlib import contextmanager
import json


@dataclass
class LogConfig:
    """Configuration for AI logger."""

    level: int = logging.INFO
    """Logging level (DEBUG, INFO, WARNING, ERROR)."""

    log_to_console: bool = True
    """Whether to log to console."""

    log_to_file: bool = False
    """Whether to log to file."""

    log_file: str = "ai_analysis.log"
    """Log file path."""

    log_requests: bool = True
    """Whether to log AI requests."""

    log_responses: bool = True
    """Whether to log AI responses."""

    log_performance: bool = True
    """Whether to log performance metrics."""


class AILogger:
    """Logger for AI operations with performance tracking."""

    def __init__(self, config: LogConfig):
        """
        Initialize AI logger.

        Args:
            config: Logger configuration
        """
        self.config = config
        self.logger = self._setup_logger(config)

    def _setup_logger(self, config: LogConfig) -> logging.Logger:
        """
        Set up logger with handlers.

        Args:
            config: Logger configuration

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger("git_deep_analyzer.ai")
        logger.setLevel(config.level)

        # Remove existing handlers
        logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        if config.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(config.level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File handler
        if config.log_to_file:
            log_path = Path(config.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(config.log_file)
            file_handler.setLevel(config.level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def set_level(self, level: int) -> None:
        """
        Set logging level.

        Args:
            level: New logging level
        """
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)

    def log_request(
        self,
        provider: str,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log AI request.

        Args:
            provider: AI provider name (e.g., "openai", "anthropic")
            prompt: Request prompt
            metadata: Optional metadata dictionary
        """
        if not self.config.log_requests:
            return

        meta_str = ""
        if metadata:
            meta_str = f" | Metadata: {json.dumps(metadata)}"

        self.logger.info(
            f"[{provider}] Request: {prompt[:200]}...{meta_str}"
        )

    def log_response(
        self,
        provider: str,
        response: str,
        duration: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log AI response.

        Args:
            provider: AI provider name
            response: Response text
            duration: Request duration in seconds
            metadata: Optional metadata dictionary
        """
        if not self.config.log_responses:
            return

        meta_str = ""
        if metadata:
            meta_str = f" | Metadata: {json.dumps(metadata)}"

        self.logger.info(
            f"[{provider}] Response (took {duration:.2f}s): "
            f"{response[:200]}...{meta_str}"
        )

    def log_error(
        self,
        provider: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log AI error.

        Args:
            provider: AI provider name
            error: Exception that occurred
            context: Optional context dictionary
        """
        context_str = ""
        if context:
            context_str = f" | Context: {json.dumps(context)}"

        self.logger.error(
            f"[{provider}] Error: {error.__class__.__name__}: {str(error)}{context_str}"
        )

    def log_performance(
        self,
        operation: str,
        duration: float,
        tokens: Optional[int] = None,
        cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log performance metrics.

        Args:
            operation: Operation name
            duration: Duration in seconds
            tokens: Number of tokens processed (optional)
            cost: Cost in USD (optional)
            metadata: Optional metadata dictionary
        """
        if not self.config.log_performance:
            return

        metrics = f"{duration:.2f}s"
        if tokens:
            metrics += f" | {tokens} tokens"
        if cost:
            metrics += f" | ${cost:.4f}"

        meta_str = ""
        if metadata:
            meta_str = f" | Metadata: {json.dumps(metadata)}"

        self.logger.debug(
            f"[Performance] {operation}: {metrics}{meta_str}"
        )

    @contextmanager
    def track_performance(
        self,
        operation: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContextManager:
        """
        Context manager for tracking operation performance.

        Args:
            operation: Operation name
            metadata: Optional metadata to log

        Yields:
            None
        """
        start_time = time.time()
        start_tokens = getattr(self, '_token_count', 0)

        try:
            yield
        finally:
            duration = time.time() - start_time
            end_tokens = getattr(self, '_token_count', 0)
            tokens = end_tokens - start_tokens

            self.log_performance(
                operation,
                duration=duration,
                tokens=tokens if tokens > 0 else None,
                metadata=metadata
            )

    def log_request_response_pair(
        self,
        provider: str,
        prompt: str,
        response: str,
        duration: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log both request and response together.

        Args:
            provider: AI provider name
            prompt: Request prompt
            response: Response text
            duration: Request duration in seconds
            metadata: Optional metadata dictionary
        """
        self.log_request(provider, prompt, metadata=metadata)
        self.log_response(provider, response, duration, metadata=metadata)

    def log_analysis_start(self, analysis_type: str) -> None:
        """
        Log analysis start.

        Args:
            analysis_type: Type of analysis being performed
        """
        self.logger.info(f"[Analysis] Starting {analysis_type} analysis")

    def log_analysis_complete(
        self,
        analysis_type: str,
        duration: float,
        success: bool = True
    ) -> None:
        """
        Log analysis completion.

        Args:
            analysis_type: Type of analysis performed
            duration: Duration in seconds
            success: Whether analysis succeeded
        """
        status = "completed successfully" if success else "failed"
        self.logger.info(
            f"[Analysis] {analysis_type} analysis {status} in {duration:.2f}s"
        )
