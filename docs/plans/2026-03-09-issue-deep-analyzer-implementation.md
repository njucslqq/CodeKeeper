# Issue 深度分析系统实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个基于 LLM 的 Issue 深度分析系统，支持多仓库、多文档系统、多维度分析、可扩展、高并发、服务化部署

**Architecture:**
- Web 服务架构（FastAPI），提供 RESTful API
- 服务启动时加载稳定配置（Git 仓库、文档系统、LLM、降级策略、历史记录）
- 请求参数动态传入（Issue IDs、输出格式、分析维度选择）
- 异步分析 + 并发处理 + WebSocket 进度通知
- Prompt 模板化配置（Markdown 格式，支持自定义扩展）
- 插件系统（目录扫描、独立运行）
- 历史记录管理
- Docker/K8s/本地部署支持，健康检查端点，透明度监控（Prometheus/Telemetry）

**Tech Stack:** FastAPI, Python 3.11+, OpenAI/Anthropic SDK, asyncio, websockets, prometheus_client, uvicorn

---

## 📋 实施阶段总览

本计划分为6个主要阶段，每个阶段完成后需获得批准方可继续：

| 阶段 | 名称 | 任务数 | 预计工作量 |
|--------|------|--------|-----------|
| **P0** | 核心基础设施 | 25 | 基础服务框架 |
| **P1** | 数据获取能力 | 20 | Git + 文档 + Issue |
| **P2** | Prompt 配置与 LLM | 15 | Prompt 系统 + Claude CLI |
| **P3** | 核心分析能力 | 25 | 业务 + 技术 + 流程 |
| **P4** | 并发与输出管理 | 20 | WebSocket + 报告生成 |
| **P5** | 测试与优化 | 30 | 单元测试 + 集成测试 |
| **P6** | 部署支持 | 15 | Docker + 监控 |

---

## 阶段 P0: 核心基础设施

**目标**: 搭建 FastAPI 服务框架，配置管理，基础数据模型

### Task 0.1: 项目结构与依赖配置

**Files:**
- Create: `pyproject.toml`（更新）
- Create: `requirements.txt`（更新）
- Create: `.env.example`
- Create: `README.md`（更新）
- Create: `progress.md`

**Step 1: 写测试验证项目结构**

Create `tests/test_p0_setup.py`:

```python
import os
from pathlib import Path

def test_project_structure():
    root = Path(__file__).parent.parent
    assert root.exists()
    assert (root / "src" / "issue_analyzer").exists()
    assert (root / "tests").exists()
    assert (root / "pyproject.toml").exists()
    assert (root / "progress.md").exists()

def test_fastapi_import():
    from fastapi import FastAPI
    from pydantic import BaseModel
    assert True
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_p0_setup.py -v`
Expected: FAIL - 目录不存在

**Step 3: 创建项目结构和配置文件**

Update `pyproject.toml`:

```toml
[project]
name = "issue-deep-analyzer"
version = "0.1.0"
description = "Deep analysis of issues with LLM"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "pyyaml>=6.0.0",
    "jinja2>=3.1.2",
    "aiohttp>=3.9.0",
    "asyncio>=3.4.3",
    "websockets>=12.0",
    "prometheus-client>=0.19.0",
    "python-gitlab>=4.0.0",
    "requests>=2.31.0",
    "openai>=1.0.0",
    "anthropic>=0.18.0",
    "GitPython>=3.1.40",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.12.0",
    "black>=23.7.0",
    "isort>=5.12.0",
    "mypy>=1.7.0",
    "ruff>=0.1.0",
]

[project.scripts]
issue-analyzer = "issue_analyzer.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100

[tool.black]
line-length = 100
```

Update `requirements.txt`:

```text
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
pyyaml>=6.0.0
jinja2>=3.1.2
aiohttp>=3.9.0
asyncio>=3.4.3
websockets>=12.0
prometheus-client>=0.19.0
python-gitlab>=4.0.0
requests>=2.31.0
openai>=1.0.0
anthropic>=0.18.0
GitPython>=3.1.40
```

