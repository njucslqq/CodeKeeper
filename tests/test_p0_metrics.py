"""P0 metrics tests."""

def test_metrics_registry():
    from issue_analyzer.metrics import MetricsRegistry
    # Just test that methods exist and can be called without error
    MetricsRegistry.increment_analysis_tasks("pending")
    MetricsRegistry.observe_analysis_duration("business", 10.0)
    MetricsRegistry.set_active_tasks("analysis", 5)
    MetricsRegistry.set_queue_length(10)
    assert True

def test_requests_metrics():
    from issue_analyzer.metrics import MetricsRegistry
    MetricsRegistry.increment_requests_total("GET", "/health", "200")
    MetricsRegistry.observe_request_duration("GET", "/health", 0.1)
    assert True

def test_llm_metrics():
    from issue_analyzer.metrics import MetricsRegistry
    MetricsRegistry.increment_llm_calls("claude_cli", "claude-3-opus", "success")
    MetricsRegistry.observe_llm_duration("claude_cli", "claude-3-opus", 5.0)
    assert True
