"""Batch operations for reducing HTTP API calls."""

from typing import List, Dict, Any, Callable, TypeVar, Optional
import asyncio
import aiohttp
from functools import partial

T = TypeVar('T')


class AsyncBatchProcessor:
    """Asynchronous batch processor for parallel API calls."""

    def __init__(self, max_concurrent: int = 10, timeout: float = 30.0):
        """
        Initialize async batch processor.

        Args:
            max_concurrent: Maximum concurrent requests
            timeout: Request timeout in seconds
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout

    async def process_async(
        self,
        items: List[Any],
        process_func: Callable[[Any], Any],
        *args,
        **kwargs
    ) -> List[Any]:
        """
        Process items asynchronously in batches.

        Args:
            items: List of items to process
            process_func: Async function to call for each item
            *args: Additional arguments to pass to process_func
            **kwargs: Additional keyword arguments

        Returns:
            List of results in same order as input
        """
        if not items:
            return []

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_item(item: Any) -> Any:
            async with semaphore:
                return await asyncio.wait_for(
                    process_func(item, *args, **kwargs),
                    timeout=self.timeout
                )

        # Process all items concurrently
        results = await asyncio.gather(
            *[process_item(item) for item in items],
            return_exceptions=True
        )

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Log or handle error
                processed_results.append({
                    "item": items[i],
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        return processed_results

    def process(
        self,
        items: List[Any],
        process_func: Callable[[Any], Any],
        *args,
        **kwargs
    ) -> List[Any]:
        """
        Synchronous wrapper for async processing.

        Args:
            items: List of items to process
            process_func: Function to call for each item
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            List of results
        """
        if not items:
            return []

        # Run async event loop
        return asyncio.run(self.process_async(items, process_func, *args, **kwargs))


class BatchFetcher:
    """Batch fetcher for API resources."""

    def __init__(self, fetch_func: Callable[[Any], Any], batch_size: int = 50):
        """
        Initialize batch fetcher.

        Args:
            fetch_func: Function to fetch single item
            batch_size: Items per batch
        """
        self.fetch_func = fetch_func
        self.batch_size = batch_size

    def fetch_all(
        self,
        identifiers: List[Any],
        *args,
        **kwargs
    ) -> List[Any]:
        """
        Fetch all items in batches.

        Args:
            identifiers: List of identifiers to fetch
            *args: Additional arguments for fetch_func
            **kwargs: Additional keyword arguments

        Returns:
            List of all fetched items
        """
        if not identifiers:
            return []

        all_results = []

        # Process in batches
        for i in range(0, len(identifiers), self.batch_size):
            batch = identifiers[i:i + self.batch_size]

            # Fetch batch
            batch_results = self._fetch_batch(batch, *args, **kwargs)
            all_results.extend(batch_results)

        return all_results

    def _fetch_batch(
        self,
        batch: List[Any],
        *args,
        **kwargs
    ) -> List[Any]:
        """
        Fetch a single batch of items.

        Args:
            batch: Batch of identifiers
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            List of fetched items
        """
        results = []

        for identifier in batch:
            try:
                result = self.fetch_func(identifier, *args, **kwargs)
                results.append(result)
            except Exception as e:
                # Log error but continue with other items
                results.append({
                    "identifier": identifier,
                    "error": str(e)
                })

        return results


class RateLimiter:
    """Rate limiter for API calls to avoid hitting rate limits."""

    def __init__(
        self,
        max_calls: int,
        time_window: float,
        backoff_factor: float = 2.0
    ):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
            backoff_factor: Exponential backoff factor
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.backoff_factor = backoff_factor
        self._call_history: List[float] = []
        self._current_backoff = 1.0

    def acquire(self) -> Optional[float]:
        """
        Acquire permission to make a call.

        Returns:
            Time to wait in seconds, or None if can proceed immediately
        """
        now = 0.0
        import time
        if self._call_history:
            now = time.time()

        # Remove old history outside time window
        cutoff_time = now - self.time_window
        self._call_history = [
            t for t in self._call_history if t > cutoff_time
        ]

        # Check if under limit
        if len(self._call_history) < self.max_calls:
            self._call_history.append(now)
            return None

        # Over limit - calculate wait time
        wait_time = self._current_backoff * self.time_window

        # Increase backoff for next time
        self._current_backoff *= self.backoff_factor

        # Limit maximum wait time to 1 minute
        wait_time = min(wait_time, 60.0)

        return wait_time

    def reset(self) -> None:
        """Reset rate limiter."""
        self._call_history.clear()
        self._current_backoff = 1.0


def batched(batch_size: int = 50):
    """
    Decorator for batching function calls.

    Args:
        batch_size: Maximum items per batch

    Returns:
        Decorated function that accumulates and batches
    """
    batch = []

    def decorator(func: Callable[..., List[Any]]) -> Callable[..., List[Any]]:
        def wrapper(*args, **kwargs) -> List[Any]:
            result = func(*args, **kwargs)

            # Add to batch
            if isinstance(result, list):
                batch.extend(result)
            else:
                batch.append(result)

            # Check if batch is full
            if len(batch) >= batch_size:
                # Flush batch
                to_return = list(batch)
                batch.clear()
                return to_return

            return result

        return wrapper