Create `.env.example`:

```ini
# Service Configuration
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
SERVICE_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/issue_analyzer.log

# Database
HISTORY_DB_PATH=./history/analysis.db
HISTORY_RETENTION_DAYS=30

# Output
OUTPUT_DIR=./reports
OUTPUT_DEFAULT_FORMAT=html

# Concurrency
MAX_CONCURRENT_ISSUES=5
MAX_CONCURRENT_DIMENSIONS=2

# LLM Configuration
LLM_PROVIDER=claude_cli
LLM_MODEL=claude-3-opus-20240229
LLM_TIMEOUT=300
LLM_MAX_TOKENS=4000
LLM_RETRIES=3
```

Create `src/issue_analyzer/__init__.py`:

```python
"""Issue Deep Analyzer - LLM-powered deep analysis of issues."""

__version__ = "0.1.0"
```

Create `progress.md`:

```markdown
# Issue Deep Analyzer 项目进展

## 版本历史

### v0.1.0 (2026-03-09)

## 实施进度

### 已完成
- 无

### 进行中
- P0: 核心基础设施 (准备中)

### 后续计划
- P1: 数据获取能力
- P2: Prompt 配置与 LLM
- P3: 核心分析能力
- P4: 并发与输出管理
- P5: 测试与优化
- P6: 部署支持

## 需求清单

详见 `docs/plans/2026-03-09-issue-deep-analyzer-prd.md`
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_p0_setup.py -v`
Expected: PASS

**Step 5: 提交**

```bash
git add pyproject.toml requirements.txt .env.example progress.md src/issue_analyzer/
git commit -m "feat(P0): initialize project structure with FastAPI"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

### Task 0.2: 实现配置管理系统

**Files:**
- Create: `src/issue_analyzer/config/__init__.py`
- Create: `src/issue_analyzer/config/settings.py`
- Create: `src/issue_analyzer/config/models.py`
- Create: `ai-analyzer.yaml.example`
- Test: `tests/test_p0_config.py`

**Step 1: 写测试验证配置加载**

Create `tests/test_p0_config.py`:

```python
import tempfile
from pathlib import Path
from issue_analyzer.config import Settings

