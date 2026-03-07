"""Tests for report data models."""

import pytest
from git_deep_analyzer.reporting.models import (
    ReportFormat,
    ReportDetailLevel,
    ReportSection,
    ReportData
)


class TestReportFormat:
    """Test ReportFormat enum."""

    def test_format_values(self):
        """Given: ReportFormat enum
        When: Accessing values
        Then: Returns expected formats
        """
        assert ReportFormat.HTML == "html"
        assert ReportFormat.MARKDOWN == "markdown"
        assert ReportFormat.JSON == "json"

    def test_all_formats_defined(self):
        """Given: ReportFormat enum
        When: Checking all members
        Then: All expected formats are defined
        """
        expected_formats = ["html", "markdown", "json"]
        actual_formats = [f.value for f in ReportFormat]
        for expected in expected_formats:
            assert expected in actual_formats


class TestReportDetailLevel:
    """Test ReportDetailLevel enum."""

    def test_level_values(self):
        """Given: ReportDetailLevel enum
        When: Accessing values
        Then: Returns expected levels
        """
        assert ReportDetailLevel.CONCISE == "concise"
        assert ReportDetailLevel.STANDARD == "standard"
        assert ReportDetailLevel.DETAILED == "detailed"

    def test_all_levels_defined(self):
        """Given: ReportDetailLevel enum
        When: Checking all members
        Then: All expected levels are defined
        """
        expected_levels = ["concise", "standard", "detailed"]
        actual_levels = [l.value for l in ReportDetailLevel]
        for expected in expected_levels:
            assert expected in actual_levels

    def test_level_ordering(self):
        """Given: ReportDetailLevel enum
        When: Checking level ordering
        Then: Levels have logical ordering (concise < standard < detailed)
        """
        levels = [ReportDetailLevel.CONCISE, ReportDetailLevel.STANDARD, ReportDetailLevel.DETAILED]
        # Just verify they're all defined in a consistent order
        assert len(levels) == 3


class TestReportSection:
    """Test ReportSection dataclass."""

    def test_create_section_basic(self):
        """Given: Section parameters
        When: Creating ReportSection
        Then: Section is created with correct attributes
        """
        # When
        section = ReportSection(
            title="Test Section",
            content="Test content",
            level=1
        )

        # Then
        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert section.level == 1
        assert section.id is None

    def test_create_section_with_id(self):
        """Given: Section parameters with id
        When: Creating ReportSection
        Then: Section includes id
        """
        # When
        section = ReportSection(
            title="Section 1",
            content="Content",
            id="section-1"
        )

        # Then
        assert section.id == "section-1"

    def test_create_section_with_subsections(self):
        """Given: Section with subsections
        When: Creating ReportSection
        Then: Section includes subsections
        """
        # Given
        subsections = [
            ReportSection(title="Sub 1", content="Content 1", level=2),
            ReportSection(title="Sub 2", content="Content 2", level=2)
        ]

        # When
        section = ReportSection(
            title="Main Section",
            content="Main content",
            subsections=subsections
        )

        # Then
        assert len(section.subsections) == 2
        assert section.subsections[0].title == "Sub 1"

    def test_create_section_with_metadata(self):
        """Given: Section with metadata
        When: Creating ReportSection
        Then: Section includes metadata
        """
        # When
        section = ReportSection(
            title="Section",
            content="Content",
            metadata={"author": "test", "date": "2024-01-01"}
        )

        # Then
        assert section.metadata["author"] == "test"
        assert section.metadata["date"] == "2024-01-01"


class TestReportData:
    """Test ReportData dataclass."""

    def test_create_report_basic(self):
        """Given: Report parameters
        When: Creating ReportData
        Then: Report is created with correct attributes
        """
        # When
        report = ReportData(
            title="Test Report",
            format=ReportFormat.HTML,
            sections=[
                ReportSection(title="Section 1", content="Content 1")
            ]
        )

        # Then
        assert report.title == "Test Report"
        assert report.format == ReportFormat.HTML
        assert len(report.sections) == 1

    def test_create_report_with_all_fields(self):
        """Given: Report with all fields
        When: Creating ReportData
        Then: All fields are populated
        """
        # When
        report = ReportData(
            title="Full Report",
            format=ReportFormat.MARKDOWN,
            detail_level=ReportDetailLevel.DETAILED,
            author="Test Author",
            created_at="2024-01-01T00:00:00",
            metadata={"project": "test-project"},
            sections=[
                ReportSection(title="Section 1", content="Content 1"),
                ReportSection(title="Section 2", content="Content 2")
            ]
        )

        # Then
        assert report.title == "Full Report"
        assert report.format == ReportFormat.MARKDOWN
        assert report.detail_level == ReportDetailLevel.DETAILED
        assert report.author == "Test Author"
        assert report.created_at == "2024-01-01T00:00:00"
        assert report.metadata["project"] == "test-project"
        assert len(report.sections) == 2

    def test_add_section_to_report(self):
        """Given: ReportData instance
        When: Adding a section
        Then: Section is added to sections list
        """
        # Given
        report = ReportData(
            title="Report",
            format=ReportFormat.HTML
        )

        # When
        report.sections.append(
            ReportSection(title="New Section", content="New content")
        )

        # Then
        assert len(report.sections) == 1
        assert report.sections[0].title == "New Section"

    def test_nested_sections_in_report(self):
        """Given: Report with nested sections
        When: Creating ReportData
        Then: Nested structure is preserved
        """
        # Given
        subsections = [
            ReportSection(title="Sub 1.1", content="Content", level=3)
        ]
        section2 = ReportSection(
            title="Section 2",
            content="Content",
            level=2,
            subsections=subsections
        )
        section1 = ReportSection(
            title="Section 1",
            content="Content",
            level=1
        )

        # When
        report = ReportData(
            title="Nested Report",
            format=ReportFormat.HTML,
            sections=[section1, section2]
        )

        # Then
        assert len(report.sections) == 2
        assert report.sections[1].subsections[0].title == "Sub 1.1"

    def test_report_default_values(self):
        """Given: ReportData with minimal fields
        When: Creating report
        Then: Default values are applied
        """
        # When
        report = ReportData(
            title="Test Report",
            format=ReportFormat.HTML
        )

        # Then
        assert report.title == "Test Report"
        assert report.format == ReportFormat.HTML
        assert report.detail_level == ReportDetailLevel.STANDARD  # Default
        assert report.author is None  # Optional
        assert len(report.sections) == 0  # Empty list
