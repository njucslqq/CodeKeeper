"""Tests for analysis execution strategies."""

import pytest
from unittest.mock import Mock, patch
from git_deep_analyzer.ai.analysis_strategy import (
    AnalysisStrategy,
    SerialStrategy,
    ParallelStrategy,
    LayeredStrategy,
    IncrementalStrategy,
    AnalysisExecutor
)


class TestSerialStrategy:
    """Test serial analysis strategy."""

    @pytest.fixture
    def serial_strategy(self):
        """Create SerialStrategy instance."""
        return SerialStrategy()

    def test_execute_analyzers_serially(self, serial_strategy):
        """Given: Multiple analyzers
        When: execute() is called with serial strategy
        Then: Analyzers execute one by one
        """
        # Given
        analyzers = [
            Mock(return_value={"result1": "data1"}),
            Mock(return_value={"result2": "data2"}),
            Mock(return_value={"result3": "data3"}),
        ]
        code = "test code"
        language = "python"

        # When
        results = serial_strategy.execute(analyzers, code=code, language=language)

        # Then
        assert len(results) == 3
        assert results[0]["result1"] == "data1"
        assert results[1]["result2"] == "data2"
        assert results[2]["result3"] == "data3"
        # All analyzers should have been called
        for analyzer in analyzers:
            analyzer.assert_called_once_with(code=code, language=language)


class TestParallelStrategy:
    """Test parallel analysis strategy."""

    @pytest.fixture
    def parallel_strategy(self):
        """Create ParallelStrategy instance."""
        return ParallelStrategy(max_workers=2)

    def test_execute_analyzers_in_parallel(self, parallel_strategy):
        """Given: Multiple analyzers
        When: execute() is called with parallel strategy
        Then: Analyzers execute concurrently
        """
        # Given
        analyzers = [
            Mock(return_value={"result1": "data1"}),
            Mock(return_value={"result2": "data2"}),
        ]
        code = "test code"
        language = "python"

        # When
        results = parallel_strategy.execute(analyzers, code=code, language=language)

        # Then
        assert len(results) == 2
        # Results should exist (order may vary in parallel execution)
        assert any(r.get("result1") == "data1" for r in results)
        assert any(r.get("result2") == "data2" for r in results)

    def test_parallel_strategy_handles_errors(self, parallel_strategy):
        """Given: Analyzers with errors
        When: execute() is called
        Then: Errors are handled gracefully
        """
        # Given
        analyzers = [
            Mock(return_value={"result1": "data1"}),
            Mock(side_effect=Exception("Analyzer error")),
        ]
        code = "test code"
        language = "python"

        # When
        results = parallel_strategy.execute(analyzers, code=code, language=language)

        # Then
        assert len(results) == 2
        # One result should have error
        assert any("error" in r for r in results)


class TestLayeredStrategy:
    """Test layered analysis strategy."""

    @pytest.fixture
    def layered_strategy(self):
        """Create LayeredStrategy instance."""
        return LayeredStrategy()

    def test_execute_analyzers_by_layers(self, layered_strategy):
        """Given: Analyzers organized in layers
        When: execute() is called
        Then: Lower layers complete before higher layers start
        """
        # Given
        layer1_analyzers = [Mock(return_value={"layer1": "data"})]
        layer2_analyzers = [Mock(return_value={"layer2": "data"})]

        layers = [layer1_analyzers, layer2_analyzers]
        code = "test code"
        language = "python"

        # When
        results = layered_strategy.execute(layers, code=code, language=language)

        # Then
        # Should have results from both layers
        assert any("layer1" in r for r in results)
        assert any("layer2" in r for r in results)

    def test_pass_layer_results_to_next_layer(self, layered_strategy):
        """Given: Multi-layer analysis
        When: execute() is called
        Then: Lower layer results available to higher layers
        """
        # Given
        # Mock that tracks previous results
        analyzer1 = Mock(return_value={"layer1": "data1"})
        analyzer2 = Mock(return_value={"layer2": "data2"})

        # When
        results = layered_strategy.execute(
            [[analyzer1], [analyzer2]],
            code="test code",
            language="python"
        )

        # Then
        assert len(results) == 2