def test_config_from_file():
    config_content = """
git:
  repos:
    - type: github
      url: https://github.com/test/repo
  auth:
    type: token
    token: ${GITHUB_TOKEN}
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()

        settings = Settings.from_file(Path(f.name))
        assert settings.git.repos[0].type == "github"
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_p0_config.py::test_config_from_file -v`
Expected: FAIL - 模块不存在

**Step 3: 实现配置模型**

Create `src/issue_analyzerator/config/models.py`:

```python
"""Configuration data models."""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Literal
from enum import Enum


class GitHubAuth(BaseModel):
    type: Literal["token", "oauth"] = "token"
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class GitlabAuth(BaseModel):
    type: Literal["token", "oauth"] = "token"
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class GitRepo(BaseModel):
    type: Literal["github", "gitlab", "local"]
    url: Optional[HttpUrl] = None
    path: Optional[str] = None
    auth: Optional[GitHubAuth | GitlabAuth] = None


class ConfluenceAuth(BaseModel):
    type: Literal["pat", "basic"] = "pat"
    api_token: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class FeishuAuth(BaseModel):
    type: Literal["api_key"]
    api_key: Optional[str] = None


class ConfluenceConfig(BaseModel):
    type: Literal["confluence"]
    base_url: HttpUrl
    auth: ConfluenceAuth
    space_key: Optional[str] = None


class FeishuConfig(BaseModelModel):
    type: Literal["feishu"]
    base_url: HttpUrl
    auth: FeishuAuth
    app_id: Optional[str] = None


class LLMProvider(BaseModel):
    type: Literal["claude_cli", "code_cli", "openai", "anthropic"]
    model: str
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
    auth: Optional[GitHubAuth | GitlabAuth] = None
    list_method: Literal["config", "submodule"] = "config"
    superproject_path: Optional[str] = None


class DocSystemConfig(BaseModel):
    systems: List[ConfluenceConfig | FeishuConfig] = []
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
    # Git Configuration
    git: GitConfig = Field(default_factory=GitConfig)

    # Document Systems
    docs: DocSystemConfig = Field(default_factory=DocSystemConfig)

    # LLM Configuration
    llm: LLMProvider = Field(
        default_factory=lambda: LLMProvider(
            type="claude_cli",
            model="claude-3-opus-20240229"
        )
    )

    # Fallback Strategy
    fallback: FallbackStrategy = Field(default_factory=FallbackStrategy)

    # History
    history: HistoryConfig = Field(default_factory=HistoryConfig)

    # Monitoring
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    # Concurrency
    max_concurrent_issues: int = 5
    max_concurrent_dimensions: int = 2

    # Output
    output_dir: str = "./reports"
    default_output_format: Literal["html", "markdown"] = "html"
```

**Step 4: 实现配置管理器**

Create `src/issue_analyzerator/config/settings.py`:

```python
"""Configuration management."""

import os
import yaml
from pathlib import Path
from typing import Optional
from .models import Config


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
        return Config(**data)

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
```

Create `src/issue_analyzerator/config/__init__.py`:

```python
"""Configuration module."""

from .settings import Settings
from .models import Config

__all__ = ["Settings", "Config"]
```

**Step 5: 创建示例配置文件**

Create `ai-analyzer.yaml.example`:

```yaml
# Git Repository Configuration
git:
  repos:
    - type: github
      url: https://github.com/org/repo
      auth:
        type: token
        token: ${GITHUB_TOKEN}

  list_method: config  # or "submodule"

  # For submodule method:
  # superproject_path: /path/to/superproject

# Document Systems
docs:
  systems:
    - type: confluence
      base_url: https://company.atlassian.net
      auth:
        type: pat
        api_token: ${CONFLUENCE_TOKEN}
        email: user@company.com
      space_key: PROJ

    - type: feishu
      base_url: https://open.feishu.cn
      auth:
        type: api_key
        api_key: ${FEISHU_API_KEY}

  naming_pattern: "{issue_id}-*"
  document_types:
    - requirements
    - design

# LLM Configuration
llm:
  type: claude_cli  # or "code_cli", "openai", "anthropic"
  model: claude-3-opus-20240229
  max_tokens: 4000
  temperature: 0.3
  timeout: 300

# Fallback Strategy
fallback:
  retry_max_attempts: 3
  retry_base_delay: 1.0
  retry_backoff_factor: 2.0
  use_backup_model: true
  fallback_to_simple: true

# History
history:
  enabled: true
  path: ./history
  retention_days: 30

# Monitoring
monitoring:
  enabled: true
  metrics_port: 9090
  prometheus_enabled: true
  tracing_enabled: false

# Concurrency
max_concurrent_issues: 5
max_concurrent_dimensions: 2

# Output
output_dir: ./reports
default_output_format: html
```

**Step 6: 运行测试验证通过**

Run: `pytest tests/test_p0_config.py -v`
Expected: PASS

**Step 7: 提交**

```bash
git add src/issue_analyzerator/config/ ai-analyzer.yaml.example tests/test_p0_config.py
git commit -m "feat(P0): implement configuration management system"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

### Task 0.3: 实现数据模型

**Files:**
- Create: `src/issue_analyzer/models/__init__.py`
- Create: `src/issue_analyzer/models/issue.py`
- Create: `src/issue_analyzer/models/commit.py`
- Create: `src/issue_analyzer/models/document.py`
- Create: `src/issue_analyzer/models/analysis.py`
- Test: `tests/test_p0_models.py`

**Step 1: 写测试验证数据模型**

Create `tests/test_p0_models.py`:

```python
from issue_analyzer.models import Issue, Commit, Document, AnalysisTask, TaskStatus

def test_issue_model():
    issue = Issue(
        id="PROJ-123",
        key="PROJ-123",
        summary="Test issue",
        status=TaskStatus.TODO
    )
    assert issue.id == "PROJ-123"
    assert issue.status == TaskStatus.TODO
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_p0_models.py::test_issue_model -v`
Expected: FAIL - 模块不存在

**Step 3: 实现数据模型**

Create `src/issue_analyzer/models/__init__.py`:

```python
"""Data models."""

from .issue import Issue, IssueStatus, IssueRelation
from .commit import Commit, CommitFileChange
from .document import Document, DocumentType
from .analysis import AnalysisTask, TaskStatus, AnalysisResult, AnalysisDimension

__all__ = [
    "Issue", "IssueStatus", "IssueRelation",
    "Commit", "CommitFileChange",
    "Document", "DocumentType",
    "AnalysisTask", "TaskStatus", "AnalysisResult", "AnalysisDimension"
]
```

Create `src/issue_analyzer/models/issue.py`:

```python
"""Issue related models."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class IssueStatus(str, Enum):
    """Issue status enumeration."""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CLOSED = "closed"


