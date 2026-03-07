"""Data visualization with Chart.js."""

from enum import Enum
from typing import Dict, Any, List, Optional
import json


class ChartType(Enum):
    """Chart type options."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    RADAR = "radar"


class DataVisualizer:
    """Generate Chart.js configurations for various chart types."""

    def __init__(self):
        """Initialize data visualizer."""
        self.default_colors = [
            'rgba(54, 162, 235, 0.8)',   # Blue
            'rgba(255, 99, 132, 0.8)',   # Red
            'rgba(255, 206, 86, 0.8)',   # Yellow
            'rgba(75, 192, 192, 0.8)',   # Teal
            'rgba(153, 102, 255, 0.8)',  # Purple
            'rgba(255, 159, 64, 0.8)',   # Orange
        ]

    def generate_chart(
        self,
        chart_type: ChartType,
        data: Dict[str, Any],
        title: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate Chart.js configuration.

        Args:
            chart_type: Type of chart to generate
            data: Chart data (labels, datasets)
            title: Chart title
            options: Additional Chart.js options

        Returns:
            Chart.js configuration dictionary
        """
        config = {
            "type": chart_type.value,
            "data": data,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": title
                    }
                }
            }
        }

        # Add default colors if not provided
        if "datasets" in data:
            # Check if datasets is a list of dicts (LINE/BAR) or list of strings (other charts)
            datasets = data["datasets"]
            if datasets and isinstance(datasets[0], dict):
                # LINE or BAR chart with dataset dicts
                for i, dataset in enumerate(datasets):
                    if "backgroundColor" not in dataset:
                        color = self.default_colors[i % len(self.default_colors)]
                        dataset["backgroundColor"] = color
                    if "borderColor" not in dataset:
                        dataset["borderColor"] = str(color).replace('0.8', '1')

        # Merge custom options
        if options:
            config["options"].update(options)

        return config

    def generate_line_chart(
        self,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        title: str = "Line Chart"
    ) -> Dict[str, Any]:
        """
        Generate line chart configuration.

        Args:
            labels: X-axis labels
            datasets: Data datasets
            title: Chart title

        Returns:
            Chart.js configuration
        """
        data = {"labels": labels, "datasets": datasets}
        return self.generate_chart(ChartType.LINE, data, title)

    def generate_bar_chart(
        self,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        title: str = "Bar Chart"
    ) -> Dict[str, Any]:
        """
        Generate bar chart configuration.

        Args:
            labels: X-axis labels
            datasets: Data datasets
            title: Chart title

        Returns:
            Chart.js configuration
        """
        data = {"labels": labels, "datasets": datasets}
        return self.generate_chart(ChartType.BAR, data, title)

    def generate_pie_chart(
        self,
        labels: List[str],
        data: List[float],
        title: str = "Pie Chart"
    ) -> Dict[str, Any]:
        """
        Generate pie chart configuration.

        Args:
            labels: Segment labels
            data: Segment values
            title: Chart title

        Returns:
            Chart.js configuration
        """
        datasets = [{
            "data": data,
            "backgroundColor": self.default_colors[:len(data)]
        }]
        chart_data = {"labels": labels, "datasets": datasets}
        return self.generate_chart(ChartType.PIE, chart_data, title)

    def generate_heatmap(
        self,
        data: Dict[str, Any],
        title: str = "Heatmap"
    ) -> Dict[str, Any]:
        """
        Generate heatmap configuration.

        Note: Chart.js doesn't have built-in heatmap support.
        This returns a configuration compatible with chartjs-chart-matrix plugin.

        Args:
            data: Heatmap data with x_labels, y_labels, values
            title: Chart title

        Returns:
            Chart.js configuration
        """
        config = {
            "type": "matrix",
            "data": {
                "labels": data.get("x_labels", []),
                "datasets": [{
                    "label": title,
                    "data": self._format_heatmap_data(data),
                    "backgroundColor": self._format_heatmap_colors(data),
                    "borderColor": "white",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": title},
                    "tooltip": {
                        "callbacks": {
                            "title": lambda items: data["x_labels"][items[0]["x"]],
                            "label": lambda item: data["y_labels"][item["y"]] + ": " + str(item["raw"]["v"])
                        }
                    }
                },
                "scales": {
                    "x": {
                        "type": "category",
                        "labels": data.get("x_labels", []),
                        "offset": True
                    },
                    "y": {
                        "type": "category",
                        "labels": data.get("y_labels", []),
                        "offset": True
                    }
                }
            }
        }
        return config

    def _format_heatmap_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format heatmap data for Chart.js matrix."""
        values = data.get("values", [])
        formatted = []
        for y, row in enumerate(values):
            for x, value in enumerate(row):
                formatted.append({"x": x, "y": y, "v": value})
        return formatted

    def _format_heatmap_colors(self, data: Dict[str, Any]) -> List[str]:
        """Generate colors for heatmap based on values."""
        values = data.get("values", [])
        if not values:
            return []

        # Find min/max for color scaling
        all_values = [v for row in values for v in row]
        min_val = min(all_values)
        max_val = max(all_values)

        colors = []
        for row in values:
            for value in row:
                # Scale from light blue to dark blue
                if max_val == min_val:
                    intensity = 0.5
                else:
                    intensity = (value - min_val) / (max_val - min_val)
                colors.append(f'rgba(54, 162, 235, {0.2 + intensity * 0.8})')

        return colors

    def generate_gantt(
        self,
        data: List[Dict[str, Any]],
        title: str = "Gantt Chart"
    ) -> Dict[str, Any]:
        """
        Generate Gantt chart configuration.

        Note: Uses floating bar chart for Gantt-like visualization.

        Args:
            data: List of tasks with name, start, duration
            title: Chart title

        Returns:
            Chart.js configuration
        """
        labels = [task["name"] for task in data]
        tasks = []
        for task in data:
            start = self._parse_date(task["start"])
            duration = task.get("duration", 1)
            tasks.append([start, start + duration])

        datasets = [{
            "label": "Timeline",
            "data": tasks,
            "backgroundColor": self.default_colors[0],
            "borderWidth": 1
        }]

        chart_data = {"labels": labels, "datasets": datasets}
        options = {
            "indexAxis": "y",
            "scales": {
                "x": {
                    "position": "top"
                }
            }
        }

        return self.generate_chart(ChartType.BAR, chart_data, title, options)

    def _parse_date(self, date_str: str) -> float:
        """Parse date string to timestamp (simplified)."""
        # In production, use proper date parsing
        # For now, just return a sequential value
        return hash(date_str) % 1000

    def generate_sankey(
        self,
        data: Dict[str, Any],
        title: str = "Sankey Diagram"
    ) -> Dict[str, Any]:
        """
        Generate Sankey diagram configuration.

        Note: Chart.js doesn't have built-in Sankey support.
        This returns a simplified configuration.

        Args:
            data: Sankey data with nodes and links
            title: Chart title

        Returns:
            Chart.js configuration (simplified)
        """
        # Sankey requires specialized library like D3.js
        # Returning a placeholder configuration
        config = {
            "type": "sankey",
            "data": data,
            "options": {
                "title": {
                    "display": True,
                    "text": title
                }
            }
        }
        return config

    def export_to_html(
        self,
        chart_config: Dict[str, Any],
        canvas_id: str,
        width: str = "100%",
        height: str = "400px"
    ) -> str:
        """
        Export chart configuration to HTML snippet.

        Args:
            chart_config: Chart.js configuration
            canvas_id: Canvas element ID
            width: Canvas width
            height: Canvas height

        Returns:
            HTML snippet
        """
        config_json = json.dumps(chart_config, indent=2)

        html = f"""
<div style="position: relative; width: {width}; height: {height};">
    <canvas id="{canvas_id}"></canvas>
</div>
<script>
    const ctx_{canvas_id} = document.getElementById('{canvas_id}').getContext('2d');
    new Chart(ctx_{canvas_id}, {config_json});
</script>
"""
        return html
