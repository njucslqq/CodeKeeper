"""Report generation module."""

from .models import (
    ReportFormat,
    ReportDetailLevel,
    ReportSection,
    ReportData
)
from .html_generator import HTMLGenerator
from .markdown_generator import MarkdownGenerator
from .data_visualizer import DataVisualizer, ChartType
from .report_interactions import ReportInteractions
from .multi_detail_reports import ReportDetailAdapter

__all__ = [
    "ReportFormat",
    "ReportDetailLevel",
    "ReportSection",
    "ReportData",
    "HTMLGenerator",
    "MarkdownGenerator",
    "DataVisualizer",
    "ChartType",
    "ReportInteractions",
    "ReportDetailAdapter"
]