class IssueRelationType(str, Enum):
    """Issue relation type enumeration."""
    RELATED = "related"
    DERIVED = "derived"
    BLOCKED = "blocked"
    BLOCKS = "blocks"


class IssueRelation(BaseModel):
    """Issue relation model."""
    type: IssueRelationType
    issue_id: str
    url: Optional[str] = None


class Issue(BaseModel):
    """Issue model."""
    id: str
    key: str
    summary: str
    description: Optional[str] = None
    status: IssueStatus = IssueStatus.TODO
    priority: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    reporter: Optional[str] = None
    assignee: Optional[str] = None
    relations: List[IssueRelation] = Field(default_factory=list)
```

Create `src/issue_analyzer/models/commit.py`:

```python
"""Commit related models."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ChangeType(str, Enum):
    """File change type enumeration."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class CommitFileChange(BaseModel):
    """File change model."""
    path: str
    old_path: Optional[str] = None
    change_type: ChangeType
    additions: int = 0
    deletions: int = 0
    is_binary: bool = False


class Commit(BaseModel):
    """Commit model."""
    hash: str
    short_hash: str = Field(default="")
    message: str
    author: str
    author_email: str
    author_time: datetime = Field(default_factory=datetime.utcnow)
    commit_time: datetime = Field(default_factory=datetime.utcnow)
    parents: List[str] = Field(default_factory=list)
    files_changed: List[CommitFileChange] = Field(default_factory=list)
    diff: Optional[str] = None
    repository: Optional[str] = None

    def __post_init__(self):
        if not self.short_hash:
            self.short_hash = self.hash[:7]
```

Create `src/issue_analyzer/models/document.py`:

```python
"""Document related models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration."""
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    RELEASE = "release"
    OPERATIONS = "operations"
    CUSTOM = "custom"


class Document(BaseModel):
    """Document model."""
    id: str
    type: DocumentType
    title: str
    content: str
    issue_id: str
    url: Optional[str] = None
    source: str  # e.g., "confluence", "feishu"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

Create `src/issue_analyzer/models/analysis.py`:

```python
"""Analysis related models."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnalysisDimension(str, Enum):
    """Analysis dimension enumeration."""
    BUSINESS = "business"
    TECHNICAL = "technical"
    PROCESS = "process"


class AnalysisResult(BaseModel):
    """Analysis result model."""
    dimension: AnalysisDimension
    sub_dimension: Optional[str] = None
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    recommendations: List[str] = Field(default_factory=list)
    duration_seconds: float = 0


class AnalysisTask(BaseModel):
    """Analysis task model."""
    id: str
    issue_id: str
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    dimensions: List[AnalysisDimension] = Field(default_factory=list)
    results: List[AnalysisResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    output_format: str = "html"
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_p0_models.py -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/issue_analyzer/models/ tests/test_p0_models.py
git commit -m "feat(P0): implement data models for issues, commits, documents, analysis"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

### Task 0.4: 实现日志系统

**Files:**
- Create: `src/issue_analyzer/logger.py`
- Test: `tests/test_p0_logger.py`

**Step 1: 写测试验证日志系统**

Create `tests/test_p0_logger.py`:

```python
import tempfile
from pathlib import Path
from issue_analyzer.logger import Logger, get_logger

