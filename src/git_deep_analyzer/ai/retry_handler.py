"""Retry handler with exponential backoff and configurable policies."""

import time
import random
import logging
from typing import Callable, Optional, Type, Any, List
from dataclasses import dataclass
from functools import wraps
import signal


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""

    max_retries: int = 3
    """Maximum number of retry attempts."""

    base_delay: float = 1.0
    """Base delay in seconds between retries."""

    max_delay: float = 60.0
    """Maximum delay in seconds."""

    backoff_factor: float = 2.0
    """Multiplier for exponential backoff."""

    jitter: bool = True
    """Add random jitter to delay to avoid thundering herd."""

    retriable_exceptions: Optional[List[Type[Exception]]] = None
    """Exception types that should trigger retry. None = all exceptions."""

    failure_behavior: str = "retry"
    """
    What to do when max retries exceeded:
    - "retry": Raise last exception (default)
    - "continue": Return None
    - "abort": Raise exception immediately
    - "fallback": Return result from fallback_func
    """

    fallback_func: Optional[Callable[[], Any]] = None
    """Fallback function used when failure_behavior is 'fallback'."""

    timeout: Optional[float] = None
    """Timeout in seconds for function execution."""

    def __post_init__(self):
        """Validate policy configuration."""
        valid_behaviors = {"retry", "continue", "abort", "fallback"}
        if self.failure_behavior not in valid_behaviors:
            raise ValueError(f"Invalid failure_behavior: {self.failure_behavior}")

        if self.failure_behavior == "fallback" and self.fallback_func is None:
            raise ValueError("fallback_func required when failure_behavior is 'fallback'")

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given retry attempt.

        Args:
            attempt: Retry attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add +/- 20% jitter
            jitter_factor = random.uniform(0.8, 1.2)
            delay *= jitter_factor

        return delay


class TimeoutError(Exception):
    """Raised when function execution times out."""
    pass


class RetryHandler:
    """Handles function execution with retry logic."""

    def __init__(self, policy: RetryPolicy, log_retries: bool = True):
        """
        Initialize retry handler.

        Args:
            policy: Retry policy configuration
            log_retries: Whether to log retry attempts
        """
        self.policy = policy
        self.log_retries = log_retries
        self.logger = logging.getLogger(__name__)

    def execute(self, func: Callable[[], Any]) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute

        Returns:
            Function result

        Raises:
            Exception: Last exception if max retries exceeded (when failure_behavior is 'retry')
            TimeoutError: If function execution exceeds timeout
        """
        last_exception = None

        for attempt in range(self.policy.max_retries + 1):
            try:
                # Execute with timeout if configured
                if self.policy.timeout:
                    return self._execute_with_timeout(func)
                else:
                    return func()

            except Exception as e:
                last_exception = e

                # Check if exception is retriable
                if self.policy.retriable_exceptions is not None:
                    if not isinstance(e, tuple(self.policy.retriable_exceptions)):
                        raise  # Non-retriable exception

                # Abort immediately if configured
                if self.policy.failure_behavior == "abort":
                    raise

                # Log retry attempt
                if self.log_retries and attempt < self.policy.max_retries:
                    self.logger.warning(
                        f"Attempt {attempt + 1}/{self.policy.max_retries + 1} failed: {e}. "
                        f"Retrying in {self.policy._calculate_delay(attempt):.2f}s..."
                    )

                # Last attempt - handle failure behavior
                if attempt == self.policy.max_retries:
                    if self.policy.failure_behavior == "continue":
                        self.logger.error(f"All {self.policy.max_retries + 1} attempts failed. Continuing anyway.")
                        return None
                    elif self.policy.failure_behavior == "fallback":
                        self.logger.error(f"All {self.policy.max_retries + 1} attempts failed. Using fallback.")
                        return self.policy.fallback_func()
                    else:  # "retry"
                        raise

                # Wait before retry
                delay = self.policy._calculate_delay(attempt)
                time.sleep(delay)

        # Should not reach here
        if last_exception:
            raise last_exception

    def _execute_with_timeout(self, func: Callable[[], Any]) -> Any:
        """
        Execute function with timeout.

        Args:
            func: Function to execute

        Returns:
            Function result

        Raises:
            TimeoutError: If execution exceeds timeout
        """
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Function execution exceeded timeout of {self.policy.timeout}s")

        # Set signal handler for timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.policy.timeout))

        try:
            result = func()
        finally:
            # Cancel alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

        return result

    def __call__(self, func: Callable[[], Any]) -> Any:
        """
        Make RetryHandler callable.

        Args:
            func: Function to execute

        Returns:
            Function result
        """
        return self.execute(func)


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retriable_exceptions: Optional[List[Type[Exception]]] = None,
    failure_behavior: str = "retry",
    fallback_func: Optional[Callable[[], Any]] = None,
    timeout: Optional[float] = None,
    log_retries: bool = True
) -> Callable:
    """
    Decorator for automatic retry with exponential backoff.

    Args:
        max_retries: Maximum retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Backoff multiplier
        jitter: Add random jitter
        retriable_exceptions: Exception types to retry
        failure_behavior: Failure handling mode
        fallback_func: Fallback function
        timeout: Execution timeout
        log_retries: Log retry attempts

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        policy = RetryPolicy(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            backoff_factor=backoff_factor,
            jitter=jitter,
            retriable_exceptions=retriable_exceptions,
            failure_behavior=failure_behavior,
            fallback_func=fallback_func,
            timeout=timeout
        )
        handler = RetryHandler(policy, log_retries=log_retries)

        @wraps(func)
        def wrapper(*args, **kwargs):
            def execute():
                return func(*args, **kwargs)
            return handler.execute(execute)

        return wrapper
    return decorator
