from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import yaml
import os
from datetime import datetime


class ConfigError:
    """配置错误"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

    def __str__(self):
        return f"{self.field}: {self.message}"


@dataclass
class GitConfig:
    """Git配置"""
    repo_path: Path
    branch: str = "main"
    time_filter_mode: str = "date_range"
    time_filter_date_range_since: Optional[str] = None
    time_filter_date_range_until: Optional[str] = None
    time_filter_last_n_days: Optional[int] = None
    time_basis: str = "author_time"


@dataclass
class OutputConfig:
    """输出配置"""
    formats: list = field(default_factory=lambda: ["html", "markdown"])
    directory: str = "./reports"
    filename_pattern: str = "{repo}-{branch}-{timestamp}"


@dataclass
class AnalysisConfig:
    """分析配置"""
    git: GitConfig
    languages: dict = field(default_factory=lambda: {"primary": ["cpp", "python"], "fallback": "auto"})
    output: OutputConfig = field(default_factory=OutputConfig)


@dataclass
class AIProviderConfig:
    """AI提供商配置"""
    type: str = "api"
    name: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.3


@dataclass
class AICLIConfig:
    """AI CLI配置"""
    command: str = "claude"
    args: list = field(default_factory=list)
    env_vars: list = field(default_factory=list)


@dataclass
class AIErrorHandling:
    """AI错误处理配置"""
    retry_enabled: bool = True
    retry_max_attempts: int = 3
    retry_backoff: str = "exponential"
    timeout_enabled: bool = True
    timeout_seconds: int = 300
    on_failure: str = "retry"  # retry | continue | abort | fallback


@dataclass
class AILogging:
    """AI日志配置"""
    level: str = "debug"
    log_file: str = "./ai_analysis.log"
    log_to_stdout: bool = True


@dataclass
class AIConfig:
    """AI配置"""
    enabled: bool = True
    provider: AIProviderConfig = field(default_factory=AIProviderConfig)
    cli: Optional[AICLIConfig] = None
    error_handling: AIErrorHandling = field(default_factory=AIErrorHandling)
    logging: AILogging = field(default_factory=AILogging)
    execution_strategy: str = "serial"


@dataclass
class ReportingConfig:
    """报告配置"""
    sections: list = field(default_factory=lambda: ["overview", "technical", "business", "evolution"])
    include_raw_data: bool = False
    language: str = "zh-CN"
    detail_level: str = "standard"


@dataclass
class Config:
    """主配置类"""
    analysis: AnalysisConfig
    ai: AIConfig = field(default_factory=AIConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)

    @classmethod
    def load_from_file(cls, path: Path) -> "Config":
        """从YAML文件加载配置"""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls._parse_config(data)

    @classmethod
    def _parse_config(cls, data: Dict) -> "Config":
        """解析配置数据"""
        # Git配置
        git_data = data.get("analysis", {}).get("git", {})
        git_config = GitConfig(
            repo_path=Path(git_data.get("repo_path")),
            branch=git_data.get("branch", "main"),
            time_filter_mode=git_data.get("time_filter", {}).get("mode", "date_range"),
            time_basis=git_data.get("time_filter", {}).get("time_basis", "author_time")
        )

        # 输出配置
        output_data = data.get("analysis", {}).get("output", {})
        output_config = OutputConfig(
            formats=output_data.get("formats", ["html", "markdown"]),
            directory=output_data.get("directory", "./reports"),
            filename_pattern=output_data.get("filename_pattern", "{repo}-{branch}-{timestamp}")
        )

        # AI配置
        ai_data = data.get("ai", {})
        ai_config = AIConfig(
            enabled=ai_data.get("enabled", True),
            error_handling=AIErrorHandling(
                timeout_seconds=ai_data.get("cli", {}).get("error_handling", {}).get("timeout", {}).get("seconds", 300)
            )
        )

        # 报告配置
        reporting_data = data.get("reporting", {})
        reporting_config = ReportingConfig(
            include_raw_data=reporting_data.get("include_raw_data", False),
            language=reporting_data.get("language", "zh-CN"),
            detail_level=reporting_data.get("detail_level", "standard")
        )

        return cls(
            analysis=AnalysisConfig(git=git_config, output=output_config),
            ai=ai_config,
            reporting=reporting_config
        )

    def expand_env_vars(self):
        """展开环境变量"""
        if self.ai.provider.api_key and self.ai.provider.api_key.startswith("${"):
            var_name = self.ai.provider.api_key[2:-1]
            self.ai.provider.api_key = os.environ.get(var_name)

    def validate(self, skip_connection_test: bool = False) -> List[ConfigError]:
        """验证配置"""
        errors = []

        # 验证Git仓库
        if not self.analysis.git.repo_path.exists():
            errors.append(ConfigError("git.repo_path", "repository path does not exist"))
        elif not (self.analysis.git.repo_path / ".git").exists():
            errors.append(ConfigError("git.repo_path", "not a git repository"))

        # 验证时间过滤配置
        if self.analysis.git.time_filter_mode == "date_range":
            if not self.analysis.git.time_filter_date_range_since:
                errors.append(ConfigError("git.time_filter.since", "since date is required"))
        elif self.analysis.git.time_filter_mode == "last_n_days":
            if not self.analysis.git.time_filter_last_n_days:
                errors.append(ConfigError("git.time_filter.days", "days is required"))

        # 验证AI配置
        if self.ai.enabled:
            if not self.ai.provider.api_key and not os.environ.get("OPENAI_API_KEY"):
                errors.append(ConfigError("ai.api_key", "API key is required"))

        return errors