def test_logger_creation():
    logger = get_logger("test")
    assert logger is not None

def test_file_logging():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "test.log"
        logger = Logger("test", file_path=log_path, level="INFO")
        logger.info("Test message")
        assert log_path.exists()
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_p0_logger.py -v`
Expected: FAIL - 模块不存在

**Step 3: 实现日志系统**

Create `src/issue_analyzer/logger.py`:

```python
"""Logging system."""

import logging
import sys
from pathlib import Path
from typing import Optional
from contextvars import ContextVar


_task_id_context: ContextVar[Optional[str]] = ContextVar("task_id", default=None)


def get_task_id() -> Optional[str]:
    """Get current task ID from context."""
    return _task_id_context.get()


def set_task_id(task_id: Optional[str]):
    """Set task ID in context."""
    _task_id_context.set(task_id)


class Logger:
    """Application logger with task context."""

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        file_path: Optional[Path] = None,
        console: bool = True
    ):
        self.name = name
        self.logger = logging.getLogger(f"issue_analyzer.{name}")
        self.logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        self.logger.handlers.clear()

        # Console handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self._get_formatter(console=True))
            self.logger.addHandler(console_handler)

        # File handler
        if file_path:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setFormatter(self._get_formatter(console=False))
            self.logger.addHandler(file_handler)

    @staticmethod
    def _get_formatter(console: bool) -> logging.Formatter:
        """Get log formatter."""
        if console:
            return logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                '%Y-%m-%d %H:%M:%S'
            )
        else:
            return logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(task_id)s | %(message)s',
                '%Y-%m-%d %H:%M:%S'
            )

    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with task context."""
        extra = {'task_id': get_task_id()}
        self.logger.log(level, message, extra=extra, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)


# Global logger cache
_loggers: dict = {}


def get_logger(name: str, **kwargs) -> Logger:
    """Get or create logger."""
    if name not not in _loggers:
        _loggers[name] = Logger(name, **kwargs)
    return _loggers[name]
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_p0_logger.py -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/issue_analyzer/logger.py tests/test_p0_logger.py
git commit -m "feat(P0): implement logging system with task context"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

### Task 0.5: 实现健康检查端点

**Files:**
- Create: `src/issue_analyzer/api/health.py`
- Modify: `src/issue_analyzer/main.py`

**Step 1: 写测试验证健康检查**

Create `tests/test_p0_health.py`:

```python
from fastapi.testclient import TestClient
from issue_analyzer.main import app

def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_p0_health.py::test_health_endpoint -v`
Expected: FAIL - 端点不存在

**Step 3: 实现健康检查端点**

Create `src/issue_analyzer/api/health.py`:

```python
"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_seconds: float
    dependencies: Dict[str, str] = {}


router = APIRouter(prefix="/health", tags=["health"])

_uptime_start: float = 0


def get_uptime() -> float:
    """Get service uptime in seconds."""
    import time
    return time.time() - _uptime_start


def start_uptime_timer():
    """Start uptime timer."""
    global _uptime_start
    import time
    _uptime_start = time.time()


@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from issue_analyzer import __version__

    # Check dependencies (simplified)
    dependencies = {"fastapi": "healthy", "llm": "unknown"}

    return HealthResponse(
(
        status="healthy",
        version=__version__,
        uptime_seconds=get_uptime(),
        dependencies=dependencies
    )
```

**Step 4: 注册健康检查端点到主应用**

Create `src/issue_analyzer/main.py`:

```python
"""Main application entry point."""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add src to path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from issue_analyzer.api.health import router as health_router, start_uptime_timer
from issue_analyzer.config import Settings
from issue_analyzer.logger import get_logger

# Create FastAPI app
app = FastAPI(
    title="Issue Deep Analyzer",
    description="LLM-powered deep analysis of issues",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
settings: Settings = None
logger = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global settings, logger

    # Startup
    logger = get_logger("main", level="INFO")
    logger.info("Starting Issue Deep Analyzer")

    # Load configuration
    config_path = os.getenv("CONFIG_PATH")
    settings = Settings(config_path=Path(config_path) if config_path else None)
    logger.info(f"Configuration loaded from: {config_path}")

    # Start uptime timer
    start_uptime_timer()

    yield

    # Shutdown
    logger.info("Shutting down Issue Deep Analyzer")


app.router.lifespan_context = lifespan

# Register routers
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Issue Deep Analyzer API", "version": "0.1.0"}


def main():
    """Main entry point."""
    import uvicorn

    host = os.getenv("SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SERVICE_PORT", "8000"))
    workers = int(os.getenv("SERVICE_WORKERS", "4"))

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "issue_analyzer.main:app",
        host=host,
        port=port,
        workers=workers if workers > 1 else None,
        log_level="info"
    )


if __name__ == "__main__":
    main()
```

**Step 5: 运行测试验证通过**

Run: `pytest tests/test_p0_health.py::test_health_endpoint -v`
Expected: PASS

**Step 6: 提交**

```bash
git add src/issue_analyzer/api/ src/issue_analyzer/main.py tests/test_p0_health.py
git commit -m "feat(P0): implement health check endpoint and main application"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

### Task 0.6: 实现监控指标

**Files:**
- Create: `src/issue_analyzer/metrics.py`
- Modify: `src/issue_analyzer/main.py`

**Step 1: 写测试验证监控指标**

Create `tests/test_p0_metrics.py`:

```python
from issue_analyzer.metrics import MetricsRegistry

def test_metrics_registry():
    registry = MetricsRegistry()
    registry.increment("requests_total")
    assert registry.get("requests_total") == 1
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_p0_metrics.py::test_metrics_registry -v`
Expected: FAIL - 模块不存在

**Step 3: 实现监控指标系统**

Create `src/issue_analyzer/metrics.py`:

```python
"""Monitoring metrics system."""

import time
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from typing import Optional


# Custom metrics registry
registry = CollectorRegistry()

# Request metrics
requests_total = Counter(
    "requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"],
    registry=registry
)

request_duration = Histogram(
    "request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.5, 1.0, 5.0],
    registry=registry
)

# Analysis metrics
analysis_tasks_total = Counter(
    "analysis_tasks_total",
    "Total number of analysis tasks",
    ["status"],
    registry=registry
)

analysis_duration = Histogram(
    "analysis_duration_seconds",
    "Analysis duration in seconds",
    ["dimension"],
    buckets=[10, 30, 60, 120, 300, 600, 1800],
    registry=registry
)

# LLM metrics
llm_calls_total = Counter(
    "llm_calls_total",
    "Total number of LLM calls",
    ["provider", "model", "status"],
    registry=registry
)

llm_duration = Histogram(
    "llm_duration_seconds",
    "LLM call duration in seconds",
    ["provider", "model"],
    buckets=[1, 5, 10, 30, 60, 120],
    registry=registry
)

# Concurrency metrics
active_tasks = Gauge(
    "active_tasks",
    "Number of currently active tasks",
    ["type"],
    registry=registry
)

queue_length = Gauge(
    "queue_length",
    "Number of tasks in queue",
    registry=registry
)


class MetricsRegistry:
    """Metrics registry for application metrics."""

    @staticmethod
    def increment_requests_total(method: str, endpoint: str, status: str):
        """Increment request counter."""
        requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

    @staticmethod
    def observe_request_duration(method: str, endpoint: str, duration: float):
        """Observe request duration."""
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    @staticmethod
    def increment_analysis_tasks(status: str):
        """Increment analysis task counter."""
        analysis_tasks_total.labels(status=status).inc()

    @staticmethod
    def observe_analysis_duration(dimension: str, duration: float):
        """Observe analysis duration."""
        analysis_duration.labels(dimension=dimension).observe(duration)

    @staticmethod
    def increment_llm_calls(provider: str, model: str, status: str):
        """Increment LLM call counter."""
        llm_calls_total.labels(provider=provider, model=model, status=status).inc()

    @staticmethod
    def observe_llm_duration(provider: str, model: str, duration: float):
        """Observe LLM call duration."""
        llm_duration.labels(provider=provider, model=model).observe(duration)

    @staticmethod
    def set_active_tasks(task_type: str, value: int):
        """Set active tasks gauge."""
        active_tasks.labels(type=task_type).set(value)

    @staticmethod
    def set_queue_length(value: int):
        """Set queue length gauge."""
        queue_length.set(value)

    @staticmethod
    def get(metric_name: str) -> float:
        """Get metric value (simplified)."""
        # Simplified implementation
        if metric_name == "requests_total":
            return requests_total._value.get()
        return 0.0
```

**Step 4: 注册监控端点到主应用**

Update `src/issue_analyzer/main.py`:

```python
# ... existing imports ...

from issue_analyzer.metrics import registry as metrics_registry

# ... existing code ...

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest
    return generate_latest(metrics_registry)

# ... rest of code ...
```

**Step 5: 运行测试验证通过**

Run: `pytest tests/test_p0_metrics.py::test_metrics_registry -v`
Expected: PASS

**Step 6: 提交**

```bash
git add src/issue_analyzer/metrics.py src/issue_analyzer/main.py tests/test_p0_metrics.py
git commit -m "feat(P0): implement monitoring metrics with Prometheus"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## 阶段 P0 完成检查

**验证清单:**
- [x] 项目结构与依赖配置
- [x] 配置管理系统
- [x] 数据模型（Issue, Commit, Document, Analysis）
- [x] 日志系统（支持任务上下文）
- [x] 健康检查端点
- [x] 监控指标（Prometheus）

**测试覆盖:** 运行 `pytest tests/test_p0_* -v --cov=src/issue_analyzerator`
**预期覆盖率:** > 80%

---

## 后续阶段概要

### P1: 数据获取能力（20个任务）
- Git 仓库集成（GitHub, GitLab）
- 文档系统集成（Confluence, 飞书）
- Issue 基础信息获取
- Commit 消息解析（可扩展）
- 文档命名解析（可扩展）

### P2: Prompt 配置与 LLM（15个任务）
- Prompt 模板系统
- Claude CLI 集成（优先）
- Prompt 自定义支持
- LLM 调用抽象
- 降级策略实现

### P3: 核心分析能力（25个任务）
- 业务维度分析
- 技术维度分析
- 流程维度分析
- 维度扩展架构
- 子维度扩展架构

### P4: 并发与输出管理（20个任务）
- 异步任务队列
- WebSocket 进度通知
- 并发控制
- 报告生成（HTML/Markdown）
- 输出管理（合并/独立）

### P5: 测试与优化（30个任务）
- 单元测试（覆盖率 85%+）
- 集成测试
- Mock LLM 模块
- 性能测试
- 错误处理测试

### P6: 部署支持（15个任务）
- Docker 配置
- Docker Compose
- K8s 配置（后续）
- 本地运行配置
- Grafana 仪表盘（后续）

---

## 📝 执行说明

1. **每个 Task 完成后**: 运行测试验证，然后提交
2. **阶段完成后**: 运行阶段测试套件，检查覆盖率
3. **获得批准**: P0 完成后请确认是否继续 P1

**P0 完成后请运行:**
```bash
pytest tests/test_p0_* -v --cov=src/issue_analyzerator --cov-report=html
```

---

**更新 progress.md**: 将 P0 标记为完成，记录完成时间和关键决策。
