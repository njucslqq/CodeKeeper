"""Tests for retry handler and error handling."""

import pytest
import time
from unittest.mock import Mock, patch
from git_deep_analyzer.ai.retry_handler import RetryHandler, RetryPolicy


class TestRetryPolicy:
    """Test RetryPolicy configuration."""

    def test_default_policy(self):
        """Given: RetryPolicy with no arguments
        When: Creating default policy
        Then: Uses sensible defaults
        """
        # When
        policy = RetryPolicy()

        # Then
        assert policy.max_retries == 3
        assert policy.base_delay == 1.0
        assert policy.max_delay == 60.0
        assert policy.backoff_factor == 2.0
        assert policy.jitter is True

    def test_custom_policy(self):
        """Given: Custom retry parameters
        When: Creating RetryPolicy
        Then: Uses custom values
        """
        # When
        policy = RetryPolicy(
            max_retries=5,
            base_delay=0.5,
            max_delay=30.0,
            backoff_factor=3.0,
            jitter=False
        )

        # Then
        assert policy.max_retries == 5
        assert policy.base_delay == 0.5
        assert policy.max_delay == 30.0
        assert policy.backoff_factor == 3.0
        assert policy.jitter is False

    def test_backoff_calculation(self):
        """Given: RetryPolicy
        When: Calculating backoff for multiple attempts
        Then: Delay increases exponentially
        """
        # Given
        policy = RetryPolicy(base_delay=1.0, backoff_factor=2.0, max_delay=10.0, jitter=False)

        # When
        delays = [policy._calculate_delay(attempt) for attempt in range(4)]

        # Then - 1, 2, 4, 8 (capped at max_delay)
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0
        assert delays[3] == 8.0

    def test_backoff_capped_at_max_delay(self):
        """Given: RetryPolicy with max_delay
        When: Calculating backoff beyond max_delay
        Then: Delay is capped at max_delay
        """
        # Given
        policy = RetryPolicy(base_delay=1.0, backoff_factor=10.0, max_delay=5.0, jitter=False)

        # When
        delays = [policy._calculate_delay(attempt) for attempt in range(5)]

        # Then
        for delay in delays:
            assert delay <= 5.0

    def test_jitter_adds_randomness(self):
        """Given: RetryPolicy with jitter enabled
        When: Calculating backoff multiple times
        Then: Delays vary within range
        """
        # Given
        policy = RetryPolicy(base_delay=1.0, backoff_factor=2.0, jitter=True)

        # When
        delays = [policy._calculate_delay(3) for _ in range(10)]

        # Then - All delays should be in range [0.8 * base, 1.2 * base]
        base_delay = 8.0
        for delay in delays:
            assert 0.8 * base_delay <= delay <= 1.2 * base_delay


