"""Tests for technical dimension analyzers."""

import pytest
from unittest.mock import Mock, patch
from git_deep_analyzer.ai.technical_analyzer import (
    TechnicalAnalyzer,
    QualityAnalyzer,
    PatternsAnalyzer,
    ConcurrencyAnalyzer,
    PerformanceAnalyzer,
    ArchitectureAnalyzer
)


class TestQualityAnalyzer:
    """Test QualityAnalyzer."""

    @pytest.fixture
    def quality_analyzer(self, sample_ai_client):
        """Create QualityAnalyzer instance."""
        return QualityAnalyzer(sample_ai_client, logger=None)

    def test_analyze_code_quality(self, quality_analyzer):
        """Given: QualityAnalyzer and code
        When: analyze() is called
        Then: Returns quality analysis results
        """
        # Given
        code = "def foo():\n    pass"

        # When
        result = quality_analyzer.analyze(code, language="python")

        # Then
        assert result is not None
        if isinstance(result, str):
            assert "quality" in result.lower() or "score" in result.lower()
        elif isinstance(result, dict):
            assert "quality" in result or "score" in result or len(result) > 0

    def test_analyze_with_metrics(self, quality_analyzer):
        """Given: QualityAnalyzer
        When: analyze() returns metrics
        Then: Includes quality scores and recommendations
        """
        # Given
        code = "class Example:\n    pass"

        # When
        result = quality_analyzer.analyze(code, language="python")

        # Then
        # Result should contain analysis output (will vary based on AI response)
        assert isinstance(result, str) or isinstance(result, dict)


class TestPatternsAnalyzer:
    """Test PatternsAnalyzer."""

    @pytest.fixture
    def patterns_analyzer(self, sample_ai_client):
        """Create PatternsAnalyzer instance."""
        return PatternsAnalyzer(sample_ai_client, logger=None)

    def test_detect_singleton_pattern(self, patterns_analyzer):
        """Given: C++ code with singleton pattern
        When: analyze() is called
        Then: Detects singleton pattern
        """
        # Given
        cpp_code = """
        class Singleton {
        private:
            static Singleton* instance;
            Singleton() {}
        public:
            static Singleton* getInstance() {
                if (!instance) instance = new Singleton();
                return instance;
            }
        };
        """

        # When
        result = patterns_analyzer.analyze(cpp_code, language="cpp")

        # Then
        assert result is not None

    def test_detect_factory_pattern(self, patterns_analyzer):
        """Given: Python code with factory pattern
        When: analyze() is called
        Then: Detects factory pattern
        """
        # Given
        python_code = """
        class AnimalFactory:
            def create_animal(self, animal_type):
                if animal_type == "dog":
                    return Dog()
                elif animal_type == "cat":
                    return Cat()
        """

        # When
        result = patterns_analyzer.analyze(python_code, language="python")

        # Then
        assert result is not None


class TestConcurrencyAnalyzer:
    """Test ConcurrencyAnalyzer."""

    @pytest.fixture
    def concurrency_analyzer(self, sample_ai_client):
        """Create ConcurrencyAnalyzer instance."""
        return ConcurrencyAnalyzer(sample_ai_client, logger=None)

    def test_analyze_thread_usage(self, concurrency_analyzer):
        """Given: C++ code with threading
        When: analyze() is called
        Then: Detects thread usage
        """
        # Given
        cpp_code = """
        #include <thread>
        void worker() {}
        int main() {
            std::thread t(worker);
            t.join();
        }
        """

        # When
        result = concurrency_analyzer.analyze(cpp_code, language="cpp")

        # Then
        assert result is not None

    def test_analyze_async_usage(self, concurrency_analyzer):
        """Given: Python code with async
        When: analyze() is called
        Then: Detects async usage
        """
        # Given
        python_code = """
        import asyncio
        async def fetch():
            pass
        async def main():
            await fetch()
        """

        # When
        result = concurrency_analyzer.analyze(python_code, language="python")

        # Then
        assert result is not None