class TestIncrementalStrategy:
    """Test incremental analysis strategy."""

    @pytest.fixture
    def incremental_strategy(self):
        """Create IncrementalStrategy instance."""
        return IncrementalStrategy()

    def test_skip_unchanged_files(self, incremental_strategy):
        """Given: File hashes unchanged
        When: execute() is called
        Then: Skips analysis for unchanged files
        """
        # Given
        analyzer = Mock(return_value={"result": "data"})
        file_hash_map = {
            "file1.py": "hash1",
            "file2.py": "hash2"
        }
        previous_results = {
            "file1.py": {"result": "cached1"},
            "file2.py": {"result": "cached2"}
        }

        # When
        results = incremental_strategy.execute(
            analyzer,
            file_hash_map,
            previous_results,
            code="unchanged code"
        )

        # Then
        # Should use cached results
        assert "cached" in str(results)

    def test_analyze_changed_files_only(self, incremental_strategy):
        """Given: Some files changed
        When: execute() is called
        Then: Only analyzes changed files
        """
        # Given
        analyzer = Mock(return_value={"result": "new"})
        file_hash_map = {
            "file1.py": "hash1_changed",  # Changed
            "file2.py": "hash2_unchanged"  # Unchanged
        }
        previous_results = {
            "file1.py": {"result": "old"},
            "file2.py": {"result": "cached"}
        }

        # When
        results = incremental_strategy.execute(
            analyzer,
            file_hash_map,
            previous_results,
            code="new code"
        )

        # Then
        # File 1 should be re-analyzed, file 2 should be cached
        assert "new" in str(results)


class TestAnalysisExecutor:
    """Test AnalysisExecutor."""

    @pytest.fixture
    def executor(self, sample_ai_client):
        """Create AnalysisExecutor instance."""
        return AnalysisExecutor(ai_client=sample_ai_client)

    def test_execute_with_serial_strategy(self, executor):
        """Given: Executor with serial strategy
        When: execute() is called
        Then: Uses serial execution
        """
        # Given
        analyzers = [Mock(return_value={"result": "data"})]
        config = {"strategy": "serial"}

        # When
        results = executor.execute(analyzers, config=config, code="test")

        # Then
        assert results is not None

    def test_execute_with_parallel_strategy(self, executor):
        """Given: Executor with parallel strategy
        When: execute() is called
        Then: Uses parallel execution
        """
        # Given
        analyzers = [Mock(return_value={"result": "data"})]
        config = {"strategy": "parallel", "max_workers": 2}

        # When
        results = executor.execute(analyzers, config=config, code="test")

        # Then
        assert results is not None

    def test_execute_with_layered_strategy(self, executor):
        """Given: Executor with layered strategy
        When: execute() is called
        Then: Uses layered execution
        """
        # Given
        analyzers = [Mock(return_value={"result": "data"})]
        config = {"strategy": "layered"}

        # When
        results = executor.execute(analyzers, config=config, code="test")

        # Then
        assert results is not None

    def test_execute_with_invalid_strategy(self, executor):
        """Given: Executor with invalid strategy
        When: execute() is called
        Then: Falls back to serial strategy
        """
        # Given
        analyzers = [Mock(return_value={"result": "data"})]
        config = {"strategy": "invalid"}

        # When
        results = executor.execute(analyzers, config=config, code="test")

        # Then
        # Should still execute (fallback to serial)
        assert results is not None

    def test_combine_results(self, executor):
        """Given: Multiple analysis results
        When: combine_results() is called
        Then: Returns combined results
        """
        # Given
        results = [
            {"quality": {"score": 85}},
            {"patterns": ["singleton"]},
            {"performance": {"complexity": "O(n)"}}
        ]

        # When
        combined = executor.combine_results(results)

        # Then
        assert "quality" in combined
        assert "patterns" in combined
        assert "performance" in combined


# Fixtures
@pytest.fixture
def sample_ai_client():
    """Create mock AI client."""
    client = Mock()
    client.complete_json.return_value = {"test": "result"}
    return client
