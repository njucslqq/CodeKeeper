"""Monitoring metrics system."""

import time
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from typing import Optional


# Custom metrics registry
registry = CollectorRegistry()

# Request metrics
requests_total = Counter(
    "requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"],
    registry=registry
)

request_duration = Histogram(
    "request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.5, 1.0, 5.0],
    registry=registry
)

# Analysis metrics
analysis_tasks_total = Counter(
    "analysis_tasks_total",
    "Total number of analysis tasks",
    ["status"],
    registry=registry
)

analysis_duration = Histogram(
    "analysis_duration_seconds",
    "Analysis duration in seconds",
    ["dimension"],
    buckets=[10, 30, 60, 120, 300, 600, 1800],
    registry=registry
)

# LLM metrics
llm_calls_total = Counter(
    "llm_calls_total",
    "Total number of LLM calls",
    ["provider", "model", "status"],
    registry=registry
)

llm_duration = Histogram(
    "llm_duration_seconds",
    "LLM call duration in seconds",
    ["provider", "model"],
    buckets=[1, 5, 10, 30, 60, 120],
    registry=registry
)

# Concurrency metrics
active_tasks = Gauge(
    "active_tasks",
    "Number of currently active tasks",
    ["type"],
    registry=registry
)

queue_length = Gauge(
    "queue_length",
    "Number of tasks in queue",
    registry=registry
)


class MetricsRegistry:
    """Metrics registry for application metrics."""

    @staticmethod
    def increment_requests_total(method: str, endpoint: str, status: str):
        """Increment request counter."""
        requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

    @staticmethod
    def observe_request_duration(method: str, endpoint: str, duration: float):
        """Observe request duration."""
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    @staticmethod
    def increment_analysis_tasks(status: str):
        """Increment analysis task counter."""
        analysis_tasks_total.labels(status=status).inc()

    @staticmethod
    def observe_analysis_duration(dimension: str, duration: float):
        """Observe analysis duration."""
        analysis_duration.labels(dimension=dimension).observe(duration)

    @staticmethod
    def increment_llm_calls(provider: str, model: str, status: str):
        """Increment LLM call counter."""
        llm_calls_total.labels(provider=provider, model=model, status=status).inc()

    @staticmethod
    def observe_llm_duration(provider: str, model: str, duration: float):
        """Observe LLM call duration."""
        llm_duration.labels(provider=provider, model=model).observe(duration)

    @staticmethod
    def set_active_tasks(task_type: str, value: int):
        """Set active tasks gauge."""
        active_tasks.labels(type=task_type).set(value)

    @staticmethod
    def set_queue_length(value: int):
        """Set queue length gauge."""
        queue_length.set(value)

    @staticmethod
    def get(metric_name: str) -> float:
        """Get metric value (simplified)."""
        # Simplified implementation - Prometheus counters don't expose values directly
        # This is a placeholder for testing
        return 0.0
