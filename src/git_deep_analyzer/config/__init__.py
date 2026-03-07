from .config import Config, GitConfig, AnalysisConfig, OutputConfig, AIConfig, ReportingConfig
from .hot_reload import ConfigReloader, ConfigWatcher

__all__ = [
    "Config", "GitConfig", "AnalysisConfig", "OutputConfig",
    "AIConfig", "ReportingConfig",
    "ConfigReloader", "ConfigWatcher"
]

# 可选导入（需要click）
try:
    from .interactive import interactive_setup, save_config_to_file
    __all__.extend(["interactive_setup", "save_config_to_file"])
except ImportError:
    pass
