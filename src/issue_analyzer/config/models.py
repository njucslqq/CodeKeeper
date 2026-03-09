"""Configuration data models."""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from enum import Enum


class GitHubAuth(BaseModel):
    type: str = "token"
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class GitlabAuth(BaseModel):
    type: str = "token"
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class GitRepo(BaseModel):
    type: str
    url: Optional[HttpUrl] = None
    path: Optional[str] = None
    auth: Optional[Union[GitHubAuth, GitlabAuth]] = None


class ConfluenceAuth(BaseModel):
    type: str = "pat"
    api_token: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class FeishuAuth(BaseModel):
    type: str = "api_key"
    api_key: Optional[str] = None


class ConfluenceConfig(BaseModel):
    type: str = "confluence"
    base_url: HttpUrl
    auth: ConfluenceAuth
    space_key: Optional[str] = None


class FeishuConfig(BaseModel):
    type: str = "feishu"
    base_url: HttpUrl
    auth: FeishuAuth
    app_id: Optional[str] = None


class LLMProvider(BaseModel):
    type: str = "claude_cli"
    model: str = "claude-3-opus-20240229"
    api_key: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    max_tokens: int = 4000
    temperature: float = 0.3
    timeout: int = 300


class FallbackStrategy(BaseModel):
    retry_max_attempts: int = 3
    retry_base_delay: float = 1.0
    retry_backoff_factor: float = 2.0
    use_backup_model: bool = True
    fallback_to_simple: bool = True


class GitConfig(BaseModel):
    repos: List[GitRepo] = []
    auth: Optional[Union[GitHubAuth, GitlabAuth]] = None
    list_method: str = "config"
    superproject_path: Optional[str] = None


class DocSystemConfig(BaseModel):
    systems: List[Union[ConfluenceConfig, FeishuConfig]] = []
    naming_pattern: str = "{issue_id}-*"
    document_types: List[str] = ["requirements", "design"]


class HistoryConfig(BaseModel):
    enabled: bool = True
    path: str = "./history"
    retention_days: int = 30


class MonitoringConfig(BaseModel):
    enabled: bool = True
    metrics_port: int = 9090
    prometheus_enabled: bool = True
    tracing_enabled: bool = False


class Config(BaseModel):
    git: GitConfig = Field(default_factory=GitConfig)
    docs: DocSystemConfig = Field(default_factory=DocSystemConfig)
    llm: LLMProvider = Field(default_factory=LLMProvider)
    fallback: FallbackStrategy = Field(default_factory=FallbackStrategy)
    history: HistoryConfig = Field(default_factory=HistoryConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    max_concurrent_issues: int = 5
    max_concurrent_dimensions: int = 2
    output_dir: str = "./reports"
    default_output_format: str = "html"
