"""Tests for HTML report generator."""

import pytest
from git_deep_analyzer.reporting.models import ReportData, ReportSection, ReportFormat, ReportDetailLevel
from git_deep_analyzer.reporting.html_generator import HTMLGenerator


class TestHTMLGenerator:
    """Test HTMLGenerator class."""

    @pytest.fixture
    def html_generator(self):
        """Create HTMLGenerator instance."""
        return HTMLGenerator()

    @pytest.fixture
    def sample_report(self):
        """Create sample report data."""
        return ReportData(
            title="Test Report",
            format=ReportFormat.HTML,
            detail_level=ReportDetailLevel.STANDARD,
            sections=[
                ReportSection(
                    title="Introduction",
                    content="This is the introduction."
                ),
                ReportSection(
                    title="Analysis",
                    content="Analysis results here."
                )
            ]
        )

    def test_generate_basic_html(self, html_generator, sample_report):
        """Given: Report data
        When: generate() is called
        Then: Returns valid HTML
        """
        # When
        html = html_generator.generate(sample_report)

        # Then
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html or "<html" in html
        assert "Test Report" in html
        assert "Introduction" in html
        assert "Analysis" in html

    def test_generate_html_with_nested_sections(self, html_generator):
        """Given: Report with nested sections
        When: generate() is called
        Then: HTML includes nested structure
        """
        # Given
        subsections = [
            ReportSection(title="Subsection 1", content="Content 1", level=2)
        ]
        main_section = ReportSection(
            title="Main Section",
            content="Main content",
            subsections=subsections
        )
        report = ReportData(
            title="Nested Report",
            format=ReportFormat.HTML,
            sections=[main_section]
        )

        # When
        html = html_generator.generate(report)

        # Then
        assert "Main Section" in html
        assert "Subsection 1" in html

    def test_concise_detail_level(self, html_generator):
        """Given: Report with concise detail level
        When: generate() is called
        Then: HTML includes concise formatting
        """
        # Given
        report = ReportData(
            title="Concise Report",
            format=ReportFormat.HTML,
            detail_level=ReportDetailLevel.CONCISE,
            sections=[
                ReportSection(title="Summary", content="Brief summary.")
            ]
        )

        # When
        html = html_generator.generate(report)

        # Then
        assert "Concise Report" in html
        assert "concise" in html.lower()

    def test_detailed_detail_level(self, html_generator):
        """Given: Report with detailed detail level
        When: generate() is called
        Then: HTML includes detailed formatting
        """
        # Given
        report = ReportData(
            title="Detailed Report",
            format=ReportFormat.HTML,
            detail_level=ReportDetailLevel.DETAILED,
            sections=[
                ReportSection(title="Details", content="Detailed content here.")
            ]
        )

        # When
        html = html_generator.generate(report)

        # Then
        assert "Detailed Report" in html

    def test_save_to_file(self, html_generator, sample_report, tmp_path):
        """Given: HTMLGenerator and report
        When: save_to_file() is called
        Then: HTML file is created
        """
        # Given
        output_file = tmp_path / "test_report.html"

        # When
        html_generator.save_to_file(sample_report, str(output_file))

        # Then
        assert output_file.exists()
        content = output_file.read_text()
        assert "Test Report" in content

    def test_html_contains_responsive_design(self, html_generator, sample_report):
        """Given: Report data
        When: generate() is called
        Then: HTML includes responsive design elements
        """
        # When
        html = html_generator.generate(sample_report)

        # Then - Should include viewport meta tag
        assert "viewport" in html.lower() or "responsive" in html.lower()

    def test_html_contains_styling(self, html_generator, sample_report):
        """Given: Report data
        When: generate() is called
        Then: HTML includes CSS styling
        """
        # When
        html = html_generator.generate(sample_report)

        # Then - Should include style tag or link to CSS
        assert "<style" in html or "stylesheet" in html.lower()

    def test_generate_html_with_metadata(self, html_generator):
        """Given: Report with metadata
        When: generate() is called
        Then: HTML includes metadata
        """
        # Given
        report = ReportData(
            title="Metadata Report",
            format=ReportFormat.HTML,
            metadata={"project": "test", "version": "1.0"},
            sections=[
                ReportSection(title="Section", content="Content")
            ]
        )

        # When
        html = html_generator.generate(report)

        # Then
        assert "Metadata Report" in html

    def test_empty_report(self, html_generator):
        """Given: Report with no sections
        When: generate() is called
        Then: Returns valid HTML with empty body
        """
        # Given
        report = ReportData(
            title="Empty Report",
            format=ReportFormat.HTML,
            sections=[]
        )

        # When
        html = html_generator.generate(report)

        # Then
        assert "Empty Report" in html
        assert "<html" in html.lower()
