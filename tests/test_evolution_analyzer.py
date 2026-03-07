"""Tests for evolution dimension analyzers."""

import pytest
from unittest.mock import Mock
from git_deep_analyzer.ai.evolution_analyzer import (
    EvolutionAnalyzer,
    TimelineAnalyzer,
    ImpactAnalyzer,
    DebtAnalyzer
)


class TestTimelineAnalyzer:
    """Test TimelineAnalyzer."""

    @pytest.fixture
    def timeline_analyzer(self, sample_ai_client):
        """Create TimelineAnalyzer instance."""
        return TimelineAnalyzer(sample_ai_client, logger=None)

    def test_analyze_commit_timeline(self, timeline_analyzer):
        """Given: Commit history
        When: analyze() is called
        Then: Analyzes timeline patterns
        """
        # Given
        commits = """
        Commit 1: Initial implementation (2024-01-01)
        Commit 2: Bug fix (2024-01-02)
        Commit 3: Feature addition (2024-01-05)
        """

        # When
        result = timeline_analyzer.analyze(commits=commits)

        # Then
        assert result is not None
        assert "timeline" in result

    def test_identify_development_phases(self, timeline_analyzer):
        """Given: Commit history
        When: analyze() is called
        Then: Identifies development phases
        """
        # Given
        commits = """
        Phase 1: Setup (Jan 2024)
        Phase 2: Core features (Feb 2024)
        Phase 3: Refactoring (Mar 2024)
        """

        # When
        result = timeline_analyzer.analyze(commits=commits)

        # Then
        assert result is not None

    def test_analyze_activity_patterns(self, timeline_analyzer):
        """Given: Commit history
        When: analyze() is called
        Then: Analyzes activity patterns
        """
        # Given
        commits = """
        10 commits in January
        5 commits in February
        20 commits in March
        """

        # When
        result = timeline_analyzer.analyze(commits=commits)

        # Then
        assert result is not None


class TestImpactAnalyzer:
    """Test ImpactAnalyzer."""

    @pytest.fixture
    def impact_analyzer(self, sample_ai_client):
        """Create ImpactAnalyzer instance."""
        return ImpactAnalyzer(sample_ai_client, logger=None)

    def test_analyze_code_impact(self, impact_analyzer):
        """Given: Diff information
        When: analyze() is called
        Then: Analyzes impact of changes
        """
        # Given
        diff = """
        Modified: core/auth.py (50 lines changed)
        Added: utils/new_feature.py (100 lines)
        Deleted: legacy/old_code.py (75 lines)
        """

        # When
        result = impact_analyzer.analyze(diff=diff)

        # Then
        assert result is not None
        assert "impact" in result

    def test_assess_risk_level(self, impact_analyzer):
        """Given: Diff information
        When: analyze() is called
        Then: Assesses risk level
        """
        # Given
        diff = """
        Modified critical security code
        """
        code = """
        def check_password(password):
            # Critical security check
            pass
        """

        # When
        result = impact_analyzer.analyze(diff=diff, code=code, language="python")

        # Then
        assert result is not None

    def test_identify_affected_areas(self, impact_analyzer):
        """Given: Diff information
        When: analyze() is called
        Then: Identifies affected areas
        """
        # Given
        diff = """
        Changed API endpoint /users
        Updated database schema
        Modified frontend components
        """

        # When
        result = impact_analyzer.analyze(diff=diff)

        # Then
        assert result is not None


class TestDebtAnalyzer:
    """Test DebtAnalyzer."""

    @pytest.fixture
    def debt_analyzer(self, sample_ai_client):
        """Create DebtAnalyzer instance."""
        return DebtAnalyzer(sample_ai_client, logger=None)

    def test_identify_technical_debt(self, debt_analyzer):
        """Given: Code and commit history
        When: analyze() is called
        Then: Identifies technical debt
        """
        # Given
        code = """
        # TODO: Fix this later
        def hacky_function():
            pass

        # FIXME: This is temporary
        class TemporaryWorkaround:
            pass
        """

        # When
        result = debt_analyzer.analyze(code=code, language="python")

        # Then
        assert result is not None
        assert "debt" in result

    def test_categorize_debt_types(self, debt_analyzer):
        """Given: Code with various issues
        When: analyze() is called
        Then: Categorizes debt types
        """
        # Given
        code = """
        # Complex function (complexity debt)
        def complex_function(a, b, c, d, e, f, g):
            pass

        # Duplicate code (duplication debt)
        def func1(): return "test"
        def func2(): return "test"
        """

        # When
        result = debt_analyzer.analyze(code=code, language="python")

        # Then
        assert result is not None

    def test_suggest_debt_remediation(self, debt_analyzer):
        """Given: Code with debt
        When: analyze() is called
        Then: Suggests remediation
        """
        # Given
        code = """
        def legacy_code():
            # Old implementation
            pass
        """

        # When
        result = debt_analyzer.analyze(code=code, language="python")

        # Then
        assert result is not None


class TestEvolutionAnalyzer:
    """Test EvolutionAnalyzer main class."""

    @pytest.fixture
    def evolution_analyzer(self, sample_ai_client):
        """Create EvolutionAnalyzer instance."""
        return EvolutionAnalyzer(
            ai_client=sample_ai_client,
            config={"analyzers": ["timeline", "impact", "debt"]},
            logger=None
        )

    def test_analyze_all_evolution_dimensions(self, evolution_analyzer):
        """Given: EvolutionAnalyzer with all analyzers
        When: analyze_all() is called
        Then: Returns combined analysis
        """
        # Given
        commits = "Commit history"
        diff = "Code changes"
        code = "Sample code"

        # When
        result = evolution_analyzer.analyze_all(
            commits=commits,
            diff=diff,
            code=code,
            language="python"
        )

        # Then
        assert result is not None

    def test_analyze_selected_dimensions(self, evolution_analyzer):
        """Given: EvolutionAnalyzer
        When: analyze() is called with specific dimensions
        Then: Analyzes only specified dimensions
        """
        # Given
        commits = "Commit history"

        # When
        result = evolution_analyzer.analyze(
            commits=commits,
            dimensions=["timeline", "debt"]
        )

        # Then
        assert result is not None


# Fixtures
@pytest.fixture
def sample_ai_client():
    """Create mock AI client."""
    client = Mock()
    client.complete_json.return_value = {"test": "result"}
    return client
