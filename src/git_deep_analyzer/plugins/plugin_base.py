"""Plugin system for extensible external system integrations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
import importlib
import inspect


class PluginBase(ABC):
    """Base class for all plugins."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize plugin.

        Args:
            config: Plugin configuration
        """
        self.config = config
        self.name = self.__class__.__name__
        self.version = getattr(self, 'VERSION', '1.0.0')

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize plugin.

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute plugin functionality.

        Returns:
            Plugin execution result
        """
        pass

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.

        Returns:
            Plugin metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.__doc__ or "",
            "class": self.__class__.__name__
        }


class IssueTrackerPlugin(PluginBase):
    """Base class for issue tracker plugins."""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to issue tracker system."""
        pass

    @abstractmethod
    def fetch_issues(self, **kwargs) -> List[Any]:
        """Fetch issues from tracker."""
        pass

    @abstractmethod
    def search_issues(self, query: str, **kwargs) -> List[Any]:
        """Search issues in tracker."""
        pass


class DocsSystemPlugin(PluginBase):
    """Base class for documentation system plugins."""

    @abstractmethod
    def fetch_documents(self, **kwargs) -> List[Any]:
        """Fetch documents from system."""
        pass

    @abstractmethod
    def fetch_document_detail(self, doc_id: str, **kwargs) -> Any:
        """Fetch document details."""
        pass


class AnalyzerPlugin(PluginBase):
    """Base class for analyzer plugins."""

    @abstractmethod
    def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Analyze data and return results."""
        pass


class PluginManager:
    """Manager for loading and managing plugins."""

    def __init__(self, plugin_paths: Optional[List[str]] = None):
        """
        Initialize plugin manager.

        Args:
            plugin_paths: List of directories to search for plugins
        """
        self.plugin_paths = plugin_paths or ["git_deep_analyzer.plugins"]
        self._plugins: Dict[str, PluginBase] = {}
        self._loaded: bool = False

    def discover_plugins(self) -> Dict[str, Type[PluginBase]]:
        """
        Discover available plugins.

        Returns:
            Dictionary of plugin name to plugin class
        """
        discovered = {}

        for plugin_path in self.plugin_paths:
            try:
                modules = importlib.import_module(plugin_path)
            except ImportError:
                continue

            # Find all plugin classes in module
            for name, obj in inspect.getmembers(modules):
                if (inspect.isclass(obj) and
                    issubclass(obj, PluginBase) and
                    obj != PluginBase):
                    discovered[name] = obj

        return discovered

    def load_plugin(
        self,
        plugin_class: Type[PluginBase],
        config: Dict[str, Any]
    ) -> Optional[PluginBase]:
        """
        Load and initialize a plugin.

        Args:
            plugin_class: Plugin class to load
            config: Plugin configuration

        Returns:
            Plugin instance or None if failed
        """
        try:
            plugin = plugin_class(config)
            if plugin.initialize():
                return plugin
        except Exception as e:
            print(f"Failed to load plugin {plugin_class.__name__}: {e}")
            return None

    def load_plugins(
        self,
        plugin_classes: Dict[str, Type[PluginBase]],
        configs: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Load multiple plugins.

        Args:
            plugin_classes: Dictionary of plugin name to plugin class
            configs: Dictionary of plugin name to configuration
        """
        for name, plugin_class in plugin_classes.items():
            config = configs.get(name, {})
            plugin = self.load_plugin(plugin_class, config)
            if plugin:
                self._plugins[name] = plugin

    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """
        Get loaded plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not loaded
        """
        return self._plugins.get(name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all loaded plugins.

        Returns:
            List of plugin information dictionaries
        """
        return [plugin.get_info() for plugin in self._plugins.values()]

    def execute_plugin(
        self,
        name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a loaded plugin.

        Args:
            name: Plugin name
            *args: Arguments to pass to plugin
            **kwargs: Keyword arguments to pass to plugin

        Returns:
            Plugin execution result
        """
        plugin = self.get_plugin(name)
        if not plugin:
            raise ValueError(f"Plugin {name} not loaded")

        return plugin.execute(*args, **kwargs)

    def cleanup_all(self) -> None:
        """Clean up all loaded plugins."""
        for plugin in self._plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"Error cleaning up plugin {plugin.name}: {e}")

        self._plugins.clear()
