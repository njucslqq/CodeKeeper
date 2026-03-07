"""Cache utilities for performance optimization."""

from functools import lru_cache
from typing import Optional, Any, Dict, Callable, TypeVar, Tuple
from datetime import datetime, timedelta
import hashlib
import json


T = TypeVar('T')


class SimpleCache:
    """Simple in-memory cache with expiration."""

    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]

        if datetime.now() > expiry:
            # Expired
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default_ttl if not specified)
        """
        expiry = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
        self._cache[key] = (value, expiry)

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def delete(self, key: str) -> bool:
        """
        Delete specific key from cache.

        Args:
            key: Cache key

        Returns:
            True if key existed, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)


class HTTPCache:
    """Cache for HTTP API responses."""

    def __init__(self, default_ttl: int = 1800):
        """
        Initialize HTTP cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 30 minutes)
        """
        self._cache = SimpleCache(default_ttl)
        self._hit_count = 0
        self._miss_count = 0

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Get HTTP response from cache.

        Args:
            url: API endpoint URL
            params: Optional query parameters

        Returns:
            Cached response or None
        """
        cache_key = self._make_key(url, params)
        cached = self._cache.get(cache_key)

        if cached is not None:
            self._hit_count += 1
        else:
            self._miss_count += 1

        return cached

    def set(self, url: str, response: Any, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Cache HTTP response.

        Args:
            url: API endpoint URL
            response: Response data
            params: Optional query parameters
        """
        cache_key = self._make_key(url, params)
        self._cache.set(cache_key, response)

    def _make_key(self, url: str, params: Optional[Dict[str, Any]]) -> str:
        """
        Create cache key from URL and parameters.

        Args:
            url: API endpoint URL
            params: Optional query parameters

        Returns:
            Cache key
        """
        if params:
            # Sort params for consistent key generation
            sorted_params = sorted(params.items())
            params_str = json.dumps(sorted_params, sort_keys=True)
            key = f"{url}:{params_str}"
        else:
            key = url

        # Hash for shorter keys
        return hashlib.md5(key.encode()).hexdigest()

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hits, misses, size
        """
        return {
            "hits": self._hit_count,
            "misses": self._miss_count,
            "size": self._cache.size(),
            "hit_rate": (
                self._hit_count / (self._hit_count + self._miss_count)
                if (self._hit_count + self._miss_count) > 0
                else 0.0
            )
        }

    def clear(self) -> None:
        """Clear all cached HTTP responses."""
        self._cache.clear()
        self._hit_count = 0
        self._miss_count = 0


def cached(default_ttl: int = 3600, maxsize: int = 128):
    """
    Decorator for caching function results.

    Args:
        default_ttl: Default time-to-live in seconds
        maxsize: Maximum cache size

    Returns:
        Decorated function
    """
    cache = SimpleCache(default_ttl)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @lru_cache(maxsize=maxsize)
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key from arguments
            cache_key = _make_cache_key(func.__name__, args, kwargs)

            # Check cache first
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper

    return decorator


def cached_http(ttl: int = 1800):
    """
    Decorator for caching HTTP API calls.

    Args:
        ttl: Time-to-live in seconds (default: 30 minutes)

    Returns:
        Decorated function
    """
    cache = HTTPCache(ttl)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            # Extract URL and params for HTTP calls
            url = kwargs.get("url") or (args[0] if args else "")
            params = kwargs.get("params")

            if url and params:
                # Check cache
                cached = cache.get(url, params)
                if cached is not None:
                    return cached

            # Call function and cache result
            result = func(*args, **kwargs)

            if url and params:
                cache.set(url, result, params=params)

            return result

        return wrapper

    return decorator


def _make_cache_key(func_name: str, args: tuple, kwargs: Dict[str, Any]) -> str:
    """
    Create cache key from function name and arguments.

    Args:
        func_name: Function name
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Cache key
    """
    key_parts = [func_name]

    # Add args to key
    if args:
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            elif isinstance(arg, datetime):
                key_parts.append(arg.isoformat())
            else:
                key_parts.append(str(hash(arg)))

    # Add kwargs to key (sorted for consistency)
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        for k, v in sorted_kwargs:
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}={v}")
            elif isinstance(v, datetime):
                key_parts.append(f"{k}={v.isoformat()}")
            else:
                key_parts.append(f"{k}={hash(v)}")

    return ":".join(key_parts)


class BatchRequestHandler:
    """Handler for batching API requests to reduce HTTP calls."""

    def __init__(self, batch_size: int = 50, max_wait: float = 2.0):
        """
        Initialize batch handler.

        Args:
            batch_size: Maximum items per batch
            max_wait: Maximum wait time before flushing batch (seconds)
        """
        self.batch_size = batch_size
        self.max_wait = max_wait
        self._pending: list = []
        self._last_flush = None

    def add(self, item: Any) -> None:
        """
        Add item to batch.

        Args:
            item: Item to add to batch
        """
        self._pending.append(item)

        # Check if batch is full
        if len(self._pending) >= self.batch_size:
            self.flush()

    def flush(self) -> list:
        """
        Flush all pending items.

        Returns:
            List of items that were in the batch
        """
        items = list(self._pending)
        self._pending.clear()
        self._last_flush = datetime.now()
        return items

    def has_pending(self) -> bool:
        """
        Check if there are pending items.

        Returns:
            True if there are pending items
        """
        return len(self._pending) > 0

    def get_batch(self) -> list:
        """
        Get current batch without flushing.

        Returns:
            List of current pending items
        """
        return list(self._pending)

    def should_flush(self) -> bool:
        """
        Check if batch should be flushed based on time.

        Returns:
            True if max_wait time exceeded
        """
        if self._last_flush is None:
            return False

        elapsed = (datetime.now() - self._last_flush).total_seconds()
        return elapsed >= self.max_wait

    def size(self) -> int:
        """Get current batch size."""
        return len(self._pending)
