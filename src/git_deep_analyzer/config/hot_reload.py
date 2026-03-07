"""Hot configuration reloading support."""

from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
import yaml
import threading
import time


class ConfigWatcher:
    """Watcher for configuration file changes."""

    def __init__(
        self,
        config_path: str,
        callback: Callable[[Dict[str, Any]], None],
        poll_interval: float = 1.0
    ):
        """
        Initialize config watcher.

        Args:
            config_path: Path to configuration file
            callback: Function to call when config changes
            poll_interval: Polling interval in seconds
        """
        self.config_path = Path(config_path)
        self.callback = callback
        self.poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_mtime: Optional[float] = None

    def start(self) -> None:
        """Start watching configuration file."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop watching configuration file."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    def _watch_loop(self) -> None:
        """Main watching loop."""
        while self._running:
            try:
                # Check file modification time
                mtime = self.config_path.stat().st_mtime

                # If file changed
                if self._last_mtime is None or mtime != self._last_mtime:
                    self._last_mtime = mtime

                    # Load new configuration
                    new_config = self._load_config()

                    # Call callback with new config
                    if new_config:
                        self.callback(new_config)

                # Wait before next check
                time.sleep(self.poll_interval)

            except FileNotFoundError:
                # Config file might have been deleted
                time.sleep(self.poll_interval)
            except Exception as e:
                # Log error but continue watching
                print(f"Error watching config: {e}")
                time.sleep(self.poll_interval)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}


class ConfigReloader:
    """Manager for hot configuration reloading."""

    def __init__(self, config_path: str):
        """
        Initialize config reloader.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self._watcher: Optional[ConfigWatcher] = None
        self._reload_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._current_config: Dict[str, Any] = {}

    def add_reload_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add callback to be called on config reload.

        Args:
            callback: Function to call with new configuration
        """
        self._reload_callbacks.append(callback)

    def start_watching(self) -> None:
        """Start watching configuration file for changes."""
        if self._watcher is not None:
            return

        # Load initial configuration
        self._current_config = self._load_config()
        notify_all_callbacks(self._current_config)

        # Start watcher
        self._watcher = ConfigWatcher(
            self.config_path,
            self._on_config_change,
            poll_interval=2.0
        )
        self._watcher.start()

    def stop_watching(self) -> None:
        """Stop watching configuration file."""
        if self._watcher:
            self._watcher.stop()
            self._watcher = None

    def reload(self) -> Dict[str, Any]:
        """
        Manually reload configuration.

        Returns:
            New configuration
        """
        new_config = self._load_config()
        self._current_config = new_config
        notify_all_callbacks(new_config)
        return new_config

    def get_current_config(self) -> Dict[str, Any]:
        """
        Get current configuration.

        Returns:
            Current configuration dictionary
        """
        return self._current_config

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update configuration and save to file.

        Args:
            updates: Dictionary of configuration updates

        Returns:
            Updated configuration
        """
        # Merge updates with current config
        new_config = {**self._current_config, **updates}

        # Write to file
        self._save_config(new_config)

        # Update current config
        self._current_config = new_config

        return new_config

    def _on_config_change(self, new_config: Dict[str, Any]) -> None:
        """Handle configuration change."""
        self._current_config = new_config
        notify_all_callbacks(new_config)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            config_path = Path(self.config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")


def notify_all_callbacks(
    callbacks: List[Callable[[Dict[str, Any]], None]],
    config: Dict[str, Any]
) -> None:
    """Notify all registered callbacks."""
    for callback in callbacks:
        try:
            callback(config)
        except Exception as e:
            print(f"Error in config reload callback: {e}")