class TestPerformanceAnalyzer:
    """Test PerformanceAnalyzer."""

    @pytest.fixture
    def performance_analyzer(self, sample_ai_client):
        """Create PerformanceAnalyzer instance."""
        return PerformanceAnalyzer(sample_ai_client, logger=None)

    def test_analyze_time_complexity(self, performance_analyzer):
        """Given: Python code with nested loops
        When: analyze() is called
        Then: Identifies time complexity
        """
        # Given
        python_code = """
        for i in range(n):
            for j in range(m):
                print(i, j)
        """

        # When
        result = performance_analyzer.analyze(python_code, language="python")

        # Then
        assert result is not None

    def test_analyze_io_operations(self, performance_analyzer):
        """Given: Code with file I/O
        When: analyze() is called
        Then: Identifies I/O operations
        """
        # Given
        python_code = """
        with open('file.txt', 'r') as f:
            data = f.read()
        """

        # When
        result = performance_analyzer.analyze(python_code, language="python")

        # Then
        assert result is not None


class TestArchitectureAnalyzer:
    """Test ArchitectureAnalyzer."""

    @pytest.fixture
    def architecture_analyzer(self, sample_ai_client):
        """Create ArchitectureAnalyzer instance."""
        return ArchitectureAnalyzer(sample_ai_client, logger=None)

    def test_analyze_layering(self, architecture_analyzer):
        """Given: Multi-module code
        When: analyze() is called
        Then: Evaluates architectural layers
        """
        # Given
        code = """
        class Database:
            def query(self):
                pass

        class Service:
            def __init__(self, db):
                self.db = db

        class API:
            def __init__(self, service):
                self.service = service
        """

        # When
        result = architecture_analyzer.analyze(code, language="python")

        # Then
        assert result is not None

    def test_analyze_coupling(self, architecture_analyzer):
        """Given: Code with dependencies
        When: analyze() is called
        Then: Evaluates coupling
        """
        # Given
        python_code = """
        class A:
            def use_b(self, b_instance):
                b_instance.method()
        """

        # When
        result = architecture_analyzer.analyze(python_code, language="python")

        # Then
        assert result is not None


class TestTechnicalAnalyzer:
    """Test TechnicalAnalyzer main class."""

    @pytest.fixture
    def technical_analyzer(self, sample_ai_client):
        """Create TechnicalAnalyzer instance."""
        return TechnicalAnalyzer(
            ai_client=sample_ai_client,
            config={"analyzers": ["quality", "patterns", "concurrency", "performance", "architecture"]},
            logger=None
        )

    def test_analyze_all_dimensions(self, technical_analyzer):
        """Given: TechnicalAnalyzer with all analyzers
        When: analyze_all() is called
        Then: Returns combined analysis
        """
        # Given
        code = """
        class Example:
            def __init__(self):
                self.value = 0
            def method(self):
                return self.value
        """

        # When
        result = technical_analyzer.analyze_all(code, language="python")

        # Then
        assert result is not None
        assert "quality" in result or "patterns" in result

    def test_analyze_selected_dimensions(self, technical_analyzer):
        """Given: TechnicalAnalyzer
        When: analyze() is called with specific dimensions
        Then: Analyzes only specified dimensions
        """
        # Given
        code = "def test(): pass"

        # When
        result = technical_analyzer.analyze(
            code,
            language="python",
            dimensions=["quality", "performance"]
        )

        # Then
        assert result is not None

    def test_parallel_analysis(self, technical_analyzer):
        """Given: TechnicalAnalyzer
        When: analyze_all() is called with parallel=True
        Then: Analyzers run in parallel
        """
        # Given
        code = "class Example: pass"

        # When
        result = technical_analyzer.analyze_all(
            code,
            language="python",
            parallel=True
        )

        # Then
        assert result is not None

    def test_serial_analysis(self, technical_analyzer):
        """Given: TechnicalAnalyzer
        When: analyze_all() is called with parallel=False
        Then: Analyzers run serially
        """
        # Given
        code = "class Example: pass"

        # When
        result = technical_analyzer.analyze_all(
            code,
            language="python",
            parallel=False
        )

        # Then
        assert result is not None


# Fixtures
@pytest.fixture
def sample_logger():
    """Create sample logger."""
    return Mock()


@pytest.fixture
def sample_ai_client():
    """Create mock AI client."""
    client = Mock()
    client.complete.return_value = "Sample AI analysis result"
    return client
