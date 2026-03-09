"""Configuration management."""

import os
import yaml
from pathlib import Path
from typing import Optional
from .models import Config


def _expand_env_vars(value):
    """Expand environment variables in a string."""
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        return os.getenv(env_var, value)
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env_vars(item) for item in value]
    return value


class Settings:
    """Application settings manager."""

    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path
        self._config: Optional[Config] = None
        self._load_config()

    def _load_config(self):
        """Load configuration from file or create default."""
        if self._config_path and self._config_path.exists():
            self._config = self._load_from_file(self._config_path)
        else:
            self._config = Config()

    def _load_from_file(self, path: Path) -> Config:
        """Load configuration from YAML file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        expanded_data = _expand_env_vars(data)
        return Config(**expanded_data)

    @property
    def config(self) -> Config:
        """Get current configuration."""
        return self._config

    @classmethod
    def from_file(cls, path: Path) -> "Settings":
        """Create Settings from file."""
        return cls(config_path=path)

    def reload(self):
        """Reload configuration from file."""
        if self._config_path:
            self._load_config()
