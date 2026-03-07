"""Plugin system for extensible integrations."""

from .plugin_base import (
    PluginBase,
    IssueTrackerPlugin,
    DocsSystemPlugin,
    AnalyzerPlugin,
    PluginManager
)

__all__ = [
    "PluginBase",
    "IssueTrackerPlugin",
    "DocsSystemPlugin",
    "AnalyzerPlugin",
    "PluginManager"
]
