"""Tests for DocLLM parser."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from git_deep_analyzer.integrations.docs.doc_llm_parser import DocLLMParser
from git_deep_analyzer.integrations.docs.models import Document, DocumentType


class TestDocLLMParser:
    """Test DocLLMParser class."""

    @pytest.fixture
    def ai_client(self):
        """Mock AI client."""
        return Mock()

    @pytest.fixture
    def logger(self):
        """Mock logger."""
        return Mock()

    @pytest.fixture
    def doc_llm_parser(self, ai_client, logger):
        """Create DocLLMParser instance."""
        return DocLLMParser(ai_client, logger)

    @pytest.fixture
    def sample_document(self):
        """Sample document for testing."""
        return Document(
            id="doc-1",
            title="User Authentication Requirements",
            content="""
            The system shall provide user authentication with the following requirements:
            1. Users can login with email and password
            2. Passwords must be at least 8 characters
            3. Users can reset password via email
            4. Session timeout after 30 minutes of inactivity

            Business Goals:
            - Secure access to system
            - User-friendly authentication process
            - Compliance with security standards
            """,
            type=DocumentType.REQUIREMENT,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 2),
            author="testuser",
            author_email="test@example.com"
        )

    def test_init(self, ai_client, logger):
        """Given: AI client and logger
        When: DocLLMParser is created
        Then: Instance is initialized correctly
        """
        parser = DocLLMParser(ai_client, logger)
        assert parser.ai_client is ai_client
        assert parser.logger is logger
        assert parser.analyzers is not None

    def test_parse_document_success(self, doc_llm_parser, sample_document):
        """Given: DocLLM parser and document
        When: parse_document() is called
        Then: Returns document with LLM analysis results
        """
        # Given
        mock_requirements = {
            "requirements": [
                {"id": "R1", "description": "Email login", "priority": "high"},
                {"id": "R2", "description": "Password length", "priority": "medium"}
            ],
            "acceptance_criteria": [],
            "dependencies": [],
            "ambiguities": []
        }
        mock_goals = {
            "goals": [
                {"name": "Secure access", "priority": "critical"},
                {"name": "User-friendly", "priority": "medium"}
            ],
            "goal_feature_mapping": {},
            "metrics": [],
            "gaps": []
        }
        mock_design = {
            "design_elements": [],
            "patterns": [],
            "architecture": {}
        }

        doc_llm_parser.ai_client.complete_json.side_effect = [
            mock_requirements,
            mock_goals,
            mock_design
        ]

        # When
        result = doc_llm_parser.parse_document(sample_document)

        # Then
        assert isinstance(result, Document)
        assert result.id == sample_document.id
        assert "requirements_analysis" in result.requirements
        assert "goals_analysis" in result.requirements
        assert "design_analysis" in result.requirements

    def test_parse_document_with_code_alignment(self, doc_llm_parser, sample_document):
        """Given: DocLLM parser with code
        When: parse_document_with_alignment() is called
        Then: Returns document with alignment analysis
        """
        # Given
        code = "def login(email, password): pass"
        mock_alignment = {
            "implemented": ["R1"],
            "partial": [],
            "missing": ["R2"],
            "extra": [],
            "coverage_score": 50
        }

        doc_llm_parser.ai_client.complete_json.return_value = mock_alignment

        # When
        result = doc_llm_parser.parse_document_with_alignment(
            sample_document,
            code=code,
            language="python"
        )

        # Then
        assert "alignment_analysis" in result.requirements
        assert result.requirements["alignment_analysis"]["coverage_score"] == 50

    def test_parse_document_with_compliance(self, doc_llm_parser, sample_document):
        """Given: DocLLM parser with specification
        When: parse_document_with_compliance() is called
        Then: Returns document with compliance analysis
        """
        # Given
        spec = "API specification v1.0"
        code = "def api(): pass"
        mock_compliance = {
            "compliant": True,
            "violations": [],
            "compliant_items": ["endpoint"],
            "compliance_score": 100,
            "remediation": []
        }

        doc_llm_parser.ai_client.complete_json.return_value = mock_compliance

        # When
        result = doc_llm_parser.parse_document_with_compliance(
            sample_document,
            specification=spec,
            code=code,
            language="python"
        )

        # Then
        assert "compliance_analysis" in result.requirements
        assert result.requirements["compliance_analysis"]["compliant"] is True

    def test_extract_requirements(self, doc_llm_parser):
        """Given: DocLLM parser
        When: extract_requirements() is called
        Then: Returns extracted requirements
        """
        # Given
        doc_text = "The system must allow users to login"
        mock_requirements = {
            "requirements": [
                {"id": "R1", "description": "User login", "priority": "high"}
            ]
        }
        doc_llm_parser.ai_client.complete_json.return_value = mock_requirements

        # When
        result = doc_llm_parser.extract_requirements(doc_text)

        # Then
        assert "requirements" in result
        assert len(result["requirements"]) == 1

    def test_identify_goals(self, doc_llm_parser):
        """Given: DocLLM parser
        When: identify_goals() is called
        Then: Returns identified business goals
        """
        # Given
        doc_text = "Goal: Secure user access"
        mock_goals = {
            "goals": [
                {"name": "Secure user access", "priority": "high"}
            ]
        }
        doc_llm_parser.ai_client.complete_json.return_value = mock_goals

        # When
        result = doc_llm_parser.identify_goals(doc_text)

        # Then
        assert "goals" in result
        assert len(result["goals"]) == 1

    def test_analyze_design_elements(self, doc_llm_parser):
        """Given: DocLLM parser
        When: analyze_design_elements() is called
        Then: Returns design elements analysis
        """
        # Given
        doc_text = "System uses MVC architecture"
        mock_design = {
            "design_elements": ["MVC pattern"],
            "patterns": ["Model-View-Controller"],
            "architecture": {"style": "MVC"}
        }
        doc_llm_parser.ai_client.complete_json.return_value = mock_design

        # When
        result = doc_llm_parser.analyze_design_elements(doc_text)

        # Then
        assert "design_elements" in result
        assert "patterns" in result

    def test_analyze_alignment(self, doc_llm_parser):
        """Given: DocLLM parser
        When: analyze_alignment() is called
        Then: Returns alignment analysis
        """
        # Given
        requirements = "Users can login"
        code = "def login(): pass"
        mock_alignment = {
            "implemented": ["login"],
            "coverage_score": 100
        }
        doc_llm_parser.ai_client.complete_json.return_value = mock_alignment

        # When
        result = doc_llm_parser.analyze_alignment(
            requirements=requirements,
            code=code,
            language="python"
        )

        # Then
        assert "implemented" in result
        assert result["coverage_score"] == 100

    def test_analyze_compliance(self, doc_llm_parser):
        """Given: DocLLM parser
        When: analyze_compliance() is called
        Then: Returns compliance analysis
        """
        # Given
        specification = "API must return JSON"
        code = "def api(): return {}"
        mock_compliance = {
            "compliant": True,
            "compliance_score": 100
        }
        doc_llm_parser.ai_client.complete_json.return_value = mock_compliance

        # When
        result = doc_llm_parser.analyze_compliance(
            specification=specification,
            code=code,
            language="python"
        )

        # Then
        assert "compliant" in result
        assert result["compliance_score"] == 100

    def test_parse_document_ai_error(self, doc_llm_parser, sample_document):
        """Given: DocLLM parser with AI error
        When: parse_document() is called
        Then: Handles error gracefully
        """
        # Given
        doc_llm_parser.ai_client.complete_json.side_effect = Exception("AI error")

        # When
        result = doc_llm_parser.parse_document(sample_document)

        # Then
        assert isinstance(result, Document)
        assert "requirements_analysis" in result.requirements
        assert "error" in result.requirements["requirements_analysis"]

    def test_parse_document_partial_failure(self, doc_llm_parser, sample_document):
        """Given: DocLLM parser with partial success
        When: parse_document() is called
        Then: Returns document with partial results
        """
        # Given
        mock_requirements = {"requirements": [{"id": "R1", "description": "Test"}]}
        doc_llm_parser.ai_client.complete_json.side_effect = [
            mock_requirements,
            Exception("Goals error"),
            Exception("Design error")
        ]

        # When
        result = doc_llm_parser.parse_document(sample_document)

        # Then
        assert "requirements_analysis" in result.requirements
        assert "goals_analysis" in result.requirements
        assert "error" in result.requirements["goals_analysis"]
        assert "error" in result.requirements["design_analysis"]
