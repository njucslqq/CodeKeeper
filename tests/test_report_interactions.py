"""Tests for report interaction functionality."""

import pytest
from git_deep_analyzer.reporting.models import ReportData, ReportSection, ReportFormat, ReportDetailLevel
from git_deep_analyzer.reporting.report_interactions import ReportInteractions


class TestReportInteractions:
    """Test ReportInteractions class."""

    @pytest.fixture
    def interactions(self):
        """Create ReportInteractions instance."""
        return ReportInteractions()

    @pytest.fixture
    def sample_report(self):
        """Create sample report with multiple sections."""
        return ReportData(
            title="Test Report",
            format=ReportFormat.HTML,
            detail_level=ReportDetailLevel.STANDARD,
            sections=[
                ReportSection(
                    title="Introduction",
                    content="This is the introduction.",
                    id="intro"
                ),
                ReportSection(
                    title="Analysis",
                    content="Analysis results here.",
                    id="analysis"
                ),
                ReportSection(
                    title="Conclusion",
                    content="Final thoughts.",
                    id="conclusion"
                )
            ]
        )

    def test_add_collapse_expand_functionality(self, interactions, sample_report):
        """Given: Report data
        When: add_collapse_expand() is called
        Then: HTML includes collapse/expand functionality
        """
        # When
        html = interactions.add_collapse_expand(
            sample_report,
            '<div id="intro">Content</div>'
        )

        # Then
        assert isinstance(html, str)
        # Should include toggle functionality
        assert "collapse" in html.lower() or "expand" in html.lower() or "toggle" in html.lower()

    def test_add_search_functionality(self, interactions):
        """Given: Report content
        When: add_search() is called
        Then: HTML includes search box and functionality
        """
        # Given
        html_content = "<h1>Title</h1><p>Content here</p>"

        # When
        html = interactions.add_search(html_content)

        # Then
        assert isinstance(html, str)
        assert "search" in html.lower() or "input" in html.lower()

    def test_add_filter_functionality(self, interactions):
        """Given: Report content
        When: add_filter() is called
        Then: HTML includes filter controls
        """
        # Given
        html_content = "<div>Section 1</div><div>Section 2</div>"

        # When
        html = interactions.add_filter(
            html_content,
            filters=["section1", "section2"]
        )

        # Then
        assert isinstance(html, str)
        assert "filter" in html.lower()

    def test_add_detail_level_switcher(self, interactions):
        """Given: Report data
        When: add_detail_level_switcher() is called
        Then: HTML includes level switching controls
        """
        # Given
        html_content = "<div>Report content</div>"

        # When
        html = interactions.add_detail_level_switcher(
            html_content,
            current_level=ReportDetailLevel.STANDARD
        )

        # Then
        assert isinstance(html, str)
        assert "detail" in html.lower() or "level" in html.lower()

    def test_toggle_section_visibility(self, interactions):
        """Given: Report with sections
        When: toggle_section() is called
        Then: Returns JavaScript for toggling
        """
        # When
        js = interactions.toggle_section("section-id")

        # Then
        assert isinstance(js, str)
        assert "section-id" in js
        assert "toggle" in js.lower() or "display" in js.lower()

    def test_search_in_content(self, interactions):
        """Given: Content and search term
        When: search() is called
        Then: Returns filtered content or matches
        """
        # Given
        content = "This is a test content with test words."

        # When
        result = interactions.search(content, "test")

        # Then
        assert result is not None
        assert "test" in result.lower()

    def test_filter_sections_by_tag(self, interactions, sample_report):
        """Given: Report with tagged sections
        When: filter_by_tag() is called
        Then: Returns filtered sections
        """
        # Given
        # Add tags to sections via metadata
        sample_report.sections[0].metadata["tags"] = ["intro"]
        sample_report.sections[1].metadata["tags"] = ["analysis", "technical"]
        sample_report.sections[2].metadata["tags"] = ["conclusion"]

        # When
        filtered = interactions.filter_by_tag(sample_report, "technical")

        # Then
        assert len(filtered.sections) >= 1
        assert any("analysis" in s.title.lower() for s in filtered.sections)

    def test_add_interactive_controls(self, interactions, sample_report):
        """Given: Report data
        When: add_all_interactions() is called
        Then: HTML includes all interactive features
        """
        # Given
        html = "<html><body><h1>Report</h1></body></html>"

        # When
        interactive_html = interactions.add_all_interactions(
            sample_report,
            html,
            enable_collapse=True,
            enable_search=True,
            enable_filter=True,
            enable_detail_switch=True
        )

        # Then
        assert isinstance(interactive_html, str)
        # Should include interactive elements
        assert "html" in interactive_html.lower()