class TestRetryHandler:
    """Test RetryHandler execution."""

    @pytest.fixture
    def retry_handler(self):
        """Create RetryHandler instance."""
        return RetryHandler(RetryPolicy(max_retries=3))

    def test_success_on_first_attempt(self, retry_handler):
        """Given: A function that succeeds
        When: execute() is called
        Then: Returns result immediately
        """
        # Given
        func = Mock(return_value="success")

        # When
        result = retry_handler.execute(func)

        # Then
        assert result == "success"
        assert func.call_count == 1

    def test_retry_until_success(self, retry_handler):
        """Given: A function that fails twice then succeeds
        When: execute() is called
        Then: Retries until success
        """
        # Given
        func = Mock(side_effect=[ValueError("error 1"), ValueError("error 2"), "success"])

        # When
        result = retry_handler.execute(func)

        # Then
        assert result == "success"
        assert func.call_count == 3

    def test_max_retries_exceeded(self, retry_handler):
        """Given: A function that always fails
        When: execute() is called
        Then: Raises last exception after max retries
        """
        # Given
        func = Mock(side_effect=ValueError("persistent error"))

        # When & Then
        with pytest.raises(ValueError, match="persistent error"):
            retry_handler.execute(func)

        # Then - Should be called max_retries + 1 times (initial + retries)
        assert func.call_count == 4  # 1 initial + 3 retries

    def test_retry_delay(self):
        """Given: RetryHandler with base delay
        When: Function fails and needs retry
        Then: Waits between retries
        """
        # Given
        policy = RetryPolicy(max_retries=2, base_delay=0.1, jitter=False)
        handler = RetryHandler(policy)
        func = Mock(side_effect=[ValueError("error"), ValueError("error"), "success"])

        # When
        start_time = time.time()
        result = handler.execute(func)
        elapsed_time = time.time() - start_time

        # Then
        assert result == "success"
        # Should have waited: 0.1 (after first failure) + 0.2 (after second failure)
        assert elapsed_time >= 0.3
        assert elapsed_time < 0.5  # Allow some margin

    def test_specific_exception_types(self):
        """Given: Handler configured for specific exceptions
        When: Non-retriable exception occurs
        Then: Fails immediately without retry
        """
        # Given
        policy = RetryPolicy(max_retries=3, retriable_exceptions=[ValueError])
        handler = RetryHandler(policy)

        func = Mock(side_effect=KeyError("non-retriable"))

        # When & Then
        with pytest.raises(KeyError):
            handler.execute(func)

        # Then - Should not retry
        assert func.call_count == 1

    def test_all_exception_types_by_default(self):
        """Given: Handler with default policy
        When: Any exception occurs
        Then: Retries all exception types
        """
        # Given
        handler = RetryHandler(RetryPolicy(max_retries=2))

        func = Mock(side_effect=[RuntimeError("error"), "success"])

        # When
        result = handler.execute(func)

        # Then
        assert result == "success"
        assert func.call_count == 2

    def test_abort_failure_behavior(self):
        """Given: Handler with abort failure behavior
        When: Max retries exceeded
        Then: Raises exception immediately (no fallback)
        """
        # Given
        policy = RetryPolicy(max_retries=2, failure_behavior="abort")
        handler = RetryHandler(policy)

        func = Mock(side_effect=ValueError("error"))

        # When & Then
        with pytest.raises(ValueError):
            handler.execute(func)

        assert func.call_count == 3  # 1 initial + 2 retries

    def test_continue_failure_behavior(self):
        """Given: Handler with continue failure behavior
        When: Max retries exceeded
        Then: Returns None instead of raising
        """
        # Given
        policy = RetryPolicy(max_retries=2, failure_behavior="continue")
        handler = RetryHandler(policy)

        func = Mock(side_effect=ValueError("error"))

        # When
        result = handler.execute(func)

        # Then
        assert result is None
        assert func.call_count == 3

    def test_fallback_failure_behavior(self):
        """Given: Handler with fallback failure behavior and fallback function
        When: Max retries exceeded
        Then: Returns fallback function result
        """
        # Given
        fallback_func = Mock(return_value="fallback_value")
        policy = RetryPolicy(max_retries=2, failure_behavior="fallback", fallback_func=fallback_func)
        handler = RetryHandler(policy)

        func = Mock(side_effect=ValueError("error"))

        # When
        result = handler.execute(func)

        # Then
        assert result == "fallback_value"
        assert func.call_count == 3
        assert fallback_func.call_count == 1

    def test_timeout_control(self):
        """Given: Handler with timeout
        When: Function takes too long
        Then: Raises TimeoutError
        """
        # Given
        policy = RetryPolicy(max_retries=1, timeout=0.1)
        handler = RetryHandler(policy)

        def slow_function():
            time.sleep(1.0)
            return "done"

        # When & Then
        with pytest.raises(TimeoutError):
            handler.execute(slow_function)

    def test_log_retry_attempts(self, caplog):
        """Given: Handler with logging enabled
        When: Retry occurs
        Then: Logs retry attempts
        """
        # Given
        import logging
        caplog.set_level(logging.INFO)

        policy = RetryPolicy(max_retries=2)
        handler = RetryHandler(policy, log_retries=True)

        func = Mock(side_effect=[ValueError("error"), "success"])

        # When
        with pytest.raises(Exception):
            handler.execute(func)

        # Then - Should log retry attempt
        assert any("Retry" in record.message for record in caplog.records)
