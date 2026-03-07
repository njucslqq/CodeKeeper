"""Tests for business dimension analyzers."""

import pytest
from unittest.mock import Mock
from git_deep_analyzer.ai.business_analyzer import (
    BusinessAnalyzer,
    RequirementsAnalyzer,
    AlignmentAnalyzer,
    ComplianceAnalyzer,
    GoalsAnalyzer
)


class TestRequirementsAnalyzer:
    """Test RequirementsAnalyzer."""

    @pytest.fixture
    def requirements_analyzer(self, sample_ai_client):
        """Create RequirementsAnalyzer instance."""
        return RequirementsAnalyzer(sample_ai_client, logger=None)

    def test_extract_requirements(self, requirements_analyzer):
        """Given: Requirements document
        When: analyze() is called
        Then: Extracts requirements
        """
        # Given
        doc = """
        Requirements:
        1. User can login with email and password
        2. User can reset password
        3. System must respond within 2 seconds
        """

        # When
        result = requirements_analyzer.analyze(doc)

        # Then
        assert result is not None
        assert "requirements" in result

    def test_prioritize_requirements(self, requirements_analyzer):
        """Given: Requirements document
        When: analyze() is called
        Then: Prioritizes requirements
        """
        # Given
        doc = """
        Priority 1: User authentication
        Priority 2: User profile
        Priority 3: User settings
        """

        # When
        result = requirements_analyzer.analyze(doc)

        # Then
        assert result is not None

    def test_identify_acceptance_criteria(self, requirements_analyzer):
        """Given: Requirements with acceptance criteria
        When: analyze() is called
        Then: Extracts acceptance criteria
        """
        # Given
        doc = """
        Feature: User login
        Acceptance criteria:
        - User can login with valid credentials
        - User cannot login with invalid credentials
        - Error messages are clear
        """

        # When
        result = requirements_analyzer.analyze(doc)

        # Then
        assert result is not None


class TestAlignmentAnalyzer:
    """Test AlignmentAnalyzer."""

    @pytest.fixture
    def alignment_analyzer(self, sample_ai_client):
        """Create AlignmentAnalyzer instance."""
        return AlignmentAnalyzer(sample_ai_client, logger=None)

    def test_match_requirements_to_implementation(self, alignment_analyzer):
        """Given: Requirements and code
        When: analyze() is called
        Then: Matches requirements to implementation
        """
        # Given
        requirements = "User must be able to login"
        code = """
        def login(username, password):
            # Implementation here
            pass
        """

        # When
        result = alignment_analyzer.analyze(
            requirements=requirements,
            code=code,
            language="python"
        )

        # Then
        assert result is not None
        assert "alignment" in result

    def test_identify_gaps(self, alignment_analyzer):
        """Given: Requirements and incomplete code
        When: analyze() is called
        Then: Identifies gaps
        """
        # Given
        requirements = "User must be able to login and logout"
        code = """
        def login(username, password):
            pass
        # Missing logout
        """

        # When
        result = alignment_analyzer.analyze(
            requirements=requirements,
            code=code,
            language="python"
        )

        # Then
        assert result is not None

    def test_score_implementation_coverage(self, alignment_analyzer):
        """Given: Requirements and code
        When: analyze() is called
        Then: Scores implementation coverage
        """
        # Given
        requirements = "Login and logout functionality"
        code = """
        def login(u, p): pass
        def logout(u): pass
        """

        # When
        result = alignment_analyzer.analyze(
            requirements=requirements,
            code=code,
            language="python"
        )

        # Then
        assert result is not None


class TestComplianceAnalyzer:
    """Test ComplianceAnalyzer."""

    @pytest.fixture
    def compliance_analyzer(self, sample_ai_client):
        """Create ComplianceAnalyzer instance."""
        return ComplianceAnalyzer(sample_ai_client, logger=None)

    def test_check_spec_compliance(self, compliance_analyzer):
        """Given: Specification and code
        When: analyze() is called
        Then: Checks compliance
        """
        # Given
        spec = """
        API Specification:
        - Endpoint: /api/users
        - Method: GET
        - Returns: JSON array of users
        """
        code = """
        @app.route('/api/users', methods=['GET'])
        def get_users():
            return jsonify(users)
        """

        # When
        result = compliance_analyzer.analyze(
            specification=spec,
            code=code,
            language="python"
        )

        # Then
        assert result is not None
        assert "compliance" in result

    def test_identify_violations(self, compliance_analyzer):
        """Given: Specification and non-compliant code
        When: analyze() is called
        Then: Identifies violations
        """
        # Given
        spec = "Must return HTTP 200 for success"
        code = """
        return 201  # Wrong status code
        """

        # When
        result = compliance_analyzer.analyze(
            specification=spec,
            code=code,
            language="python"
        )

        # Then
        assert result is not None


class TestGoalsAnalyzer:
    """Test GoalsAnalyzer."""

    @pytest.fixture
    def goals_analyzer(self, sample_ai_client):
        """Create GoalsAnalyzer instance."""
        return GoalsAnalyzer(sample_ai_client, logger=None)

    def test_extract_business_goals(self, goals_analyzer):
        """Given: Business document
        When: analyze() is called
        Then: Extracts business goals
        """
        # Given
        doc = """
        Business Goals:
        - Increase user engagement by 20%
        - Reduce page load time
        - Improve customer satisfaction
        """

        # When
        result = goals_analyzer.analyze(doc)

        # Then
        assert result is not None
        assert "goals" in result

    def test_map_goals_to_features(self, goals_analyzer):
        """Given: Goals and feature list
        When: analyze() is called
        Then: Maps goals to features
        """
        # Given
        goals = "Reduce page load time"
        features = """
        - Caching
        - Image optimization
        - CDN integration
        """

        # When
        result = goals_analyzer.analyze(goals=goals, features=features)

        # Then
        assert result is not None


class TestBusinessAnalyzer:
    """Test BusinessAnalyzer main class."""

    @pytest.fixture
    def business_analyzer(self, sample_ai_client):
        """Create BusinessAnalyzer instance."""
        return BusinessAnalyzer(
            ai_client=sample_ai_client,
            config={"analyzers": ["requirements", "alignment", "compliance", "goals"]},
            logger=None
        )

    def test_analyze_all_business_dimensions(self, business_analyzer):
        """Given: BusinessAnalyzer with all analyzers
        When: analyze_all() is called
        Then: Returns combined analysis
        """
        # Given
        requirements = "User authentication system"
        code = "class Auth: pass"
        spec = "Auth specification"

        # When
        result = business_analyzer.analyze_all(
            requirements=requirements,
            code=code,
            language="python",
            specification=spec
        )

        # Then
        assert result is not None

    def test_analyze_selected_dimensions(self, business_analyzer):
        """Given: BusinessAnalyzer
        When: analyze() is called with specific dimensions
        Then: Analyzes only specified dimensions
        """
        # Given
        doc = "Requirements document"

        # When
        result = business_analyzer.analyze(
            doc,
            dimensions=["requirements", "goals"]
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
