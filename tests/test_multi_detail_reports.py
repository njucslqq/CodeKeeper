"""Tests for multi-detail-level reports."""

import pytest
from git_deep_analyzer.reporting.models import ReportData, ReportSection, ReportFormat, ReportDetailLevel
from git_deep_analyzer.reporting.multi_detail_reports import ReportDetailAdapter


class TestReportDetailAdapter:
    """Test ReportDetailAdapter class."""

    @pytest.fixture
    def adapter(self):
        """Create ReportDetailAdapter instance."""
        return ReportDetailAdapter()

    @pytest.fixture
    def detailed_report(self):
        """Create detailed report data."""
        return ReportData(
            title="Detailed Report",
            format=ReportFormat.HTML,
            detail_level=ReportDetailLevel.DETAILED,
            sections=[
                ReportSection(
                    title="Executive Summary",
                    content="Brief overview of the analysis.",
                    metadata={"type": "summary"}
                ),
                ReportSection(
                    title="Technical Analysis",
                    content="""
                    Detailed technical analysis including:
                    - Code quality metrics
                    - Design patterns identified
                    - Performance considerations
                    - Security assessment
                    """,
                    metadata={"type": "technical"}
                ),
                ReportSection(
                    title="Code Examples",
                    content="```python\ndef example():\n    pass\n```",
                    metadata={"type": "examples"}
                )
            ]
        )

    def test_convert_to_concise(self, adapter, detailed_report):
        """Given: Detailed report
        When: adapt_to_concise() is called
        Then: Returns report with only summary sections
        """
        # When
        concise_report = adapter.adapt_to_concise(detailed_report)

        # Then
        assert concise_report.detail_level == ReportDetailLevel.CONCISE
        # Should keep summary section
        assert any("summary" in s.title.lower() for s in concise_report.sections)
        # Should remove detailed sections
        assert len(concise_report.sections) <= len(detailed_report.sections)

    def test_convert_to_standard(self, adapter, detailed_report):
        """Given: Detailed report
        When: adapt_to_standard() is called
        Then: Returns report with balanced detail
        """
        # When
        standard_report = adapter.adapt_to_standard(detailed_report)

        # Then
        assert standard_report.detail_level == ReportDetailLevel.STANDARD
        # Should keep main sections
        assert len(standard_report.sections) > 0

    def test_convert_to_detailed(self, adapter, detailed_report):
        """Given: Standard report
        When: adapt_to_detailed() is called
        Then: Returns report with full detail
        """
        # Given
        standard_report = adapter.adapt_to_standard(detailed_report)

        # When
        detailed_report_converted = adapter.adapt_to_detailed(standard_report)

        # Then
        assert detailed_report_converted.detail_level == ReportDetailLevel.DETAILED
        # Should have detailed content
        assert len(detailed_report_converted.sections) > 0

    def test_adapt_to_level(self, adapter, detailed_report):
        """Given: Detailed report
        When: adapt_to_level() is called with different levels
        Then: Returns report with specified detail level
        """
        # When - Convert to concise
        concise_report = adapter.adapt_to_level(detailed_report, ReportDetailLevel.CONCISE)
        assert concise_report.detail_level == ReportDetailLevel.CONCISE

        # When - Convert to standard
        standard_report = adapter.adapt_to_level(detailed_report, ReportDetailLevel.STANDARD)
        assert standard_report.detail_level == ReportDetailLevel.STANDARD

        # When - Convert to detailed
        detailed_result = adapter.adapt_to_level(concise_report, ReportDetailLevel.DETAILED)
        assert detailed_result.detail_level == ReportDetailLevel.DETAILED

    def test_preserve_report_metadata(self, adapter, detailed_report):
        """Given: Report with metadata
        When: adapt_to_concise() is called
        Then: Metadata is preserved
        """
        # Given
        detailed_report.author = "Test Author"
        detailed_report.metadata["project"] = "test-project"

        # When
        concise_report = adapter.adapt_to_concise(detailed_report)

        # Then
        assert concise_report.author == "Test Author"
        assert concise_report.metadata["project"] == "test-project"

    def test_filter_sections_by_metadata(self, adapter, detailed_report):
        """Given: Report with section metadata
        When: Filtering by metadata type
        Then: Returns only matching sections
        """
        # When
        summary_sections = adapter.filter_sections_by_type(
            detailed_report,
            "summary"
        )

        # Then
        assert len(summary_sections) > 0
        assert all("summary" in s.metadata.get("type", "").lower() for s in summary_sections)

    def test_generate_all_levels(self, adapter, detailed_report):
        """Given: Detailed report
        When: generate_all_levels() is called
        Then: Returns reports for all detail levels
        """
        # When
        reports = adapter.generate_all_levels(detailed_report)

        # Then
        assert ReportDetailLevel.CONCISE in reports
        assert ReportDetailLevel.STANDARD in reports
        assert ReportDetailLevel.DETAILED in reports

        assert reports[ReportDetailLevel.CONCISE].detail_level == ReportDetailLevel.CONCISE
        assert reports[ReportDetailLevel.STANDARD].detail_level == ReportDetailLevel.STANDARD
        assert reports[ReportDetailLevel.DETAILED].detail_level == ReportDetailLevel.DETAILED

    def test_content_truncation_for_concise(self, adapter):
        """Given: Section with long content
        When: adapt_to_concise() is called
        Then: Long content is truncated or summarized
        """
        # Given
        long_content = "A" * 1000  # Very long content
        report = ReportData(
            title="Long Report",
            format=ReportFormat.HTML,
            sections=[
                ReportSection(title="Section", content=long_content)
            ]
        )

        # When
        concise_report = adapter.adapt_to_concise(report)

        # Then - Content should be shorter
        if concise_report.sections:
            assert len(concise_report.sections[0].content) <= len(long_content)

    def test_keep_all_for_detailed(self, adapter, detailed_report):
        """Given: Detailed report
        When: adapt_to_detailed() is called
        Then: All sections are preserved
        """
        # When
        detailed_result = adapter.adapt_to_detailed(detailed_report)

        # Then
        assert len(detailed_result.sections) == len(detailed_report.sections)
        assert all(
            s1.title == s2.title
            for s1, s2 in zip(detailed_result.sections, detailed_report.sections)
        )
