"""Tests for Markdown report generator."""

import pytest
from git_deep_analyzer.reporting.models import ReportData, ReportSection, ReportFormat, ReportDetailLevel
from git_deep_analyzer.reporting.markdown_generator import MarkdownGenerator


class TestMarkdownGenerator:
    """Test MarkdownGenerator class."""

    @pytest.fixture
    def markdown_generator(self):
        """Create MarkdownGenerator instance."""
        return MarkdownGenerator()

    @pytest.fixture
    def sample_report(self):
        """Create sample report data."""
        return ReportData(
            title="Test Report",
            format=ReportFormat.MARKDOWN,
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

    def test_generate_basic_markdown(self, markdown_generator, sample_report):
        """Given: Report data
        When: generate() is called
        Then: Returns valid Markdown
        """
        # When
        markdown = markdown_generator.generate(sample_report)

        # Then
        assert isinstance(markdown, str)
        assert "# Test Report" in markdown or "## Test Report" in markdown
        assert "Introduction" in markdown
        assert "Analysis" in markdown

    def test_generate_markdown_with_nested_sections(self, markdown_generator):
        """Given: Report with nested sections
        When: generate() is called
        Then: Markdown includes nested structure
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
            format=ReportFormat.MARKDOWN,
            sections=[main_section]
        )

        # When
        markdown = markdown_generator.generate(report)

        # Then
        assert "Main Section" in markdown
        assert "Subsection 1" in markdown

    def test_heading_levels_correct(self, markdown_generator, sample_report):
        """Given: Report with sections
        When: generate() is called
        Then: Headings have correct Markdown levels
        """
        # When
        markdown = markdown_generator.generate(sample_report)

        # Then - Should have #, ##, etc.
        assert "#" in markdown

    def test_concise_detail_level(self, markdown_generator):
        """Given: Report with concise detail level
        When: generate() is called
        Then: Markdown is concise
        """
        # Given
        report = ReportData(
            title="Concise Report",
            format=ReportFormat.MARKDOWN,
            detail_level=ReportDetailLevel.CONCISE,
            sections=[
                ReportSection(title="Summary", content="Brief summary.")
            ]
        )

        # When
        markdown = markdown_generator.generate(report)

        # Then
        assert "Concise Report" in markdown

    def test_detailed_detail_level(self, markdown_generator):
        """Given: Report with detailed detail level
        When: generate() is called
        Then: Markdown includes detailed content
        """
        # Given
        report = ReportData(
            title="Detailed Report",
            format=ReportFormat.MARKDOWN,
            detail_level=ReportDetailLevel.DETAILED,
            sections=[
                ReportSection(title="Details", content="Detailed content here.")
            ]
        )

        # When
        markdown = markdown_generator.generate(report)

        # Then
        assert "Detailed Report" in markdown

    def test_save_to_file(self, markdown_generator, sample_report, tmp_path):
        """Given: MarkdownGenerator and report
        When: save_to_file() is called
        Then: Markdown file is created
        """
        # Given
        output_file = tmp_path / "test_report.md"

        # When
        markdown_generator.save_to_file(sample_report, str(output_file))

        # Then
        assert output_file.exists()
        content = output_file.read_text()
        assert "Test Report" in content

    def test_markdown_includes_metadata(self, markdown_generator):
        """Given: Report with metadata
        When: generate() is called
        Then: Markdown includes metadata
        """
        # Given
        report = ReportData(
            title="Metadata Report",
            format=ReportFormat.MARKDOWN,
            author="Test Author",
            metadata={"project": "test", "version": "1.0"},
            sections=[
                ReportSection(title="Section", content="Content")
            ]
        )

        # When
        markdown = markdown_generator.generate(report)

        # Then
        assert "Metadata Report" in markdown
        assert "Test Author" in markdown

    def test_empty_report(self, markdown_generator):
        """Given: Report with no sections
        When: generate() is called
        Then: Returns valid Markdown with minimal content
        """
        # Given
        report = ReportData(
            title="Empty Report",
            format=ReportFormat.MARKDOWN,
            sections=[]
        )

        # When
        markdown = markdown_generator.generate(report)

        # Then
        assert "Empty Report" in markdown

    def test_flat_structure(self, markdown_generator):
        """Given: Report with multiple sections
        When: generate() is called
        Then: Sections are in flat structure (not nested)
        """
        # Given
        report = ReportData(
            title="Flat Report",
            format=ReportFormat.MARKDOWN,
            sections=[
                ReportSection(title="Section 1", content="Content 1", level=1),
                ReportSection(title="Section 2", content="Content 2", level=2),
            ]
        )

        # When
        markdown = markdown_generator.generate(report)

        # Then
        assert "Section 1" in markdown
        assert "Section 2" in markdown

    def test_markdown_code_blocks(self, markdown_generator):
        """Given: Report with code content
        When: generate() is called
        Then: Code is formatted correctly
        """
        # Given
        report = ReportData(
            title="Code Report",
            format=ReportFormat.MARKDOWN,
            sections=[
                ReportSection(
                    title="Code Section",
                    content="```python\ndef hello():\n    print('Hello')\n```"
                )
            ]
        )

        # When
        markdown = markdown_generator.generate(report)

        # Then
        assert "```" in markdown
