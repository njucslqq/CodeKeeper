"""Logging system."""

import logging
import sys
from pathlib import Path
from typing import Optional
from contextvars import ContextVar


_task_id_context: ContextVar[Optional[str]] = ContextVar("task_id", default=None)


def get_task_id() -> Optional[str]:
    """Get current task ID from context."""
    return _task_id_context.get()


def set_task_id(task_id: Optional[str]):
    """Set task ID in context."""
    _task_id_context.set(task_id)


class Logger:
    """Application logger with task context."""

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        file_path: Optional[Path] = None,
        console: bool = True
    ):
        self.name = name
        self.logger = logging.getLogger(f"issue_analyzer.{name}")
        self.logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        self.logger.handlers.clear()

        # Console handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self._get_formatter(console=True))
            self.logger.addHandler(console_handler)

        # File handler
        if file_path:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setFormatter(self._get_formatter(console=False))
            self.logger.addHandler(file_handler)

    @staticmethod
    def _get_formatter(console: bool) -> logging.Formatter:
        """Get log formatter."""
        if console:
            return logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                '%Y-%m-%d %H:%M:%S'
            )
        else:
            return logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(task_id)s | %(message)s',
                '%Y-%m-%d %H:%M:%S'
            )

    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with task context."""
        extra = {'task_id': get_task_id()}
        self.logger.log(level, message, extra=extra, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)


# Global logger cache
_loggers: dict = {}


def get_logger(name: str, **kwargs) -> Logger:
    """Get or create logger."""
    if name not in _loggers:
        _loggers[name] = Logger(name, **kwargs)
    return _loggers[name]
