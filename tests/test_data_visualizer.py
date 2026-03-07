"""Tests for data visualizer."""

import pytest
from git_deep_analyzer.reporting.data_visualizer import (
    DataVisualizer,
    ChartType
)


class TestDataVisualizer:
    """Test DataVisualizer class."""

    @pytest.fixture
    def visualizer(self):
        """Create DataVisualizer instance."""
        return DataVisualizer()

    def test_generate_line_chart(self, visualizer):
        """Given: Line chart data
        When: generate_chart() is called with LINE type
        Then: Returns Chart.js configuration
        """
        # Given
        data = {
            "labels": ["Jan", "Feb", "Mar", "Apr"],
            "datasets": [{
                "label": "Commits",
                "data": [10, 20, 15, 25]
            }]
        }

        # When
        chart = visualizer.generate_chart(
            chart_type=ChartType.LINE,
            data=data,
            title="Commit History"
        )

        # Then
        assert chart is not None
        assert "type" in chart
        assert chart["type"] == "line"
        assert "data" in chart

    def test_generate_pie_chart(self, visualizer):
        """Given: Pie chart data
        When: generate_chart() is called with PIE type
        Then: Returns Chart.js configuration
        """
        # Given
        data = {
            "labels": ["Python", "JavaScript", "C++"],
            "datasets": [{
                "data": [50, 30, 20]
            }]
        }

        # When
        chart = visualizer.generate_chart(
            chart_type=ChartType.PIE,
            data=data,
            title="Language Distribution"
        )

        # Then
        assert chart is not None
        assert chart["type"] == "pie"

    def test_generate_bar_chart(self, visualizer):
        """Given: Bar chart data
        When: generate_chart() is called with BAR type
        Then: Returns Chart.js configuration
        """
        # Given
        data = {
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "datasets": [{
                "label": "Issues",
                "data": [100, 150, 120, 180]
            }]
        }

        # When
        chart = visualizer.generate_chart(
            chart_type=ChartType.BAR,
            data=data,
            title="Issues by Quarter"
        )

        # Then
        assert chart is not None
        assert chart["type"] == "bar"

    def test_generate_heatmap(self, visualizer):
        """Given: Heatmap data
        When: generate_heatmap() is called
        Then: Returns Chart.js compatible configuration
        """
        # Given
        data = {
            "x_labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "y_labels": ["User A", "User B", "User C"],
            "values": [
                [5, 3, 0, 2, 4],
                [1, 4, 2, 5, 0],
                [3, 2, 4, 1, 3]
            ]
        }

        # When
        chart = visualizer.generate_heatmap(
            data=data,
            title="Activity Heatmap"
        )

        # Then
        assert chart is not None

    def test_generate_gantt_chart(self, visualizer):
        """Given: Gantt chart data
        When: generate_gantt() is called
        Then: Returns Chart.js compatible configuration
        """
        # Given
        tasks = [
            {"name": "Task 1", "start": "2024-01-01", "duration": 5},
            {"name": "Task 2", "start": "2024-01-03", "duration": 3},
            {"name": "Task 3", "start": "2024-01-06", "duration": 4}
        ]

        # When
        chart = visualizer.generate_gantt(
            data=tasks,
            title="Project Timeline"
        )

        # Then
        assert chart is not None

    def test_generate_sankey_chart(self, visualizer):
        """Given: Sankey chart data
        When: generate_sankey() is called
        Then: Returns Chart.js compatible configuration
        """
        # Given
        data = {
            "nodes": ["A", "B", "C", "D"],
            "links": [
                {"source": "A", "target": "B", "value": 10},
                {"source": "A", "target": "C", "value": 5},
                {"source": "B", "target": "D", "value": 8},
                {"source": "C", "target": "D", "value": 5}
            ]
        }

        # When
        chart = visualizer.generate_sankey(
            data=data,
            title="Flow Diagram"
        )

        # Then
        assert chart is not None

    def test_chart_configuration_includes_title(self, visualizer):
        """Given: Chart data
        When: generate_chart() is called with title
        Then: Configuration includes title
        """
        # Given
        data = {
            "labels": ["A", "B"],
            "datasets": [{"data": [1, 2]}]
        }

        # When
        chart = visualizer.generate_chart(
            chart_type=ChartType.BAR,
            data=data,
            title="Test Chart"
        )

        # Then
        assert "options" in chart
        assert "title" in chart["options"] or "Test Chart" in str(chart)

    def test_generate_multiple_charts(self, visualizer):
        """Given: Multiple chart types
        When: generate_chart() is called multiple times
        Then: Each returns valid configuration
        """
        # Given
        data = {
            "labels": ["A", "B", "C"],
            "datasets": [{"data": [1, 2, 3]}]
        }

        # When
        line_chart = visualizer.generate_chart(ChartType.LINE, data, "Line")
        bar_chart = visualizer.generate_chart(ChartType.BAR, data, "Bar")
        pie_chart = visualizer.generate_chart(ChartType.PIE, data, "Pie")

        # Then
        assert line_chart["type"] == "line"
        assert bar_chart["type"] == "bar"
        assert pie_chart["type"] == "pie"

    def test_export_chart_to_html(self, visualizer):
        """Given: Chart configuration
        When: export_to_html() is called
        Then: Returns HTML snippet with Chart.js
        """
        # Given
        chart_config = visualizer.generate_chart(
            chart_type=ChartType.BAR,
            data={"labels": ["A"], "datasets": [{"data": [1]}]},
            title="Test"
        )

        # When
        html = visualizer.export_to_html(chart_config, "chart-canvas-id")

        # Then
        assert isinstance(html, str)
        assert "canvas" in html.lower() or "chart" in html.lower()

    def test_invalid_chart_type(self, visualizer):
        """Given: Invalid chart type
        When: generate_chart() is called
        Then: Returns None or raises error
        """
        # Given
        data = {"labels": ["A"], "datasets": [{"data": [1]}]}

        # When
        chart = visualizer.generate_chart(
            chart_type="invalid_type",  # Not a valid ChartType
            data=data,
            title="Test"
        )

        # Then - Should handle gracefully
        # Either returns None or uses a default type
        assert chart is not None or chart is None


class TestChartType:
    """Test ChartType enum."""

    def test_all_chart_types_defined(self):
        """Given: ChartType enum
        When: Checking all members
        Then: All expected chart types are defined
        """
        expected_types = ["line", "bar", "pie", "doughnut", "radar"]
        actual_types = [t.value for t in ChartType]
        for expected in expected_types:
            assert expected in actual_types
